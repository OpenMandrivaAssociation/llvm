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
%ifarch aarch64
%bcond_without bootstrap_gcc
# Temporary workaround for existing clang not working
%define cross_compiling 0
%else
%bcond_with bootstrap_gcc
%endif
%ifarch %{ix86} aarch64
# lldb uses some atomics that haven't been ported to x86_32 yet
# lldb also fails on aarch64 as of 3.7.0
%bcond_with lldb
%else
%bcond_without lldb
%endif

Summary:	Low Level Virtual Machine (LLVM)
Name:		llvm
Version:	3.7.0
Release:	1.1
License:	NCSA
Group:		Development/Other
Url:		http://llvm.org/
# There's a branch of LLVM maintained at
# git://people.freedesktop.org/~tstellar/llvm
# Ir is the working branch of the AMDGPU/R600 backend needed by Mesa (and is otherwise
# more or less identical to upstream llvm).
# At times it may be necessary to package this branch instead.
Source0:	http://llvm.org/releases/%{version}/llvm-%{version}.src.tar.xz
Source1:	http://llvm.org/releases/%{version}/cfe-%{version}.src.tar.xz
Source2:	http://llvm.org/releases/%{version}/clang-tools-extra-%{version}.src.tar.xz
Source3:	http://llvm.org/releases/%{version}/polly-%{version}.src.tar.xz
Source4:	http://llvm.org/releases/%{version}/compiler-rt-%{version}.src.tar.xz
Source5:	http://llvm.org/releases/%{version}/libcxx-%{version}.src.tar.xz
Source6:	http://llvm.org/releases/%{version}/libcxxabi-%{version}.src.tar.xz
Source7:	http://llvm.org/releases/%{version}/libunwind-%{version}.src.tar.xz
Source8:	http://llvm.org/releases/%{version}/lldb-%{version}.src.tar.xz
Source1000:	llvm.rpmlintrc
# Versionize libclang.so (Anssi 08/2012):
Patch0:		clang-soname.patch
# Adjust search paths to match the OS
Patch1:		0000-clang-mandriva.patch
# ARM hardfloat hack
# see http://llvm.org/bugs/show_bug.cgi?id=15557
# and https://bugzilla.redhat.com/show_bug.cgi?id=803433
Patch2:		clang-hardfloat-hack.patch
Patch3:		llvm-3.7.0-PATH_MAX-compile.patch
# Claim compatibility with gcc 4.9.1 rather than 4.2.1, it's
# much much closer in terms of standards supported etc.
Patch7:		clang-gcc-compat.patch
# Support -fuse-ld=XXX properly
Patch8:		clang-fuse-ld.patch
# Patches from AOSP
Patch4:		0000-llvm-Add-support-for-64-bit-longs.patch
Patch5:		0001-llvm-Make-EnableGlobalMerge-non-static-so-we-can-modify-i.patch
# End AOSP patch section
Patch6:		llvm-3.5-detect-hardfloat.patch
Patch9:		ddsan-compile.patch
Patch10:	polly-adapt-to-API-changes.patch
Patch11:	llvm-nm-workaround-libstdc++.patch
# Patches for musl support, (partially) stolen from Alpine Linux and ported
Patch20:	llvm-3.7-musl.patch
Patch21:	llvm-3.7-musl-triple.patch
Patch22:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/compiler-rt-sanitizer-off_t.patch
Patch23:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/compiler-rt-3.6-musl-no-dlvsym.patch
# http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.6-remove-lgcc-when-using-compiler-rt.patch
# breaks exception handling -- removes gcc_eh
Patch26:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.6-musl-use-init-array.patch
Patch27:	clang-3.7-musl-fix-dynamic-linker-paths.patch
Patch29:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.6-fix-unwind-chain-inclusion.patch
Patch30:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.6-default-runtime-compiler-rt.patch
Patch31:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.5-fix-stdint.patch
Patch40:	libc++-3.7.0-musl-compat.patch
# https://llvm.org/bugs/show_bug.cgi?id=23935
Patch41:	llvm-3.7-bootstrap.patch
# https://llvm.org/bugs/show_bug.cgi?id=12587
# https://code.google.com/p/chromium/issues/detail?id=496370
Patch42:	r-switch.patch
# Make it possible to override CLANG_LIBDIR_SUFFIX
# (that is used only to find LLVMgold.so)
# https://llvm.org/bugs/show_bug.cgi?id=23793
Patch43:	clang-0002-cmake-Make-CLANG_LIBDIR_SUFFIX-overridable.patch
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
BuildRequires:	python >= 3.4
BuildRequires:	cmake
BuildRequires:	ninja
%if %{with apidox}
BuildRequires:	doxygen
%endif
Requires:	libstdc++-devel
Obsoletes:	llvm-ocaml
# For lldb
BuildRequires:	swig
BuildRequires:	pkgconfig(python2)

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
%{_bindir}/git-clang-format
%{_bindir}/llc
%{_bindir}/lli
%{_bindir}/opt
%{_bindir}/llvm-ar
%{_bindir}/llvm-as
%{_bindir}/llvm-bcanalyzer
%{_bindir}/llvm-c-test
%{_bindir}/llvm-diff
%{_bindir}/llvm-dis
%{_bindir}/llvm-dsymutil
%{_bindir}/llvm-extract
%{_bindir}/llvm-lib
%{_bindir}/llvm-link
%{_bindir}/llvm-lto
%{_bindir}/llvm-mc
%{_bindir}/llvm-nm
%{_bindir}/llvm-objdump
%{_bindir}/llvm-ranlib
%{_bindir}/llvm-readobj
%{_bindir}/llvm-cov
%{_bindir}/llvm-dwarfdump
%{_bindir}/llvm-mcmarkup
%{_bindir}/llvm-PerfectShuffle
%{_bindir}/llvm-profdata
%{_bindir}/llvm-rtdyld
%{_bindir}/llvm-size
%{_bindir}/llvm-stress
%{_bindir}/llvm-symbolizer
%{_bindir}/llvm-tblgen
%{_bindir}/llvm-cxxdump
%{_bindir}/llvm-pdbdump
%{_bindir}/verify-uselistorder
%{_bindir}/obj2yaml
%{_bindir}/yaml2obj
%{_bindir}/yaml-bench
%{_bindir}/macho-dump
%{_bindir}/not

#-----------------------------------------------------------

%define major %(echo %{version} |cut -d. -f1-2)  
%define major1 %(echo %{version} |cut -d. -f1)

%define LLVMLibs LLVMAArch64AsmParser LLVMAArch64AsmPrinter LLVMAArch64CodeGen LLVMAArch64Desc LLVMAArch64Disassembler LLVMAArch64Info LLVMAArch64Utils LLVMARMAsmParser LLVMARMAsmPrinter LLVMARMCodeGen LLVMARMDesc LLVMARMDisassembler LLVMARMInfo LLVMAnalysis LLVMAsmParser LLVMAsmPrinter LLVMBitReader LLVMBitWriter LLVMBPFAsmPrinter LLVMBPFCodeGen LLVMBPFDesc LLVMBPFInfo LLVMCodeGen LLVMCore LLVMCppBackendCodeGen LLVMCppBackendInfo LLVMDebugInfoDWARF LLVMDebugInfoPDB LLVMExecutionEngine LLVMHexagonCodeGen LLVMHexagonDesc LLVMHexagonDisassembler LLVMHexagonInfo LLVMIRReader LLVMInstCombine LLVMInstrumentation LLVMInterpreter LLVMLTO LLVMLibDriver LLVMLineEditor LLVMLinker LLVMMC LLVMMCDisassembler LLVMMCJIT LLVMMCParser LLVMMIRParser LLVMMSP430AsmPrinter LLVMMSP430CodeGen LLVMMSP430Desc LLVMMSP430Info LLVMMipsAsmParser LLVMMipsAsmPrinter LLVMMipsCodeGen LLVMMipsDesc LLVMMipsDisassembler LLVMMipsInfo LLVMNVPTXAsmPrinter LLVMNVPTXCodeGen LLVMNVPTXDesc LLVMNVPTXInfo LLVMObjCARCOpts LLVMObject LLVMOption LLVMOrcJIT LLVMPasses LLVMPowerPCAsmParser LLVMPowerPCAsmPrinter LLVMPowerPCCodeGen LLVMPowerPCDesc LLVMPowerPCDisassembler LLVMPowerPCInfo LLVMProfileData LLVMAMDGPUAsmParser LLVMAMDGPUAsmPrinter LLVMAMDGPUCodeGen LLVMAMDGPUDesc LLVMAMDGPUInfo LLVMAMDGPUUtils LLVMRuntimeDyld LLVMScalarOpts LLVMSelectionDAG LLVMSparcAsmParser LLVMSparcAsmPrinter LLVMSparcCodeGen LLVMSparcDesc LLVMSparcDisassembler LLVMSparcInfo LLVMSupport LLVMSystemZAsmParser LLVMSystemZAsmPrinter LLVMSystemZCodeGen LLVMSystemZDesc LLVMSystemZDisassembler LLVMSystemZInfo LLVMTableGen LLVMTarget LLVMTransformUtils LLVMVectorize LLVMX86AsmParser LLVMX86AsmPrinter LLVMX86CodeGen LLVMX86Desc LLVMX86Disassembler LLVMX86Info LLVMX86Utils LLVMXCoreAsmPrinter LLVMXCoreCodeGen LLVMXCoreDesc LLVMXCoreDisassembler LLVMXCoreInfo LLVMipa LLVMipo

%define ClangLibs LTO clang clangARCMigrate clangAST clangASTMatchers clangAnalysis clangApplyReplacements clangBasic clangCodeGen clangDriver clangDynamicASTMatchers clangEdit clangFormat clangFrontend clangFrontendTool clangIndex clangLex clangParse clangQuery clangRename clangRewrite clangRewriteFrontend clangSema clangSerialization clangStaticAnalyzerCheckers clangStaticAnalyzerCore clangStaticAnalyzerFrontend clangTidy clangTidyGoogleModule clangTidyLLVMModule clangTidyMiscModule clangTidyReadabilityModule clangTidyUtils clangTooling clangToolingCore

%{expand:%(for i in %{LLVMLibs} %{ClangLibs}; do echo %%libpackage $i %{major1}; done)}
%libpackage modernizeCore %{major1}

%libpackage unwind 1.0
%{_libdir}/libunwind.so.1

#-----------------------------------------------------------
%libpackage c++ 1
%libpackage c++abi 1

%define cxxdevname %mklibname c++ -d
%define cxxabistatic %mklibname c++abi -d -s

%package -n %{cxxdevname}
Summary: Development files for libc++, an alternative implementation of the STL
Group: Development/C
Requires: %{mklibname c++ 1} = %{EVRD}
Requires: %{mklibname c++abi 1} = %{EVRD}
Provides: c++-devel = %{EVRD}

%description -n %{cxxdevname}
Development files for libc++, an alternative implementation of the STL

%files -n %{cxxdevname}
%{_includedir}/c++

%package -n %{cxxabistatic}
Summary: Static library for libc++ C++ ABI support
Group: Development/C
Requires: %{cxxdevname} = %{EVRD}

%description -n %{cxxabistatic}
Static library for libc++'s C++ ABI library

%files -n %{cxxabistatic}
%{_libdir}/libc++abi.a

#-----------------------------------------------------------
%define libname %mklibname %{name} %{major}

%package -n %{libname}
Summary:	LLVM shared libraries
Group:		System/Libraries
Conflicts:	llvm < 3.0-4
Obsoletes:	%{mklibname %{name} 3.5.0}
Obsoletes:	%{mklibname %{name} 3.6.0}
%{expand:%(for i in %{LLVMLibs}; do echo Requires:	%%{mklibname $i %{major1}} = %{EVRD}; done)}

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
Conflicts:	llvm < 3.0-7
Conflicts:	%{_lib}llvm3.0 < 3.0-9

%description -n %{devname}
This package contains the development files for LLVM;

%files -n %{devname}
%{_bindir}/%{name}-config
%{_libdir}/lib*.so
# Stuff from clang
%exclude %{_libdir}/libclang*.so
%exclude %{_libdir}/libLTO.so
%{_includedir}/%{name}
%{_includedir}/%{name}-c
%{_libdir}/BugpointPasses.so
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/cmake

#-----------------------------------------------------------

%package doc
Summary:	Documentation for LLVM
Group:		Books/Computer books
Requires:	%{name} = %{version}
BuildArch:	noarch
Obsoletes:	llvm-doc-devel

%description doc
Documentation for the LLVM compiler infrastructure.

%files doc
%doc README.txt
%doc docs/*.html
%doc docs/tutorial
%doc examples
%if %{with apidox}
%doc docs/doxygen
%endif

#-----------------------------------------------------------
%package polly
Summary: Polyhedral optimizations for LLVM
License: MIT
Group: Development/Other

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

#-----------------------------------------------------------
%package polly-devel
Summary: Development files for Polly
License: MIT
Group: Development/Other

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
%{_includedir}/polly
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


%package -n clang-doc
Summary:	Documentation for Clang
Group:		Books/Computer books
BuildArch:	noarch
Requires:	%{name} = %{EVRD}

%description -n clang-doc
Documentation for the Clang compiler front-end.

%files -n clang-doc

%endif

%if %{with ocaml}
%package -n ocaml-%{name}
Summary:	Objective-CAML bindings for LLVM
Group:		Development/Other
Requires:	%{name} = %{EVRD}

%description -n ocaml-%{name}
Objective-CAML bindings for LLVM

%files -n ocaml-%{name}
%{_libdir}/ocaml/*
%endif
#-----------------------------------------------------------

%if %{with lldb}
%libpackage lldb %{major}

%package -n lldb
Summary:	Debugger from the LLVM toolchain
Group:		Development/Tools

%description -n lldb
Debugger from the LLVM toolchain

%files -n lldb
%{_bindir}/argdumper
%{_bindir}/lldb*
%{_libdir}/python*/site-packages/lldb
%{_libdir}/python*/site-packages/readline.so

%define lldbdev %mklibname -d lldb

%package -n %{lldbdev}
Summary:	Development files for the LLDB debugger
Group:		Development/Tools
Requires:	lldb = %{EVRD}

%description -n %{lldbdev}
Development files for the LLDB debugger

%files -n %{lldbdev}
%{_includedir}/lldb
%{_libdir}/liblldb*.a
%endif
#-----------------------------------------------------------

%prep
%setup -q %{?with_clang:-a1 -a2 -a3 -a4} -a5 -a6 -a7 %{?with_lldb:-a8} -n %{name}-%{version}.src
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
cd tools/clang
%patch0 -p0 -b .soname~
%patch1 -p1 -b .mandriva~
%patch8 -p1 -b .fuseLd~
cd -
%patch2 -p1 -b .armhf~
%patch3 -p1 -b .compile~
%patch4 -p1 -b .64bitLongs~
%patch5 -p1 -b .EnableGlobalMerge~
%endif
if [ -d libcxx-%{version}%{?prerel}.src ]; then
	mv libcxx-%{version}%{?prerel}.src projects/libcxx
	cd projects/libcxx
%patch40 -p1 -b .libcxxmusl~
	cd ../..
fi
[ -d libcxxabi-%{version}%{?prerel}.src ] && mv libcxxabi-%{version}%{?prerel}.src projects/libcxxabi
%patch6 -p1 -b .detectHardfloat~
%patch7 -p1 -b .gcc49~
%patch9 -p1 -b .ddsan~
%patch10 -p1 -b .polly~
%patch11 -p1 -b .libstdc++~

%patch20 -p1 -b .musl1~
%patch21 -p1 -b .musl2~
%patch22 -p1 -b .musl3~
%patch23 -p1 -b .musl4~
%patch26 -p1 -b .musl7~
%patch27 -p1 -b .musl8~
%patch29 -p1 -b .musl10~
%ifnarch aarch64
# AArch64 isn't supported by compiler-rt yet
%patch30 -p1 -b .musl11~
%endif
%patch31 -p1 -b .musl12~

%if %{cross_compiling}
# This is only needed when crosscompiling glibc to musl or the likes
%patch41 -p1 -b .bootstrap~
%endif
%patch42 -p1 -b .reloc~

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

if echo %{_target_platform} | grep -q musl; then
	sed -i -e 's,set(COMPILER_RT_HAS_SANITIZER_COMMON TRUE),set(COMPILER_RT_HAS_SANITIZER_COMMON FALSE),' projects/compiler-rt/cmake/config-ix.cmake
fi

# We set an RPATH in CMAKE_EXE_LINKER_FLAGS to make sure the newly built
# clang and friends use the just-built shared libraries -- there's no guarantee
# that the ABI remains compatible between a snapshot libclang.so.3.7 and the
# final libclang.so.3.7 at the moment.
# We strip out the rpath in %%install though - so we aren't really being evil.
%cmake \
	-DBUILD_SHARED_LIBS:BOOL=ON \
%if %{with ffi}
	-DLLVM_ENABLE_FFI:BOOL=ON \
%else
	-DLLVM_ENABLE_FFI:BOOL=OFF \
%endif
	-DLLVM_TARGETS_TO_BUILD=all \
	-DLLVM_ENABLE_CXX1Y:BOOL=ON \
	-DLLVM_ENABLE_RTTI:BOOL=ON \
	-DLLVM_ENABLE_PIC:BOOL=ON \
	-DLLVM_INCLUDE_DOCS:BOOL=ON \
	-DLLVM_ENABLE_EH:BOOL=ON \
	-DLLVM_INSTALL_UTILS:BOOL=ON \
	-DLLVM_BINUTILS_INCDIR=%{_includedir} \
	-DLLVM_BUILD_DOCS:BOOL=ON \
	-DOCAMLFIND=NOTFOUND \
	-DLLVM_LIBDIR_SUFFIX=$(echo %{_lib} |sed -e 's,^lib,,') \
	-DCLANG_LIBDIR_SUFFIX=$(echo %{_lib} |sed -e 's,^lib,,') \
	-DLLVM_OPTIMIZED_TABLEGEN:BOOL=ON \
%ifarch %arm
	-DLLVM_DEFAULT_TARGET_TRIPLE=%{__arch}-%{_build_vendor}-%{_os}%{_build_gnu} \
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
%ifarch %{arm}
	-DLIBCXXABI_USE_LLVM_UNWINDER:BOOL=ON \
%endif
	-G Ninja

ninja

%install
%if %{with ocaml}
#cp bindings/ocaml/llvm/META.llvm bindings/ocaml/llvm/Release/
%endif
DESTDIR="%{buildroot}" ninja install -C build

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

%if "%{_lib}" != "lib"
# Buggy make install for Polly
mv %{buildroot}%{_prefix}/lib/*.so* %{buildroot}%{_libdir}/

sed -i -e 's,/lib/,/%{_lib}/,g' %{buildroot}%{_datadir}/llvm/cmake/LLVMExports-release.cmake
%endif

# Code sample -- binary not needed
rm %{buildroot}%{_libdir}/LLVMHello.so

# Don't look for stuff we just deleted...
sed -i -e 's,gtest gtest_main ,,;s, LLVMHello , ,' -e '/LLVMHello/d' -e '/gtest/d' %{buildroot}%{_datadir}/llvm/cmake/LLVMExports.cmake
sed -i -e '/gtest/ { N;d }' -e '/LLVMHello/ { N;d }' %{buildroot}%{_datadir}/llvm/cmake/LLVMExports-release.cmake

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
