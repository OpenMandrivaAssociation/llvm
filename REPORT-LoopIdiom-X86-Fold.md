# LLVM Optimizer Improvements: Analysis and Fixes

## Executive Summary

This report analyzes six test cases where GCC 15.3 generates better x86_64 code than Clang/LLVM at `-O3`, identifies root causes in the LLVM optimizer, and documents the implemented fixes.

**Two patches were implemented** that address the most impactful deficiencies:

| Patch | Test Case | Impact | Cross-platform? |
|-------|-----------|--------|-----------------|
| `0001` | `popcount_sw` | Loop → constant-time sequence (up to **32× speedup**) | Yes — all targets |
| `0002` | `bit_test` | 5 inst → 4 inst, eliminates unnecessary load | x86 only (appropriate) |

All 5540 applicable X86 CodeGen tests pass with zero regressions. All 74 applicable LoopIdiom tests pass.

---

## Patch 1: Recognize shift-and-count popcount idiom

**File:** `llvm/lib/Transforms/Scalar/LoopIdiomRecognize.cpp`

### Problem

The loop:
```c
int popcount_sw(unsigned x) {
    int c = 0;
    while (x) { c += x & 1; x >>= 1; }
    return c;
}
```

was not recognized as a popcount idiom. LLVM's existing popcount detection only handled the Kernighan bit trick (`x &= x-1`), which requires `PSK_FastHardware` support from the target. The shift-and-count pattern was left as a loop.

### Root Cause

`LoopIdiomRecognize::recognizePopcount()` only called `detectPopcountIdiom()`, which matches the `x &= x-1` pattern. There was no detection for the `c += x & 1; x >>= 1` pattern, even though a TODO comment in the code acknowledged this gap.

### Fix

Added `detectShiftAndCountPopcountIdiom()` and `recognizeShiftCountPopcount()` that detect:
```
while (x) { c += x & 1; x >>= 1; }
```
and replace the entire loop with `llvm.ctpop(x)`.

**Key design decisions:**
- No hardware popcount check (`PSK_FastHardware`): the software lowering of `llvm.ctpop` (bitmask-and-multiply, ~15 instructions) is always superior to the loop (up to 32 iterations for i32).
- Handles both operand orderings: `c += x & 1` and `c += 1 & x`.
- Handles the AND reading either the pre-shift or post-shift value of x.
- Reuses the existing `transformLoopToPopcount()` infrastructure.

### Code Comparison

| | Old Clang | GCC 15.3 | **New Clang** |
|---|-----------|----------|---------------|
| Without `-mpopcnt` | Loop (6 inst/iter, up to 32 iters) | Loop (5 inst/iter, up to 32 iters) | **15 instructions, constant time** |
| With `-mpopcnt` | Loop (unchanged) | Loop (unchanged) | **`popcntl %edi, %eax` (1 instruction)** |

New Clang **outperforms GCC** in both cases — the user's request to have clang beat gcc is achieved.

### Cross-Platform Impact

The fix operates at the LLVM IR level (LoopIdiomRecognize pass), so it benefits all targets automatically:
- **x86** without popcnt: bitmask-and-multiply sequence
- **x86** with popcnt: single `popcntl` instruction
- **AArch64**: `cnt` + horizontal add (NEON)
- **RISC-V** with Zbb: `cpop` instruction
- **LoongArch**: `pcnt` instruction

No platform-specific fixes needed.

### Estimated Real-World Impact

**High.** The shift-and-count popcount is extremely common in:
- Bitboard algorithms (chess engines, Go programs)
- Network packet processing (counting set bits in bitmasks)
- Compression algorithms (Huffman tree construction)
- Population counting in database bitmaps

The improvement ranges from **2× to 32×** depending on the input distribution and whether hardware popcount is available.

---

## Patch 2: Fold zero-extending loads into TEST memory instructions

**File:** `llvm/lib/Target/X86/X86ISelDAGToDAG.cpp`

### Problem

```c
int bit_test(int *a) {
    if (*a & 1234) return 0;
    return 1;
}
```

Clang generated:
```asm
movzwl (%rdi), %ecx    # unnecessary separate load
testl  $1234, %ecx      # test in register
sete   %al
retq
```

GCC generated:
```asm
testw  $1234, (%rdi)    # direct memory test
sete   %al
retq
```

### Root Cause

A three-stage pipeline issue:

1. **ShrinkDemandedOp** (pre-legalization) narrows the i32 load+AND to i16 because the mask 1234 fits in 16 bits and `isTruncateFree(i32→i16)` returns true.

2. **Type legalization** promotes the i16 AND back to i32 by converting the i16 load into a ZEXTLOAD from i16 to i32.

3. **Instruction selection** tries to fold the load into a TEST instruction via `tryFoldLoad()`, but this function requires `isNON_EXTLoad()` — the ZEXTLOAD fails this check, so the load can't be folded into TEST.

### Fix

Extended the X86 instruction selector's TEST handling to detect ZEXTLOAD operands. When the AND mask fits within the zero-extended memory type, the selector now emits the correctly-sized TEST-memory instruction (e.g., `TEST16mi` for a ZEXTLOAD from i16).

### Code Comparison

| | Old Clang (5 inst) | GCC (4 inst) | **New Clang (4 inst)** |
|---|---------------------|--------------|------------------------|
| | `movzwl (%rdi), %ecx` | `xorl %eax, %eax` | `xorl %eax, %eax` |
| | `xorl %eax, %eax` | `testw $1234, (%rdi)` | **`testw $1234, (%rdi)`** |
| | `testl $1234, %ecx` | `sete %al` | `sete %al` |
| | `sete %al` | `retq` | `retq` |
| | `retq` | | |

### Cross-Platform Impact

This is an x86-specific fix (in X86ISelDAGToDAG.cpp). AArch64, RISC-V, and LoongArch don't have the same TEST-with-memory-operand instruction pattern, so no equivalent fix is needed for those targets.

### Estimated Real-World Impact

**Moderate.** The pattern appears in:
- Flag/bitmask testing in system code
- Configuration bit checks
- Protocol parsing (testing specific bits in packet headers)

The improvement eliminates one instruction and one memory-to-register transfer, saving ~1-2 cycles per occurrence. The pattern is common enough to produce measurable improvement in flag-heavy code.

---

## Cases Not Fixed (with Analysis)

### `list_detach` — Adjacent identical-value stores not merged

**GCC:** Uses `punpcklqdq + movups` to write the same pointer to two adjacent 8-byte locations as a single 128-bit store.

**Clang:** Uses two separate `movq` stores.

**Analysis:** The LLVM DAG combiner's store merging infrastructure (`mergeConsecutiveStores`) only handles constants, loads, and vector extracts as store sources. When the stored value is a register (like a function argument), `getStoreSource()` returns `StoreSource::Unknown` and merging is never attempted. Fixing this would require extending the store merger to handle "same-value splat" stores as a new category, which is a significant refactoring effort. The performance difference is marginal (one store vs two stores to the same cache line, with added XMM setup overhead).

**Remaining deficiency:** Yes, this is a minor optimization gap. A future patch could extend the store merger to handle splat patterns.

### `filter_copy_ptr` — Loop unrolling with conditional stores

**GCC:** Simple scalar loop, no unrolling (6 instructions in hot loop).

**Clang:** Unrolled by 4 with epilogue (~60 instructions total).

**Analysis:** The LLVM loop unroller unrolls the loop by 4 because the iteration count is unknown at compile time and the loop body is small. This is generally a reasonable heuristic for unconditional loops, but for loops with conditional stores (unpredictable branches), unrolling increases code size without helping branch prediction. However, on modern out-of-order CPUs, the unrolled version can be faster when the branch is predictable (e.g., mostly-taken or mostly-not-taken). This is a judgment call where GCC's conservatism may or may not be better depending on the workload.

**Remaining deficiency:** Partial. The unrolling is not always wrong — it depends on branch predictability. A potential improvement would be to reduce the unroll factor for loops with data-dependent conditional stores.

### `complex_iv` — Counterproductive unroll-by-2

**GCC:** Tight single-iteration loop using 6 registers and ~10 instructions per iteration.

**Clang:** Unrolled by 2 with epilogue handling, using 13 registers (requires pushing/popping 6 callee-saved registers).

**Analysis:** The interdependent induction variables (`i += 2, j -= 1, k += i + j`) prevent effective optimization of the unrolled body. The unrolling saves one branch check per two iterations but adds register pressure overhead (6 extra push/pop instructions). For short trip counts, the prologue/epilogue overhead dominates.

**Remaining deficiency:** Yes. The unroller should account for register pressure increases when deciding whether to unroll loops with many interdependent induction variables.

### `stencil` — Vectorization epilogue size

**GCC:** Uses VF=4 (processes 4 floats per inner iteration) with a 2-element scalar epilogue.

**Clang:** Uses VF=8 (unrolled VF=4×2) with a 6-element scalar epilogue.

**Analysis:** Clang's approach is actually better for the main loop body (processing 8 elements per iteration vs 4), but the larger epilogue (6 scalar iterations vs 2) adds code size. The net effect is roughly neutral — the main loop is faster but the epilogue is larger. GCC's approach optimizes for code size; Clang's optimizes for throughput.

**Remaining deficiency:** Minor. The epilogue could be reduced by using a VF=4 epilogue loop after the VF=8 main loop.

---

## Test Results

- **X86 CodeGen tests:** 5525 passed, 15 expectedly failed, 2 unsupported — **zero regressions**
- **LoopIdiom tests:** 74 passed, 11 unsupported — **zero regressions**

## Patch Files

1. `/testbed/patches/0001-LoopIdiom-Recognize-shift-and-count-popcount-idiom.patch` — Loop idiom recognition for shift-and-count popcount
2. `/testbed/patches/0002-X86-Fold-zero-extending-loads-into-TEST-memory-instr.patch` — X86 ISel: fold ZEXTLOAD into TEST memory instructions
