# Barfs because of python2 files
%define _python_bytecompile_build 0

%define debug_package %{nil}
%define debugcflags %{nil}
%define build_lto 1
%define _disable_ld_no_undefined 0
%define _disable_lto 1

# clang header paths are hard-coded at compile time
# and need adjustment whenever there's a new GCC version
%define gcc_version %(gcc -dumpversion)

%bcond_without default_compiler

# As of 238820, the "make install" target for apidox
# is broken with cmake. Re-enable later.
%bcond_with apidox
# Note: --with libcxx doesn't mean "build libcxx", but "USE libcxx",
# as in "link llvm libs and clang libs to libcxx rather than libstdc++
# Don't do this if you care about binary compatibility...
%bcond_with libcxx
%bcond_without clang
%ifarch aarch64
# AArch64 doesn't have a working ocaml compiler yet
%bcond_with ocaml
# No graphviz yet either
%bcond_without bootstrap
%else
%bcond_with ocaml
%bcond_with bootstrap
%endif
%bcond_without ffi
# Force gcc to compile, in case previous clang is busted
%ifarch x86_64
%bcond_with bootstrap_gcc
%else
%bcond_without bootstrap_gcc
%endif
%if %{with bootstrap_gcc}
# libcxx fails to bootstrap with gcc
%bcond_with build_libcxx
%else
%bcond_without build_libcxx
%endif
%ifarch %{ix86} aarch64
# lldb uses some atomics that haven't been ported to x86_32 yet
# lldb also fails on aarch64 as of 3.7.0
%bcond_with lldb
%else
# Currently (2016/06/18) fails because of missing
# llvm_regcomp llvm_regfree llvm_regexec
%bcond_with lldb
%endif
%bcond_without openmp
# FIXME Currently llgo fails to build on anything but x86_64,
# and triggers https://sourceware.org/bugzilla/show_bug.cgi?id=17729
# on x86_64
%bcond_with llgo
%bcond_without lld

# Prefer compiler-rt over libgcc
%bcond_with default_compilerrt

# Clang's libLLVMgold.so shouldn't trigger devel(*) dependencies
%define __noautoreq 'devel.*'

%define ompmajor 1
%define ompname %mklibname omp %{ompmajor}

Summary:	Low Level Virtual Machine (LLVM)
Name:		llvm
Version:	6.0.0
Release:	1
License:	NCSA
Group:		Development/Other
Url:		http://llvm.org/
Source0:	http://llvm.org/releases/%{version}/llvm-%{version}.src.tar.xz
Source1:	http://llvm.org/releases/%{version}/cfe-%{version}.src.tar.xz
Source2:	http://llvm.org/releases/%{version}/clang-tools-extra-%{version}.src.tar.xz
Source3:	http://llvm.org/releases/%{version}/polly-%{version}.src.tar.xz
Source4:	http://llvm.org/releases/%{version}/compiler-rt-%{version}.src.tar.xz
Source5:	http://llvm.org/releases/%{version}/libcxx-%{version}.src.tar.xz
Source6:	http://llvm.org/releases/%{version}/libcxxabi-%{version}.src.tar.xz
Source7:	http://llvm.org/releases/%{version}/libunwind-%{version}.src.tar.xz
Source8:	http://llvm.org/releases/%{version}/lldb-%{version}.src.tar.xz
Source9:	http://llvm.org/releases/%{version}/llgo-%{version}.src.tar.xz
Source10:	http://llvm.org/releases/%{version}/lld-%{version}.src.tar.xz
Source11:	http://llvm.org/releases/%{version}/openmp-%{version}.src.tar.xz
Source1000:	llvm.rpmlintrc
# Adjust search paths to match the OS
Patch1:		0000-clang-mandriva.patch
# ARM hardfloat hack
# see http://llvm.org/bugs/show_bug.cgi?id=15557
# and https://bugzilla.redhat.com/show_bug.cgi?id=803433
Patch2:		clang-hardfloat-hack.patch
Patch3:		llvm-3.7.0-PATH_MAX-compile.patch
# https://reviews.llvm.org/D26893
Patch4:		https://reviews.llvm.org/file/data/xict532f6ykwoei2obz3/PHID-FILE-yztwplfdu7fncle5sjk2/D26893.diff
# Patches from AOSP
Patch5:		0001-llvm-Make-EnableGlobalMerge-non-static-so-we-can-modify-i.patch
# End AOSP patch section
Patch6:		llvm-4.0.0-libcxx-libcxxabi-dep.patch
# Claim compatibility with gcc 7.1.1 rather than 4.2.1, it's
# much much closer in terms of standards supported etc.
Patch7:		clang-gcc-compat.patch
# Support -fuse-ld=XXX properly
Patch8:		clang-fuse-ld.patch
Patch9:		ddsan-compile.patch
Patch10:	lldb-3.8.0-compile.patch
Patch11:	llvm-nm-workaround-libstdc++.patch
Patch12:	llvm-3.8.0-sonames.patch
# Silently turn -O9 into -O3 etc. for increased gcc compatibility
Patch13:	llvm-3.8.0-fix-optlevel.patch
# because we have an odd combination (compiler-rt but using libstdc++) we need to add
# the unwind exception handling code which is found in libgcc by linking to libgcc anyway...
Patch14:	llvm-3.8.0-stdc++-unwind-linkage.patch
Patch15:	libunwind-3.8-aarch64-gas.patch
Patch16:	clang-rename-fix-linkage.patch
Patch17:	lld-4.0.0-fix-build-with-libstdc++.patch
# Patches for musl support, (partially) stolen from Alpine Linux and ported
Patch20:	llvm-3.7-musl.patch
Patch21:	llvm-5.0-MuslX32.patch
Patch23:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/compiler-rt-3.6-musl-no-dlvsym.patch
# http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.6-remove-lgcc-when-using-compiler-rt.patch
# breaks exception handling -- removes gcc_eh
Patch29:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.6-fix-unwind-chain-inclusion.patch
Patch31:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.5-fix-stdint.patch
Patch40:	libc++-3.7.0-musl-compat.patch
# https://llvm.org/bugs/show_bug.cgi?id=23935
Patch41:	llvm-3.7-bootstrap.patch
# Make it possible to override CLANG_LIBDIR_SUFFIX
# (that is used only to find LLVMgold.so)
# https://llvm.org/bugs/show_bug.cgi?id=23793
Patch43:	clang-0002-cmake-Make-CLANG_LIBDIR_SUFFIX-overridable.patch
# Fix library versioning
Patch46:	llvm-4.0.1-libomp-versioning.patch
# Fix mcount name for arm and armv8
# https://llvm.org/bugs/show_bug.cgi?id=27248
Patch48:	llvm-3.8.0-mcount-name.patch
Patch49:	llvm-4.0-lldb-static.patch
Patch50:	llvm-4.0-default-compiler-rt.patch
# Show more information when aborting because posix_spawn failed
# (happens in qemu aarch64 chroots)
Patch51:	llvm-4.0.1-debug-posix_spawn.patch
# llgo bits
Patch60:	llgo-4.0rc1-compile-workaround.patch
Patch61:	llgo-4.0rc1-compilerflags-workaround.patch
BuildRequires:	bison
BuildRequires:	binutils-devel
BuildRequires:	chrpath
BuildRequires:	flex
BuildRequires:	pkgconfig(libedit)
%if %{without bootstrap}
BuildRequires:	graphviz
%endif
BuildRequires:	chrpath
BuildRequires:	groff
BuildRequires:	libtool
BuildRequires:	python-sphinx
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
%ifnarch aarch64
BuildRequires:	devel(libatomic)
%endif
BuildRequires:	python >= 3.4
BuildRequires:	cmake
BuildRequires:	ninja
%if %{with apidox}
BuildRequires:	doxygen
%endif
%if %{with llgo}
BuildRequires:	go
%endif
Requires:	libstdc++-devel
Obsoletes:	llvm-ocaml
# For lldb
BuildRequires:	swig
BuildRequires:	pkgconfig(python2)
BuildRequires:	gcc
%if %mdvver > 3000000
%if !%{with lld}
BuildRequires:	lld < %{EVRD}
%endif
%endif
%if %{with openmp}
Requires:	%{ompname} = %{EVRD}
%endif

Obsoletes: %{mklibname LLVMRISCVCodeGen 5} < %{EVRD}
Obsoletes: %{mklibname LLVMRISCVDesc 5} < %{EVRD}
Obsoletes: %{mklibname LLVMRISCVInfo 5} < %{EVRD}
Obsoletes: %{mklibname lldConfig 5} < %{EVRD}

%description
LVM is a robust system, particularly well suited for developing new mid-level
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
%{_bindir}/find-all-symbols
%{_bindir}/git-clang-format
%{_bindir}/llc
%{_bindir}/lli
%{_bindir}/lli-child-target
%{_bindir}/opt
%{_bindir}/llvm-ar
%{_bindir}/llvm-as
%{_bindir}/llvm-bcanalyzer
%{_bindir}/llvm-cat
%{_bindir}/llvm-c-test
%{_bindir}/llvm-cfi-verify
%{_bindir}/llvm-cvtres
%{_bindir}/llvm-cxxfilt
%{_bindir}/llvm-diff
%{_bindir}/llvm-dis
%{_bindir}/llvm-dsymutil
%{_bindir}/llvm-dwp
%{_bindir}/llvm-extract
%{_bindir}/llvm-lib
%{_bindir}/llvm-link
%{_bindir}/llvm-lto
%{_bindir}/llvm-lto2
%{_bindir}/llvm-mc
%{_bindir}/llvm-nm
%{_bindir}/llvm-objdump
%{_bindir}/llvm-objcopy
%{_bindir}/llvm-pdbutil
%{_bindir}/llvm-ranlib
%{_bindir}/llvm-rc
%{_bindir}/llvm-readobj
%{_bindir}/llvm-split
%{_bindir}/llvm-cov
%{_bindir}/llvm-dwarfdump
%{_bindir}/llvm-mcmarkup
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
%{_bindir}/modularize
%{_bindir}/sancov
%{_bindir}/sanstats
%{_bindir}/verify-uselistorder
%{_bindir}/obj2yaml
%{_bindir}/wasm-ld
%{_bindir}/yaml2obj
%{_bindir}/yaml-bench
%{_bindir}/not
# clang static analyzer -- maybe should be a separate package
%{_bindir}/scan-build
%{_bindir}/scan-view
%{_libexecdir}/ccc-analyzer
%{_libexecdir}/c++-analyzer
%{_datadir}/scan-build
%{_datadir}/scan-view
%{_mandir}/man1/FileCheck.1*
%{_mandir}/man1/bugpoint.1*
%{_mandir}/man1/dsymutil.1*
%{_mandir}/man1/lit.1*
%{_mandir}/man1/llc.1*
%{_mandir}/man1/lli.1*
%{_mandir}/man1/llvm-*.1*
%{_mandir}/man1/opt.1*
%{_mandir}/man1/scan-build.1*
%{_mandir}/man1/tblgen.1*

#-----------------------------------------------------------

%define major %(echo %{version} |cut -d. -f1-2)  
%define major1 %(echo %{version} |cut -d. -f1)

%define LLVMLibs LLVMAArch64AsmParser LLVMAArch64AsmPrinter LLVMAArch64CodeGen LLVMAArch64Desc LLVMAArch64Disassembler LLVMAArch64Info LLVMAArch64Utils LLVMARMAsmParser LLVMARMAsmPrinter LLVMARMCodeGen LLVMARMDesc LLVMARMDisassembler LLVMARMInfo LLVMARMUtils LLVMAnalysis LLVMAsmParser LLVMAsmPrinter LLVMBPFAsmParser LLVMBitReader LLVMBitWriter LLVMBPFAsmPrinter LLVMBPFCodeGen LLVMBPFDesc LLVMBPFDisassembler LLVMBPFInfo LLVMBinaryFormat LLVMCodeGen LLVMCore LLVMDebugInfoCodeView LLVMCoroutines LLVMDebugInfoDWARF LLVMDebugInfoMSF LLVMDebugInfoPDB LLVMDemangle LLVMDlltoolDriver LLVMExecutionEngine LLVMFuzzMutate LLVMHexagonAsmParser LLVMHexagonCodeGen LLVMHexagonDesc LLVMHexagonDisassembler LLVMHexagonInfo LLVMIRReader LLVMInstCombine LLVMInstrumentation LLVMInterpreter LLVMLanaiAsmParser LLVMLanaiAsmPrinter LLVMLanaiCodeGen LLVMLanaiDesc LLVMLanaiDisassembler LLVMLanaiInfo LLVMLTO LLVMLibDriver LLVMLineEditor LLVMLinker LLVMMC LLVMMCDisassembler LLVMMCJIT LLVMMCParser LLVMMIRParser LLVMMSP430AsmPrinter LLVMMSP430CodeGen LLVMMSP430Desc LLVMMSP430Info LLVMMipsAsmParser LLVMMipsAsmPrinter LLVMMipsCodeGen LLVMMipsDesc LLVMMipsDisassembler LLVMMipsInfo LLVMNVPTXAsmPrinter LLVMNVPTXCodeGen LLVMNVPTXDesc LLVMNVPTXInfo LLVMObjCARCOpts LLVMObject LLVMOption LLVMOrcJIT LLVMPasses LLVMPowerPCAsmParser LLVMPowerPCAsmPrinter LLVMPowerPCCodeGen LLVMPowerPCDesc LLVMPowerPCDisassembler LLVMPowerPCInfo LLVMProfileData LLVMAMDGPUAsmParser LLVMAMDGPUAsmPrinter LLVMAMDGPUCodeGen LLVMAMDGPUDesc LLVMAMDGPUDisassembler LLVMAMDGPUInfo LLVMAMDGPUUtils LLVMRuntimeDyld LLVMScalarOpts LLVMSelectionDAG LLVMSparcAsmParser LLVMSparcAsmPrinter LLVMSparcCodeGen LLVMSparcDesc LLVMSparcDisassembler LLVMSparcInfo LLVMSupport LLVMSymbolize LLVMSystemZAsmParser LLVMSystemZAsmPrinter LLVMSystemZCodeGen LLVMSystemZDesc LLVMSystemZDisassembler LLVMSystemZInfo LLVMTableGen LLVMTarget LLVMTransformUtils LLVMVectorize LLVMWindowsManifest LLVMX86AsmParser LLVMX86AsmPrinter LLVMX86CodeGen LLVMX86Desc LLVMX86Disassembler LLVMX86Info LLVMX86Utils LLVMXCoreAsmPrinter LLVMXCoreCodeGen LLVMXCoreDesc LLVMXCoreDisassembler LLVMXCoreInfo LLVMXRay LLVMipo LLVMCoverage LLVMGlobalISel LLVMObjectYAML findAllSymbols

%define ClangLibs LTO clang clangARCMigrate clangAST clangASTMatchers clangAnalysis clangApplyReplacements clangBasic clangChangeNamespace clangCodeGen clangCrossTU clangDaemon clangDriver clangDynamicASTMatchers clangEdit clangFormat clangFrontend clangFrontendTool clangHandleCXX clangIncludeFixerPlugin clangIndex clangLex clangMove clangParse clangQuery clangRewrite clangRewriteFrontend clangReorderFields clangSema clangSerialization clangStaticAnalyzerCheckers clangStaticAnalyzerCore clangStaticAnalyzerFrontend clangTidy clangTidyAndroidModule clangTidyBugproneModule clangTidyCERTModule clangTidyCppCoreGuidelinesModule clangTidyFuchsiaModule clangTidyGoogleModule clangTidyHICPPModule clangTidyLLVMModule clangTidyMiscModule clangTidyModernizeModule clangTidyMPIModule clangTidyObjCModule clangTidyReadabilityModule clangTidyPerformanceModule clangTidyUtils clangTooling clangToolingASTDiff clangToolingCore clangToolingRefactor clangIncludeFixer clangTidyBoostModule clangTidyPlugin

%if %{with lld}
%define LLDLibs lldCOFF lldCommon lldCore lldDriver lldELF lldMachO lldMinGW lldReaderWriter lldWasm lldYAML
%else
%define LLDLibs %{nil}
%endif

%{expand:%(for i in %{LLVMLibs} %{ClangLibs} %{LLDLibs}; do echo %%libpackage $i %{major1}; done)}

%define libunwind_major 1.0
%define libunwind %mklibname unwind %{libunwind_major}

%package -n %{libunwind}
Summary: Development files for libunwind
Group: Development/C

%description -n %{libunwind}
The unwind library, a part of llvm.

%files -n %{libunwind}
%doc %{_docdir}/libunwind
%{_libdir}/libunwind.so.%{libunwind_major}
%{_libdir}/libunwind.so.1
%{_libdir}/libunwind.a

#-----------------------------------------------------------
%if %{with build_libcxx}
%libpackage c++ 1
%libpackage c++abi 1
%{_libdir}/libc++abi.so
%{_libdir}/libc++.a
%{_libdir}/libc++experimental.a

%define cxxdevname %mklibname c++ -d
%define cxxabistatic %mklibname c++abi -d -s

%package -n %{cxxdevname}
Summary: Development files for libc++, an alternative implementation of the STL
Group: Development/C
Requires: %{mklibname c++ 1} = %{EVRD}
Requires: %{mklibname c++abi 1} = %{EVRD}
Provides: c++-devel = %{EVRD}

%description -n %{cxxdevname}
Development files for libc++, an alternative implementation of the STL.

%files -n %{cxxdevname}
%doc %{_docdir}/libcxx
%{_includedir}/c++

%package -n %{cxxabistatic}
Summary: Static library for libc++ C++ ABI support
Group: Development/C
Requires: %{cxxdevname} = %{EVRD}

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
%{expand:%(for i in %{LLVMLibs}; do echo Requires:	%%{mklibname $i %{major1}} = %{EVRD}; done)}
Obsoletes:	%{mklibname LLVMCppBackendCodeGen 3} < %{EVRD}
Obsoletes:	%{mklibname LLVMCppBackendInfo 3} < %{EVRD}

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
Conflicts:	llvm < 3.0-7
Conflicts:	%{_lib}llvm3.0 < 3.0-9
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
%{_libdir}/BugpointPasses.so
%{_libdir}/cmake/%{name}
%{_libdir}/lib*.so
%if %{with openmp}
%exclude %{_libdir}/libomp.so
%endif
%if %{with build_libcxx}
%exclude %{_libdir}/libc++abi.so
%endif
# Stuff from clang
%exclude %{_libdir}/libclang*.so
%if %{with llgo}
%exclude %{_libdir}/libgo-llgo.so
%endif
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
%{_libdir}/libomp.so*
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
%doc README.txt
%doc docs/tutorial
%doc examples
%doc %{_docdir}/llvm
%if %{with apidox}
%doc docs/doxygen
%endif

#-----------------------------------------------------------
%package polly
Summary: Polyhedral optimizations for LLVM
License: MIT
Group: Development/Other
Obsoletes: llvm-devel < 4.0.1
Obsoletes: %{_lib}llvm-devel < 4.0.1
Conflicts: %{_lib}llvm-devel < 4.0.1

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
%{_bindir}/pollycc
%{_bindir}/pollyc++
%{_libdir}/LLVMPolly.so
# Unversioned library, not -devel file
%{_libdir}/libPolly.so
%{_libdir}/libPollyISL.so
%{_libdir}/libPollyPPCG.so
%{_mandir}/man1/polly.1*

#-----------------------------------------------------------
%package polly-devel
Summary: Development files for Polly
License: MIT
Group: Development/Other
Requires: %{name}-polly = %{EVRD}

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
Requires:	%{_lib}unwind1.0 = %{EVRD}
Obsoletes:	%{mklibname clang 3.7.0}
%{expand:%(for i in %{ClangLibs}; do echo Requires:	%%{mklibname $i %{major1}} = %{EVRD}; done)}

%description -n clang
clang: noun
    1. A loud, resonant, metallic sound.
    2. The strident call of a crane or goose.
    3. C-language family front-end toolkit.

The goal of the Clang project is to create a new C, C++, Objective C
and Objective C++ front-end for the LLVM compiler. Its tools are built
as libraries and designed to be loosely-coupled and extensible.

%files -n clang
%{_bindir}/clang*
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
%{_mandir}/man1/extraclangtools.1*

#-----------------------------------------------------------

%define devclang %mklibname -d clang

%package -n %{devclang}
Summary:	Development files for clang
Group:		Development/Other
Requires:	clang = %{EVRD}
Provides:	clang-devel = %{EVRD}
Conflicts:	llvm-devel < 3.1
Obsoletes:	clang-devel < 3.1

%description -n %{devclang}
This package contains header files and libraries needed for using
libclang.

%files -n %{devclang}
%{_includedir}/clang
%{_includedir}/clang-c
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

%if %{with lldb}
%define oldlib %mklibname lldb %{major}

%package -n lldb
Summary:	Debugger from the LLVM toolchain
Group:		Development/Other
Obsoletes:	%{oldlib} < %{EVRD}

%description -n lldb
Debugger from the LLVM toolchain.

%files -n lldb
%{_bindir}/lldb*
# FIXME weird place for a plugin...
%{_bindir}/liblldb-intel-mpxtable.so
%{_libdir}/python*/site-packages/lldb
%{_libdir}/python*/site-packages/readline.so
%{_libdir}/python*/site-packages/six.py

%define lldbdev %mklibname -d lldb

%package -n %{lldbdev}
Summary:	Development files for the LLDB debugger
Group:		Development/Other
Requires:	lldb = %{EVRD}

%description -n %{lldbdev}
Development files for the LLDB debugger.

%files -n %{lldbdev}
%{_includedir}/lldb
%{_libdir}/liblldb*.a
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
%{_bindir}/lld
%{_bindir}/lld-link
%{_bindir}/llvm-dlltool
%{_bindir}/llvm-readelf
%{_bindir}/llvm-mt

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
#{_libdir}/liblld*.so
%endif
#-----------------------------------------------------------

%if %{with llgo}
%package -n llgo
Summary:	LLVM based implementation of the Go language
Group:		Development/Other

%description -n llgo
LLVM based implementation of the Go language.

%files -n llgo
%{_bindir}/llgo
%{_bindir}/llgo-go
%{_bindir}/llgoi
%{_libdir}/libgo-llgo.so*
%{_libdir}/libgo-llgo.a
%{_libdir}/libgobegin-llgo.a
%{_libdir}/go/llgo-%{version}*
%endif

#-----------------------------------------------------------

%prep
%setup -q %{?with_clang:-a1 -a2 -a3 -a4} %{?with_build_libcxx:-a5} %{?with_build_libcxx:-a6} -a7 %{?with_lldb:-a8} %{?with_llgo:-a9} %{?with_lld:-a10} %{?with_openmp:-a11} -n %{name}-%{version}.src
rm -rf tools/clang
%if %{with clang}
mv cfe-%{version}%{?prerel}.src tools/clang
mv polly-%{version}%{?prerel}.src tools/polly
mv clang-tools-extra-%{version}%{?prerel}.src tools/clang/tools/extra
mv compiler-rt-%{version}%{?prerel}.src projects/compiler-rt
mv libunwind-%{version}%{?prerel}.src projects/libunwind
%if %{with lldb}
mv lldb-%{version}%{?prerel}.src tools/lldb
%endif
%if %{with llgo}
mv llgo-%{version}%{?prerel}.src tools/llgo
%endif
%if %{with lld}
mv lld-%{version}%{?prerel}.src tools/lld
%endif
%if %{with openmp}
mv openmp-%{version}%{?prerel}.src projects/openmp
%endif
cd tools/clang
%patch1 -p1 -b .mandriva~
#patch4 -p3 -b .templateFix~
%patch8 -p1 -b .fuseLd~
cd -
%patch2 -p1 -b .armhf~
%patch3 -p1 -b .compile~
%patch5 -p1 -b .EnableGlobalMerge~
%endif
if [ -d libcxx-%{version}%{?prerel}.src ]; then
	mv libcxx-%{version}%{?prerel}.src projects/libcxx
	cd projects/libcxx
%patch40 -p3 -b .libcxxmusl~
	cd ../..
%patch6 -p1 -b .libcxxabi~
fi
[ -d libcxxabi-%{version}%{?prerel}.src ] && mv libcxxabi-%{version}%{?prerel}.src projects/libcxxabi
%patch7 -p1 -b .gcc71~
%patch9 -p1 -b .ddsan~
%if %{with lldb}
%patch10 -p1 -b .lldb~
%endif
%patch11 -p1 -b .libstdc++~
%patch12 -p1 -b .soname~
%patch13 -p1 -b .fixOptlevel~
%patch14 -p1 -b .unwindlibstdc~
%patch15 -p1 -b .unwindaarch64~
%patch16 -p1 -b .clangRenameLink~
%if %{with lldb}
# LLVM bug 30887
%patch49 -p1 -b .lldbstatic~
%endif
%if %{with lld}
%patch17 -p1 -b .lldcompile~
%endif

%patch20 -p1 -b .musl1~
%patch21 -p1 -b .musl2~

%patch23 -p1 -b .musl4~
%patch29 -p1 -b .musl10~
%patch31 -p1 -b .musl12~

%if %{cross_compiling}
# This is only needed when crosscompiling glibc to musl or the likes
%patch41 -p1 -b .bootstrap~
%endif

%patch46 -p1 -b .soname~

%patch48 -p1 -b .mcount~
%if %{with default_compilerrt}
%patch50 -p1 -b .compilerrt~
%endif
%patch51 -p1 -b .posix_spawn~

%if %{with llgo}
%patch60 -p1 -b .llgoCompile~
%patch61 -p1 -b .llgoCompilerFlags~
%endif

# Fix bogus permissions
find . -type d |while read r; do chmod 0755 "$r"; done

%build
%if %{with bootstrap_gcc}
export CC=gcc
export CXX=g++
%endif
TOP=$(pwd)

# Workaround for previous build having a problem with debug info
# generation
#export CFLAGS="%{optflags} -g0"
#export CXXFLAGS="%{optflags} -g0"

# Currently broken, but potentially interesting:
#	-DLLVM_ENABLE_MODULES:BOOL=ON

# compiler-rt assumes off_t is 64 bits -- make sure this is true even on 32 bit
# OSes
%ifarch %ix86
# compiler-rt doesn't support ix86 with x<6 either
export CFLAGS="%{optflags} -march=i686 -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
export CXXFLAGS="%{optflags} -march=i686 -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
%endif
%ifarch %armx sparc mips
export CFLAGS="%{optflags} -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
export CXXFLAGS="%{optflags} -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
%endif

%ifarch aarch64
# Workaround for
# /usr/bin/aarch64-mandriva-linux-gnu-ld: internal error in relocate_tls, at ../../gold/aarch64.cc:7419
# collect2: error: ld returned 1 exit status
# while linking lli built with gcc, last verified with gold 2.27
export CFLAGS="$CFLAGS -fuse-ld=bfd"
export CXXFLAGS="$CXXFLAGS -fuse-ld=bfd"
export LDFLAGS="$LDFLAGS -fuse-ld=bfd"
%endif

if echo %{_target_platform} | grep -q musl; then
	sed -i -e 's,set(COMPILER_RT_HAS_SANITIZER_COMMON TRUE),set(COMPILER_RT_HAS_SANITIZER_COMMON FALSE),' projects/compiler-rt/cmake/config-ix.cmake
fi

%ifarch %ix86
# Fix noexecstack
for i in projects/compiler-rt/lib/builtins/i386/*.S; do
	cat >>$i <<'EOF'
#if defined(__linux__) && defined(__ELF__)
.section .note.GNU-stack,"",%progbits
#endif
EOF
done
%endif

# We set an RPATH in CMAKE_EXE_LINKER_FLAGS to make sure the newly built
# clang and friends use the just-built shared libraries -- there's no guarantee
# that the ABI remains compatible between a snapshot libclang.so.3.8 and the
# final libclang.so.3.8 at the moment.
# We strip out the rpath in %%install though - so we aren't really being evil.
%cmake \
	-DBUILD_SHARED_LIBS:BOOL=ON \
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
	-DLLVM_BUILD_RUNTIME:BOOL=ON \
	-DLLVM_TOOL_COMPILER_RT_BUILD:BOOL=ON \
	-DENABLE_LINKER_BUILD_ID:BOOL=ON \
	-DOCAMLFIND=NOTFOUND \
	-DLLVM_LIBDIR_SUFFIX=$(echo %{_lib} |sed -e 's,^lib,,') \
	-DCLANG_LIBDIR_SUFFIX=$(echo %{_lib} |sed -e 's,^lib,,') \
	-DLLVM_OPTIMIZED_TABLEGEN:BOOL=ON \
%ifarch %arm
	-DLLVM_DEFAULT_TARGET_TRIPLE=%{product_arch}-%{_build_vendor}-%{_os}%{_build_gnu} \
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
	-DLIBCXXABI_LIBCXX_INCLUDES=${TOP}/projects/libcxx/include \
	-DLIBCXX_CXX_ABI_INCLUDE_PATHS=${TOP}/projects/libcxxabi/include \
	-DLIBCXXABI_LIBDIR_SUFFIX="$(echo %{_lib} | sed -e 's,^lib,,')" \
	-DLIBCXX_LIBDIR_SUFFIX="$(echo %{_lib} | sed -e 's,^lib,,')" \
	-DCMAKE_SHARED_LINKER_FLAGS="-L`pwd`/%{_lib}" \
	-DCMAKE_EXE_LINKER_FLAGS="-Wl,--disable-new-dtags,-rpath,`pwd`/%{_lib}" \
%if %{with apidox}
	-DLLVM_ENABLE_DOXYGEN:BOOL=ON \
%endif
%if %{cross_compiling}
	-DCMAKE_CROSSCOMPILING=True \
	-DLLVM_TABLEGEN=%{_bindir}/llvm-tblgen \
	-DCLANG_TABLEGEN=%{_bindir}/clang-tblgen \
	-DLLVM_DEFAULT_TARGET_TRIPLE=%{_target_platform} \
%endif
%ifnarch armv7hl
	-DLIBCXXABI_USE_LLVM_UNWINDER:BOOL=ON \
%endif
	-G Ninja

%ninja_build

%install
%if %{with ocaml}
#cp bindings/ocaml/llvm/META.llvm bindings/ocaml/llvm/Release/
%endif

%ninja_install -C build

# Polly bits as described on
# http://polly.llvm.org/example_load_Polly_into_clang.html
cat >%{buildroot}%{_bindir}/pollycc <<'EOF'
#!/bin/sh
exec %{_bindir}/clang -O3 -Xclang -load -Xclang %{_libdir}/LLVMPolly.so "$@"
EOF

cat >%{buildroot}%{_bindir}/pollyc++ <<'EOF'
#!/bin/sh
exec %{_bindir}/clang++ -O3 -Xclang -load -Xclang %{_libdir}/LLVMPolly.so "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/pollycc %{buildroot}%{_bindir}/pollyc++

%if %{with default_compiler}
ln -s clang %{buildroot}%{_bindir}/cc
ln -s clang++ %{buildroot}%{_bindir}/c++
cat >%{buildroot}%{_bindir}/c89 <<'EOF'
#!/bin/sh

fl="-std=c89"
for opt; do
	case "$opt" in
		-ansi|-std=c89|-std=iso9899:1990) fl="";;
		-std=*) echo "`basename $0` called with non ANSI/ISO C option $opt" >&2
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
		-std=*) echo "`basename $0` called with non ISO C99 option $opt" >&2
			exit 1;;
	esac
done
exec %{_bindir}/clang $fl ${1+"$@"}
EOF
chmod 0755 %{buildroot}%{_bindir}/c89 %{buildroot}%{_bindir}/c99
%endif

# Code sample -- binary not needed
rm %{buildroot}%{_libdir}/LLVMHello.so

# Don't look for stuff we just deleted...
sed -i -e 's,gtest gtest_main ,,;s, LLVMHello , ,' -e '/LLVMHello/d' -e '/gtest/d' %{buildroot}%{_libdir}/cmake/llvm/LLVMExports.cmake
sed -i -e '/gtest/ { N;d }' -e '/LLVMHello/ { N;d }' %{buildroot}%{_libdir}/cmake/llvm/LLVMExports-release.cmake

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

# (tpg) fix bug https://issues.openmandriva.org/show_bug.cgi?id=2214
mv %{buildroot}%{_libdir}/libunwind.so %{buildroot}%{_libdir}/libunwind-llvm.so
