# Barfs because of python2 files
%define _python_bytecompile_build 0

%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif
%if %{with compat32}
%bcond_with bootstrap32
%endif
# Never enable this in production builds.
# On multiarch platforms, it skips the 64bit
# builds for the sole purpose of debugging
# problems with 32bit builds without having
# to wait for the 64bit builds.
%bcond_with skip64

# (tpg) set snapshot date
# 20240905 is close to 19.1.0-rc4
#define gitdate 20240905

# Allow empty debugsource package for some subdirs
%define _empty_manifest_terminate_build 0

%define build_lto 1
%define _disable_ld_no_undefined 1

%if %{cross_compiling}
# When bootstrapping to a new architecture, we use gcc for
# reasons of paranoia (Thompson attack) -- better not to
# use the same compiler...
%define prefer_gcc 1

# Since the build system forces HOST cflags == TARGET cflags,
# we have to get rid of any -march= stuff. Might as well play it safe.
%global optflags -O2 -fno-semantic-interposition -DNDEBUG

%bcond_with tests
%else
# (tpg) optimize it a bit
# And reduce debug level to save some space
%global optflags %(echo %{optflags} |sed -e 's,-m64,,g') -O3 -fpic -fno-semantic-interposition -Qunused-arguments -Wl,-Bsymbolic-functions -g1 -DNDEBUG
%global build_ldflags %{build_ldflags} -fno-semantic-interposition -Wl,-Bsymbolic-functions
%bcond_without tests
%endif

# clang header paths are hard-coded at compile time
# and need adjustment whenever there's a new GCC version
%define gcc_version %(gcc -dumpversion)

%bcond_without default_compiler

# apidox are *huge* (> 8 GB)
# Enabling this option will take forever and create
# a giant package that might even cause timeouts when
# uploading to ABF...
%bcond_with apidox
%bcond_without clang
%bcond_without bolt
%bcond_without flang
# As of 18.0.0-rc1, libc only generates a static lib without
# dynamic loader, or complete headers
%bcond_without libc
%bcond_without mlir
%bcond_without z3
%ifarch %{arm} %{riscv}
%ifarch %{arm} %{riscv}
# RISC-V and armv7 don't have a working ocaml compiler yet
%bcond_with ocaml
%endif
# No graphviz yet either
%bcond_without bootstrap
%else
%bcond_with ocaml
%bcond_with bootstrap
%endif
%bcond_without ffi
# Force gcc to compile, in case previous clang is busted
%ifarch %{riscv} i686
%bcond_without bootstrap_gcc
%else
%bcond_with bootstrap_gcc
%endif
%if %{with bootstrap_gcc}
# gcc and clang don't fully agree about function name
# pretty printing, causing lldb to bomb out when built
# with gcc format checking
%global Werror_cflags %{nil}
# libcxx fails to bootstrap with gcc
%bcond_with libcxx
%else
%ifarch %{ix86}
# FIXME libc++ seems to be broken on x86_32
%bcond_with libcxx
%else
%bcond_without libcxx
%endif
%endif
%bcond_without lldb
%if %{cross_compiling}
# FIXME openmp and unwind don't crosscompile in 16.0.4
# (no error; just not being built even if listed)
%bcond_with openmp
%bcond_with unwind
%else
%bcond_without openmp
%bcond_without unwind
%endif
%bcond_without lld

# Use libcxx instead of libstdc++. Good, but
# don't do this if you care about binary compatibility...
%bcond_with use_libcxx

# If enabled, prefer compiler-rt over libgcc
%bcond_with default_compilerrt

# Clang's libLLVMgold.so shouldn't trigger devel(*) dependencies
%define __requires_exclude 'devel.*'

%define ompmajor 1
%define ompname %mklibname omp
%define oldompname %mklibname omp %{ompmajor}

%define major %(echo %{version} |cut -d. -f1-2)
%define major1 %(echo %{version} |cut -d. -f1)
#define is_main 1
%if 0%{?is_main:1}
# Separate because SPIRV_LLVM_Translator and friends frequently tag
# llvm_release_XXX branches only after the release
%undefine spirv_is_main
%endif
%undefine spirv_is_main

%bcond_without crosscrt

# We set LLVM_VERSION_SUFFIX affects the soname of libraries. If unset,
# LLVM_VERSION_SUFFIX is set to "git", resulting in libraries like
# libLLVMSupport.so.13git - a major of "13git" that is different from
# the major for the release ("13"). Better to set LLVM_VERSION_SUFFIX
# to something beginning with a ., leaving the major untouched.
#define SOMINOR .%(echo %{version}|cut -d. -f2-)%{?gitdate:.%{gitdate}}
# As of 13.0-rc1, the build system doesn't set a .so.13 symlink
# even if the soname is .so.13.0 or so, so let's set SOMINOR to nothing
# for now
%define SOMINOR %{nil}

Summary:	Low Level Virtual Machine (LLVM)
Name:		llvm
Version:	20.1.8
License:	Apache 2.0 with linking exception
Group:		Development/Other
Url:		https://llvm.org/
%if 0%{?gitdate:1}
# git archive-d from https://github.com/llvm/llvm-project
Source0:	https://github.com/llvm/llvm-project/archive/%{?is_main:main}%{!?is_main:release/%{major1}.x}/llvm-%{major1}-%{gitdate}.tar.gz
# llvm-spirv-translator and friends
Source20:	https://github.com/KhronosGroup/SPIRV-LLVM-Translator/archive/refs/heads/%{?spirv_is_main:master}%{!?spirv_is_main:llvm_release_%{major1}0}.tar.gz#/spirv-llvm-translator-%{version}.tar.gz
Release:	0.%{gitdate}.1
%else
Source0:	https://github.com/llvm/llvm-project/archive/refs/tags/llvmorg-%{version}.tar.gz
# llvm-spirv-translator and friends
Source20:	https://github.com/KhronosGroup/SPIRV-LLVM-Translator/archive/refs/heads/%{?spirv_is_main:master}%{!?spirv_is_main:llvm_release_%{major1}0}.tar.gz#/spirv-llvm-translator-%{version}.tar.gz
Release:	1
%endif
# Commits listed in https://github.com/KhronosGroup/glslang/blob/master/known_good.json as of 2025/07/10
Source21:	https://github.com/KhronosGroup/SPIRV-Headers/archive/2a611a970fdbc41ac2e3e328802aed9985352dca.tar.gz
Source22:	https://github.com/KhronosGroup/SPIRV-Tools/archive/44c93ad924b647b0d803ef4c924251c4341b838b.tar.gz
#Source21:	https://github.com/KhronosGroup/SPIRV-Headers/archive/refs/heads/main.tar.gz
#Source22:	https://github.com/KhronosGroup/SPIRV-Tools/archive/refs/tags/v2023.2.tar.gz
# For compatibility with the nongnu.org libunwind
Source50:	libunwind.pc.in
Source1000:	llvm.rpmlintrc
# Adjust search paths to match the OS
Patch1:		0000-clang-openmandriva-triples.patch
# ARM hardfloat hack
# see http://llvm.org/bugs/show_bug.cgi?id=15557
# and https://bugzilla.redhat.com/show_bug.cgi?id=803433
Patch2:		clang-hardfloat-hack.patch
# Default to a newer -fgnuc-version to get better performance
# out of stuff that does the likes of
# #if __GNUC__ > 5
# // assume SSE and friends are supported
# #else
# // slow workaround
# #endif
Patch3:		clang-default-newer-gnuc-version.patch
Patch4:		bolt-no-sse.patch
# Patches from AOSP
Patch5:		0001-llvm-Make-EnableGlobalMerge-non-static-so-we-can-modify-i.patch
# End AOSP patch section
Patch6:		llvm-11-compiler-rt-cmake-verbose.patch
# Set _GXX_ABI_VERSION correctly while pretending to be a newer gcc
Patch7:		clang-gcc-compat.patch
# Support -fuse-ld=XXX properly
Patch8:		clang-fuse-ld.patch
Patch9:		lld-10.0.1-format.patch
Patch10:	lldb-9.0.0-swig-compile.patch
Patch11:	bolt-no-underlinking.patch
Patch12:	spirv-tools-17.0-compile.patch
# Silently turn -O9 into -O3 etc. for increased gcc compatibility
Patch13:	llvm-3.8.0-fix-optlevel.patch
Patch14:	llvm-10.0-fix-m32.patch
Patch15:	spirv-llvm-translator-16.0.3-workaround-spirv-tools-crosscompile.patch
# https://github.com/KhronosGroup/SPIRV-LLVM-Translator/issues/3217
# https://github.com/KhronosGroup/SPIRV-LLVM-Translator/pull/3218
Patch16:	spirv-llvm-translator-bug3217.patch
#Patch16:	clang-rename-fix-linkage.patch
Patch17:	llvm-16.0.3-plugin-api-searchpath-hack.patch
Patch18:	lld-17.0.6-default-undefined-version.patch
# Enable --no-undefined, --as-needed, --enable-new-dtags,
# --hash-style=gnu, --warn-common, --icf=safe, --build-id=sha1,
# -O by default
Patch19:	lld-default-settings.patch
# Patches for musl support, (partially) stolen from Alpine Linux and ported
Patch20:	llvm-3.7-musl.patch
Patch21:	llvm-libc-compile.patch
Patch22:	lld-9.0-error-on-option-conflict.patch
#Patch23:	llvm-9.0-lld-workaround.patch
#Patch24:	llvm-11-flang-missing-docs.patch
#Patch25:	llvm-7.0-compiler-rt-arches.patch
#Patch26:	llvm-19-spirv-work-around-spirv-ext-clash.patch
Patch27:	spirv-tools-20.1.6-compile.patch
Patch28:	lldb-lua-swig-4.1.patch
Patch29:	compiler-rt-7.0.0-workaround-i386-build-failure.patch
# http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.6-remove-lgcc-when-using-compiler-rt.patch
# breaks exception handling -- removes gcc_eh
Patch30:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.6-fix-unwind-chain-inclusion.patch
Patch31:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.5-fix-stdint.patch
Patch40:	libc++-3.7.0-musl-compat.patch
Patch42:	llvm-bug-50640.patch
# Make it possible to override CLANG_LIBDIR_SUFFIX
# (that is used only to find LLVMgold.so)
# https://llvm.org/bugs/show_bug.cgi?id=23793
Patch43:	clang-0002-cmake-Make-CLANG_LIBDIR_SUFFIX-overridable.patch
# Fix library versioning
Patch46:	llvm-4.0.1-libomp-versioning.patch
# Fix mcount name for arm and armv8
# https://llvm.org/bugs/show_bug.cgi?id=27248
Patch48:	llvm-3.8.0-mcount-name.patch
# Show more information when aborting because posix_spawn failed
# (happened in some qemu aarch64 chroots)
Patch51:	llvm-4.0.1-debug-posix_spawn.patch
# Polly LLVM OpenMP backend
Patch56:	polly-8.0-default-llvm-backend.patch
#Patch57:	tsan-realpath-redefinition.patch
# libomp needs to link to libm so it can see
# logbl and fmaxl when using compiler-rt
Patch58:	llvm-10-omp-needs-libm.patch
# This increases compatibility with ld.bfd and friends,
# but results in ALL symbols being unversioned
#Patch59:	lld-16-compat-bug-60859.patch
Patch60:	llvm-15-default-build-id-sha1.patch
# Unbreak compiler-rt crosscompiles
Patch61:	compiler-rt-no-Iusrinclude.patch
# Really a patch -- but we want to apply it conditionally
# and we use %%autosetup for other patches...
Source62:	llvm-10-default-compiler-rt.patch
Patch63:	llvm-19-float128-buildfix.patch
Patch64:	llvm-19-libc-aarch64-compile.patch
Patch65:	spirv-tools-compile.patch
# SPIR-V fixes
#Patch90:	spirv-fix-warnings.patch
Patch91:	SPRIV-Tools-soname.patch

# This needs to be cleaned up before sending it upstream
Patch95:	spirv-llvm-translator-use-just-built-spirv-tools.patch
Patch99:	bootstrap-gcc-nostdlib.patch

# Xtensa patches will come back when they're rebased to 18 upstream
%if 0
# Patches for Xtensa support from
# https://github.com/espressif/llvm-project
Patch1001:	0001-Xtensa-Initial-support-of-the-ALU-operations.patch
Patch1002:	0002-Xtensa-Codegen-support-for-memory-operations.patch
Patch1003:	0003-Xtensa-Add-Constant-Pool.patch
Patch1004:	0004-Xtensa-Implement-assembler-representation-of-the.patch
Patch1005:	0005-Xtensa-Implement-lowering-constants.patch
Patch1006:	0006-Xtensa-Add-support-of-the-Xtensa-function-calls.patch
Patch1007:	0007-Xtensa-Implement-lowering-ConstantPool-and-address.patch
Patch1008:	0008-Xtensa-Implement-emitPrologue-emitEpilogue.patch
Patch1009:	0009-Xtensa-Lower-stack-operations.patch
Patch1010:	0010-Xtensa-Implement-lowering-SELECT_CC-SETCC.patch
Patch1011:	0011-Xtensa-Support-for-a-variety-of-additional-LLVM-IR.patch
Patch1012:	0012-Xtensa-Lower-SHIFT-PARTS-and-shift-operations.patch
Patch1013:	0013-Xtensa-Implement-load-pseudo-operations-and.patch
Patch1014:	0014-Xtensa-Support-for-variable-arguments.patch
Patch1015:	0015-Xtensa-Implement-lowering-BR_JT-operation.patch
Patch1016:	0016-Xtensa-Support-for-address-intrinsics.patch
Patch1017:	0017-Xtensa-Add-basic-support-for-inline-asm-constraints.patch
Patch1018:	0018-Xtensa-Implement-volatile-load-store.patch
Patch1019:	0019-Xtensa-Implement-branch-analysis.patch
Patch1020:	0020-Xtensa-Implement-support-for-the-BranchRelaxation.patch
Patch1021:	0021-Xtensa-Implement-code-density-feature-operations.patch
Patch1022:	0022-Xtensa-Add-code-size-reduction-pass.patch
Patch1023:	0023-Xtensa-Implement-Windowed-feature-operations.patch
Patch1024:	0024-Xtensa-Implement-Windowed-Call-ABI.patch
Patch1025:	0025-Xtensa-Reserve-an-emergency-spill-slot-for.patch
Patch1026:	0026-Xtensa-Implement-Boolean-feature-operations.patch
Patch1027:	0027-Xtensa-Implement-Floating-Point-feature-operations.patch
Patch1028:	0028-Xtensa-Lowering-Floating-Point-Operations.patch
Patch1029:	0029-Xtensa-Implement-DAG-Combine-for-FADD-and-FSUB.patch
Patch1030:	0030-Xtensa-Implement-Loop-SEXT-and-NSA-features.patch
Patch1031:	0031-Xtensa-Implement-Mul32-Mul32High-and-Div32.patch
Patch1032:	0032-Xtensa-Implement-Mac16-feature-and-operations.patch
Patch1033:	0033-Xtensa-Implement-Xtensa-features-and-operations.patch
Patch1034:	0034-Xtensa-Implement-Xtensa-features-and-operations.patch
Patch1035:	0035-Xtensa-Add-the-Xtensa-target.patch
Patch1036:	0036-Xtensa-Implement-Xtensa-ABI-lowering.patch
Patch1037:	0037-Xtensa-Add-subtargets-ESP32.-ESP8266-and-ESP32-S2.patch
Patch1038:	0038-Xtensa-Add-esp32-esp8266-and-esp32-s2-to-valid-cpu.patch
Patch1039:	0039-Xtensa-Improve-parsing-of-the-SR-and-UR-registers.patch
Patch1040:	0040-Xtensa-Emit-literals.patch
Patch1041:	0041-Xtensa-Improve-assembler-parsing.-Improve-CFA.patch
Patch1042:	0042-Xtensa-Lowering-Exception-Selector-and-Pointer.patch
Patch1043:	0043-Xtensa-Lowering-GLobalTLSAddress-operation.patch
Patch1044:	0044-Xtensa-Lower-ATOMIC_FENCE.-Add-Atomic-Expand-pass.patch
Patch1045:	0045-Xtensa-Lower-atomic_cmp_swap_-8-16-32-operations.patch
Patch1046:	0046-Xtensa-Lower-atomic_swap_-8-16-32-operations.patch
Patch1047:	0047-Xtensa-Lower-atomic-operations.patch
Patch1048:	0048-Xtensa-Implement-Xtensa-toolchain.patch
Patch1049:	0049-Xtensa-Implement-multilib-support.patch
Patch1050:	0050-Xtensa-Implemented-builtins-for-Xtensa-MAC16.patch
Patch1051:	0051-Xtensa-Implemented-builtins-for-Xtensa-MAC16.patch
Patch1052:	0052-Xtensa-Implement-lowering-llvm-intrinsics.patch
Patch1053:	0053-Xtensa-Not-for-upstream-Add-functions-needed-to.patch
Patch1054:	0054-Xtensa-Correct-Call-ABI-for-function-return.patch
Patch1055:	0055-Xtensa-Implement-rest-part-of-FP-instructions.patch
Patch1056:	0056-Xtensa-Correct-lowering-BR_CC-with-FP-operands.patch
Patch1057:	0057-Xtensa-Use-ctors-for-Xtensa-target-by-default.patch
Patch1058:	0058-Xtensa-Implement-Hardware-Loop-optimization-pass.patch
Patch1059:	0059-Xtensa-Change-using-of-Frame-Pointer.patch
Patch1060:	0060-esp-maint-Adds-Github-workfows.patch
Patch1061:	0061-Xtensa-Implement-esp32-psram-cache-fixes.patch
Patch1062:	0062-Xtensa-Fix-Hardware-Loop-optimization.patch
Patch1063:	0063-Xtensa-Remove-unnecessary-MOVSP-in-epilogue.patch
Patch1064:	0064-Xtensa-Support-f-Inline-Assembly-Constraint.patch
Patch1065:	0065-Xtensa-Correction-of-the-PSRAM-fix-pass.patch
Patch1066:	0066-Xtensa-Correction-of-the-hardware-loop-instrinsics.patch
Patch1067:	0067-Xtensa-Correction-of-the-ESP32-S2-target.patch
Patch1068:	0068-Xtensa-Implement-ESP32-S3-target.patch
Patch1069:	0069-Xtensa-Define-register-type-for-CC.patch
Patch1070:	0070-Xtensa-Correcting-FP-instructions-and-intrinsics.patch
Patch1071:	0071-Xtensa-Implement-MUL16-feature.patch
Patch1072:	0072-Xtensa-Add-a-no-op-mlongcalls-option-for-better.patch
Patch1073:	0073-Xtensa-Initialize-MCSubtargetInfo-with-esp32.patch
Patch1074:	0074-Xtensa-Initialize-MCSubtargetInfo-with-esp32.patch
Patch1075:	0075-Xtensa-Correction-of-the-Hardware-Loop-pass.patch
Patch1076:	0076-Xtensa-Fix-atomic-swap-for-8-16-bit-operands.patch
Patch1077:	0077-Xtensa-Initial-porting-compiler-rt-library-for.patch
Patch1078:	0078-Xtensa-Add-support-of-mcpu-option.patch
Patch1079:	0079-Xtensa-Improve-Xtensa-multilib-support-in-clang.patch
Patch1080:	0080-Xtensa-Add-rtlib-option-support-for-ESP-Xtensa.patch
Patch1081:	0081-Xtensa-Add-fuse-ld-option-support-to-ESP-Xtensa.patch
Patch1082:	0082-Xtensa-Use-B0-register-for-FP-cmp-operations.patch
Patch1083:	0083-ci-add-.gitlab-ci.yml-to-support-CI-CD.patch
Patch1084:	0084-Xtensa-Fix-inline-asm.patch
Patch1085:	0085-Xtensa-Fix-handling-of-empty-fuse-ld-option-for.patch
# rediffed to not conflict with OM triplet additions
Patch1086:	0086-esp-Adds-support-for-vendor-Espressif-to-target.patch
Patch1087:	0087-esp-riscv-Use-GCC-assembler-for-ESP-RISCV-chips.patch
# rediffed to not conflict with OM triplet additions
Patch1088:	0088-esp-riscv-Adds-support-for-riscv32-esp-elf-target.patch
Patch1089:	0089-riscv-Add-default-multilib.patch
Patch1090:	0090-esp-riscv-Add-multilib-support-for-riscv32-esp-elf.patch
Patch1091:	0091-esp-riscv-Add-libnosys-to-linker-command-line-by.patch
Patch1092:	0092-esp-riscv-Exclude-crt0.o-from-linking-in.patch
Patch1093:	0093-riscv-Add-ESP-toolchain-tests.patch
Patch1094:	0094-esp-ci-Adds-Linux-build.patch
Patch1095:	0095-esp-ci-Adds-Mingw32-build.patch
Patch1096:	0096-Xtensa-Remove-redundant-target-features.patch
Patch1097:	0097-esp-ci-Upgrade-universal-toolchain-to.patch
Patch1098:	0098-esp-ci-Allow-failure-for-universal-toolchain-builds.patch
Patch1099:	0099-Xtensa-Implement-support-of-the-sysroot.patch
Patch1100:	0100-Xtensa-Fix-crtbegin-crtend-implementation.patch
Patch1101:	0101-Xtensa-Build-compiler-rt-libs.patch
Patch1102:	0102-Xtensa-Fix-ill.n-instruction-econding.patch
Patch1103:	0103-ci-add-jobs-for-arm64-toolchains.patch
Patch1104:	0104-ci-cd-fix-clang-version-in-gitlab-ci.yml.patch
Patch1105:	0105-Xtensa-fix-compiler-rt-crt-build-script.patch
Patch1106:	0106-Xtensa-Implement-asm-macro-for-bbci-bbsi.patch
Patch1107:	0107-Xtensa-Implement-support-of-literal-and-region-asm.patch
Patch1108:	0108-Xtensa-Corrected-asm-parser.patch
Patch1109:	0109-riscv-gnu-Adds-no-rtti-multilib-support.patch
Patch1110:	0110-Xtensa-Guess-GCC-toolchain-triplet-from-MCPU-option.patch
Patch1111:	0111-esp-ci-Adds-MacOS-x86_64-ARM64-universal-toolchain.patch
Patch1112:	0112-esp-ci-Adds-minimal-distro-with-libraries-headres.patch
Patch1113:	0113-esp-ci-Upgrade-GCC-toolchain-to-esp-2022r1.patch
Patch1114:	0114-esp-ci-Move-newlib-build-to-separate-job.patch
Patch1115:	0115-esp-ci-Adds-Linux-ARM-ARM64-universal-toolchain.patch
Patch1116:	0116-esp-ci-Upgrade-Clang-ver-to-15.patch
Patch1117:	0117-esp-ci-Adds-support-to-switch-between-legacy-and.patch
Patch1118:	0118-esp-ci-Adds-MacOS-binaries-signing-stage.patch
Patch1119:	0119-Xtensa-Xtensa-ABI-128bit-arg-alignment.patch
Patch1120:	0120-Xtensa-Fix-Call-ABI-for-16-byte-alignment.patch
Patch1121:	0121-Xtensa-Add-IR-test-for-16byte-alignment.patch
Patch1122:	0122-esp-ci-Run-LLD-tests.-Output-test-logs-in.patch
Patch1123:	0123-Xtensa-Fix-atomic-rmw-operation.patch
Patch1124:	0124-Xtensa-Fix-Hardware-Loop-pass.patch
Patch1125:	0125-Xtensa-Add-LLD-linker-support.patch
Patch1126:	0126-Xtensa-LLD-add-more-tests.patch
Patch1127:	0127-Xtensa-LLD-Fix-J-formula.patch
Patch1128:	0128-Xtensa-Add-emit-constant-pool-option.patch
Patch1129:	0129-Xtensa-Add-support-of-the-mcmodel-option.patch
Patch1130:	0130-Xtensa-Fix-lowering-funnel-shift-left.patch
Patch1131:	0131-Xtensa-Make-it-possible-to-use-fuse-ld-when-GCC.patch
Patch1132:	0132-esp-ci-Fixes-Windows-release-archives.patch
Patch1133:	0133-esp-ci-Check-for-OOM-failures-after-build.patch
Patch1134:	0134-LLD-Xtensa-Cover-DIFF-8-16-32-relocations.patch
Patch1135:	0135-Xtensa-Implement-constant-islands-pass.patch
Patch1136:	0136-Xtensa-Disable-hardware-loops-by-default.patch
Patch1137:	0137-Xtensa-Improve-fixup-error-messages-in-asm-backend.patch
Patch1138:	0138-Xtensa-Fix-hwloop-tests.patch
Patch1139:	0139-Xtensa-Place-aggregate-constants-in-global-variable.patch
Patch1140:	0140-esp-ci-change-clang-version-to-16.patch
Patch1141:	0141-toolchain-Adds-compiler-rt-multilibs-support-for-Esp.patch
Patch1142:	0142-esp-ci-Build-compiler-rt.patch
Patch1143:	0143-toolchain-xtensa-Enable-frtti-by-default-for-multili.patch
Patch1144:	0144-toolchain-esp-Add-tests-for-compiler-rt-multilib.patch
Patch1145:	0145-toolchain-xtensa-Use-GNU-linker-when-no-GCC-installa.patch
Patch1146:	0146-tooclahin-xtensa-Add-crt0.o-to-linker-command-line-a.patch
Patch1147:	0147-Xtensa-Implement-__ieee754_sqrtf-builtin.patch
Patch1148:	0148-compiler-rt-tests-Adds-specific-build-options-for-Es.patch
Patch1149:	0149-compiler-rt-tests-Disable-tests-failing-for-Espressi.patch
Patch1150:	0150-esp-ci-Update-newlib-branch.patch
Patch1151:	0151-esp-ci-Saves-log-for-test_x86_64-linux-gnu.patch
Patch1152:	0152-esp-ci-Update-llvm-xtensa-testsuite-ref.patch
Patch1153:	0153-esp-ci-Update-xtensa-clang-toolchain-ref.patch
Patch1154:	0154-esp-ci-Upload-only-x86_64-linux-gnu-distro-to-HTTP-s.patch
Patch1155:	0155-esp-ci-stick-to-binutils-2.35.patch
Patch1156:	0156-Xtensa-Fix-i8-i16-ABI-alignment.patch
Patch1157:	0157-esp-toolchain-Adds-fdata-sections-to-newlib-target-C.patch
Patch1158:	0158-toolchain-esp-Bring-libgcc-back-to-the-toolchain.patch
%endif

BuildRequires:	bison
BuildRequires:	binutils-devel
BuildRequires:	chrpath
BuildRequires:	flex
BuildRequires:	pkgconfig(libedit)
BuildRequires:	pkgconfig(libelf)
BuildRequires:	pkgconfig(lua)
BuildRequires:	cmake(tsl-robin-map)
# libclc
BuildRequires:	vulkan-headers
BuildRequires:	pkgconfig(vulkan)
%if %{without bootstrap}
BuildRequires:	spirv-llvm-translator
BuildRequires:	graphviz
# Without this, generating man pages fails
# Handler <function process_automodsumm_generation at 0x7fa70fc2a5e0> for event 'builder-inited' threw an exception (exception: No module named 'lldb')
BuildRequires:	lldb
%endif
BuildRequires:	chrpath
BuildRequires:	groff
BuildRequires:	libtool
BuildRequires:	pkgconfig(ncursesw)
BuildRequires:	python%{pyver}dist(numpy)
BuildRequires:	python%{pyver}dist(nanobind)
BuildRequires:	python-sphinx
# For sphinx plugins
BuildRequires:	python%{pyver}dist(recommonmark)
BuildRequires:	python%{pyver}dist(sphinxcontrib-websupport)
BuildRequires:	python%{pyver}dist(sphinx-automodapi)
BuildRequires:	python%{pyver}dist(sphinx-markdown-tables)
BuildRequires:	python%{pyver}dist(furo)
BuildRequires:	python%{pyver}dist(myst-parser)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(requests)
%if %{with ocaml}
BuildRequires:	ocaml-compiler
BuildRequires:	ocaml-compiler-libs
BuildRequires:	ocaml-camlp4
BuildRequires:	ocaml-findlib >= 1.5.5-2
BuildRequires:	ocaml-ctypes
%endif
BuildRequires:	tcl
BuildRequires:	sed
BuildRequires:	zip
BuildRequires:	libstdc++-devel
BuildRequires:	%{_lib}zstd-static-devel
%if %{with ffi}
BuildRequires:	pkgconfig(libffi)
%endif
BuildRequires:	pkgconfig(cloog-isl)
BuildRequires:	pkgconfig(isl) >= 0.13
BuildRequires:	pkgconfig(libtirpc)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(icu-i18n)
%ifnarch %{riscv64}
BuildRequires:	atomic-devel
%endif
BuildRequires:	python >= 3.4
BuildRequires:	python%{py_ver}dist(pybind11)
BuildRequires:	python%{py_ver}dist(pyyaml)
BuildRequires:	python%{py_ver}dist(pygments)
BuildRequires:	python%{py_ver}dist(matplotlib-inline)
BuildRequires:	python%{py_ver}dist(backcall)
BuildRequires:	python%{py_ver}dist(prompt-toolkit)
BuildRequires:	python%{py_ver}dist(pickleshare)
BuildRequires:	python%{py_ver}dist(jedi)
BuildRequires:	python%{py_ver}dist(ptyprocess)
# Make sure lld doesn't install its own copy
BuildRequires:	python-six
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	which
# For building libc++.a
BuildRequires:	glibc-static-devel
%if %{with apidox}
BuildRequires:	doxygen
%endif
Obsoletes:	llvm-ocaml < 14.0.0
# Some cmake files try to look up the commit hash
BuildRequires:	git-core
# For lldb
BuildRequires:	swig
BuildRequires:	pkgconfig(python3)
BuildRequires:	gcc
BuildRequires:	pkgconfig(libtirpc)
# FIXME really just need libcurses.so to point
# at something that exists
BuildRequires:	%{_lib}ncurses6
%if !%{with lld}
BuildRequires:	lld < %{EVRD}
%endif
%if %{with openmp}
Requires:	%{ompname} = %{EVRD}
%endif
%if %{with compat32}
BuildRequires:	libc6
BuildRequires:	devel(libffi)
BuildRequires:	devel(libxml2)
BuildRequires:	devel(libelf)
BuildRequires:	devel(libedit)
BuildRequires:	devel(libpython%{py_ver})
BuildRequires:	libzstd-static-devel
# For Polly
BuildRequires:	devel(libgmp)
BuildRequires:	devel(libisl)
%endif
%ifarch %{armx} %{ix86} %{riscv}
# Temporary workaround for missing libunwind.so
BuildRequires:	llvm-devel
%ifarch %{ix86}
BuildRequires:	libunwind-devel
%endif
%endif
%ifnarch %{riscv}
BuildRequires:	pkgconfig(OpenCL)
BuildRequires:	mesa-opencl-devel
%endif
%if %{with compat32} && ! %{with bootstrap32}
BuildRequires:	devel(libOpenCL)
BuildRequires:	devel(libMesaOpenCL)
BuildRequires:	libunwind-devel
%endif
%if %{with z3}
BuildRequires:	pkgconfig(z3)
%endif

Obsoletes:	%{mklibname LLVMRISCVCodeGen 5} < %{EVRD}
Obsoletes:	%{mklibname LLVMRISCVDesc 5} < %{EVRD}
Obsoletes:	%{mklibname LLVMRISCVInfo 5} < %{EVRD}
Obsoletes:	%{mklibname lldConfig 5} < %{EVRD}

%if %{with crosscrt}
%ifnarch %{aarch64}
BuildRequires:	cross-aarch64-openmandriva-linux-gnu-binutils
BuildRequires:	cross-aarch64-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-aarch64-openmandriva-linux-gnu-libc
BuildRequires:	cross-aarch64-openmandriva-linux-gnu-kernel-headers
%endif
%ifnarch %{arm}
BuildRequires:	cross-armv7hnl-openmandriva-linux-gnueabihf-binutils
BuildRequires:	cross-armv7hnl-openmandriva-linux-gnueabihf-gcc-bootstrap
BuildRequires:	cross-armv7hnl-openmandriva-linux-gnueabihf-libc
BuildRequires:	cross-armv7hnl-openmandriva-linux-gnueabihf-kernel-headers
%endif
%ifnarch %{ix86}
BuildRequires:	cross-i686-openmandriva-linux-gnu-binutils
BuildRequires:	cross-i686-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-i686-openmandriva-linux-gnu-libc
BuildRequires:	cross-i686-openmandriva-linux-gnu-kernel-headers
%endif
%ifnarch ppc64le
BuildRequires:	cross-ppc64le-openmandriva-linux-gnu-binutils
BuildRequires:	cross-ppc64le-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-ppc64le-openmandriva-linux-gnu-libc
BuildRequires:	cross-ppc64le-openmandriva-linux-gnu-kernel-headers
%endif
%ifnarch ppc64
BuildRequires:	cross-ppc64-openmandriva-linux-gnu-binutils
BuildRequires:	cross-ppc64-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-ppc64-openmandriva-linux-gnu-libc
BuildRequires:	cross-ppc64-openmandriva-linux-gnu-kernel-headers
%endif
%ifnarch %{riscv64}
BuildRequires:	cross-riscv64-openmandriva-linux-gnu-binutils
BuildRequires:	cross-riscv64-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-riscv64-openmandriva-linux-gnu-libc
BuildRequires:	cross-riscv64-openmandriva-linux-gnu-kernel-headers
%endif
%ifnarch %{x86_64}
BuildRequires:	cross-x86_64-openmandriva-linux-gnu-binutils
BuildRequires:	cross-x86_64-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-x86_64-openmandriva-linux-gnu-libc
BuildRequires:	cross-x86_64-openmandriva-linux-gnu-kernel-headers
%endif
%endif

%description
LLVM is a robust system, particularly well suited for developing new mid-level
language-independent analyses and optimizations of all sorts, including those
that require  extensive interprocedural analysis. LLVM is also a great target
for front-end development for conventional or research programming languages,
including those which require compile-time, link-time, or run-time optimization 
for effective implementation, proper tail calls or garbage collection.

%files
%{_bindir}/FileCheck
%{_bindir}/bugpoint
%{_bindir}/count
%{_bindir}/c-index-test
%{_bindir}/dsymutil
%{_bindir}/git-clang-format
%{_bindir}/llc
%{_bindir}/lli
%{_bindir}/lli-child-target
%{_bindir}/opt
%{_bindir}/llvm-addr2line
%{_bindir}/llvm-ar
%{_bindir}/llvm-as
%{_bindir}/llvm-bcanalyzer
%{_bindir}/llvm-cat
%{_bindir}/llvm-c-test
%{_bindir}/llvm-cfi-verify
%{_bindir}/llvm-cvtres
%{_bindir}/llvm-cxxfilt
%{_bindir}/llvm-cxxmap
%{_bindir}/llvm-debuginfo-analyzer
%{_bindir}/llvm-diff
%{_bindir}/llvm-dis
%{_bindir}/llvm-dwp
%{_bindir}/llvm-exegesis
%{_bindir}/llvm-extract
%{_bindir}/llvm-gsymutil
%{_bindir}/llvm-ifs
%{_bindir}/llvm-install-name-tool
%{_bindir}/llvm-reduce
%{_bindir}/llvm-jitlink
%{_bindir}/llvm-lib
%{_bindir}/llvm-link
%{_bindir}/llvm-lipo
%{_bindir}/llvm-lto
%{_bindir}/llvm-lto2
%{_bindir}/llvm-mc
%{_bindir}/llvm-mca
%{_bindir}/llvm-ml
%{_bindir}/llvm-nm
%{_bindir}/llvm-objdump
%{_bindir}/llvm-objcopy
%{_bindir}/llvm-readtapi
%if %{with openmp}
%{_bindir}/llvm-omp-kernel-replay
%endif
%{_bindir}/llvm-otool
%{_bindir}/llvm-remarkutil
%{_bindir}/llvm-sim
%{_bindir}/llvm-windres
%{_bindir}/llvm-bitcode-strip
%{_bindir}/llvm-jitlink-executor
%{_bindir}/llvm-libtool-darwin
%{_bindir}/llvm-profgen
%{_bindir}/llvm-cgdata
%{_bindir}/llvm-ctxprof-util
%{_bindir}/llvm-offload-device-info
%{_bindir}/llvm-debuginfod-find
%{_bindir}/llvm-tli-checker
%{_bindir}/llvm-debuginfod
%{_bindir}/llvm-dwarfutil
%{_bindir}/split-file
%{_bindir}/llvm-pdbutil
%{_bindir}/llvm-ranlib
%{_bindir}/llvm-rc
%{_bindir}/llvm-readelf
%{_bindir}/llvm-readobj
%{_bindir}/llvm-split
%{_bindir}/llvm-strip
%{_bindir}/llvm-undname
%{_bindir}/llvm-cov
%{_bindir}/llvm-dwarfdump
%{_bindir}/llvm-modextract
%{_bindir}/llvm-opt-report
%{_bindir}/llvm-PerfectShuffle
%{_bindir}/llvm-profdata
%{_bindir}/llvm-rtdyld
%{_bindir}/llvm-size
%{_bindir}/llvm-stress
%{_bindir}/llvm-strings
%{_bindir}/llvm-symbolizer
%{_bindir}/llvm-tblgen
%{_bindir}/tblgen-to-irdl
%{_bindir}/tblgen-lsp-server
%{_bindir}/llvm-cxxdump
%{_bindir}/llvm-xray
%if !%{with lld}
%{_bindir}/llvm-dlltool
%{_bindir}/llvm-mt
%{_bindir}/llvm-readelf
%endif
%{_bindir}/prepare_builtins
%{_bindir}/reduce-chunk-list
%{_bindir}/UnicodeNameMappingGenerator

%{_bindir}/sancov
%{_bindir}/sanstats
%{_bindir}/verify-uselistorder
%{_bindir}/obj2yaml
%{_bindir}/wasm-ld
%{_bindir}/yaml2obj
%{_bindir}/yaml-bench
%{_bindir}/not

%doc %{_mandir}/man1/FileCheck.1*
%doc %{_mandir}/man1/bugpoint.1*

%doc %{_mandir}/man1/dsymutil.1*
%doc %{_mandir}/man1/lit.1*
%doc %{_mandir}/man1/llc.1*
%doc %{_mandir}/man1/lli.1*
%doc %{_mandir}/man1/llvm-*.1*
%doc %{_mandir}/man1/opt.1*

%doc %{_mandir}/man1/tblgen.1*
%doc %{_mandir}/man1/mlir-tblgen.1*

#-----------------------------------------------------------
%define LLVMLibs LLVMAArch64AsmParser LLVMAArch64CodeGen LLVMAArch64Desc LLVMAArch64Disassembler LLVMAArch64Info LLVMAArch64Utils LLVMAggressiveInstCombine LLVMARMAsmParser LLVMARMCodeGen LLVMARMDesc LLVMARMDisassembler LLVMARMInfo LLVMARMUtils LLVMAnalysis LLVMAsmParser LLVMAsmPrinter LLVMBPFAsmParser LLVMBitReader LLVMBitstreamReader LLVMBitWriter LLVMBPFCodeGen LLVMBPFDesc LLVMBPFDisassembler LLVMBPFInfo LLVMBinaryFormat LLVMCodeGen LLVMCore LLVMDebugInfoCodeView LLVMCoroutines LLVMDebugInfoDWARF LLVMDebugInfoMSF LLVMDebugInfoPDB LLVMDemangle LLVMDlltoolDriver LLVMExecutionEngine LLVMFuzzMutate LLVMHexagonAsmParser LLVMHexagonCodeGen LLVMHexagonDesc LLVMHexagonDisassembler LLVMHexagonInfo LLVMIRReader LLVMInstCombine LLVMInstrumentation LLVMInterpreter LLVMLanaiAsmParser LLVMLanaiCodeGen LLVMLanaiDesc LLVMLanaiDisassembler LLVMLanaiInfo LLVMLTO LLVMLibDriver LLVMLineEditor LLVMLinker LLVMMC LLVMMCDisassembler LLVMMCJIT LLVMMCParser LLVMMIRParser LLVMMSP430CodeGen LLVMMSP430Desc LLVMMSP430Info LLVMMipsAsmParser LLVMMipsCodeGen LLVMMipsDesc LLVMMipsDisassembler LLVMMipsInfo LLVMNVPTXCodeGen LLVMNVPTXDesc LLVMNVPTXInfo LLVMObjCARCOpts LLVMObject LLVMOption LLVMOrcJIT LLVMPasses LLVMPowerPCAsmParser LLVMPowerPCCodeGen LLVMPowerPCDesc LLVMPowerPCDisassembler LLVMPowerPCInfo LLVMProfileData LLVMAMDGPUAsmParser LLVMAMDGPUCodeGen LLVMAMDGPUDesc LLVMAMDGPUDisassembler LLVMAMDGPUInfo LLVMAMDGPUUtils LLVMRuntimeDyld LLVMScalarOpts LLVMSelectionDAG LLVMSparcAsmParser LLVMSparcCodeGen LLVMSparcDesc LLVMSparcDisassembler LLVMSparcInfo LLVMSupport LLVMSymbolize LLVMSystemZAsmParser LLVMSystemZCodeGen LLVMSystemZDesc LLVMSystemZDisassembler LLVMSystemZInfo LLVMTableGen LLVMTarget LLVMTransformUtils LLVMVectorize LLVMWindowsManifest LLVMX86AsmParser LLVMX86CodeGen LLVMX86Desc LLVMX86Disassembler LLVMX86Info LLVMXCoreCodeGen LLVMXCoreDesc LLVMXCoreDisassembler LLVMXCoreInfo LLVMXRay LLVMipo LLVMCoverage LLVMGlobalISel LLVMObjectYAML LLVMMCA LLVMMSP430AsmParser LLVMMSP430Disassembler LLVMRemarks LLVMTextAPI LLVMWebAssemblyAsmParser LLVMWebAssemblyCodeGen LLVMWebAssemblyDesc LLVMWebAssemblyDisassembler LLVMWebAssemblyInfo LLVMRISCVAsmParser LLVMRISCVCodeGen LLVMRISCVDesc LLVMRISCVDisassembler LLVMRISCVInfo LLVMDebugInfoGSYM LLVMJITLink LLVMCFGuard LLVMDWARFLinker LLVMFrontendOpenMP LLVMAVRAsmParser LLVMAVRCodeGen LLVMAVRDesc LLVMAVRDisassembler LLVMAVRInfo LLVMExtensions LLVMFrontendOpenACC LLVMFileCheck LLVMInterfaceStub LLVMOrcShared LLVMOrcTargetProcess Polly LLVMCFIVerify LLVMDWP LLVMExegesis LLVMExegesisAArch64 LLVMExegesisMips LLVMExegesisPowerPC LLVMExegesisX86 LLVMWebAssemblyUtils LLVMSPIRVLib LLVMAMDGPUTargetMCA LLVMDebuginfod LLVMDiff LLVMVEAsmParser LLVMVECodeGen LLVMVEDesc LLVMVEDisassembler LLVMVEInfo LLVMX86TargetMCA LLVMFuzzerCLI LLVMObjCopy LLVMWindowsDriver LLVMDWARFLinkerParallel LLVMDebugInfoLogicalView LLVMFrontendHLSL LLVMIRPrinter LLVMLoongArchAsmParser LLVMLoongArchCodeGen LLVMLoongArchDesc LLVMLoongArchDisassembler LLVMLoongArchInfo LLVMRISCVTargetMCA LLVMTargetParser LLVMARCCodeGen LLVMARCDesc LLVMARCDisassembler LLVMARCInfo LLVMCSKYAsmParser LLVMCSKYCodeGen LLVMCSKYDesc LLVMCSKYDisassembler LLVMCSKYInfo LLVMM68kAsmParser LLVMM68kCodeGen LLVMM68kDesc LLVMM68kDisassembler LLVMM68kInfo LLVMSPIRVCodeGen LLVMSPIRVDesc LLVMSPIRVInfo LLVMXtensaAsmParser LLVMXtensaCodeGen LLVMXtensaDesc LLVMXtensaDisassembler LLVMXtensaInfo LLVMCodeGenTypes LLVMDebugInfoBTF LLVMTableGenCommon LLVMDWARFLinkerClassic LLVMFrontendDriver LLVMFrontendOffloading LLVMHipStdPar LLVMOrcDebugging LLVMTextAPIBinaryReader LLVMOptDriver LLVMSPIRVAnalysis LLVMSandboxIR LLVMTableGenBasic LLVMCGData LLVMExegesisRISCV LLVMFrontendAtomic LLVMTelemetry

# Removed in 14: LLVMMCACustomBehaviourAMDGPU
# New in 16: Starting from LLVMDWARFLinkerParallel
# New in 18: Starting from LLVMDRAWFLinkerClassic
# Removed in 19: LLVMTableGenGlobalISel
# Only in 19: Starting from LLVMCodeGenData
# New in 20: Starting from LLVMOptDriver

%define LLVM64Libs findAllSymbols

%define ClangLibs clangAnalysisFlowSensitive clangAnalysis clangAPINotes clangARCMigrate clangASTMatchers clangAST clangBasic clangCodeGen clangCrossTU clangDependencyScanning clangDirectoryWatcher clangDriver clangDynamicASTMatchers clangEdit clangFormat clangFrontend clangFrontendTool clangHandleCXX clangHandleLLVM clangIndexSerialization clangIndex clangInterpreter clangLex clangParse clangRewriteFrontend clangRewrite clangSema clangSerialization clangStaticAnalyzerCheckers clangStaticAnalyzerCore clangStaticAnalyzerFrontend clangToolingASTDiff clangToolingCore clangToolingInclusions clangToolingRefactoring clangTooling clangToolingSyntax clangTransformer clangAnalysisFlowSensitiveModels clangExtractAPI clangSupport clangToolingInclusionsStdlib clangInstallAPI
# New in 16: clangToolingInclusionsStdlib
# New in 19: clangInstallAPI

%define Clang64Libs clangApplyReplacements clangChangeNamespace clangDaemon clangDaemonTweaks clangDoc clangIncludeFixer clangIncludeFixerPlugin clangMove clangQuery clangReorderFields clangTidy clangTidyPlugin clangTidyAbseilModule clangTidyAlteraModule clangTidyAndroidModule clangTidyBoostModule clangTidyBugproneModule clangTidyCERTModule clangTidyCppCoreGuidelinesModule clangTidyConcurrencyModule clangTidyDarwinModule clangTidyFuchsiaModule clangTidyGoogleModule clangTidyHICPPModule clangTidyLLVMModule clangTidyLinuxKernelModule clangTidyMiscModule clangTidyModernizeModule clangTidyMPIModule clangTidyObjCModule clangTidyOpenMPModule clangTidyPortabilityModule clangTidyReadabilityModule clangTidyPerformanceModule clangTidyZirconModule clangTidyUtils clangTidyLLVMLibcModule clangTidyMain clangdRemoteIndex clangdSupport clangIncludeCleaner clangdMain

%if %{with flang}
%global FlangLibs FIRBuilder FIRCodeGen FIRDialect FIRSupport FIRTransforms FortranCommon FortranDecimal FortranEvaluate FortranLower FortranParser FortranRuntime FortranSemantics flangFrontend flangFrontendTool HLFIRDialect HLFIRTransforms FIRAnalysis FIRDialectSupport CUFAttrs CUFDialect FIROpenACCSupport FIRTestOpenACCInterfaces FlangOpenMPTransforms FortranSupport flangPasses
%if %{with tests}
%global FlangLibs %{FlangLibs} FIRTestAnalysis
%endif
%else
%global FlangLibs %{nil}
%endif
# Removed in 14: FIROptimizer
# New in 16: HLFIRDialect HLFIRTransforms FIRAnalysis FIRTestAnalysis

%if %{with bolt}
%define BOLTLibs LLVMBOLTCore LLVMBOLTPasses LLVMBOLTProfile LLVMBOLTRewrite LLVMBOLTRuntimeLibs LLVMBOLTTargetAArch64 LLVMBOLTTargetX86 LLVMBOLTTargetRISCV LLVMBOLTUtils
%else
%define BOLTLibs %{nil}
%endif

%if %{with mlir}
%global MLIRLibs MLIRAffineAnalysis MLIRAffineToStandard MLIRAffineTransforms MLIRAffineUtils MLIRAMXToLLVMIRTranslation MLIRAMXTransforms MLIRAnalysis MLIRArmNeon2dToIntr MLIRArmNeonToLLVMIRTranslation MLIRArmSVEToLLVMIRTranslation MLIRArmSVETransforms MLIRAsyncToLLVM MLIRAsyncTransforms MLIRBufferizationToMemRef MLIRBufferizationTransforms MLIRCallInterfaces MLIRCAPIAsync MLIRCAPIConversion MLIRCAPIDebug MLIRCAPIExecutionEngine MLIRCAPIGPU MLIRCAPIInterfaces MLIRCAPIIR MLIRCAPILinalg MLIRCAPILLVM MLIRCAPIPDL MLIRCAPIQuant MLIRCAPISCF MLIRCAPIShape MLIRCAPISparseTensor MLIRCAPITensor MLIRCAPITransforms MLIRCastInterfaces MLIRComplexToLLVM MLIRComplexToStandard MLIRControlFlowInterfaces MLIRCopyOpInterface MLIRDataLayoutInterfaces MLIRDerivedAttributeOpInterface MLIRDialect MLIRDialectUtils MLIRExecutionEngine MLIRGPUToGPURuntimeTransforms MLIRGPUToNVVMTransforms MLIRGPUToROCDLTransforms MLIRGPUToSPIRV MLIRGPUTransforms MLIRInferTypeOpInterface MLIRIR MLIRJitRunner MLIRLinalgToStandard MLIRLinalgTransforms MLIRLinalgUtils MLIRLLVMCommonConversion MLIRLLVMIRTransforms MLIRLLVMToLLVMIRTranslation MLIRLoopLikeInterface MLIRLspServerLib MLIRMathToLibm MLIRMathToLLVM MLIRMathToSPIRV MLIRMathTransforms MLIRMemRefToLLVM MLIRMemRefToSPIRV MLIRMemRefTransforms MLIRMemRefUtils MLIRMlirOptMain MLIRNVVMToLLVMIRTranslation MLIROpenACCToLLVMIRTranslation MLIROpenACCToSCF MLIROpenMPToLLVMIRTranslation MLIROpenMPToLLVM MLIROptLib MLIRParser MLIRPass MLIRPDLLAST MLIRPDLToPDLInterp MLIRPresburger MLIRReconcileUnrealizedCasts MLIRReduceLib MLIRReduce MLIRRewrite MLIRROCDLToLLVMIRTranslation MLIRSCFToGPU MLIRSCFToOpenMP MLIRSCFToSPIRV MLIRSCFTransforms MLIRShapeOpsTransforms MLIRShapeToStandard MLIRSideEffectInterfaces MLIRSparseTensorTransforms MLIRSparseTensorUtils MLIRSPIRVBinaryUtils MLIRSPIRVConversion MLIRSPIRVDeserialization MLIRSPIRVModuleCombiner MLIRSPIRVSerialization MLIRSPIRVToLLVM MLIRSPIRVTransforms MLIRSPIRVTranslateRegistration MLIRSPIRVUtils MLIRSupport MLIRTargetCpp MLIRTargetLLVMIRExport MLIRTargetLLVMIRImport MLIRTensorInferTypeOpInterfaceImpl MLIRTensorTransforms MLIRTilingInterface MLIRToLLVMIRTranslationRegistration MLIRTosaToLinalg MLIRTosaToSCF MLIRTosaTransforms MLIRTransforms MLIRTransformUtils MLIRVectorInterfaces MLIRVectorToGPU MLIRVectorToLLVM MLIRVectorToSCF MLIRVectorToSPIRV MLIRViewLikeInterface MLIRX86VectorToLLVMIRTranslation MLIRX86VectorTransforms MLIRTensorTilingInterfaceImpl MLIRTensorUtils MLIRSCFUtils MLIRSparseTensorPipelines MLIRVectorTransforms MLIRVectorUtils MLIRAMDGPUDialect MLIRAMDGPUToROCDL MLIRAMXDialect MLIRAffineDialect MLIRArmNeonDialect MLIRArmSVEDialect MLIRAsmParser MLIRAsyncDialect MLIRBufferizationDialect MLIRBufferizationTransformOps MLIRCAPIControlFlow MLIRCAPIFunc MLIRCAPIRegisterEverything MLIRComplexDialect MLIRComplexToLibm MLIRControlFlowDialect MLIRControlFlowToLLVM MLIRControlFlowToSPIRV MLIRDLTIDialect MLIREmitCDialect MLIRExecutionEngineUtils MLIRFuncDialect MLIRFuncToLLVM MLIRFuncToSPIRV MLIRFuncTransforms MLIRInferIntRangeInterface MLIRLLVMDialect MLIRLinalgDialect MLIRLinalgTransformOps MLIRLspServerSupportLib MLIRMLProgramDialect MLIRMathDialect MLIRMemRefDialect MLIRNVGPUDialect MLIRNVGPUToNVVM MLIRNVGPUTransforms MLIRNVVMDialect MLIROpenACCDialect MLIROpenMPDialect MLIRPDLDialect MLIRPDLInterpDialect MLIRPDLLCodeGen MLIRPDLLODS MLIRParallelCombiningOpInterface MLIRQuantDialect MLIRQuantUtils MLIRROCDLDialect MLIRSCFDialect MLIRSCFToControlFlow MLIRSCFTransformOps MLIRSPIRVDialect MLIRShapeDialect MLIRSparseTensorDialect MLIRTensorDialect MLIRTensorToLinalg MLIRTensorToSPIRV MLIRTosaDialect MLIRTosaToArith MLIRTosaToTensor MLIRTransformDialect MLIRTransformDialectTransforms MLIRTranslateLib MLIRVectorDialect MLIRX86VectorDialect MLIRAffineTransformOps MLIRArithAttrToLLVMConversion MLIRArithDialect MLIRArithToLLVM MLIRArithToSPIRV MLIRArithTransforms MLIRArithUtils MLIRBytecodeReader MLIRBytecodeWriter MLIRCAPIMLProgram MLIRCAPITransformDialect MLIRDestinationStyleOpInterface MLIRFromLLVMIRTranslationRegistration MLIRGPUTransformOps MLIRIndexDialect MLIRIndexToLLVM MLIRInferIntRangeCommon MLIRLLVMIRToLLVMTranslation MLIRMaskableOpInterface MLIRMaskingOpInterface MLIRMathToFuncs MLIRMemRefTransformOps MLIRNVGPUUtils MLIRRuntimeVerifiableOpInterface MLIRShapedOpInterfaces MLIRSparseTensorRuntime MLIRTblgenLib MLIRTransformDialectUtils MLIRVectorTransformOps MLIRAMDGPUTransforms MLIRAMDGPUUtils MLIRArithValueBoundsOpInterfaceImpl MLIRArmSMEDialect MLIRArmSMEToLLVMIRTranslation MLIRArmSMETransforms MLIRBuiltinToLLVMIRTranslation MLIRBytecodeOpInterface MLIRCAPIArith MLIRCAPIMath MLIRCAPIMemRef MLIRCAPIVector MLIRComplexToSPIRV MLIRDebug MLIRFuncAllExtensions MLIRFuncInlinerExtension MLIRGPUDialect MLIRGPUToLLVMIRTranslation MLIRIRDL MLIRMemorySlotInterfaces MLIRNVGPUTransformOps MLIRNVVMToLLVM MLIRObservers MLIRPluginsLib MLIRTensorTransformOps MLIRTransformPDLExtension MLIRUBDialect MLIRUBToLLVM MLIRUBToSPIRV MLIRValueBoundsOpInterface MLIRVectorToArmSME MLIRArithToAMDGPU MLIRArithToArmSME MLIRArmSMEToLLVM MLIRArmSMEToSCF MLIRBufferizationPipelines MLIRCAPIAMDGPU MLIRCAPINVGPU MLIRCAPINVVM MLIRCAPIOpenMP MLIRCAPIROCDL MLIRCAPISPIRV MLIRCAPITarget MLIRControlFlowToSCF MLIRControlFlowTransforms MLIRConvertToLLVMInterface MLIRConvertToLLVMPass MLIREmitCTransforms MLIRFuncTransformOps MLIRFunctionInterfaces MLIRGPUPipelines MLIRIndexToSPIRV MLIRLLVMIRToNVVMTranslation MLIRMLProgramTransforms MLIRMeshDialect MLIRMeshTransforms MLIRNVVMTarget MLIROpenACCMPCommon MLIRQuery MLIRQueryLib MLIRQueryMatcher MLIRROCDLTarget MLIRRewritePDL MLIRSCFToEmitC MLIRSPIRVTarget MLIRSPIRVToLLVMIRTranslation MLIRShardingInterface MLIRSparseTensorTransformOps MLIRSubsetOpInterface MLIRTargetLLVM MLIRTosaShardingInterfaceImpl MLIRTosaToMLProgram MLIRTransformDebugExtension MLIRTransformLoopExtension MLIRVectorToLLVMPass MLIRArithToEmitC MLIRArmNeonTransforms MLIRCAPIIRDL MLIRCAPITransformDialectTransforms MLIRConvertToSPIRVPass MLIRFuncMeshShardingExtensions MLIRFuncToEmitC MLIRGPUToLLVMSPV MLIRMPIDialect MLIRMathToROCDL MLIRMemRefToEmitC MLIROpenACCTransforms MLIRPolynomialDialect MLIRPtrDialect MLIRTransformDialectIRDLExtension MLIRTransformDialectInterfaces MLIRVCIXDialect MLIRVCIXToLLVMIRTranslation MLIRXeGPUDialect MLIRXeGPUTransforms MLIRCAPIEmitC MLIRDLTITransformOps MLIRGPUUtils MLIRMathToEmitC MLIRMeshToMPI MLIRQuantTransforms MLIRSPIRVAttrToLLVMConversion MLIRTensorAllExtensions MLIRTensorMeshShardingExtensions MLIRVectorToXeGPU
%if %{with tests}
%global MLIRLibs %{MLIRLibs} MLIRAffineTransformsTestPasses MLIRDLTITestPasses MLIRGPUTestPasses MLIRLinalgTestPasses MLIRMathTestPasses MLIRSCFTestPasses MLIRShapeTestPasses MLIRSPIRVTestPasses MLIRTosaTestPasses MLIRVectorTestPasses MLIRMemRefTestPasses MLIRFuncTestPasses MLIRTensorTestPasses MLIRTilingInterfaceTestPasses MLIRArithTestPasses MLIRBufferizationTestPasses MLIRControlFlowTestPasses MLIRLLVMTestPasses MLIRNVGPUTestPasses MLIRLoopLikeInterfaceTestPasses MLIRTestAnalysis MLIRTestDialect MLIRTestIR MLIRTestPass MLIRTestReducer MLIRTestRewrite MLIRTestTransforms MLIRTestFuncToLLVM MLIRTestPDLL MLIRTestTransformDialect MLIRTestDynDialect MLIRTestOneToNTypeConversionPass MLIRTestVectorToSPIRV MLIRMeshTest MLIRTestToLLVMIRTranslation MLIRArmNeonTestPasses MLIRArmSMETestPasses MLIRTestConvertToSPIRV MLIRTestFromLLVMIRTranslation MLIRTestMathToVCIX
%endif

# New in 16: Anything starting from MLIRAffineTransformOps
# New in 18: Anything starting from MLIRArithToAMDGPU
# New in 19: Anything starting from MLIRArithToEmitC (main) and MLIRArmNeonTestPasses (tests)

# Removed in 14: MLIRLoopAnalysis
# Removed in 16: MLIRArithmeticToLLVM MLIRArithmeticToSPIRV MLIRArithmeticTransform MLIRLinalgToSPIRV MLIRArithmeticDialect MLIRArithmeticUtils MLIRQuantTransforms
# Removed in 17: MLIRGPUOps MLIRLinalgAnalysis  MLIROpenACCToLLVM  MLIRSupportIndentedOstream 
# Removed in 18: MLIRLinalgToLLVM MLIRArmSMEUtils
# Removed in 20: MLIRGPUToVulkanTransforms 
%else
%global MLIRLibs %{nil}
%endif

%if %{with lld}
%define LLDLibs lldCOFF lldCommon lldELF lldMachO lldMinGW lldWasm
%else
%define LLDLibs %{nil}
%endif
# Removed as of 14: lldCore lldDriver lldMachO2 lldReaderWriter lldYAML

%{expand:%(for i in %{LLVMLibs} %{LLVM64Libs} %{ClangLibs} %{Clang64Libs} %{LLDLibs} %{MLIRLibs} %{FlangLibs} %{BOLTLibs}; do
	cat <<EOF
%%define static$i %%{mklibname -d -s $i}
%%package -n %%{static$i}
Summary: LLVM $i static library
Group: Development/Libraries
EOF

	if [ "$i" = "MLIRArithUtils" ]; then
		echo "Obsoletes: %{mklibname -d -s MLIRArithmeticUtils} < %{EVRD}"
	elif [ "$i" = "MLIRArithToLLVM" ]; then
		echo "Obsoletes: %{mklibname -d -s MLIRArithmeticToLLVM} < %{EVRD}"
	elif [ "$i" = "MLIRArithToSPIRV" ]; then
		echo "Obsoletes: %{mklibname -d -s MLIRArithmeticToSPIRV} < %{EVRD}"
	elif [ "$i" = "MLIRArithTransforms" ]; then
		echo "Obsoletes: %{mklibname -d -s MLIRArithmeticTransform} < %{EVRD}"
	elif [ "$i" = "MLIRMathToSPIRV" ]; then
		echo "Obsoletes: %{mklibname -d -s MLIRLinalgToSPIRV} < %{EVRD}"
	elif [ "$i" = "MLIRArithDialect" ]; then
		echo "Obsoletes: %{mklibname -d -s MLIRArithmeticDialect} < %{EVRD}"
	elif [ "$i" = "MLIRLinalgToStandard" ]; then
		echo "Obsoletes: %{mklibname -d -s MLIRLinalgToLLVM} < %{EVRD}"
	elif [ "$i" = "MLIRArmSMEDialect" ]; then
		echo "Obsoletes: %{mklibname -d -s MLIRArmSMEUtils} < %{EVRD}"
	elif [ "$i" = "MLIRQuantUtils" ]; then
		echo "Obsoletes: %{mklibname -d -s MLIRQuantTransforms} < %{EVRD}"
	elif [ "$i" = "LLVMAMDGPUCodeGen" ]; then
		echo "Obsoletes: %{mklibname -d -s LLVMMCACustomBehaviourAMDGPU} < %{EVRD}"
	elif [ "$i" = "LLVMTableGenBasic" ]; then
		echo "Obsoletes: %{mklibname -d -s LLVMTableGenGlobalISel} < %{EVRD}"
	elif [ "$i" = "LLVMCodeGen" ]; then
		echo "Obsoletes: %{mklibname -d -s LLVMCodeGenData} < %{EVRD}"
	fi

	cat <<EOF

%%description -n %%{static$i}
LLVM $i static library

%%files -n %%{static$i}
%{_libdir}/lib$i.a
EOF
done)}

%if %{with compat32}
%{expand:%(for i in %{LLVMLibs} %{ClangLibs}; do
	cat <<EOF
%%package -n lib$i-static-devel
Summary: LLVM $i static library (32-bit)
Group: Development/Libraries

%%description -n lib$i-static-devel
LLVM $i static library (32-bit)

%%files -n lib$i-static-devel
%{_prefix}/lib/lib$i.a
EOF
done)}
%endif

%if %{with unwind}
%define libunwind_major 1.0
%define libunwind %mklibname unwind %{libunwind_major}
%define devunwind %mklibname -d unwind

%package -n %{libunwind}
Summary:	The LLVM unwind library
Group:		System/Libraries

%description -n %{libunwind}
The unwind library, a part of llvm.

%files -n %{libunwind}
%{_libdir}/libunwind.so.%{libunwind_major}
%{_libdir}/libunwind.so.1

%package -n %{devunwind}
Summary:	Development files for libunwind
Group:		Development/C
Requires:	%{libunwind} = %{EVRD}

%description -n %{devunwind}
Development files for libunwind.

%files -n %{devunwind}
%{_libdir}/libunwind.a
%{_libdir}/libunwind.so
%if %{with default_compilerrt}
%{_libdir}/pkgconfig/libunwind.pc
%else
%{_libdir}/pkgconfig/libunwind-llvm.pc
%endif
%{_includedir}/unwind.h
%{_includedir}/libunwind.h
%{_includedir}/__libunwind_config.h
%{_includedir}/libunwind.modulemap
%{_includedir}/unwind_arm_ehabi.h
%{_includedir}/unwind_itanium.h
%{_includedir}/mach-o
%endif

#-----------------------------------------------------------
%if %{with libcxx}
%package -n %{mklibname c++}
Summary: The libc++ library, an implementation of the C++ STL
Group: System/Libraries
%rename %{mklibname c++ 1}

%description -n %{mklibname c++}
The libc++ library, an implementation of the C++ STL

%files -n %{mklibname c++}
%{_libdir}/libc++.so.1*

%package -n %{mklibname c++abi}
Summary: Low level implementation of the C++ ABI
Group: System/Libraries
%rename %{mklibname c++abi 1}

%description -n %{mklibname c++abi}
The libc++ library, an implementation of the C++ STL

%files -n %{mklibname c++abi}
%{_libdir}/libc++abi.so.1*

%define cxxdevname %mklibname c++ -d
%define cxxabistatic %mklibname c++abi -d -s

%package -n %{cxxdevname}
Summary:	Development files for libc++, an alternative implementation of the STL
Group:		Development/C
Requires:	%{mklibname c++ 1} = %{EVRD}
Requires:	%{mklibname c++abi 1} = %{EVRD}
Provides:	c++-devel = %{EVRD}

%description -n %{cxxdevname}
Development files for libc++, an alternative implementation of the STL.

%files -n %{cxxdevname}
%{_includedir}/c++
%{_includedir}/__pstl*
%{_includedir}/pstl
%{_prefix}/lib/cmake/ParallelSTL
%{_libdir}/libc++experimental.a
%{_libdir}/libc++abi.so
%{_libdir}/libc++.so
%{_libdir}/libc++.a
%{_libdir}/libc++.modules.json
%{_datadir}/libc++

%package -n %{cxxabistatic}
Summary:	Static library for libc++ C++ ABI support
Group:		Development/C
Requires:	%{cxxdevname} = %{EVRD}

%description -n %{cxxabistatic}
Static library for libc++'s C++ ABI library.

%files -n %{cxxabistatic}
%{_libdir}/libc++abi.a
%endif

#-----------------------------------------------------------
%define libname %mklibname %{name}

%package -n %{libname}
Summary:	LLVM shared libraries
Group:		System/Libraries
Conflicts:	llvm < 3.0-4
Obsoletes:	%{mklibname %{name} 3.5.0} < 14.0.0
Obsoletes:	%{mklibname %{name} 3.6.0} < 14.0.0
Obsoletes:	%{mklibname LLVMCppBackendCodeGen 3} < 14.0.0
Obsoletes:	%{mklibname LLVMCppBackendInfo 3} < 14.0.0
Obsoletes:	%{mklibname LLVMAArch64AsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMARMAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMLanaiAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMMSP430AsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMMipsAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMNVPTXAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMPowerPCAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMAMDGPUAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMSparcAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMSystemZAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMX86AsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMXCoreAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMWebAssemblyAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMRISCVAsmPrinter 9} < 14.0.0
%rename		%{mklibname LLVMLTO 11}
%rename		%{mklibname clangCodeGen 11}
%rename		%{mklibname %{name} %{major}}
Obsoletes:	%{mklibname clang-cpp 11} < 14.0.0
Obsoletes:	%{mklibname LLVMExtensions 11} < 14.0.0
Obsoletes:	%{mklibname LLVMExtensions 14} < %{EVRD}
Obsoletes:	%{mklibname LLVMLTO 14} < %{EVRD}
Obsoletes:	%{mklibname Remarks 14} < %{EVRD}

%description -n %{libname}
Shared libraries for the LLVM compiler infrastructure. This is needed by
programs that are dynamically linked against libLLVM.

%files -n %{libname}
%{_libdir}/libLLVM-*.so
%{_libdir}/libLLVM.so.%{major}
%{_libdir}/libLLVMOffload.so.%{major}
%{_libdir}/libRemarks.so.*

#-----------------------------------------------------------

%define devname %mklibname -d %{name}

%package -n %{devname}
Summary:	Development files for LLVM
Group:		Development/Other
Provides:	llvm-devel = %{EVRD}
Requires:	%{libname} = %{EVRD}
Requires:	%{name} = %{EVRD}
# Have to do those manually because we filter
# devel(*) deps for clang
Requires:	pkgconfig(libedit)
Requires:	ffi-devel
Requires:	pkgconfig(ncursesw)
Requires:	stdc++-devel
Requires:	pkgconfig(zlib)
%if %{with mlir}
# Required because of references in LLVMExports.cmake
Requires:	llvm-mlir-tools = %{EVRD}
%endif
# Back to regular dependencies
%if %{with openmp}
Provides:	openmp-devel = %{EVRD}
Requires:	%{ompname} = %{EVRD}
%if "%{_lib}" == "lib64"
Provides:	devel(libomp(64bit))
%else
Provides:	devel(libomp)
%endif
%endif

%description -n %{devname}
This package contains the development files for LLVM.

%files -n %{devname}
%{_bindir}/%{name}-config
%{_includedir}/%{name}
%{_includedir}/%{name}-c
%{_includedir}/offload
%{_libdir}/cmake/%{name}
%{_libdir}/lib*.so
%exclude %{_libdir}/libLLVM-*.so
%if %{with openmp}
%exclude %{_libdir}/libomptarget.so
%endif
# FIXME this needs a real soname
%exclude %{_libdir}/libSPIRV-Tools-shared.so
%ifnarch %{arm} %{riscv}
%{_libdir}/libarcher_static.a
%endif
%if %{with openmp}
%exclude %{_libdir}/libomp.so
%endif
%if %{with libcxx}
%exclude %{_libdir}/libc++abi.so
%endif
# Stuff from clang
%exclude %{_libdir}/libclang*.so
%exclude %{_libdir}/libLTO.so

#-----------------------------------------------------------
%define staticname %mklibname -d -s %{name}

%package -n %{staticname}
Summary:	Static library files for LLVM
Group:		Development/Other
Provides:	llvm-static-devel = %{EVRD}
Requires:	%{devname} = %{EVRD}
%{expand:%(for i in %{LLVMLibs} %{LLVM64Libs} %{ClangLibs} %{Clang64Libs} %{LLDLibs} %{MLIRLibs} %{FlangLibs} %{BOLTLibs}; do
	echo "Requires: %%{mklibname -d -s $i} = %{EVRD}"
done)}

%description -n %{staticname}
Static library files for LLVM

%files -n %{staticname}

#-----------------------------------------------------------
%if %{with openmp}
%package -n %{ompname}
Summary:	LLVM OpenMP shared libraries
Group:		System/Libraries
%rename %{oldompname}
# For libomp.so compatibility (see comment in file list)
%if "%{_lib}" == "lib64"
Provides:	libomp.so()(64bit)
Provides:	libomp.so(GOMP_1.0)(64bit)
Provides:	libomp.so(GOMP_2.0)(64bit)
Provides:	libomp.so(GOMP_3.0)(64bit)
Provides:	libomp.so(GOMP_4.0)(64bit)
Provides:	libomp.so(OMP_1.0)(64bit)
Provides:	libomp.so(OMP_2.0)(64bit)
Provides:	libomp.so(OMP_3.0)(64bit)
Provides:	libomp.so(OMP_3.1)(64bit)
Provides:	libomp.so(OMP_4.0)(64bit)
Provides:	libomp.so(VERSION)(64bit)
%else
Provides:	libomp.so
Provides:	libomp.so(GOMP_1.0)
Provides:	libomp.so(GOMP_2.0)
Provides:	libomp.so(GOMP_3.0)
Provides:	libomp.so(GOMP_4.0)
Provides:	libomp.so(OMP_1.0)
Provides:	libomp.so(OMP_2.0)
Provides:	libomp.so(OMP_3.0)
Provides:	libomp.so(OMP_3.1)
Provides:	libomp.so(OMP_4.0)
Provides:	libomp.so(VERSION)
%endif

%description -n %{ompname}
Shared libraries for LLVM OpenMP support.

%files -n %{ompname}
# (Slightly) nonstandard behavior: We package the .so
# file in the library package.
# This is because upstream doesn't assign sonames, and
# by keeping the .so we can keep compatible with binaries
# built against upstream libomp
%{_libdir}/libomp.so*
%{_libdir}/libomptarget.so
%{_libdir}/libomptarget-*.bc
%{_libdir}/libomptarget.devicertl.a
%{_libdir}/libomptarget.so.%{major}
%endif

#-----------------------------------------------------------

%package doc
Summary:	Documentation for LLVM
Group:		Books/Computer books
Requires:	%{name} = %{version}
BuildArch:	noarch
Obsoletes:	llvm-doc-devel < 6.0.0

%description doc
Documentation for the LLVM compiler infrastructure.

%files doc
%doc %dir %{_docdir}/LLVM
%doc %{_docdir}/LLVM/llvm

#-----------------------------------------------------------
%package polly
Summary:	Polyhedral optimizations for LLVM
License:	MIT
Group:		Development/Other
Obsoletes:	llvm-devel < 4.0.1
Obsoletes:	%{_lib}llvm-devel < 4.0.1
Conflicts:	%{_lib}llvm-devel < 4.0.1
Obsoletes:	%{_lib}Polly13 < %{EVRD}
Obsoletes:	%{_lib}Polly14 < %{EVRD}

%description polly
Polly is a polyhedral optimizer for LLVM.

Using an abstract mathematical representation it analyzes and optimizes
the memory access pattern of a program. This includes data-locality
optimizations for cache locality as well as automatic parallelization
for thread-level and SIMD parallelism.

Our overall goal is an integrated optimizer for data-locality and
parallelism that takes advantage of multi-cores, cache hierarchies,
short vector instructions as well as dedicated accelerators.

%files polly
%{_libdir}/LLVMPolly.so
%doc %{_mandir}/man1/polly.1*

#-----------------------------------------------------------
%package polly-devel
Summary:	Development files for Polly
License:	MIT
Group:		Development/Other
Requires:	%{name}-polly = %{EVRD}
Requires:	%{mklibname -d -s Polly} = %{EVRD}

%description polly-devel
Development files for Polly.

Polly is a polyhedral optimizer for LLVM.

Using an abstract mathematical representation it analyzes and optimizes
the memory access pattern of a program. This includes data-locality
optimizations for cache locality as well as automatic parallelization
for thread-level and SIMD parallelism.

Our overall goal is an integrated optimizer for data-locality and
parallelism that takes advantage of multi-cores, cache hierarchies,
short vector instructions as well as dedicated accelerators.

%files polly-devel
%doc %{_docdir}/LLVM/polly
%{_includedir}/polly
%{_libdir}/cmake/polly
%{_libdir}/libPollyISL.a
#-----------------------------------------------------------

%if %{with clang}
%package -n clang
Summary:	A C language family front-end for LLVM
License:	NCSA
Group:		Development/Other
Provides:	%{_bindir}/cc
# TODO: is this requires:llvm needed, or just legacy from fedora pkg layout?
Requires:	llvm%{?_isa} = %{EVRD}
# clang requires gcc, clang++ requires libstdc++-devel
Requires:	gcc
Requires:	libstdc++-devel >= %{gcc_version}
%if %{with unwind} && %{with default_compilerrt}
Requires:	%{_lib}unwind1.0 = %{EVRD}
Requires:	%{devunwind} = %{EVRD}
%else
%ifnarch %{riscv}
%ifarch %{ix86}
# Workaround for missing previous packaging change
BuildRequires:	pkgconfig(libunwind)
%else
BuildRequires:	pkgconfig(libunwind-llvm)
%endif
%endif
%endif
Obsoletes:	%{mklibname clang 3.7.0} < 14.0.0
Obsoletes:	%{mklibname clang_shared 9} < 14.0.0
# Remains of BUILD_SHARED_LIBS=ON builds
Obsoletes:	%{_lib}clangCodeGen14 < %{EVRD}
Obsoletes:	%{_lib}clang-cpp14 < %{EVRD}
Obsoletes:	%{_lib}clangFrontendTool14 < %{EVRD}
Obsoletes:	%{_lib}clangDependencyScanning14 < %{EVRD}
Obsoletes:	%{_lib}clangInterpreter14 < %{EVRD}
Obsoletes:	%{_lib}clangHandleCXX14 < %{EVRD}
Obsoletes:	%{_lib}LTO14 < %{EVRD}

%description -n clang
clang: noun
    1. A loud, resonant, metallic sound.
    2. The strident call of a crane or goose.
    3. C-language family front-end toolkit.

The goal of the Clang project is to create a new C, C++, Objective C
and Objective C++ front-end for the LLVM compiler. Its tools are built
as libraries and designed to be loosely-coupled and extensible.

%files -n clang
%{_bindir}/clang
%{_bindir}/clang-linker-wrapper
%{_bindir}/clang++
%{_bindir}/clang-%{major1}
%{_bindir}/clang-offload-packager
%{_bindir}/clang-cpp
%{_libdir}/LLVMgold.so
%if %{build_lto}
%{_libdir}/bfd-plugins/LLVMgold.so
%endif
%{_libdir}/libLTO.so.*
%{_libdir}/libclang-cpp.so.*
%{_libdir}/libclang.so.*
%{_libdir}/libLTO.so
%{_datadir}/clang
%if %{with default_compiler}
%{_bindir}/cc
%{_bindir}/c89
%{_bindir}/c99
%{_bindir}/c++
%endif
%doc %{_mandir}/man1/clang.1*
%dir %{_libdir}/clang
%dir %{_libdir}/clang/%{major1}
%dir %{_libdir}/clang/%{major1}/lib
%dir %{_libdir}/clang/%{major1}/lib/*
%{_libdir}/clang/%{major1}/lib/*/clang_rt*.o
%{_libdir}/clang/%{major1}/lib/*/libclang_rt*.a
# No sanitizers on RISC-V yet, only static clang_rt
%ifnarch %{riscv}
%{_libdir}/clang/%{major1}/lib/*/libclang_rt*.so
%{_libdir}/clang/%{major1}/lib/*/libclang_rt*.syms
# Contains hwasan, therefore no RISC-V
%{_libdir}/clang/%{major1}/bin
# Contains sanitizer configs, therefore no RISC-V
%{_libdir}/clang/%{major1}/share
%endif
%{_libdir}/clang/%{major1}/lib/*/liborc_rt*.a
%{_libdir}/clang/%{major1}/include
%if %{with openmp}
%{_libdir}/cmake/openmp/FindOpenMPTarget.cmake
%{_datadir}/gdb/python/ompd
%endif

#-----------------------------------------------------------

%if %{with bolt}
%package bolt
Summary:	Binary optimizer for LLVM
License:	NCSA
Group:		Development/Other

%description bolt
Binary Optimization and Layout Tool - A linux command-line utility used for
optimizing performance of binaries

%files bolt
%doc %{_docdir}/LLVM/bolt
%{_bindir}/llvm-bolt
%{_bindir}/llvm-bolt-binary-analysis
%{_bindir}/llvm-bolt-heatmap
%{_bindir}/llvm-boltdiff
%{_bindir}/merge-fdata
%{_bindir}/perf2bolt
%ifarch %{x86_64} %{aarch64}
%{_libdir}/libbolt_rt_hugify.a
%{_libdir}/libbolt_rt_instr.a
%endif
#doc %{_docdir}/bolt
%endif

#-----------------------------------------------------------

%package -n clang-tools
Summary:	Various tools for LLVM/clang
Group:		Development/Other
Requires:	clang = %{EVRD}

%description -n clang-tools
A various tools for LLVM/clang.

%files -n clang-tools
%{_bindir}/clang-apply-replacements
%{_bindir}/clang-change-namespace
%{_bindir}/clang-check
%{_bindir}/clang-cl
%{_bindir}/clang-doc
%{_bindir}/clang-extdef-mapping
%{_bindir}/clang-format
%{_bindir}/clang-include-cleaner
%{_bindir}/clang-include-fixer
%{_bindir}/clang-move
%{_bindir}/clang-offload-bundler
%{_bindir}/clang-query
%{_bindir}/clang-refactor
%{_bindir}/clang-repl
%{_bindir}/clang-reorder-fields
%{_bindir}/clang-scan-deps
%{_bindir}/clang-sycl-linker
%{_bindir}/clang-tidy
%{_bindir}/clang-installapi
%{_bindir}/clang-nvlink-wrapper
%{_bindir}/run-clang-tidy
%{_bindir}/clangd
%{_bindir}/diagtool
%{_bindir}/find-all-symbols
%{_bindir}/hmaptool
%{_bindir}/modularize
%{_bindir}/pp-trace
%{_datadir}/clang-doc
%doc %{_mandir}/man1/diagtool.1*
%doc %{_mandir}/man1/extraclangtools.1*

%define devclang %mklibname -d clang

%package -n %{devclang}
Summary:	Development files for clang
Group:		Development/Other
Requires:	clang = %{EVRD}
Requires:	clang-tools = %{EVRD}
Provides:	clang-devel = %{EVRD}
Conflicts:	llvm-devel < 3.1
Obsoletes:	clang-devel < 3.1
Conflicts:	llvm < 8.0.1-0.359209.2
Obsoletes:	%{_lib}clang14

%description -n %{devclang}
This package contains header files and libraries needed for using
libclang.

%files -n %{devclang}
%{_bindir}/clang-tblgen
%{_includedir}/clang
%{_includedir}/clang-c
%{_includedir}/clang-tidy
%{_libdir}/libclang*.so
%{_libdir}/cmake/clang
%doc %{_mandir}/man1/clang-tblgen.1*

%package -n clang-analyzer
Summary:	A source code analysis framework
License:	NCSA
Group:		Development/Other
Requires:	clang%{?_isa} = %{EVRD}
# not picked up automatically since files are currently not instaled
# in standard Python hierarchies yet
Requires:	python

%description -n clang-analyzer
The Clang Static Analyzer consists of both a source code analysis
framework and a standalone tool that finds bugs in C and Objective-C
programs. The standalone tool is invoked from the command-line, and is
intended to run in tandem with a build of a project or code base.

%files -n clang-analyzer
%{_datadir}/opt-viewer
%{_bindir}/analyze-build
%{_bindir}/intercept-build
%{_bindir}/scan-build
%{_bindir}/scan-build-py
%{_bindir}/scan-view
%{_prefix}/lib/libear
%{_prefix}/lib/libscanbuild
%{_libexecdir}/ccc-analyzer
%{_libexecdir}/c++-analyzer
%{_libexecdir}/analyze-c++
%{_libexecdir}/analyze-cc
%{_libexecdir}/intercept-c++
%{_libexecdir}/intercept-cc
%{_datadir}/scan-build
%{_datadir}/scan-view
%doc %{_mandir}/man1/scan-build.1*

%package -n clang-doc
Summary:	Documentation for Clang
Group:		Books/Computer books
BuildArch:	noarch
Requires:	%{name} = %{EVRD}

%description -n clang-doc
Documentation for the Clang compiler front-end.

%files -n clang-doc
%doc %{_docdir}/LLVM/clang-tools
%doc %{_docdir}/LLVM/clang
%endif

%if %{with ocaml}
%package -n ocaml-%{name}
Summary:	Objective-CAML bindings for LLVM
Group:		Development/Other
Requires:	%{name} = %{EVRD}

%description -n ocaml-%{name}
Objective-CAML bindings for LLVM.

%files -n ocaml-%{name}
%{_libdir}/ocaml/*
%endif
#-----------------------------------------------------------

%if %{with flang}
%package -n flang
Summary:	A Fortran language front-end for LLVM
License:	NCSA
Group:		Development/Other
Requires:	clang = %{EVRD}
%if %{with unwind}
Requires:	%{_lib}unwind1.0 = %{EVRD}
Requires:	%{devunwind} = %{EVRD}
%endif

%description -n flang
A Fortran language front-end for LLVM

%files -n flang
%{_bindir}/bbc
%{_bindir}/flang
%{_bindir}/flang-%{major1}
%{_bindir}/flang-new
%{_bindir}/fir-lsp-server
%{_bindir}/fir-opt
%{_bindir}/f18-parse-demo
%{_bindir}/tco
%doc %{_docdir}/LLVM/flang

%define flangdev %mklibname -d flang

%package -n %{flangdev}
Summary:	Development files for Flang, the LLVM Fortran compiler
Group:		Development/Fortran

%description -n %{flangdev}
Development files for Flang, the LLVM Fortran compiler.

%files -n %{flangdev}
%{_includedir}/flang
%{_libdir}/cmake/flang
%endif

#-----------------------------------------------------------

%if %{with lldb}
%package -n lldb
Summary:	Debugger from the LLVM toolchain
Group:		Development/Other
Requires:	python-six
Obsoletes:	%{_lib}lldb14 < %{EVRD}
Obsoletes:	%{_lib}lldbIntelFeatures14 < %{EVRD}

%description -n lldb
Debugger from the LLVM toolchain.

%files -n lldb
%{_bindir}/lldb*
%{_libdir}/liblldb.so.*
%{_libdir}/liblldbIntelFeatures.so.*
%{_libdir}/lua/*/lldb.so
%{_libdir}/python*/site-packages/lldb
%doc %{_mandir}/man1/lldb.1*
%doc %{_mandir}/man1/lldb-server.1*
%doc %{_docdir}/LLVM/lldb
%doc %{_mandir}/man1/lldb-tblgen.1*

%define lldbdev %mklibname -d lldb

%package -n %{lldbdev}
Summary:	Development files for the LLDB debugger
Group:		Development/Other
Requires:	lldb = %{EVRD}

%description -n %{lldbdev}
Development files for the LLDB debugger.

%files -n %{lldbdev}
%{_includedir}/lldb
%endif

#-----------------------------------------------------------
%if %{with lld}
%package -n lld
Summary:	The linker from the LLVM project
License:	NCSA
Group:		Development/Other
# Stuff from lld 3.8 that has been removed in 3.9
Obsoletes:	%{mklibname lldAArch64ELFTarget 3} < 14.0.0
Obsoletes:	%{mklibname lldARMELFTarget 3} < 14.0.0
Obsoletes:	%{mklibname lldELF2 3} < 14.0.0
Obsoletes:	%{mklibname lldExampleSubTarget 3} < 14.0.0
Obsoletes:	%{mklibname lldHexagonELFTarget 3} < 14.0.0
Obsoletes:	%{mklibname lldMipsELFTarget 3} < 14.0.0
Obsoletes:	%{mklibname lldX86ELFTarget 3} < 14.0.0
Obsoletes:	%{mklibname lldX86_64ELFTarget 3} < 14.0.0
# Stuff from lld 5.0 that has been removed in 6.0
Obsoletes:	%{mklibname lldELF 5} < 14.0.0
Obsoletes:	%{mklibname lldConfig 5} < 14.0.0
# From BUILD_SHARED_LIBS=ON builds
Obsoletes:	%{_lib}lldCOFF14 < %{EVRD}
Obsoletes:	%{_lib}lldELF14 < %{EVRD}
Obsoletes:	%{_lib}lldMachO14 < %{EVRD}
Obsoletes:	%{_lib}lldWasm14 < %{EVRD}
Obsoletes:	%{_lib}lldMinGW14 < %{EVRD}

%description -n lld
The linker from the LLVM project.

%files -n lld
#doc %{_docdir}/lld
%{_bindir}/ld.lld
%{_bindir}/ld64.lld
%{_bindir}/lld
%{_bindir}/lld-link
%{_bindir}/llvm-dlltool
%{_bindir}/llvm-mt
%doc %{_mandir}/man1/ld.lld.1*

#-----------------------------------------------------------

%define devlld %mklibname -d lld

%package -n %{devlld}
Summary:	Development files for lld
Group:		Development/Other
Requires:	lld = %{EVRD}

%description -n %{devlld}
This package contains header files and libraries needed for
writing lld plugins.

%files -n %{devlld}
%doc %{_docdir}/LLVM/lld
%{_includedir}/lld
%{_libdir}/cmake/lld
%endif
#-----------------------------------------------------------

%package -n python-clang
Summary:	Python bindings to parts of the Clang library
Group:		Development/Python

%description -n python-clang
Python bindings to parts of the Clang library

%files -n python-clang
%{python_sitelib}/clang
#-----------------------------------------------------------

%package libgomp
Summary:	LLVM's version of libgomp (the GCC variant of OpenMP)
Group:		System/Libraries

%description libgomp
LLVM's version of libgomp (the GCC variant of OpenMP)

%files libgomp
%{_libdir}/libgomp.so.1

#-----------------------------------------------------------
%if %{with compat32}
%package -n libllvm
Summary:	32-bit LLVM library
Group:		System/Libraries
Obsoletes:	libLTO14 < %{EVRD}
Obsoletes:	libclangInterpreter14 < %{EVRD}
Obsoletes:	libRemarks14 < %{EVRD}

%description -n libllvm
32-bit LLVM library

%files -n libllvm
%{_prefix}/lib/libLLVM-*.so
%{_prefix}/lib/libLLVM.so.%{major}
%{_prefix}/lib/libRemarks.so.*

%package -n libllvm-devel
Summary:	32-bit LLVM development files
Group:		Development/C
# Leftovers from BUILD_SHARED_LIBS builds
Obsoletes:	libLLVMLTO14 < %{EVRD}
Obsoletes:	libLLVMExtensions14 < %{EVRD}

%description -n libllvm-devel
32-bit LLVM development files.

%files -n libllvm-devel
%{_prefix}/lib/cmake/llvm
%{_prefix}/lib/libLLVM.so
%{_prefix}/lib/libLTO.so
%{_prefix}/lib/libRemarks.so

%package -n libclang
Summary:	32-bit Clang library
Group:		Development/C
# Old naming scheme
Obsoletes:	libclang14 < %{EVRD}

%description -n libclang
32-bit Clang library

%files -n libclang
%{_prefix}/lib/libclang-cpp.so.*
%{_prefix}/lib/libclang.so.*
%{_prefix}/lib/libLTO.so.*

%package -n libclang-devel
Summary:	32-bit Clang development files
Group:		Development/C
Requires:	libllvm-devel = %{EVRD}
Requires:	libclang = %{EVRD}
# Leftovers from BUILD_SHARED_LIBS builds
Obsoletes:	libclangCodeGen14 < %{EVRD}
Obsoletes:	libclangFrontendTool14 < %{EVRD}
Obsoletes:	libclangDependencyScanning14 < %{EVRD}
Obsoletes:	libclangHandleCXX14 < %{EVRD}
Obsoletes:	libclang-cpp14 < %{EVRD}

%description -n libclang-devel
32-bit Clang development files.

%files -n libclang-devel
%{_prefix}/lib/cmake/clang
%{_prefix}/lib/libclang*.so

%package -n libomp
Summary:	32-bit OpenMP runtime
Group:		System/Libraries
%rename libomp1

%description -n libomp
32-bit OpenMP runtime.

%files -n libomp
%{_prefix}/lib/libomp.so.1*
# FIXME does this need a SOVERSION?
%{_prefix}/lib/libompd.so
%{_prefix}/lib/libarcher.so

%package -n libomp-devel
Summary:	Development files for the 32-bit OpenMP runtime
Group:		Development/C

%description -n libomp-devel
Development files for the 32-bit OpenMP runtime.

%files -n libomp-devel
%{_prefix}/lib/libiomp5.so
%{_prefix}/lib/libomp.so
%{_prefix}/lib/cmake/openmp/FindOpenMPTarget.cmake
%{_prefix}/lib/libarcher_static.a

%if "%{_lib}" != "lib"
%package libgomp32
Summary:	LLVM's version of 32-bit libgomp (the GCC variant of OpenMP)
Group:		System/Libraries

%description libgomp32
LLVM's version of 32-bit libgomp (the GCC variant of OpenMP)

%files libgomp32
%{_prefix}/lib/libgomp.so.1
%endif

%package polly32
Summary:	Polyhedral optimizations for LLVM (32-bit)
License:	MIT
Group:		Development/Other
Obsoletes:	libPolly13 < %{EVRD}
Obsoletes:	libPolly14 < %{EVRD}

%description polly32
Polly is a polyhedral optimizer for LLVM.

Using an abstract mathematical representation it analyzes and optimizes
the memory access pattern of a program. This includes data-locality
optimizations for cache locality as well as automatic parallelization
for thread-level and SIMD parallelism.

Our overall goal is an integrated optimizer for data-locality and
parallelism that takes advantage of multi-cores, cache hierarchies,
short vector instructions as well as dedicated accelerators.

%files polly32
%{_prefix}/lib/LLVMPolly.so

%package polly32-devel
Summary:	Development files for Polly (32-bit)
License:	MIT
Group:		Development/Other
Requires:	%{name}-polly32 = %{EVRD}
Requires:	%{name}-polly-devel = %{EVRD}
Requires:	%{mklib32name -d -s Polly} = %{EVRD}

%description polly32-devel
Development files for Polly.

Polly is a polyhedral optimizer for LLVM.

Using an abstract mathematical representation it analyzes and optimizes
the memory access pattern of a program. This includes data-locality
optimizations for cache locality as well as automatic parallelization
for thread-level and SIMD parallelism.

Our overall goal is an integrated optimizer for data-locality and
parallelism that takes advantage of multi-cores, cache hierarchies,
short vector instructions as well as dedicated accelerators.

%files polly32-devel
%{_prefix}/lib/libPollyISL.a
%{_prefix}/lib/cmake/polly

%define lib32unwind libunwind%{libunwind_major}
%define dev32unwind libunwind-devel

%package -n %{lib32unwind}
Summary:	The LLVM unwind library (32-bit)
Group:		System/Libraries

%description -n %{lib32unwind}
The unwind library, a part of llvm.

%files -n %{lib32unwind}
%{_prefix}/lib/libunwind.so.%{libunwind_major}
%{_prefix}/lib/libunwind.so.1

%package -n %{dev32unwind}
Summary:	Development files for libunwind (32-bit)
Group:		Development/C
Requires:	%{lib32unwind} = %{EVRD}
Requires:	%{devunwind} = %{EVRD}

%description -n %{dev32unwind}
Development files for libunwind.

%files -n %{dev32unwind}
%{_prefix}/lib/libunwind.a
%{_prefix}/lib/libunwind.so
%if %{with default_compilerrt}
%{_prefix}/lib/pkgconfig/libunwind.pc
%else
%{_prefix}/lib/pkgconfig/libunwind-llvm.pc
%endif
%endif

%if %{with mlir}
#-----------------------------------------------------------
%package mlir-tools
Summary:	Tools for working with MLIR (Multi-Level Intermediate Representation)
Group:		Development/C

%description mlir-tools
Tools for working with MLIR (Multi-Level Intermediate Representation)

The MLIR project is a novel approach to building reusable and extensible
compiler infrastructure. MLIR aims to address software fragmentation,
improve compilation for heterogeneous hardware, significantly reduce
the cost of building domain specific compilers, and aid in connecting
existing compilers together.

%files mlir-tools
%{_bindir}/mlir-*

#-----------------------------------------------------------
%define mlirlib %{mklibname mlir}
%package -n %{mlirlib}
Summary:	Libraries for dealing with MLIR
Group:		Development/C
Obsoletes:	%{_lib}mlir_async_runtime14 < %{EVRD}
Obsoletes:	%{_lib}mlir_c_runner_utils14 < %{EVRD}
Obsoletes:	%{_lib}mlir_runner_utils14 < %{EVRD}

%description -n %{mlirlib}
Libraries for dealing with MLIR.

The MLIR project is a novel approach to building reusable and extensible
compiler infrastructure. MLIR aims to address software fragmentation,
improve compilation for heterogeneous hardware, significantly reduce
the cost of building domain specific compilers, and aid in connecting
existing compilers together.

%files -n %{mlirlib}
%{_libdir}/libMLIR-C.so.*
%{_libdir}/libMLIR.so.*
%{_libdir}/libmlir_async_runtime.so.*
%{_libdir}/libmlir_c_runner_utils.so.*
%{_libdir}/libmlir_float16_utils.so.*
%{_libdir}/libmlir_runner_utils.so.*
%{_libdir}/libmlir_arm_runner_utils.so.*
%{_libdir}/libmlir_arm_sme_abi_stubs.so.*
%{_libdir}/libmlir_spirv_cpu_runtime.so.*
%{_libdir}/libmlir_vulkan_runtime.so.*
%{_libdir}/libMLIRExecutionEngineShared.so.*

%define mlirdev %{mklibname -d mlir}
%package -n %{mlirdev}
Summary:	Development files for MLIR
Group:		Development/C
Requires:	%{mlirlib} = %{EVRD}

%description -n %{mlirdev}
Development files for MLIR

The MLIR project is a novel approach to building reusable and extensible
compiler infrastructure. MLIR aims to address software fragmentation,
improve compilation for heterogeneous hardware, significantly reduce
the cost of building domain specific compilers, and aid in connecting
existing compilers together.

%files -n %{mlirdev}
%{_includedir}/mlir
%{_includedir}/mlir-c
%{_libdir}/cmake/mlir
%{_libdir}/libMLIRTableGen.a
#-----------------------------------------------------------
%endif

%package -n libclc
Summary:	Core library of the OpenCL language runtime
Group:		Development/Other
Url:		https://libclc.llvm.org/

%description -n libclc
Core library of the OpenCL language runtime.

%package -n libclc-spirv
Summary:	SPIR-V (Vulkan) backend for the libclc OpenCL library
Group:		System/Libraries
Requires:	libclc = %{EVRD}

%description -n libclc-spirv
SPIR-V (Vulkan) backend for the libclc OpenCL library.

%package -n libclc-r600
Summary:	Radeon 600 (older ATI/AMD GPU) backend for the libclc OpenCL library
Group:		System/Libraries
Requires:	libclc = %{EVRD}

%description -n libclc-r600
Radeon 600 (older ATI/AMD GPU) backend for the libclc OpenCL library.

%package -n libclc-amdgcn
Summary:	AMD GCN (newer ATI/AMD GPU) backend for the libclc OpenCL library
Group:		System/Libraries
Requires:	libclc = %{EVRD}

%description -n libclc-amdgcn
AMD GCN (newer ATI/AMD GPU) backend for the libclc OpenCL library.

%package -n libclc-nvptx
Summary:	Nvidia PTX backend for the libclc OpenCL library
Group:		System/Libraries
Requires:	libclc = %{EVRD}

%description -n libclc-nvptx
Nvidia PTX backend for the libclc OpenCL library.

%if %{without bootstrap}
%files -n libclc
%{_includedir}/clc
%dir %{_datadir}/clc
%{_datadir}/pkgconfig/libclc.pc
# Should this be a separate package? It's an
# OpenCL to Vulkan compute shader compiler.
%{_datadir}/clc/clspv--.bc
%{_datadir}/clc/clspv64--.bc

%files -n libclc-spirv
%{_datadir}/clc/spirv*

%files -n libclc-r600
%{_datadir}/clc/*-r600-*

%files -n libclc-nvptx
%{_bindir}/nvptx-arch
%{_datadir}/clc/nvptx*

%files -n libclc-amdgcn
%{_bindir}/amdgpu-arch
%{_datadir}/clc/*amdgcn*
%endif

%package -n spirv-headers
Summary:	Headers for working with SPIR-V, a language for running on GPUs
Group:		Development/Tools
BuildArch:	noarch

%description -n spirv-headers
This package contains machine-readable files for the SPIR-V Registry.

This includes:

* Header files for various languages.
* JSON files describing the grammar for the SPIR-V core instruction
  set and the extended instruction sets.
* The XML registry file.
* A tool to build the headers from the JSON grammar.

Headers are provided in the include directory, with up-to-date
headers in the unified1 subdirectory. Older headers are provided
according to their version.

%files -n spirv-headers
%{_includedir}/spirv
%dir %{_datadir}/cmake/SPIRV-Headers
%{_datadir}/cmake/SPIRV-Headers/*.cmake
%{_datadir}/pkgconfig/SPIRV-Headers.pc

%package -n spirv-llvm-translator
Summary:	Library for bi-directional translation between SPIR-V and LLVM IR
Group:		Development/Tools

%description -n spirv-llvm-translator
Library for bi-directional translation between SPIR-V and LLVM IR.

%files -n spirv-llvm-translator
%{_bindir}/llvm-spirv

%define oldlibspirv %mklibname LLVMSPIRVLib %{major1}
%define libspirv %mklibname LLVMSPIRVLib
%define devspirv %mklibname -d LLVMSPIRVLib

%package -n %{devspirv}
Summary:	Library for bi-directional translation between SPIR-V and LLVM IR
Group:		Development/Tools
# FIXME we may want to restore the shared lib here
Obsoletes:	%{oldlibspirv} < %{EVRD}

%description -n %{devspirv}
Library for bi-directional translation between SPIR-V and LLVM IR.

%files -n %{devspirv}
%{_includedir}/LLVMSPIRVLib
%{_libdir}/libLLVMSPIRVLib.a
%{_libdir}/pkgconfig/LLVMSPIRVLib.pc

%package -n spirv-tools
Summary:	Tools for working with SPIR-V, a language for running on GPUs
Group:		Development/Tools

%description -n spirv-tools
Tools for working with SPIR-V, a language for running on GPUs.

%files -n spirv-tools
%{_bindir}/spirv-as
%{_bindir}/spirv-cfg
%{_bindir}/spirv-dis
%{_bindir}/spirv-lesspipe.sh
%{_bindir}/spirv-link
%{_bindir}/spirv-lint
%{_bindir}/spirv-objdump
%{_bindir}/spirv-opt
%{_bindir}/spirv-reduce
%{_bindir}/spirv-val

%define oldlibspirvtools %mklibname spirv-tools %{major1}
%define libspirvtools %mklibname spirv-tools
%define devspirvtools %mklibname -d spirv-tools

%package -n %{libspirvtools}
Summary:	Libraries needed for SPIRV-Tools
Group:		System/Libraries
%rename %{_lib}spirv-tools0
%rename %{oldlibspirvtools}

%description -n %{libspirvtools}
Libraries needed for SPIRV-Tools.

%files -n %{libspirvtools}
%{_libdir}/libSPIRV-Tools-shared.so.*

%package -n %{devspirvtools}
Summary:	Development files for SPIRV-Tools
Group:		Development/C++ and C
Requires:	%{libspirvtools} = %{EVRD}
Requires:	spirv-tools = %{EVRD}

%description -n %{devspirvtools}
Development files for SPIRV-Tools.

%files -n %{devspirvtools}
%{_includedir}/spirv-tools
%{_libdir}/cmake/SPIRV-Tools*
%{_libdir}/libSPIRV-Tools*.a
%{_libdir}/libSPIRV-Tools*.so
%{_libdir}/pkgconfig/SPIRV-Tools*.pc

%if %{with compat32}
%define lib32spirv libLLVMSPIRVLib%{major1}
%define dev32spirv libLLVMSPIRVLib-devel
%define oldlib32spirvtools %mklib32name spirv-tools %{major1}
%define lib32spirvtools %mklib32name spirv-tools
%define dev32spirvtools %mklib32name -d spirv-tools

%package -n %{dev32spirv}
Summary:	Library for bi-directional translation between SPIR-V and LLVM IR (32-bit)
Group:		Development/Tools
Requires:	%{devspirv} = %{EVRD}
# FIXME probably makes sense to restore the shared library builds...
Obsoletes:	%{lib32spirv} < %{EVRD}

%description -n %{dev32spirv}
Library for bi-directional translation between SPIR-V and LLVM IR (32-bit).

%files -n %{dev32spirv}
#%{_prefix}/lib/libLLVMSPIRVLib.so
%{_prefix}/lib/pkgconfig/LLVMSPIRVLib.pc

%package -n %{lib32spirvtools}
Summary:	Libraries needed for SPIRV-Tools (32-bit)
Group:		System/Libraries
%rename libspirv-tools0
%rename %{oldlib32spirvtools}

%description -n %{lib32spirvtools}
Libraries needed for SPIRV-Tools (32-bit).

%files -n %{lib32spirvtools}
%{_prefix}/lib/libSPIRV-Tools-shared.so.*

%package -n %{dev32spirvtools}
Summary:	Development files for SPIRV-Tools (32-bit)
Group:		Development/C++ and C
Requires:	%{devspirvtools} = %{EVRD}
Requires:	%{lib32spirvtools} = %{EVRD}
Provides:	libspirv-tools-devel = %{EVRD}

%description -n %{dev32spirvtools}
Development files for SPIRV-Tools.

%files -n %{dev32spirvtools}
%{_prefix}/lib/cmake/SPIRV-Tools*
%{_prefix}/lib/libSPIRV-Tools*.a
%{_prefix}/lib/libSPIRV-Tools*.so
%{_prefix}/lib/pkgconfig/SPIRV-Tools*.pc
%endif

%define libcname %mklibname llvmlibc -d -s

%package -n %{libcname}
Summary:	Libc implementation from the LLVM project
Group:		Development/C++ and C

%description -n %{libcname}
Libc implementation from the LLVM project

%if %{with libc}
%files -n %{libcname}
%{_libdir}/libllvmlibc.a
%endif

%prep
%if 0%{?gitdate:1}
%setup -q -n llvm-project-%{?is_main:main}%{!?is_main:release-%{major1}.x} -a 20 -a 21 -a 22
%else
%setup -q -n llvm-project-llvmorg-%{version} -a 20 -a 21 -a 22
%endif
mv SPIRV-LLVM-Translator-* llvm/projects/SPIRV-LLVM-Translator
mv SPIRV-Headers-* llvm/projects/SPIRV-Headers
mv SPIRV-Tools-* llvm/projects/SPIRV-Tools
%autopatch -p1
%if %{with default_compilerrt}
patch -p1 -b -z .crt~ <%{S:62}
%endif
git init
git config user.email build@openmandriva.org
git config user.name "OpenMandriva builder"
git add * >/dev/null
git commit --quiet -am "Fake commit to make cmake files happy"

# Fix bogus permissions
find . -type d -exec chmod 0755 {} \;

# lldb pretends it requires exactly lua 5.3 -- but works fine with 5.4
LUAVER="$(pkg-config --variable=V lua)"
sed -i -e "s,5\.3,$LUAVER,g" lldb/test/API/lua_api/TestLuaAPI.py lldb/CMakeLists.txt lldb/cmake/modules/FindLuaAndSwig.cmake

# LLVM doesn't use autoconf, but it uses autoconf's config.guess
# to find target arch and friends (hidden away in cmake/).
# Let's make sure we replace its outdated copy (which doesn't
# know what riscv64 is) with a current version.
%config_update

%build
# FIXME do we need to enable cross-project-tests anywhere?
PROJECTS="llvm"
%if %{with bolt}
PROJECTS="$PROJECTS;bolt"
%endif
%if %{with clang}
PROJECTS="$PROJECTS;clang;clang-tools-extra;polly"
%endif
%if %{with mlir}
PROJECTS="$PROJECTS;mlir"
%endif
%if %{with flang}
PROJECTS="$PROJECTS;flang"
%endif
%if %{with unwind}
RUNTIMES="$RUNTIMES;libunwind"
%endif
%if %{with lldb}
PROJECTS="$PROJECTS;lldb"
%endif
%if %{with lld}
PROJECTS="$PROJECTS;lld"
%endif
%if %{with openmp}
RUNTIMES="$RUNTIMES;openmp"
%endif
%if %{with libcxx}
RUNTIMES="$RUNTIMES;pstl;libcxx;libcxxabi"
%endif
%if %{with libc}
RUNTIMES="$RUNTIMES;libc"
%endif
PROJECTS="$PROJECTS;libclc"
RUNTIMES="$RUNTIMES;compiler-rt"
# llvm-libgcc is incompatible with libunwind
#RUNTIMES="$RUNTIMES;llvm-libgcc"
RUNTIMES="$RUNTIMES;offload"

[ $(echo $RUNTIMES |cut -b1) = ';' ] && RUNTIMES="$(echo $RUNTIMES |cut -b2-)"
[ $(echo $PROJECTS |cut -b1) = ';' ] && PROJECTS="$(echo $PROJECTS |cut -b2-)"

%if %{with bootstrap_gcc}
export CC=gcc
export CXX=g++
%endif
TOP=$(pwd)

# compiler-rt assumes off_t is 64 bits -- make sure this is true even on 32 bit
# OSes
%ifarch %ix86
# compiler-rt doesn't support ix86 with x<6 either
export CFLAGS="%{optflags} -march=i686 -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
export CXXFLAGS="%{optflags} -march=i686 -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
%endif
%ifarch %armx sparc mips riscv64
export CFLAGS="%{optflags} -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
export CXXFLAGS="%{optflags} -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
%endif

if echo %{_target_platform} | grep -q musl; then
    sed -i -e 's,set(COMPILER_RT_HAS_SANITIZER_COMMON TRUE),set(COMPILER_RT_HAS_SANITIZER_COMMON FALSE),' compiler-rt/cmake/config-ix.cmake
fi

# Fix noexecstack
for i in compiler-rt/lib/builtins/i386/*.S; do
    cat >>$i <<'EOF'
#if defined(__linux__) && defined(__ELF__)
.section .note.GNU-stack,"",%progbits
#endif
EOF
done

PROCESSES="$(getconf _NPROCESSORS_ONLN)"
LPROCESSES="$PROCESSES"
CPROCESSES="$PROCESSES"
# Linking LLVM with LTO enabled is VERY RAM intensive
# and breaks boxes that have loads of CPU cores but no
# terabytes of RAM...
[ "$PROCESSES" -gt 4 ] && LPROCESSES=4
[ "$CPROCESSES" -gt 8 ] && CPROCESSES=8

# The "%if ! %{with skip64}" below is just a quick way to get rid of the real
# 64-bit build to debug 32-bit build issues. Don't enable skip64 in real builds!
%if ! %{with skip64}
# We set an RPATH in CMAKE_EXE_LINKER_FLAGS to make sure the newly built
# clang and friends use the just-built shared libraries -- there's no guarantee
# that the ABI remains compatible between a snapshot libclang.so.11 and the
# final libclang.so.11 at the moment.
# We strip out the rpath in %%install though - so we aren't really being evil.
#
# We should probably use
#	-DLLVM_RUNTIME_TARGETS="x86_64-pc-linux-gnu;i686-pc-linux-gnu;aarch64-linux-gnu;..."
# to crosscompile the runtimes -- unfortunately as of 16.0-rc3, that doesn't work
# (incorrectly claiming the crosscompiler doesn't support -fuse-ld=lld)
#
# For new LLVM_EXPERIMENTAL_TARGETS_TO_BUILD, compare "ls llvm/lib/Target" to
# the "set(LLVM_ALL_TARGETS" list in llvm/CMakeLists.txt
#
# FIXME We set LLVM_SPIRV below because the just built llvm-spirv isn't detectable
# because it doesn't exist at cmake time yet -- the drawback is that this breaks
# major updates (llvm-spirv version X not working with llvm X+1) until the second
# build
#
#
# POLLY_BUNDLED_ISL:BOOL=OFF doesn't work because upstream ISL doesn't have an
# "isl/isl-noexceptions.h" header
#
# Things to try out:
# LLVM_ENABLE_MODULES=ON (C++ modules support)
# LLVM_TOOL_COMPILER_RT_BUILD=ON (how is this different from having compiler-rt in RUNTIMES?)
# LLVM_TOOL_LIBCXXABI_BUILD=ON
# LLVM_TOOL_LIBCXX_BUILD=ON
# LLVM_TOOL_LIBC_BUILD=ON
# LLVM_TOOL_LIBUNWIND_BUILD=ON
# LLVM_TOOL_OPENMP_BUILD=ON
# LLVM_TOOL_PSTL_BUILD=ON
# MLIR_ENABLE_ROCM_RUNNER=ON (once ROCm is built)
# MLIR_ENABLE_SYCL_RUNNER=ON (once SyCL is built)
# CLANG_BOLT=Instrument/Perf/LBR (need to figure out which one works best)
%cmake \
%if %{?cross_compiling}
	-DCLANG=%{_bindir}/clang \
	-DLLVM_TABLEGEN=%{_bindir}/llvm-tblgen \
	-DOPT=%{_bindir}/opt \
%endif
	-DCLANG_PYTHON_BINDINGS_VERSION=%{pyver} \
	-DLLVM_ENABLE_CURL:BOOL=ON \
%if %{with z3}
	-DLLVM_ENABLE_Z3_SOLVER:BOOL=ON \
%endif
	-DLLVM_HAS_LOGF128:BOOL=ON \
	-DLLVM_TOOL_PSTL_BUILD:BOOL=ON \
%if %{with mlir}
	-DMLIR_ENABLE_BINDINGS_PYTHON:BOOL=ON \
%endif
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DLLVM_LIBGCC_EXPLICIT_OPT_IN=Yes \
	-DFETCHCONTENT_FULLY_DISCONNECTED:BOOL=ON \
	-DFETCHCONTENT_UPDATES_DISCONNECTED:BOOL=ON \
	-DLLVM_PARALLEL_LINK_JOBS=$LPROCESSES \
	-DLLVM_PARALLEL_COMPILE_JOBS=$CPROCESSES \
	-DLLVM_VERSION_SUFFIX="%{SOMINOR}" \
	-DLLVM_ENABLE_PROJECTS="$PROJECTS" \
	-DLLVM_ENABLE_PER_TARGET_RUNTIME_DIR:BOOL=ON \
	-DLLVM_ENABLE_RUNTIMES="$RUNTIMES" \
	-DLLVM_ENABLE_LLD:BOOL=ON \
%if %{build_lto} && ! %{cross_compiling}
	-DLLVM_ENABLE_LTO=Thin \
%else
	-DLLVM_ENABLE_LTO=OFF \
%endif
	-DLLVM_TOOL_OPENMP_BUILD:BOOL=ON \
	-DLLDB_USE_SYSTEM_SIX:BOOL=ON \
	-DLLDB_SKIP_STRIP:BOOL=ON \
%if %{cross_compiling}
	-DLLDB_PYTHON_RELATIVE_PATH=%{_lib}/python%{pyver}/site-packages \
	-DLLDB_PYTHON_EXE_RELATIVE_PATH=bin/python \
	-DLLDB_PYTHON_EXT_SUFFIX=".so" \
%endif
%if ! %{with tests}
	-DLLVM_INCLUDE_TESTS:BOOL=OFF \
%endif
	-DCOMPILER_RT_USE_BUILTINS_LIBRARY:BOOL=OFF \
	-DCOMPILER_RT_ENABLE_SOFTWARE_INT128:BOOL=ON \
	-DCOMPILER_RT_INSTALL_BINARY_DIR:PATH=%{_libdir}/clang/%{major1}/bin \
	-DCOMPILER_RT_INSTALL_DATA_DIR:PATH=%{_libdir}/clang/%{major1}/share \
	-DCOMPILER_RT_INSTALL_INCLUDE_DIR:PATH=%{_libdir}/clang/%{major1}/include \
	-DCOMPILER_RT_INSTALL_LIBRARY_DIR:PATH=%{_libdir}/clang/%{major1}/lib \
	-DCLANG_VENDOR="OpenMandriva %{version}-%{release}" \
	-DFLANG_VENDOR="OpenMandriva %{version}-%{release}" \
	-DLLD_VENDOR="OpenMandriva %{version}-%{release}" \
	-DLLVM_ENABLE_NEW_PASS_MANAGER:BOOL=ON \
	-DENABLE_X86_RELAX_RELOCATIONS:BOOL=ON \
	-DCLANG_DEFAULT_LINKER=lld \
	-DCLANG_DEFAULT_OBJCOPY=llvm-objcopy \
%if %{with default_compilerrt}
	-DCLANG_DEFAULT_RTLIB=compiler-rt \
%else
	-DCLANG_DEFAULT_RTLIB=libgcc \
%endif
%ifarch %{riscv}
	-DCOMPILER_RT_BUILD_LIBFUZZER:BOOL=OFF \
	-DCOMPILER_RT_BUILD_SANITIZERS:BOOL=OFF \
	-DCOMPILER_RT_BUILD_PROFILE:BOOL=OFF \
%endif
%if %{with ffi}
	-DLLVM_ENABLE_FFI:BOOL=ON \
%else
	-DLLVM_ENABLE_FFI:BOOL=OFF \
%endif
	-DLLVM_ENABLE_SPHINX:BOOL=ON \
	-DSPHINX_WARNINGS_AS_ERRORS:BOOL=OFF \
	-DLLVM_TARGETS_TO_BUILD=all \
	-DLLVM_EXPERIMENTAL_TARGETS_TO_BUILD="ARC;CSKY;M68k;SPIRV;Xtensa" \
	-DLLVM_ENABLE_CXX1Y:BOOL=ON \
	-DLLVM_ENABLE_RTTI:BOOL=ON \
	-DLLVM_ENABLE_PIC:BOOL=ON \
	-DLLVM_INCLUDE_DOCS:BOOL=ON \
	-DLLVM_INSTALL_UTILS:BOOL=ON \
%if %{cross_compiling}
	-DLLVM_BINUTILS_INCDIR=%{_prefix}/%{_target_platform}/include \
	-DLIBOMPTARGET_DEP_LIBFFI_INCLUDE_DIR=%{_prefix}/%{_target_platform}/include \
%else
	-DLLVM_BINUTILS_INCDIR=%{_includedir} \
%endif
	-DLLVM_BUILD_DOCS:BOOL=ON \
	-DLLVM_BUILD_EXAMPLES:BOOL=OFF \
	-DLLVM_BUILD_RUNTIME:BOOL=ON \
	-DLLVM_TOOL_COMPILER_RT_BUILD:BOOL=OFF \
	-DCOMPILER_RT_BUILD_BUILTINS:BOOL=OFF \
	-DCOMPILER_RT_BUILD_CRT:BOOL=ON \
	-DENABLE_LINKER_BUILD_ID:BOOL=ON \
	-DOCAMLFIND=NOTFOUND \
	-DLLVM_LIBDIR_SUFFIX=$(echo %{_lib} |sed -e 's,^lib,,') \
	-DCLANG_LIBDIR_SUFFIX=$(echo %{_lib} |sed -e 's,^lib,,') \
	-DOPENMP_LIBDIR_SUFFIX=$(echo %{_lib} |sed -e 's,^lib,,') \
	-DOPENMP_INSTALL_LIBDIR=%{_lib} \
	-DLLVM_OPTIMIZED_TABLEGEN:BOOL=ON \
%ifarch %{arm}
	-DLLVM_DEFAULT_TARGET_TRIPLE=%{product_arch}-%{_vendor}-%{_os}%{_gnu} \
%endif
	-DPOLLY_ENABLE_GPGPU_CODEGEN:BOOL=ON \
	-DWITH_POLLY:BOOL=ON \
%if %{with use_libcxx}
	-DLLVM_ENABLE_LIBCXX:BOOL=ON \
	-DLLVM_ENABLE_LIBCXXABI:BOOL=ON \
%endif
%if ! %{with bootstrap}
	-DLLVM_SPIRV=%{_bindir}/llvm-spirv \
%endif
	-DLIBCXX_CXX_ABI=libcxxabi \
	-DLIBCXX_ENABLE_CXX1Y:BOOL=ON \
	-DLIBCXXABI_ENABLE_SHARED:BOOL=ON \
	-DLIBCXXABI_ENABLE_STATIC:BOOL=ON \
	-DLIBCXX_ENABLE_SHARED:BOOL=ON \
	-DLIBCXX_ENABLE_STATIC:BOOL=ON \
	-DLIBCXXABI_LIBCXX_INCLUDES=${TOP}/libcxx/include \
	-DLIBCXX_CXX_ABI_INCLUDE_PATHS=${TOP}/libcxxabi/include \
	-DLIBCXXABI_LIBDIR_SUFFIX="$(echo %{_lib} | sed -e 's,^lib,,')" \
	-DLIBCXX_LIBDIR_SUFFIX="$(echo %{_lib} | sed -e 's,^lib,,')" \
	-DLLVM_TOOL_PSTL_BUILD:BOOL=ON \
	-DPSTL_PARALLEL_BACKEND=omp \
	-DCMAKE_SHARED_LINKER_FLAGS="-L$(pwd)/%{_lib}" \
	-DCMAKE_EXE_LINKER_FLAGS="-Wl,--disable-new-dtags,-rpath,$(pwd)/%{_lib},-rpath,$(pwd)/lib" \
%if %{with mlir}
	-DMLIR_ENABLE_SPIRV_CPU_RUNNER:BOOL=ON \
	-DMLIR_ENABLE_VULKAN_RUNNER:BOOL=ON \
%endif
%if %{with apidox}
	-DLLVM_ENABLE_DOXYGEN:BOOL=ON \
%endif
%if %{cross_compiling}
	-DCMAKE_CROSSCOMPILING=True \
	-DLLVM_TABLEGEN=%{_bindir}/llvm-tblgen \
	-DCLANG_TABLEGEN=%{_bindir}/clang-tblgen \
	-DLLVM_DEFAULT_TARGET_TRIPLE=%{_target_platform} \
%endif
%if %{with default_compilerrt}
%if %{with unwind}
	-DLIBCXXABI_USE_LLVM_UNWINDER:BOOL=ON \
	-DCLANG_DEFAULT_UNWINDLIB=libunwind \
%endif
%else
	-DCLANG_DEFAULT_UNWINDLIB=libgcc \
%endif
	-DBUILD_SHARED_LIBS:BOOL=OFF \
	-DLLVM_BUILD_LLVM_DYLIB:BOOL=ON \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
%if %{with clang}
	-DCLANG_LINK_CLANG_DYLIB:BOOL=ON \
%endif
%if %{with mlir}
	-DMLIR_BUILD_MLIR_C_DYLIB:BOOL=ON \
%endif
	-DSPIRV_HEADERS_ENABLE_INSTALL:BOOL=ON \
	-DSPIRV_TOOLS_BUILD_STATIC:BOOL=OFF \
	-G Ninja \
	../llvm

if ! %ninja_build; then
# With many threads, there's a chance of libc++ being built
# before libc++abi, causing linkage to fail. Simply trying
# again "fixes" it.
# flang also seems to have SMP build issues
    for i in $(seq 1 30); do
	if %ninja_build; then
	    break
	fi
    done
    %ninja_build -j1
fi

cd ..
%endif

%if %{with compat32}
TOP="$(pwd)"
gccver="$(i686-openmandriva-linux-gnu-gcc --version |head -n1 |cut -d' ' -f3)"
cat >xc <<EOF
#!/bin/sh
%if %{with bootstrap32}
exec %{_bindir}/clang --rtlib=libgcc --unwindlib=libgcc -m32 "\$@"
%else
exec %{_bindir}/clang -m32 "\$@"
%endif
EOF
cat >xc++ <<EOF
#!/bin/sh
%if %{with bootstrap32}
exec %{_bindir}/clang++ -std=gnu++17 --rtlib=libgcc --unwindlib=libgcc -m32 -isystem %{_includedir}/c++/x86_64-openmandriva-linux-gnu/32 -isystem $TOP/pstl/include -isystem $TOP/build32/runtimes/runtimes-bins/pstl/generated_headers "\$@"
%else
exec %{_bindir}/clang++ -std=gnu++17 -m32 -isystem %{_includedir}/c++/${gccver}/x86_64-openmandriva-linux-gnu/32 -isystem $TOP/pstl/include -isystem $TOP/build32/runtimes/runtimes-bins/pstl/generated_headers "\$@"
%endif
EOF
chmod +x xc xc++
cat >cmake-i686.toolchain <<EOF
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR i686)
set(CMAKE_C_COMPILER ${TOP}/xc)
set(CMAKE_CXX_COMPILER ${TOP}/xc++)
EOF
%endif

%if %{with compat32}
# FIXME libc in LLVM_ENABLE_RUNTIMES breaks the build
# FIXME -DLIBUNWIND_USE_COMPILER_RT:BOOL=ON breaks the build (adds -lNOTFOUND)
%cmake32 \
	-DCMAKE_BUILD_TYPE=MinSizeRel \
	-DLLVM_LIBGCC_EXPLICIT_OPT_IN=Yes \
	-DFETCHCONTENT_FULLY_DISCONNECTED:BOOL=ON \
	-DFETCHCONTENT_UPDATES_DISCONNECTED:BOOL=ON \
	-DLLVM_PARALLEL_LINK_JOBS=$LPROCESSES \
	-DLLVM_PARALLEL_COMPILE_JOBS=$CPROCESSES \
	-DLLVM_VERSION_SUFFIX="%{SOMINOR}" \
	-DCMAKE_TOOLCHAIN_FILE="${TOP}/cmake-i686.toolchain" \
	-DLLVM_CONFIG_PATH=$(pwd)/../build/bin/llvm-config \
	-DLLVM_ENABLE_PROJECTS="llvm;clang;polly;openmp" \
	-DLLVM_ENABLE_RUNTIMES="libunwind;compiler-rt" \
	-DLLVM_TOOL_PSTL_BUILD:BOOL=ON \
	-DLLVM_TOOL_LIBUNWIND_BUILD:BOOL=ON \
	-DLLVM_ENABLE_NEW_PASS_MANAGER:BOOL=ON \
	-DENABLE_X86_RELAX_RELOCATIONS:BOOL=ON \
%if %{with default_compilerrt}
	-DCLANG_DEFAULT_RTLIB=compiler-rt \
%if ! %{with bootstrap32}
	-DCOMPILER_RT_USE_BUILTINS_LIBRARY:BOOL=ON \
%endif
%else
	-DCLANG_DEFAULT_RTLIB=libgcc \
%endif
	-DCLANG_DEFAULT_UNWINDLIB:STRING=libunwind \
	-DLIBOMPTARGET_DEP_LIBFFI_LIBRARIES:FILEPATH=%{_prefix}/lib/libffi.so \
	-Dpkgcfg_lib_LIBOMPTARGET_SEARCH_LIBFFI_ffi:FILEPATH=%{_prefix}/lib/libffi.so \
	-DLIBXML2_LIBRARY:FILEPATH=%{_prefix}/lib/libxml2.so \
	-DLLVM_ENABLE_FFI:BOOL=ON \
	-DLLVM_TARGETS_TO_BUILD=all \
	-DLLVM_EXPERIMENTAL_TARGETS_TO_BUILD="ARC;CSKY;M68k;SPIRV;Xtensa" \
	-DLLVM_ENABLE_CXX1Y:BOOL=ON \
	-DLLVM_ENABLE_RTTI:BOOL=ON \
	-DLLVM_ENABLE_PIC:BOOL=ON \
	-DLLVM_INCLUDE_DOCS:BOOL=ON \
	-DLLVM_INSTALL_UTILS:BOOL=ON \
	-DLLVM_BINUTILS_INCDIR=%{_includedir} \
	-DLLVM_BUILD_DOCS:BOOL=OFF \
	-DLLVM_BUILD_EXAMPLES:BOOL=OFF \
	-DLLVM_BUILD_RUNTIME:BOOL=ON \
	-DLLVM_TOOL_COMPILER_RT_BUILD:BOOL=ON \
	-DCOMPILER_RT_BUILD_BUILTINS:BOOL=ON \
	-DCOMPILER_RT_BUILD_CRT:BOOL=ON \
	-DENABLE_LINKER_BUILD_ID:BOOL=ON \
	-DOCAMLFIND=NOTFOUND \
	-DLLVM_OPTIMIZED_TABLEGEN:BOOL=OFF \
	-DLLVM_DEFAULT_TARGET_TRIPLE=i686-%{_vendor}-%{_os}%{_gnu} \
	-DPOLLY_ENABLE_GPGPU_CODEGEN:BOOL=ON \
	-DWITH_POLLY:BOOL=ON \
	-DLINK_POLLY_INTO_TOOLS:BOOL=ON \
	-DLIBCXX_CXX_ABI=libcxxabi \
	-DLIBCXX_ENABLE_CXX1Y:BOOL=ON \
	-DLIBCXXABI_ENABLE_SHARED:BOOL=ON \
	-DLIBCXXABI_ENABLE_STATIC:BOOL=ON \
	-DLIBCXX_ENABLE_SHARED:BOOL=ON \
	-DLIBCXX_ENABLE_STATIC:BOOL=ON \
	-DLIBCXX_ENABLE_PARALLEL_ALGORITHMS:BOOL=ON \
	-DLIBCXX_HAS_MUSL_LIBC:BOOL=OFF \
	-DLIBCXXABI_LIBCXX_INCLUDES=${TOP}/libcxx/include \
	-DLIBCXX_CXX_ABI_INCLUDE_PATHS=${TOP}/libcxxabi/include \
	-DCMAKE_SHARED_LINKER_FLAGS="-L$(pwd)/lib" \
	-DCMAKE_EXE_LINKER_FLAGS="-Wl,--disable-new-dtags,-rpath,$(pwd)/lib" \
	-DLLVM_ENABLE_DOXYGEN:BOOL=OFF \
	-DLIBCXXABI_USE_LLVM_UNWINDER:BOOL=ON \
%if %{with default_compilerrt}
	-DCLANG_DEFAULT_UNWINDLIB=libunwind \
%else
	-DCLANG_DEFAULT_UNWINDLIB=libgcc \
%endif
	-DCOMPILER_RT_DEFAULT_TARGET_TRIPLE=i686-openmandriva-linux-gnu \
	-DLIBCXX_USE_COMPILER_RT:BOOL=OFF \
	-DLIBCXXABI_USE_COMPILER_RT:BOOL=OFF \
	-DLIBUNWIND_USE_COMPILER_RT:BOOL=OFF \
	-DLLVM_ENABLE_PER_TARGET_RUNTIME:BOOL=ON \
	-DLLVM_HOST_TRIPLE=i686-openmandriva-linux-gnu \
	-DLLVM_TARGET_ARCH=i686 \
	-DLIBCXX_ENABLE_CXX1Y:BOOL=ON \
	-DLIBCXXABI_ENABLE_SHARED:BOOL=ON \
	-DLIBCXXABI_ENABLE_STATIC:BOOL=ON \
	-DLIBCXX_ENABLE_SHARED:BOOL=ON \
	-DLIBCXX_ENABLE_STATIC:BOOL=ON \
	-DLIBCXXABI_USE_LLVM_UNWINDER:BOOL=ON \
	-DBUILD_SHARED_LIBS:BOOL=OFF \
	-DLLVM_BUILD_LLVM_DYLIB:BOOL=ON \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DLIBC_BUILD_GPU_LOADER:BOOL=ON \
	-DLIBC_USE_NEW_HEADER_GEN:BOOL=ON \
	-G Ninja \
	../llvm
%ninja_build
cd ..
%endif

# Where our just-built compilers can be found...
BINDIR=$(pwd)/build/bin
# The build process tries to use the just built
# libLLVMAnalysis.so.*
export LD_LIBRARY_PATH=$(pwd)/build/%{_lib}:$LD_LIBRARY_PATH

%if %{with crosscrt}
# Build compiler-rt for all potential crosscompiler targets
unset CFLAGS
unset CXXFLAGS
XCRTARCHES=""
%ifnarch %{arm}
XCRTARCHES="$XCRTARCHES armv7hnl"
%endif
%ifnarch %{aarch64}
XCRTARCHES="$XCRTARCHES aarch64"
%endif
%ifnarch %{ix86}
XCRTARCHES="$XCRTARCHES i686"
%endif
%ifnarch %{riscv64}
XCRTARCHES="$XCRTARCHES riscv64"
%endif
%ifnarch ppc64
XCRTARCHES="$XCRTARCHES ppc64"
%endif
%ifnarch ppc64le
XCRTARCHES="$XCRTARCHES ppc64le"
%endif
if [ -n "$XCRTARCHES" ]; then
	for arch in $XCRTARCHES; do
		if [ "$arch" = "armv7hnl" ]; then
			LIBC=gnueabihf
		else
			LIBC=gnu
		fi
		mkdir xbuild-crt-${arch}
		cd xbuild-crt-${arch}
		gccver="$(${arch}-openmandriva-linux-${LIBC}-gcc --version |head -n1 |cut -d' ' -f3)"
		if [ %{_build} = "${arch}-openmandriva-linux-${LIBC}" ]; then
			SYSROOT=""
		else
			SYSROOT="--sysroot=/usr/${arch}-openmandriva-linux-${LIBC}"
		fi
		LFLAGS="-O3 $SYSROOT --gcc-install-dir=%{_libdir}/gcc/${arch}-openmandriva-linux-${LIBC}/${gccver}"
		FLAGS="$LFLAGS -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
		cmake \
			../compiler-rt \
			-DCMAKE_BUILD_TYPE=MinSizeRel \
			-DLLVM_ENABLE_PER_TARGET_RUNTIME_DIR:BOOL=ON \
			-DCOMPILER_RT_INSTALL_BINARY_DIR:PATH=%{_libdir}/clang/%{major1}/bin \
			-DCOMPILER_RT_INSTALL_DATA_DIR:PATH=%{_libdir}/clang/%{major1}/share \
			-DCOMPILER_RT_INSTALL_INCLUDE_DIR:PATH=%{_libdir}/clang/%{major1}/include \
			-DCOMPILER_RT_INSTALL_LIBRARY_DIR:PATH=%{_libdir}/clang/%{major1}/lib \
			-DLLVM_PARALLEL_LINK_JOBS=$LPROCESSES \
			-DLLVM_PARALLEL_COMPILE_JOBS=$CPROCESSES \
			-DLLVM_VERSION_SUFFIX="%{SOMINOR}" \
			-DLLVM_INCLUDE_DIR="${TOP}/llvm/include/llvm" \
			-DCMAKE_CROSSCOMPILING:BOOL=ON \
			-DCMAKE_INSTALL_PREFIX=%{_libdir}/clang/%{major1} \
%if ! %{cross_compiling}
			-DCMAKE_AR=${BINDIR}/llvm-ar \
			-DCMAKE_NM=${BINDIR}/llvm-nm \
			-DCMAKE_RANLIB=${BINDIR}/llvm-ranlib \
			-DCMAKE_C_COMPILER=${BINDIR}/clang \
			-DCMAKE_CXX_COMPILER=${BINDIR}/clang++ \
%else
			-DCMAKE_AR=%{_bindir}/llvm-ar \
			-DCMAKE_NM=%{_bindir}/llvm-nm \
			-DCMAKE_RANLIB=%{_bindir}/llvm-ranlib \
			-DCMAKE_C_COMPILER=%{_bindir}/clang \
			-DCMAKE_CXX_COMPILER=%{_bindir}/clang++ \
%endif
			-DCMAKE_ASM_COMPILER_TARGET=${arch}-openmandriva-linux-${LIBC} \
			-DCMAKE_C_COMPILER_TARGET=${arch}-openmandriva-linux-${LIBC} \
			-DCMAKE_CXX_COMPILER_TARGET=${arch}-openmandriva-linux-${LIBC} \
			-DCOMPILER_RT_DEFAULT_TARGET_TRIPLE=${arch}-openmandriva-linux-${LIBC} \
			-DCMAKE_ASM_FLAGS="$FLAGS -isystem %{_prefix}/${arch}-openmandriva-linux-${LIBC}/include/c++/${gccver}/${arch}-openmandriva-linux-${LIBC}" \
			-DCMAKE_C_FLAGS="$FLAGS -isystem %{_prefix}/${arch}-openmandriva-linux-${LIBC}/include/c++/${gccver}/${arch}-openmandriva-linux-${LIBC}" \
			-DCMAKE_CXX_FLAGS="$FLAGS -isystem %{_prefix}/${arch}-openmandriva-linux-${LIBC}/include/c++/${gccver}/${arch}-openmandriva-linux-${LIBC}" \
			-DCMAKE_EXE_LINKER_FLAGS="$LFLAGS" \
			-DCMAKE_MODULE_LINKER_FLAGS="$LFLAGS" \
			-DCMAKE_SHARED_LINKER_FLAGS="$LFLAGS" \
			-DCOMPILER_RT_BUILD_BUILTINS:BOOL=ON \
			-DCOMPILER_RT_BUILD_SANITIZERS:BOOL=OFF \
			-DCOMPILER_RT_BUILD_LIBFUZZER:BOOL=OFF \
			-DCOMPILER_RT_BUILD_MEMPROF:BOOL=OFF \
			-DCOMPILER_RT_BUILD_PROFILE:BOOL=OFF \
			-DCOMPILER_RT_BUILD_XRAY:BOOL=OFF \
			-DCOMPILER_RT_DEFAULT_TARGET_ONLY:BOOL=OFF \
			-G Ninja
		%ninja_build
		cd ..
	done
fi
%endif

%install
%if %{with ocaml}
#cp bindings/ocaml/llvm/META.llvm bindings/ocaml/llvm/Release/
%endif

%if %{with compat32}
%ninja_install -C build32
# Get rid of compat32 stuff that isn't needed in a 64-bit
# environment
rm -rf \
    %{buildroot}%{_prefix}/lib/libear \
    %{buildroot}%{_prefix}/lib/libscanbuild \
    %{buildroot}%{_prefix}/lib/LLVMgold.so \
    %{buildroot}%{_prefix}/lib/clang \
    %{buildroot}%{_bindir}
%endif

%ninja_install -C build

%if %{with crosscrt}
XCRTARCHES=""
%ifnarch %{arm}
XCRTARCHES="$XCRTARCHES armv7hnl"
%endif
%ifnarch %{aarch64}
XCRTARCHES="$XCRTARCHES aarch64"
%endif
%ifnarch %{ix86}
XCRTARCHES="$XCRTARCHES i686"
%endif
%ifnarch %{riscv64}
XCRTARCHES="$XCRTARCHES riscv64"
%endif
%ifnarch ppc64
XCRTARCHES="$XCRTARCHES ppc64"
%endif
%ifnarch ppc64le
XCRTARCHES="$XCRTARCHES ppc64le"
%endif
if [ -n "$XCRTARCHES" ]; then
    for arch in $XCRTARCHES; do
	%ninja_install -C xbuild-crt-${arch}
    done
fi
%endif

%if "%{_lib}" != "lib"
# FIXME this should be fixed properly, in the CMake files...
# lldb's lua plugin gets installed to the wrong place.
mv %{buildroot}%{_prefix}/lib/lua %{buildroot}%{_libdir}
%endif

# https://bugs.llvm.org/show_bug.cgi?id=42455
cp lld/docs/ld.lld.1 %{buildroot}%{_mandir}/man1/

# Install the clang python bits
mkdir -p %{buildroot}%{python_sitelib}
cp -a clang/bindings/python/clang %{buildroot}%{python_sitelib}/

%if %{with default_compiler}
ln -s clang %{buildroot}%{_bindir}/cc
ln -s clang++ %{buildroot}%{_bindir}/c++
cat >%{buildroot}%{_bindir}/c89 <<'EOF'
#!/bin/sh

fl="-std=c89"
for opt; do
	case "$opt" in
		-ansi|-std=c89|-std=iso9899:1990) fl="";;
		-std=*) echo "$(basename $0) called with non ANSI/ISO C option $opt" >&2
			exit 1;;
	esac
done
exec %{_bindir}/clang $fl ${1+"$@"}
EOF
cat >%{buildroot}%{_bindir}/c99 <<'EOF'
#!/bin/sh

fl="-std=c99"
for opt; do
	case "$opt" in
		-std=c99|-std=iso9899:1999) fl="";;
		-std=*) echo "$(basename $0) called with non ISO C99 option $opt" >&2
			exit 1;;
	esac
done
exec %{_bindir}/clang $fl ${1+"$@"}
EOF
chmod 0755 %{buildroot}%{_bindir}/c89 %{buildroot}%{_bindir}/c99
%endif

%if %{build_lto}
# Put the LTO plugin where ld can see it...
mkdir -p %{buildroot}%{_libdir}/bfd-plugins
ln -s %{_libdir}/LLVMgold.so %{buildroot}%{_libdir}/bfd-plugins/LLVMgold.so
%endif

for i in %{buildroot}%{_bindir}/*; do
# We allow this to fail because some stuff in %{_bindir}
# is shell scripts -- no point in excluding them separately
    chrpath -d $i || :
done

# Relics of libcxx_msan installing a copy of libc++ headers to
# %{buildroot}/$RPM_BUILD_DIR
rm -rf %{buildroot}/home %{buildroot}/builddir
rm -rf %{buildroot}%{_libdir}/python*/site-packages/lib

# Fix bogus pointers to incorrect locations
%if "%{_lib}" != "lib"
# Weird, but for some reason those files seem to get installed only on x86
if [ -e %{buildroot}%{_prefix}/lib/cmake/clang/ClangTargets-*.cmake ]; then
    sed -i -e "s,/lib/,/%{_lib}/,g" %{buildroot}%{_prefix}/lib/cmake/clang/ClangTargets-*.cmake %{buildroot}%{_prefix}/lib/cmake/llvm/LLVMExports-*.cmake
fi
%endif

# FIXME for some reason, runtimes aren't built when cross-compiling
# (at least to RISC-V)
%if ! %{cross_compiling}
# Fix Debianisms
mv %{buildroot}%{_includedir}/*/c++/v1/__config_site %{buildroot}%{_includedir}/c++/v1/
rm -rf %{buildroot}%{_includedir}/*-*-*
%ifarch %{x86_64}
mv %{buildroot}%{_libdir}/x86_64-*/* %{buildroot}%{_libdir}/
rmdir %{buildroot}%{_libdir}/x86_64-*
%if %{with compat32}
mv %{buildroot}%{_prefix}/lib/i686-*/cmake/* %{buildroot}%{_prefix}/lib/cmake/
rmdir %{buildroot}%{_prefix}/lib/i686-*/cmake
mv %{buildroot}%{_prefix}/lib/i686-*/* %{buildroot}%{_prefix}/lib/
rmdir %{buildroot}%{_prefix}/lib/i686-*
%endif
%else
mv %{buildroot}%{_libdir}/*-linux-*/* %{buildroot}%{_libdir}/
rmdir %{buildroot}%{_libdir}/*-linux-*
%endif
%endif

%if %{with unwind}
# Add more headers and a pkgconfig file so we can use the llvm
# unwinder instead of the traditional nongnu.org libunwind
cp libunwind/include/libunwind.h libunwind/include/__libunwind_config.h %{buildroot}%{_includedir}/
# And move unwind.h to where gcc can see it as well
mv %{buildroot}%{_libdir}/clang/%{major1}/include/unwind.h %{buildroot}%{_includedir}/
mkdir -p %{buildroot}%{_libdir}/pkgconfig %{buildroot}%{_prefix}/lib/pkgconfig
%if %{with default_compilerrt}
sed -e 's,@LIBDIR@,%{_libdir},g;s,@VERSION@,%{version},g' %{S:50} >%{buildroot}%{_libdir}/pkgconfig/libunwind.pc
%if %{with compat32}
sed -e 's,@LIBDIR@,%{_prefix}/lib,g;s,@VERSION@,%{version},g' %{S:50} >%{buildroot}%{_prefix}/lib/pkgconfig/libunwind.pc
%endif
%else
sed -e 's,@LIBDIR@,%{_libdir},g;s,@VERSION@,%{version},g' %{S:50} >%{buildroot}%{_libdir}/pkgconfig/libunwind-llvm.pc
%if %{with compat32}
sed -e 's,@LIBDIR@,%{_prefix}/lib,g;s,@VERSION@,%{version},g' %{S:50} >%{buildroot}%{_prefix}/lib/pkgconfig/libunwind-llvm.pc
%endif
%endif
%endif

%if %{with apidocs}
mv %{buildroot}%{_prefix}/docs/html/html %{buildroot}%{_docdir}/llvm/doxygen-polly
rm -rf %{buildroot}%{_prefix}/docs
%endif

# Python modules get installed to a weird place that is hardcoded...
mv %{buildroot}%{_prefix}/python_packages/* %{buildroot}%{_libdir}/python%{pyver}
rm -rf %{buildroot}%{_prefix}/python_packages

%if %{with bootstrap}
# Just amdgpu-arch and nvptx-arch without the rest of libclc
# are entirely useless...
rm -f %{buildroot}%{_bindir}/amdgpu-arch \
	%{buildroot}%{_bindir}/nvptx-arch
%endif

# This seems to be a build system glitch
rm -rf %{buildroot}%{_mandir}/man1/python.1*

# We get libgomp from gcc, so don't symlink libomp to it
rm -f %{buildroot}%{_libdir}/libgomp.so
rm -f %{buildroot}%{_prefix}/lib/libgomp.so

# Not equally sure about this one... Are those object files installed on purpose?
# Let's see if anything doesn't work if we don't package them...
rm -rf %{buildroot}%{_libdir}/objects-Rel*

%if ! %{?cross_compiling}
%check
# Relatively common bug:
# llvm-spirv crashes on startup because
# ": CommandLine Error: Option 'spirv-ext' registered more than once!"
# "LLVM ERROR: inconsistency in registered CommandLine options"
# So let's just make sure it runs...
LD_LIBRARY_PATH=$(pwd)/%{_lib} ./build/bin/llvm-spirv --help
%endif

%package -n python-mlir
Summary: Python bindings for MLIR
Group: Development/Python

%description -n python-mlir
Python bindings for MLIR

%files -n python-mlir
%{_libdir}/python%{pyver}/mlir_core
%{_libdir}/libMLIRCAPIPythonTestDialect.a
%{_libdir}/libMLIRPythonTestDialect.a
%{_prefix}/src/python
