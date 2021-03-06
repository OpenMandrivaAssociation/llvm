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

# (tpg) set snapshot date
%undefine date

# Allow empty debugsource package for some subdirs
%define _empty_manifest_terminate_build 0

%define build_lto 1
%define _disable_ld_no_undefined 1
%define _disable_lto 1
# (tpg) optimize it a bit
%global optflags %(echo %{optflags} |sed -e 's,-m64,,g') -O3 -fpic -fno-semantic-interposition -Wl,-Bsymbolic
%global build_ldflags %{build_ldflags} -fno-semantic-interposition -Wl,-Bsymbolic

%ifarch %{riscv}
# Workaround for broken previous version
%global optflags %{optflags} -fpermissive
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
# Note: --with libcxx doesn't mean "build libcxx", but "USE libcxx",
# as in "link llvm libs and clang libs to libcxx rather than libstdc++
# Don't do this if you care about binary compatibility...
%bcond_with libcxx
%bcond_without clang
%bcond_with flang
%ifarch %{aarch64}
# Temporary workaround -- building mlir on aarch64 with clang 11
# fails (but it works with clang 12 - so we just need a bootstrap
# version)
%bcond_with mlir
%else
%bcond_without mlir
%endif
%ifarch armv7hnl riscv64
# RISC-V and armv7 don't have a working ocaml compiler yet
%bcond_with ocaml
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
%bcond_with build_libcxx
%else
%ifarch %{ix86}
# FIXME libc++ seems to be broken on x86_32
%bcond_with build_libcxx
%else
%bcond_without build_libcxx
%endif
%endif
%ifarch %{riscv}
# Disabled until we get a RISC-V implementation of NativeRegisterContext
# lldb/source/Plugins/Process/Linux/NativeRegisterContext*
%bcond_with lldb
%else
%bcond_without lldb
%endif
%bcond_without openmp
%bcond_without unwind
%bcond_without lld

# If enabled, prefer compiler-rt over libgcc
%bcond_with default_compilerrt

# Clang's libLLVMgold.so shouldn't trigger devel(*) dependencies
%define __requires_exclude 'devel.*'

%define ompmajor 1
%define ompname %mklibname omp %{ompmajor}

%bcond_with upstream_tarballs

%define major %(echo %{version} |cut -d. -f1-2)  
%define major1 %(echo %{version} |cut -d. -f1)
#define is_main 1

%bcond_without crosscrt

Summary:	Low Level Virtual Machine (LLVM)
Name:		llvm
Version:	12.0.1
License:	Apache 2.0 with linking exception
Group:		Development/Other
Url:		http://llvm.org/
%if 0%{?date:1}
# git archive-d from https://github.com/llvm/llvm-project
Source0:	https://github.com/llvm/llvm-project/archive/%{?is_main:main}%{!?is_main:release/%{major1}.x}/llvm-%{major1}-%{date}.tar.gz
Release:	0.%{date}.1
%else
Release:	1
%if %{with upstream_tarballs}
Source0:	http://llvm.org/releases/%{version}/llvm-%{version}.src.tar.xz
Source1:	http://llvm.org/releases/%{version}/cfe-%{version}.src.tar.xz
Source2:	http://llvm.org/releases/%{version}/clang-tools-extra-%{version}.src.tar.xz
Source3:	http://llvm.org/releases/%{version}/polly-%{version}.src.tar.xz
Source4:	http://llvm.org/releases/%{version}/compiler-rt-%{version}.src.tar.xz
Source5:	http://llvm.org/releases/%{version}/libcxx-%{version}.src.tar.xz
Source6:	http://llvm.org/releases/%{version}/libcxxabi-%{version}.src.tar.xz
Source7:	http://llvm.org/releases/%{version}/libunwind-%{version}.src.tar.xz
Source8:	http://llvm.org/releases/%{version}/lldb-%{version}.src.tar.xz
Source9:	http://llvm.org/releases/%{version}/lld-%{version}.src.tar.xz
Source10:	http://llvm.org/releases/%{version}/openmp-%{version}.src.tar.xz
Source11:	http://llvm.org/releases/%{version}/libclc-%{version}.src.tar.xz
%else
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/llvm-project-%{version}.src.tar.xz
%endif
%endif
# For compatibility with the nongnu.org libunwind
Source50:	libunwind.pc.in
Source1000:	llvm.rpmlintrc
# Adjust search paths to match the OS
Patch1:		0000-clang-mandriva.patch
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
Patch12:	llvm-3.8.0-sonames.patch
# Silently turn -O9 into -O3 etc. for increased gcc compatibility
Patch13:	llvm-3.8.0-fix-optlevel.patch
Patch14:	llvm-10.0-fix-m32.patch
Patch16:	clang-rename-fix-linkage.patch
#Patch17:	lld-4.0.0-fix-build-with-libstdc++.patch
# Enable --no-undefined, --as-needed, --enable-new-dtags,
# --hash-style=gnu, --warn-common, --icf=safe, --build-id=sha1,
# -O by default
Patch19:	lld-default-settings.patch
# Patches for musl support, (partially) stolen from Alpine Linux and ported
Patch20:	llvm-3.7-musl.patch
Patch21:	llvm-5.0-MuslX32.patch
Patch22:	lld-9.0-error-on-option-conflict.patch
Patch23:	llvm-9.0-lld-workaround.patch
Patch24:	llvm-11-flang-missing-docs.patch
#Patch25:	llvm-7.0-compiler-rt-arches.patch
Patch27:	compiler-rt-7.0.0-workaround-i386-build-failure.patch
# http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.6-remove-lgcc-when-using-compiler-rt.patch
# breaks exception handling -- removes gcc_eh
Patch29:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.6-fix-unwind-chain-inclusion.patch
Patch31:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.5-fix-stdint.patch
Patch40:	libc++-3.7.0-musl-compat.patch
# Make it possible to override CLANG_LIBDIR_SUFFIX
# (that is used only to find LLVMgold.so)
# https://llvm.org/bugs/show_bug.cgi?id=23793
Patch43:	clang-0002-cmake-Make-CLANG_LIBDIR_SUFFIX-overridable.patch
# Fix library versioning
Patch46:	llvm-4.0.1-libomp-versioning.patch
# Fix mcount name for arm and armv8
# https://llvm.org/bugs/show_bug.cgi?id=27248
Patch48:	llvm-3.8.0-mcount-name.patch
Patch49:	llvm-9.0-riscv.patch
# Show more information when aborting because posix_spawn failed
# (happened in some qemu aarch64 chroots)
Patch51:	llvm-4.0.1-debug-posix_spawn.patch
# Polly LLVM OpenMP backend
Patch56:	polly-8.0-default-llvm-backend.patch
#Patch57:	tsan-realpath-redefinition.patch
# libomp needs to link to libm so it can see
# logbl and fmaxl when using compiler-rt
Patch58:	llvm-10-omp-needs-libm.patch
# Use ELFv2 ABI even for big-endian PPC64
# for compatibility with LLD
Patch59:	llvm-12.0-ppc64-elfv2-abi.patch
# Really a patch -- but we want to apply it conditionally
# and we use %%autosetup for other patches...
Source62:	llvm-10-default-compiler-rt.patch
# Another patch, applied conditionally
Source63:	llvm-riscv-needs-libatomic-linkage.patch
# Allow -fno-semantic-interposition on non-x86
Patch64:	https://reviews.llvm.org/file/data/miwnzzepgeylrlupg5po/PHID-FILE-rydrnduho62obbuww2uw/D101873.diff
Patch65:	https://reviews.llvm.org/file/data/drgodafek2r5f5pr7kqz/PHID-FILE-rjzonmxi7hovvd6qbdim/D101876.diff
# RISC-V improvements
# ===================
# Linker relaxation support for LLD
# https://reviews.llvm.org/D100835
Patch70:	https://reviews.llvm.org/file/data/uxcqagnbvcinly5c7tmp/PHID-FILE-sjeuqpsqsxwbjengaxdp/D100835.diff
BuildRequires:	bison
BuildRequires:	binutils-devel
BuildRequires:	chrpath
BuildRequires:	flex
BuildRequires:	pkgconfig(libedit)
BuildRequires:	pkgconfig(libelf)
%if %{without bootstrap}
BuildRequires:	graphviz
# Without this, generating man pages fails
# Handler <function process_automodsumm_generation at 0x7fa70fc2a5e0> for event 'builder-inited' threw an exception (exception: No module named 'lldb')
BuildRequires:	lldb
# For libclc
BuildRequires:	spirv-llvm-translator
BuildRequires:	pkgconfig(LLVMSPIRVLib)
%if %{with compat32}
BuildRequires:	devel(libLLVMSPIRVLib)
%endif
%endif
BuildRequires:	chrpath
BuildRequires:	groff
BuildRequires:	libtool
BuildRequires:	pkgconfig(ncursesw)
BuildRequires:	python-sphinx
# For sphinx plugins
BuildRequires:	python-recommonmark
BuildRequires:	python-sphinxcontrib-websupport
BuildRequires:	python-sphinx-automodapi
BuildRequires:	python-setuptools
BuildRequires:	python-requests
%if %{with ocaml}
BuildRequires:	ocaml-compiler ocaml-compiler-libs ocaml-camlp4 ocaml-findlib >= 1.5.5-2 ocaml-ctypes
%endif
BuildRequires:	tcl
BuildRequires:	sed
BuildRequires:	zip
BuildRequires:	libstdc++-devel
%if %{with ffi}
BuildRequires:	pkgconfig(libffi)
%endif
BuildRequires:	pkgconfig(cloog-isl)
BuildRequires:	pkgconfig(isl) >= 0.13
BuildRequires:	pkgconfig(libtirpc)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(icu-i18n)
%ifnarch riscv64
BuildRequires:	atomic-devel
%endif
BuildRequires:	python >= 3.4
BuildRequires:	python3dist(pyyaml)
BuildRequires:	python3dist(pygments)
# Make sure lld doesn't install its own copy
BuildRequires:	python-six
BuildRequires:	cmake
BuildRequires:	ninja
%if %{with apidox}
BuildRequires:	doxygen
%endif
Obsoletes:	llvm-ocaml
# Some cmake files try to look up the commit hash
BuildRequires:	git-core
# For lldb
BuildRequires:	swig
BuildRequires:	pkgconfig(python3)
BuildRequires:	gcc
BuildRequires:	pkgconfig(libtirpc)
%if %mdvver > 3000000
%if !%{with lld}
BuildRequires:	lld < %{EVRD}
%endif
%endif
%if %{with openmp}
Requires:	%{ompname} = %{EVRD}
%endif
%if %{with compat32}
BuildRequires:	devel(libffi)
BuildRequires:	devel(libxml2)
BuildRequires:	devel(libelf)
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
# for libGPURuntime in Polly
%ifnarch %{riscv}
BuildRequires:	pkgconfig(OpenCL)
BuildRequires:	mesa-opencl-devel
%endif
%if %{with compat32} && ! %{with bootstrap32}
BuildRequires:	devel(libOpenCL)
BuildRequires:	devel(libMesaOpenCL)
BuildRequires:	libunwind-devel
%endif

Obsoletes: %{mklibname LLVMRISCVCodeGen 5} < %{EVRD}
Obsoletes: %{mklibname LLVMRISCVDesc 5} < %{EVRD}
Obsoletes: %{mklibname LLVMRISCVInfo 5} < %{EVRD}
Obsoletes: %{mklibname lldConfig 5} < %{EVRD}

%if %{with crosscrt}
%ifnarch %{aarch64}
BuildRequires:	cross-aarch64-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-aarch64-openmandriva-linux-gnu-libc
%endif
%ifnarch %{arm}
BuildRequires:	cross-armv7hnl-openmandriva-linux-gnueabihf-gcc-bootstrap
BuildRequires:	cross-armv7hnl-openmandriva-linux-gnueabihf-libc
%endif
%ifnarch %{ix86}
BuildRequires:	cross-i686-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-i686-openmandriva-linux-gnu-libc
%endif
%ifnarch ppc64le
BuildRequires:	cross-ppc64le-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-ppc64le-openmandriva-linux-gnu-libc
%endif
%ifnarch ppc64
BuildRequires:	cross-ppc64-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-ppc64-openmandriva-linux-gnu-libc
%endif
%ifnarch %{riscv64}
BuildRequires:	cross-riscv64-openmandriva-linux-gnu-binutils
BuildRequires:	cross-riscv64-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-riscv64-openmandriva-linux-gnu-libc
BuildRequires:	cross-riscv64-openmandriva-linux-gnu-kernel-headers
%endif
%ifnarch %{x86_64}
BuildRequires:	cross-x86_64-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-x86_64-openmandriva-linux-gnu-libc
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
%{_bindir}/llvm-diff
%{_bindir}/llvm-dis
%{_bindir}/llvm-dwp
%{_bindir}/llvm-elfabi
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
%{_bindir}/llvm-bitcode-strip
%{_bindir}/llvm-jitlink-executor
%{_bindir}/llvm-libtool-darwin
%{_bindir}/llvm-profgen
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
%{_bindir}/llvm-cxxdump
%{_bindir}/llvm-xray
%if !%{with lld}
%{_bindir}/llvm-dlltool
%{_bindir}/llvm-mt
%{_bindir}/llvm-readelf
%endif

%{_bindir}/sancov
%{_bindir}/sanstats
%{_bindir}/verify-uselistorder
%{_bindir}/obj2yaml
%{_bindir}/wasm-ld
%{_bindir}/yaml2obj
%{_bindir}/yaml-bench
%{_bindir}/not

%{_mandir}/man1/FileCheck.1*
%{_mandir}/man1/bugpoint.1*

%{_mandir}/man1/dsymutil.1*
%{_mandir}/man1/lit.1*
%{_mandir}/man1/llc.1*
%{_mandir}/man1/lli.1*
%{_mandir}/man1/llvm-*.1*
%{_mandir}/man1/opt.1*
%{_mandir}/man1/xxx-tblgen.1*

#-----------------------------------------------------------
%define LLVMLibs LLVMAArch64AsmParser LLVMAArch64CodeGen LLVMAArch64Desc LLVMAArch64Disassembler LLVMAArch64Info LLVMAArch64Utils LLVMAggressiveInstCombine LLVMARMAsmParser LLVMARMCodeGen LLVMARMDesc LLVMARMDisassembler LLVMARMInfo LLVMARMUtils LLVMAnalysis LLVMAsmParser LLVMAsmPrinter LLVMBPFAsmParser LLVMBitReader LLVMBitstreamReader LLVMBitWriter LLVMBPFCodeGen LLVMBPFDesc LLVMBPFDisassembler LLVMBPFInfo LLVMBinaryFormat LLVMCodeGen LLVMCore LLVMDebugInfoCodeView LLVMCoroutines LLVMDebugInfoDWARF LLVMDebugInfoMSF LLVMDebugInfoPDB LLVMDemangle LLVMDlltoolDriver LLVMExecutionEngine LLVMFuzzMutate LLVMHexagonAsmParser LLVMHexagonCodeGen LLVMHexagonDesc LLVMHexagonDisassembler LLVMHexagonInfo LLVMIRReader LLVMInstCombine LLVMInstrumentation LLVMInterpreter LLVMLanaiAsmParser LLVMLanaiCodeGen LLVMLanaiDesc LLVMLanaiDisassembler LLVMLanaiInfo LLVMLTO LLVMLibDriver LLVMLineEditor LLVMLinker LLVMMC LLVMMCDisassembler LLVMMCJIT LLVMMCParser LLVMMIRParser LLVMMSP430CodeGen LLVMMSP430Desc LLVMMSP430Info LLVMMipsAsmParser LLVMMipsCodeGen LLVMMipsDesc LLVMMipsDisassembler LLVMMipsInfo LLVMNVPTXCodeGen LLVMNVPTXDesc LLVMNVPTXInfo LLVMObjCARCOpts LLVMObject LLVMOption LLVMOrcJIT LLVMPasses LLVMPowerPCAsmParser LLVMPowerPCCodeGen LLVMPowerPCDesc LLVMPowerPCDisassembler LLVMPowerPCInfo LLVMProfileData LLVMAMDGPUAsmParser LLVMAMDGPUCodeGen LLVMAMDGPUDesc LLVMAMDGPUDisassembler LLVMAMDGPUInfo LLVMAMDGPUUtils LLVMRuntimeDyld LLVMScalarOpts LLVMSelectionDAG LLVMSparcAsmParser LLVMSparcCodeGen LLVMSparcDesc LLVMSparcDisassembler LLVMSparcInfo LLVMSupport LLVMSymbolize LLVMSystemZAsmParser LLVMSystemZCodeGen LLVMSystemZDesc LLVMSystemZDisassembler LLVMSystemZInfo LLVMTableGen LLVMTarget LLVMTransformUtils LLVMVectorize LLVMWindowsManifest LLVMX86AsmParser LLVMX86CodeGen LLVMX86Desc LLVMX86Disassembler LLVMX86Info LLVMXCoreCodeGen LLVMXCoreDesc LLVMXCoreDisassembler LLVMXCoreInfo LLVMXRay LLVMipo LLVMCoverage LLVMGlobalISel LLVMObjectYAML LLVMMCA LLVMMSP430AsmParser LLVMMSP430Disassembler LLVMRemarks LLVMTextAPI LLVMWebAssemblyAsmParser LLVMWebAssemblyCodeGen LLVMWebAssemblyDesc LLVMWebAssemblyDisassembler LLVMWebAssemblyInfo Remarks LLVMRISCVAsmParser LLVMRISCVCodeGen LLVMRISCVDesc LLVMRISCVDisassembler LLVMRISCVInfo LLVMDebugInfoGSYM LLVMJITLink LLVMCFGuard LLVMDWARFLinker LLVMFrontendOpenMP LLVMAVRAsmParser LLVMAVRCodeGen LLVMAVRDesc LLVMAVRDisassembler LLVMAVRInfo LLVMExtensions LLVMFrontendOpenACC LLVMFileCheck LLVMHelloNew LLVMInterfaceStub LLVMOrcShared LLVMOrcTargetProcess Polly

%define LLVM64Libs findAllSymbols

%define ClangLibs LTO clang clangARCMigrate clangAST clangASTMatchers clangAnalysis clangBasic clangCodeGen clangCrossTU clangDriver clangDynamicASTMatchers clangEdit clangFormat clangFrontend clangFrontendTool clangHandleCXX clangIndex clangLex clangParse clangRewrite clangRewriteFrontend clangSema clangSerialization clangStaticAnalyzerCheckers clangStaticAnalyzerCore clangStaticAnalyzerFrontend clangTooling clangToolingASTDiff clangToolingCore clangHandleLLVM clangToolingInclusions clangDependencyScanning clangToolingRefactoring clangToolingSyntax clang-cpp clangDirectoryWatcher clangTransformer clangTesting clangAPINotes clangIndexSerialization

%define Clang64Libs clangApplyReplacements clangChangeNamespace clangDaemon clangDaemonTweaks clangDoc clangIncludeFixer clangIncludeFixerPlugin clangMove clangQuery clangReorderFields clangTidy clangTidyPlugin clangTidyAbseilModule clangTidyAndroidModule clangTidyBoostModule clangTidyBugproneModule clangTidyCERTModule clangTidyCppCoreGuidelinesModule clangTidyDarwinModule clangTidyFuchsiaModule clangTidyGoogleModule clangTidyHICPPModule clangTidyLLVMModule clangTidyLinuxKernelModule clangTidyMiscModule clangTidyModernizeModule clangTidyMPIModule clangTidyObjCModule clangTidyOpenMPModule clangTidyPortabilityModule clangTidyReadabilityModule clangTidyPerformanceModule clangTidyZirconModule clangTidyUtils clangTidyLLVMLibcModule clangTidyMain clangdRemoteIndex clangdSupport clangTidyAlteraModule clangTidyConcurrencyModule

%define FlangLibs FIROptimizer FortranCommon FortranDecimal FortranEvaluate FortranLower FortranParser FortranRuntime FortranSemantics

%if %{with mlir}
%define MLIRLibs MLIRAffine MLIRArmNeon MLIRArmNeonToLLVM MLIRArmSVE MLIRArmSVEToLLVM MLIRAsync MLIRAsyncToLLVM MLIRAsyncTransforms MLIRAVX512 MLIRAVX512ToLLVM MLIRAffineEDSC MLIRAffineToStandard MLIRAffineTransforms MLIRAffineTransformsTestPasses MLIRAffineUtils MLIRAnalysis MLIRCAPIIR MLIRCAPILinalg MLIRCAPIRegistration MLIRCAPISCF MLIRCAPIShape MLIRCAPIStandard MLIRCAPITensor MLIRCAPITransforms MLIRCastInterfaces MLIRCallInterfaces MLIRComplex MLIRComplexToLLVM MLIRControlFlowInterfaces MLIRCopyOpInterface MLIRDerivedAttributeOpInterface MLIRDialect MLIREDSC MLIRExecutionEngine MLIRGPU MLIRGPUToGPURuntimeTransforms MLIRGPUToNVVMTransforms MLIRGPUToROCDLTransforms MLIRGPUToSPIRV MLIRLLVMArmNeon MLIRLLVMArmSVE MLIRLinalg MLIRGPUToVulkanTransforms MLIRIR MLIRInferTypeOpInterface MLIRJitRunner MLIRLLVMAVX512 MLIRLLVMIR MLIRLLVMIRTransforms MLIRLinalgAnalysis MLIRLinalgEDSC MLIRLinalgToLLVM MLIRLinalgToSPIRV MLIRLinalgToStandard MLIRLinalgTransforms MLIRLinalgUtils MLIRLoopAnalysis MLIRLoopLikeInterface MLIRMlirOptMain MLIRNVVMIR MLIROpenACC MLIROpenMP MLIROpenMPToLLVM MLIROptLib MLIRParser MLIRPass MLIRPresburger MLIRQuant MLIRROCDLIR MLIRReduce MLIRSCF MLIRSCFToGPU MLIRSCFToOpenMP MLIRSCFToSPIRV MLIRSCFToStandard MLIRSCFTransforms MLIRSDBM MLIRSPIRV MLIRSPIRVSerialization MLIRSPIRVTestPasses MLIRSPIRVToLLVM MLIRSPIRVTransforms MLIRShape MLIRShapeOpsTransforms MLIRShapeToStandard MLIRSideEffectInterfaces MLIRStandardOpsTransforms MLIRStandardToLLVM MLIRStandardToSPIRV MLIRSupport MLIRSupportIndentedOstream MLIRTargetArmNeon MLIRTargetArmSVE MLIRTargetAVX512 MLIRTargetLLVMIR MLIRTargetLLVMIRModuleTranslation MLIRTargetNVVMIR MLIRTargetROCDLIR MLIRTestDialect MLIRTestIR MLIRTestPass MLIRTestReducer MLIRTestRewrite MLIRTestTransforms MLIRTransformUtils MLIRTransforms MLIRTranslation MLIRVector MLIRVectorInterfaces MLIRVectorToLLVM MLIRVectorToROCDL MLIRVectorToSCF MLIRVectorToSPIRV MLIRViewLikeInterface mlir_async_runtime mlir_c_runner_utils mlir_c_runner_utils_static mlir_runner_utils mlir_test_cblas mlir_test_cblas_interface MLIRPDL MLIRPDLInterp MLIRPDLToPDLInterp MLIRPublicAPI MLIRRewrite MLIRSPIRVBinaryUtils MLIRSPIRVConversion MLIRSPIRVDeserialization MLIRSPIRVModuleCombiner MLIRSPIRVTranslateRegistration MLIRSPIRVUtils MLIRShapeTestPasses MLIRStandard MLIRTensor MLIRTensorTransforms MLIRTosa MLIRTosaTestPasses MLIRTosaToLinalg MLIRTosaTransforms
%else
%define MLIRLibs %{nil}
%endif

%if %{with lld}
%define LLDLibs lldCOFF lldCommon lldCore lldDriver lldELF lldMachO lldMachO2 lldMinGW lldReaderWriter lldWasm lldYAML
%else
%define LLDLibs %{nil}
%endif

%if %{with lldb}
%define LLDBLibs lldb lldbIntelFeatures
%else
%define LLDBLibs %{nil}
%endif

%{expand:%(for i in %{LLVMLibs} %{LLVM64Libs} %{ClangLibs} %{Clang64Libs} %{LLDLibs} %{LLDBLibs} %{MLIRLibs}; do echo %%libpackage $i %{major1}; done)}

%if %{with flang}
%{expand:%(for i in %{FlangLibs}; do echo %%libpackage $i %{major1}; done)}
%endif

%if %{with compat32}
%{expand:%(for i in %{LLVMLibs} %{ClangLibs}; do cat <<EOF
%%package -n lib${i}%{major1}
Summary: 32-bit LLVM ${i} library
Group: Development/C

%%description -n lib${i}%{major1}
32-bit LLVM ${i} library

%%files -n lib${i}%{major1}
%%{_prefix}/lib/lib${i}.so.%{major1}*
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
%doc %{_docdir}/libunwind
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
%endif

#-----------------------------------------------------------
%if %{with build_libcxx}
%libpackage c++ 1
%libpackage c++abi 1
%{_libdir}/libc++abi.so
%{_libdir}/libc++.a

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
%doc %{_docdir}/libcxx
%{_includedir}/c++
%{_includedir}/__pstl*
%{_includedir}/pstl
%{_prefix}/lib/cmake/ParallelSTL
%{_libdir}/libc++experimental.a

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
%define libname %mklibname %{name} %{major}

%package -n %{libname}
Summary:	LLVM shared libraries
Group:		System/Libraries
Conflicts:	llvm < 3.0-4
Obsoletes:	%{mklibname %{name} 3.5.0}
Obsoletes:	%{mklibname %{name} 3.6.0}
%{expand:%(for i in %{LLVMLibs} %{LLVM64Libs}; do echo Requires:	%%{mklibname $i %{major1}} = %{EVRD}; done)}
Obsoletes:	%{mklibname LLVMCppBackendCodeGen 3} < %{EVRD}
Obsoletes:	%{mklibname LLVMCppBackendInfo 3} < %{EVRD}
Obsoletes:	%{mklibname LLVMAArch64AsmPrinter 9} < %{EVRD}
Obsoletes:	%{mklibname LLVMARMAsmPrinter 9} < %{EVRD}
Obsoletes:	%{mklibname LLVMLanaiAsmPrinter 9} < %{EVRD}
Obsoletes:	%{mklibname LLVMMSP430AsmPrinter 9} < %{EVRD}
Obsoletes:	%{mklibname LLVMMipsAsmPrinter 9} < %{EVRD}
Obsoletes:	%{mklibname LLVMNVPTXAsmPrinter 9} < %{EVRD}
Obsoletes:	%{mklibname LLVMPowerPCAsmPrinter 9} < %{EVRD}
Obsoletes:	%{mklibname LLVMAMDGPUAsmPrinter 9} < %{EVRD}
Obsoletes:	%{mklibname LLVMSparcAsmPrinter 9} < %{EVRD}
Obsoletes:	%{mklibname LLVMSystemZAsmPrinter 9} < %{EVRD}
Obsoletes:	%{mklibname LLVMX86AsmPrinter 9} < %{EVRD}
Obsoletes:	%{mklibname LLVMXCoreAsmPrinter 9} < %{EVRD}
Obsoletes:	%{mklibname LLVMWebAssemblyAsmPrinter 9} < %{EVRD}
Obsoletes:	%{mklibname LLVMRISCVAsmPrinter 9} < %{EVRD}
Obsoletes:	%{mklibname LLVMLTO 11} < %{EVRD}
Obsoletes:	%{mklibname clangCodeGen 11} < %{EVRD}
Obsoletes:	%{mklibname clang-cpp 11} < %{EVRD}
Obsoletes:	%{mklibname LLVMExtensions 11} < %{EVRD}

%description -n %{libname}
Shared libraries for the LLVM compiler infrastructure. This is needed by
programs that are dynamically linked against libLLVM.

%files -n %{libname}

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
Requires:	%{_lib}mlir_test_cblas%{major1} = %{EVRD}
Requires:	%{_lib}mlir_test_cblas_interface%{major1} = %{EVRD}
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
%ifnarch %{riscv}
Requires:	%{_lib}gpuruntime
BuildRequires:	%{_lib}gpuruntime
%endif

%description -n %{devname}
This package contains the development files for LLVM.

%files -n %{devname}
%{_bindir}/%{name}-config
%{_includedir}/%{name}
%{_includedir}/%{name}-c
%{_libdir}/cmake/%{name}
%{_libdir}/lib*.so
%ifnarch %{riscv}
%exclude %{_libdir}/libGPURuntime.so
%endif
%ifnarch %{arm}
%{_libdir}/libarcher_static.a
%endif
%if %{with openmp}
%exclude %{_libdir}/libomp.so
%endif
%if %{with build_libcxx}
%exclude %{_libdir}/libc++abi.so
%endif
# Stuff from clang
%exclude %{_libdir}/libclang*.so
%exclude %{_libdir}/libLTO.so
%exclude %{_libdir}/libPolly.so
%exclude %{_libdir}/libPollyISL.so
%exclude %{_libdir}/libPollyPPCG.so

#-----------------------------------------------------------
%if %{with openmp}
%package -n %{ompname}
Summary:	LLVM OpenMP shared libraries
Group:		System/Libraries
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
%doc %{_docdir}/openmp
%{_libdir}/libomp.so*
%{_libdir}/libomptarget.so.*
%ifnarch armv7hnl
%{_includedir}/ompt-multiplex.h
%endif
%{_mandir}/man1/llvmopenmp.1*
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
%doc llvm/README.txt
%doc llvm/docs/tutorial
%doc llvm/examples
%doc %{_docdir}/llvm

#-----------------------------------------------------------
%package polly
Summary:	Polyhedral optimizations for LLVM
License:	MIT
Group:		Development/Other
Obsoletes:	llvm-devel < 4.0.1
Obsoletes:	%{_lib}llvm-devel < 4.0.1
Conflicts:	%{_lib}llvm-devel < 4.0.1

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
# Unversioned library, not -devel file
%{_libdir}/libPollyISL.so
%{_libdir}/libPollyPPCG.so
%{_mandir}/man1/polly.1*

#-----------------------------------------------------------
%package polly-devel
Summary:	Development files for Polly
License:	MIT
Group:		Development/Other
Requires:	%{name}-polly = %{EVRD}

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
%doc %{_docdir}/polly
%{_includedir}/polly
%{_libdir}/cmake/polly
%{_libdir}/libPolly.so
#-----------------------------------------------------------

%if %{with clang}
%package -n clang
Summary:	A C language family front-end for LLVM
License:	NCSA
Group:		Development/Other
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
Obsoletes:	%{mklibname clang 3.7.0}
Obsoletes:	%{mklibname clang_shared 9}
%{expand:%(for i in %{ClangLibs} %{Clang64Libs}; do echo Requires:	%%{mklibname $i %{major1}} = %{EVRD}; done)}

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
%{_bindir}/clang++
%{_bindir}/clang-%{major1}

%{_bindir}/clang-cpp
%{_libdir}/LLVMgold.so
%if %{build_lto}
%{_libdir}/bfd-plugins/LLVMgold.so
%endif
%{_libdir}/libLTO.so
%{_libdir}/clang
%{_datadir}/clang
%if %{with default_compiler}
%{_bindir}/cc
%{_bindir}/c89
%{_bindir}/c99
%{_bindir}/c++
%endif
%{_mandir}/man1/clang.1*

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
%{_bindir}/clang-include-fixer
%{_bindir}/clang-move
%{_bindir}/clang-offload-bundler
%{_bindir}/clang-offload-wrapper
%{_bindir}/clang-query
%{_bindir}/clang-refactor
%{_bindir}/clang-rename
%{_bindir}/clang-reorder-fields
%{_bindir}/clang-scan-deps
%{_bindir}/clang-tidy
%{_bindir}/clangd
%{_bindir}/diagtool
%{_bindir}/find-all-symbols
%{_bindir}/hmaptool
%{_bindir}/modularize
%{_bindir}/pp-trace
%{_mandir}/man1/diagtool.1*
%{_mandir}/man1/extraclangtools.1*

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

%description -n %{devclang}
This package contains header files and libraries needed for using
libclang.

%files -n %{devclang}
%{_includedir}/clang
%{_includedir}/clang-c
%{_includedir}/clang-tidy
%{_libdir}/libclang*.so
%{_libdir}/cmake/clang

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
# clang static analyzer -- maybe should be a separate package
%{_bindir}/scan-build
%{_bindir}/scan-view
%{_libexecdir}/ccc-analyzer
%{_libexecdir}/c++-analyzer
%{_datadir}/scan-build
%{_datadir}/scan-view
%{_mandir}/man1/scan-build.1*

%package -n clang-doc
Summary:	Documentation for Clang
Group:		Books/Computer books
BuildArch:	noarch
Requires:	%{name} = %{EVRD}

%description -n clang-doc
Documentation for the Clang compiler front-end.

%files -n clang-doc
%doc %{_docdir}/clang-tools
%doc %{_docdir}/clang
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
%{_bindir}/flang
%{_bindir}/f18
%{_bindir}/f18-parse-demo
%{_bindir}/tco

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
%{expand:%(for i in %{LLDBLibs}; do echo Requires:	%%{mklibname $i %{major1}} = %{EVRD}; done)}

%description -n lldb
Debugger from the LLVM toolchain.

%files -n lldb
%{_bindir}/lldb*
%{_libdir}/python*/site-packages/lldb
%{_mandir}/man1/lldb.1*
%{_mandir}/man1/lldb-server.1*
%doc %{_docdir}/lldb

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
%{expand:%(for i in %{LLDLibs}; do echo Requires:	%%{mklibname $i %{major1}} = %{EVRD}; done)}
# Stuff from lld 3.8 that has been removed in 3.9
Obsoletes:	%{mklibname lldAArch64ELFTarget 3} < %{EVRD}
Obsoletes:	%{mklibname lldARMELFTarget 3} < %{EVRD}
Obsoletes:	%{mklibname lldELF2 3} < %{EVRD}
Obsoletes:	%{mklibname lldExampleSubTarget 3} < %{EVRD}
Obsoletes:	%{mklibname lldHexagonELFTarget 3} < %{EVRD}
Obsoletes:	%{mklibname lldMipsELFTarget 3} < %{EVRD}
Obsoletes:	%{mklibname lldX86ELFTarget 3} < %{EVRD}
Obsoletes:	%{mklibname lldX86_64ELFTarget 3} < %{EVRD}
# Stuff from lld 5.0 that has been removed in 6.0
Obsoletes:	%{mklibname lldELF 5} < %{EVRD}
Obsoletes:	%{mklibname lldConfig 5} < %{EVRD}

%description -n lld
The linker from the LLVM project.

%files -n lld
%doc %{_docdir}/lld
%{_bindir}/ld.lld
%{_bindir}/ld64.lld
%{_bindir}/ld64.lld.darwinnew
%{_bindir}/lld
%{_bindir}/lld-link
%{_bindir}/llvm-dlltool
%{_bindir}/llvm-mt
%{_mandir}/man1/ld.lld.1*

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

%package -n %{_lib}gpuruntime
Summary:	GPU runtime library
Group:		System/Libraries

%description -n %{_lib}gpuruntime
GPU runtime library.

%ifnarch %{riscv}
%files -n %{_lib}gpuruntime
%{_libdir}/libGPURuntime.so
%endif

#-----------------------------------------------------------

%if %{with compat32}
%package -n libllvm-devel
Summary:	32-bit LLVM development files
Group:		Development/C
%{expand:%(for i in %{LLVMLibs}; do echo Requires:	lib${i}%{major1} = %{EVRD}; done)}

%description -n libllvm-devel
32-bit LLVM development files.

%files -n libllvm-devel
%{_prefix}/lib/cmake/clang
%{_prefix}/lib/cmake/llvm
%{_prefix}/lib/libLLVM*.so
%{_prefix}/lib/libLTO.so
%{_prefix}/lib/libRemarks.so
%{_prefix}/lib/libarcher.so
%{_prefix}/lib/libarcher_static.a

%package -n libclang-devel
Summary:	32-bit Clang development files
Group:		Development/C
%{expand:%(for i in %{ClangLibs}; do echo Requires:	lib${i}%{major1} = %{EVRD}; done)}

%description -n libclang-devel
32-bit Clang development files.

%files -n libclang-devel
%{_prefix}/lib/libclang*.so

%package -n libgpuruntime
Summary:	32-bit GPU runtime library
Group:		System/Libraries

%description -n libgpuruntime
32-bit GPU runtime library.

%ifnarch %{riscv}
%if ! %{with bootstrap32}
%files -n libgpuruntime
%{_prefix}/lib/libGPURuntime.so
%endif
%endif

%package -n libomp1
Summary:	32-bit OpenMP runtime
Group:		System/Libraries

%description -n libomp1
32-bit OpenMP runtime.

%files -n libomp1
%{_prefix}/lib/libomp.so.1*
%{_prefix}/lib/libomptarget.so.*

%package -n libomp-devel
Summary:	Development files for the 32-bit OpenMP runtime
Group:		Development/C

%description -n libomp-devel
Development files for the 32-bit OpenMP runtime.

%files -n libomp-devel
%{_prefix}/lib/libgomp.so
%{_prefix}/lib/libiomp5.so
%{_prefix}/lib/libomp.so
%{_prefix}/lib/libomptarget.so

%package polly32
Summary:	Polyhedral optimizations for LLVM (32-bit)
License:	MIT
Group:		Development/Other

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
%{_prefix}/lib/libPolly.so.*
# Unversioned libraries, not -devel files
%{_prefix}/lib/LLVMPolly.so
%{_prefix}/lib/libPollyISL.so
%{_prefix}/lib/libPollyPPCG.so

%package polly32-devel
Summary:	Development files for Polly (32-bit)
License:	MIT
Group:		Development/Other
Requires:	%{name}-polly32 = %{EVRD}
Requires:	%{name}-polly-devel = %{EVRD}

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
%{_prefix}/lib/libPolly.so
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

%define mlirdev %{mklibname -d mlir}
%package -n %{mlirdev}
Summary:	Development files for MLIR
Group:	Development/C

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
Url:		http://libclc.llvm.org/

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

%files -n libclc-spirv
%{_datadir}/clc/spirv*

%files -n libclc-r600
%{_datadir}/clc/*-r600-*

%files -n libclc-nvptx
%{_datadir}/clc/nvptx*

%files -n libclc-amdgcn
%{_datadir}/clc/*amdgcn*
%endif


%prep
%if 0%{?date:1}
%autosetup -p1 -n llvm-project-%{?is_main:main}%{!?is_main:release-%{major1}.x}
%else
%if %{with upstream_tarballs}
%setup -n %{name}-%{version}.src -c 0 -a 1 -a 2 -a 3 -a 4 -a 5 -a 6 -a 7 -a 8 -a 9 -a 10 -a 11
mv llvm-%{version}.src llvm
mv cfe-%{version}.src clang
mv clang-tools-extra-%{version}.src clang-tools-extra
mv polly-%{version}.src polly
mv compiler-rt-%{version}.src compiler-rt
mv libcxx-%{version}.src libcxx
mv libcxxabi-%{version}.src libcxxabi
mv libunwind-%{version}.src libunwind
mv lld-%{version}.src lld
mv lldb-%{version}.src lldb
mv openmp-%{version}.src openmp
mv libclc-%{version}.src libclc
%autopatch -p1
%else
%autosetup -p1 -n llvm-project-%{version}.src
%endif
%endif
%if %{with default_compilerrt}
patch -p1 -b -z .crt~ <%{S:62}
%endif
%ifarch %{riscv}
patch -p1 -b -z .rvatomic~ <%{S:63}
%endif
git init
git config user.email build@openmandriva.org
git config user.name "OpenMandriva builder"
git add * >/dev/null
git commit --quiet -am "Fake commit to make cmake files happy"

# Fix bogus permissions
find . -type d -exec chmod 0755 {} \;

# LLVM doesn't use autoconf, but it uses autoconf's config.guess
# to find target arch and friends (hidden away in cmake/).
# Let's make sure we replace its outdated copy (which doesn't
# know what riscv64 is) with a current version.
%config_update

%build
# Temporary workaround for compiling with lld that doesn't have patch 21
#mkdir path-override
#ln -s %{_bindir}/ld.gold path-override/ld
#export PATH=$(pwd)/path-override:$PATH

COMPONENTS="llvm"
%if %{with clang}
COMPONENTS="$COMPONENTS;clang;clang-tools-extra;polly;compiler-rt"
%endif
%if %{with mlir}
COMPONENTS="$COMPONENTS;mlir"
%endif
%if %{with flang}
COMPONENTS="$COMPONENTS;flang"
%endif
%if %{with unwind}
COMPONENTS="$COMPONENTS;libunwind"
%endif
%if %{with lldb}
COMPONENTS="$COMPONENTS;lldb"
%endif
%if %{with lld}
COMPONENTS="$COMPONENTS;lld"
%endif
%if %{with openmp}
COMPONENTS="$COMPONENTS;openmp"
%endif
%if %{with build_libcxx}
COMPONENTS="$COMPONENTS;libcxx;libcxxabi;pstl;parallel-libs"
%endif
COMPONENTS="$COMPONENTS;libclc"
# Not yet
#COMPONENTS="$COMPONENTS;libc"

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

# The "%if 1" below is just a quick way to get rid of the real
# 64-bit build to debug 32-bit build issues. No need to do a
# proper define/with condition here, the switch is useless for
# any regular use.
%if 1
# We set an RPATH in CMAKE_EXE_LINKER_FLAGS to make sure the newly built
# clang and friends use the just-built shared libraries -- there's no guarantee
# that the ABI remains compatible between a snapshot libclang.so.11 and the
# final libclang.so.11 at the moment.
# We strip out the rpath in %%install though - so we aren't really being evil.
#
# We should probably enable
#	-DLIBUNWIND_BUILD_32_BITS:BOOL=ON \
#	-DLIBCXXABI_BUILD_32_BITS:BOOL=ON \
#	-DLIBCXX_BUILD_32_BITS:BOOL=ON \
# at some point - but right now, builds are broken
%cmake \
	-DLLVM_ENABLE_PROJECTS="$COMPONENTS" \
	-DCLANG_VENDOR="OpenMandriva %{version}-%{release}" \
	-DLLD_VENDOR="OpenMandriva %{version}-%{release}" \
	-DBUILD_SHARED_LIBS:BOOL=ON \
	-DENABLE_EXPERIMENTAL_NEW_PASS_MANAGER:BOOL=ON \
	-DENABLE_X86_RELAX_RELOCATIONS:BOOL=ON \
	-DCLANG_DEFAULT_LINKER=lld \
	-DCLANG_DEFAULT_OBJCOPY=llvm-objcopy \
%if %{with default_compilerrt}
	-DCLANG_DEFAULT_RTLIB=compiler-rt \
	-DCOMPILER_RT_USE_BUILTINS_LIBRARY:BOOL=ON \
%else
	-DCLANG_DEFAULT_RTLIB=libgcc \
%endif
%if %{with ffi}
	-DLLVM_ENABLE_FFI:BOOL=ON \
%else
	-DLLVM_ENABLE_FFI:BOOL=OFF \
%endif
	-DLLVM_ENABLE_SPHINX:BOOL=ON \
	-DSPHINX_WARNINGS_AS_ERRORS:BOOL=OFF \
	-DLLVM_TARGETS_TO_BUILD=all \
	-DLLVM_ENABLE_CXX1Y:BOOL=ON \
	-DLLVM_ENABLE_RTTI:BOOL=ON \
	-DLLVM_ENABLE_PIC:BOOL=ON \
	-DLLVM_INCLUDE_DOCS:BOOL=ON \
	-DLLVM_ENABLE_EH:BOOL=ON \
	-DLLVM_INSTALL_UTILS:BOOL=ON \
	-DLLVM_BINUTILS_INCDIR=%{_includedir} \
	-DLLVM_BUILD_DOCS:BOOL=ON \
	-DLLVM_BUILD_EXAMPLES:BOOL=OFF \
	-DLLVM_BUILD_RUNTIME:BOOL=ON \
	-DLLVM_TOOL_COMPILER_RT_BUILD:BOOL=ON \
	-DCOMPILER_RT_BUILD_BUILTINS:BOOL=ON \
	-DCOMPILER_RT_BUILD_CRT:BOOL=ON \
	-DENABLE_LINKER_BUILD_ID:BOOL=ON \
	-DOCAMLFIND=NOTFOUND \
	-DLLVM_LIBDIR_SUFFIX=$(echo %{_lib} |sed -e 's,^lib,,') \
	-DCLANG_LIBDIR_SUFFIX=$(echo %{_lib} |sed -e 's,^lib,,') \
	-DLLVM_OPTIMIZED_TABLEGEN:BOOL=ON \
%ifarch %{arm}
	-DLLVM_DEFAULT_TARGET_TRIPLE=%{product_arch}-%{_vendor}-%{_os}%{_gnu} \
%endif
	-DPOLLY_ENABLE_GPGPU_CODEGEN:BOOL=ON \
	-DWITH_POLLY:BOOL=ON \
	-DLINK_POLLY_INTO_TOOLS:BOOL=ON \
%if %{with libcxx}
	-DLLVM_ENABLE_LIBCXX:BOOL=ON \
	-DLLVM_ENABLE_LIBCXXABI:BOOL=ON \
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
	-DCMAKE_SHARED_LINKER_FLAGS="-L$(pwd)/%{_lib}" \
	-DCMAKE_EXE_LINKER_FLAGS="-Wl,--disable-new-dtags,-rpath,$(pwd)/%{_lib},-rpath,$(pwd)/lib" \
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
	-G Ninja \
	../llvm

if ! %ninja_build; then
    # With many threads, there's a chance of libc++ being built
    # before libc++abi, causing linkage to fail. Simply trying
    # again "fixes" it.
    %ninja_build
fi

cd ..
%endif

%if %{with compat32}
TOP="$(pwd)"
cat >xc <<EOF
#!/bin/sh
%if %{with bootstrap32}
exec %{_bindir}/clang --rtlib=libgcc --unwindlib=libgcc -m32 "\$@"
%else
exec %{_bindir}/clang -m32 "\$@"
%endif
EOF
gccver="$(i686-openmandriva-linux-gnu-gcc --version |head -n1 |cut -d' ' -f3)"
cat >xc++ <<EOF
#!/bin/sh
%if %{with bootstrap32}
exec %{_bindir}/clang++ --rtlib=libgcc --unwindlib=libgcc -m32 -isystem %{_includedir}/c++/x86_64-openmandriva-linux-gnu/32 "\$@"
%else
exec %{_bindir}/clang++ -m32 -isystem %{_includedir}/c++/${gccver}/x86_64-openmandriva-linux-gnu/32 "\$@"
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
%cmake32 \
	-DCMAKE_TOOLCHAIN_FILE="${TOP}/cmake-i686.toolchain" \
	-DLLVM_CONFIG_PATH=$(pwd)/../build/bin/llvm-config \
	-DLLVM_ENABLE_PROJECTS="llvm;clang;libunwind;compiler-rt;openmp;parallel-libs;polly" \
	-DENABLE_EXPERIMENTAL_NEW_PASS_MANAGER:BOOL=ON \
	-DENABLE_X86_RELAX_RELOCATIONS:BOOL=ON \
%if %{with default_compilerrt}
	-DCLANG_DEFAULT_RTLIB=compiler-rt \
%if ! %{with bootstrap32}
	-DCOMPILER_RT_USE_BUILTINS_LIBRARY:BOOL=ON \
%endif
%else
	-DCLANG_DEFAULT_RTLIB=libgcc \
%endif
	-DBUILD_SHARED_LIBS:BOOL=ON \
	-DLLVM_ENABLE_FFI:BOOL=ON \
	-DLLVM_TARGETS_TO_BUILD=all \
	-DLLVM_ENABLE_CXX1Y:BOOL=ON \
	-DLLVM_ENABLE_RTTI:BOOL=ON \
	-DLLVM_ENABLE_PIC:BOOL=ON \
	-DLLVM_INCLUDE_DOCS:BOOL=ON \
	-DLLVM_ENABLE_EH:BOOL=ON \
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
	-DLLVM_OPTIMIZED_TABLEGEN:BOOL=ON \
	-DLLVM_DEFAULT_TARGET_TRIPLE=i686-%{_vendor}-%{_os}%{_gnu} \
	-DPOLLY_ENABLE_GPGPU_CODEGEN:BOOL=ON \
	-DWITH_POLLY:BOOL=ON \
	-DLINK_POLLY_INTO_TOOLS:BOOL=ON \
%if %{with libcxx}
	-DLLVM_ENABLE_LIBCXX:BOOL=ON \
	-DLLVM_ENABLE_LIBCXXABI:BOOL=ON \
%endif
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
	-DLIBCXX_USE_COMPILER_RT:BOOL=ON \
	-DLIBCXXABI_USE_COMPILER_RT:BOOL=ON \
	-DLIBUNWIND_USE_COMPILER_RT:BOOL=ON \
	-DLLVM_ENABLE_PER_TARGET_RUNTIME:BOOL=ON \
	-DLLVM_HOST_TRIPLE=i686-openmandriva-linux-gnu \
	-DLLVM_TARGET_ARCH=i686 \
	-DLIBCXX_CXX_ABI=libcxxabi \
	-DLIBCXX_ENABLE_CXX1Y:BOOL=ON \
	-DLIBCXXABI_ENABLE_SHARED:BOOL=ON \
	-DLIBCXXABI_ENABLE_STATIC:BOOL=ON \
	-DLIBCXX_ENABLE_SHARED:BOOL=ON \
	-DLIBCXX_ENABLE_STATIC:BOOL=ON \
	-DLIBCXXABI_LIBCXX_INCLUDES=${TOP}/libcxx/include \
	-DLIBCXX_CXX_ABI_INCLUDE_PATHS=${TOP}/libcxxabi/include \
	-DLIBCXXABI_USE_LLVM_UNWINDER:BOOL=ON \
	-G Ninja \
	../llvm
%ninja_build
cd ..
%endif

# Where our just-built compilers can be found...
BINDIR=$(pwd)/build/bin

%if %{without bootstrap}
# libclc integration into the main build seems to be broken
mkdir build-libclc
cd build-libclc
ln -sf %{_bindir}/llvm-spirv ../build/bin
cmake \
	../libclc \
	-G Ninja \
	-DCMAKE_INSTALL_PREFIX=%{_prefix} \
	-DCMAKE_AR=${BINDIR}/llvm-ar \
	-DCMAKE_NM=${BINDIR}/llvm-nm \
	-DCMAKE_RANLIB=${BINDIR}/llvm-ranlib \
	-DLLVM_CONFIG=${BINDIR}/llvm-config \
	-DCMAKE_C_COMPILER=${BINDIR}/clang
%ninja_build
cd ..
%endif

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
		LFLAGS="-O3 --sysroot=/usr/${arch}-openmandriva-linux-${LIBC} --gcc-toolchain=%{_prefix}"
		FLAGS="$LFLAGS -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
		if echo $arch |grep -q riscv; then
			# Workaround of lack of linker relaxation support in lld
			LFLAGS="$LFLAGS -fuse-ld=bfd"
		fi
		cmake \
			../compiler-rt \
			-G Ninja \
			-DCMAKE_CROSSCOMPILING:BOOL=ON \
			-DCMAKE_INSTALL_PREFIX=%{_libdir}/clang/%{version} \
			-DCMAKE_AR=${BINDIR}/llvm-ar \
			-DCMAKE_NM=${BINDIR}/llvm-nm \
			-DCMAKE_RANLIB=${BINDIR}/llvm-ranlib \
%if 0
			-DLLVM_CONFIG_PATH=${BINDIR}/llvm-config \
%endif
			-DCMAKE_ASM_COMPILER_TARGET=${arch}-openmandriva-linux-${LIBC} \
			-DCMAKE_C_COMPILER_TARGET=${arch}-openmandriva-linux-${LIBC} \
			-DCMAKE_CXX_COMPILER_TARGET=${arch}-openmandriva-linux-${LIBC} \
			-DCOMPILER_RT_DEFAULT_TARGET_TRIPLE=${arch}-openmandriva-linux-${LIBC} \
			-DCMAKE_C_COMPILER=${BINDIR}/clang \
			-DCMAKE_CXX_COMPILER=${BINDIR}/clang++ \
			-DCMAKE_ASM_FLAGS="$FLAGS" \
			-DCMAKE_C_FLAGS="$FLAGS" \
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
			-DCOMPILER_RT_DEFAULT_TARGET_ONLY:BOOL=OFF
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
	%{buildroot}%{_prefix}/lib/LLVMgold.so \
	%{buildroot}%{_prefix}/lib/clang \
	%{buildroot}%{_bindir}
%endif

%ninja_install -C build

%if %{without bootstrap}
%ninja_install -C build-libclc
%endif

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

# Nuke the internal copy, we have system python-six
rm -f %{buildroot}%{_libdir}/python*/site-packages/six.py

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

# We get libgomp from gcc, so don't symlink libomp to it
rm -f %{buildroot}%{_libdir}/libgomp.so

# Fix bogus pointers to incorrect locations
%if "%{_lib}" != "lib"
# Weird, but for some reason those files seem to get installed only on x86
if [ -e %{buildroot}%{_prefix}/lib/cmake/clang/ClangTargets-*.cmake ]; then
    sed -i -e "s,/lib/,/%{_lib}/,g" %{buildroot}%{_prefix}/lib/cmake/clang/ClangTargets-*.cmake %{buildroot}%{_prefix}/lib/cmake/llvm/LLVMExports-*.cmake
fi
%endif

%if %{with unwind}
# Add more headers and a pkgconfig file so we can use the llvm
# unwinder instead of the traditional nongnu.org libunwind
cp libunwind/include/libunwind.h libunwind/include/__libunwind_config.h %{buildroot}%{_includedir}/
# And move unwind.h to where gcc can see it as well
mv %{buildroot}%{_libdir}/clang/%{version}/include/unwind.h %{buildroot}%{_includedir}/
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
