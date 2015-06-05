%define debug_package %{nil}
%define _disable_ld_no_undefined 0

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

Summary:	Low Level Virtual Machine (LLVM)
Name:		llvm
Version:	3.7.0
Release:	0.239129.1
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
Source1000:	llvm.rpmlintrc
# Versionize libclang.so (Anssi 08/2012):
Patch0:		clang-soname.patch
# Adjust search paths to match the OS
Patch1:		0000-clang-mandriva.patch
# ARM hardfloat hack
# see http://llvm.org/bugs/show_bug.cgi?id=15557
# and https://bugzilla.redhat.com/show_bug.cgi?id=803433
Patch2:		clang-hardfloat-hack.patch
# Claim compatibility with gcc 4.9.1 rather than 4.2.1, it's
# much much closer in terms of standards supported etc.
Patch7:		clang-gcc-compat.patch
# Support -fuse-ld=XXX properly
Patch8:		clang-fuse-ld.patch
# Patches from AOSP
Patch4:		0000-llvm-Add-support-for-64-bit-longs.patch
Patch5:		0001-llvm-Make-EnableGlobalMerge-non-static-so-we-can-modify-i.patch
Patch6:		llvm-3.5-detect-hardfloat.patch
Patch9:		ddsan-compile.patch
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
BuildRequires:	bison
BuildRequires:	binutils-devel
BuildRequires:	chrpath
BuildRequires:	flex
%if %{without bootstrap}
BuildRequires:	graphviz
%endif
BuildRequires:	groff
BuildRequires:	libtool
%if %{with ocaml}
BuildRequires:	ocaml-compiler ocaml-compiler-libs ocaml-camlp4 ocaml-findlib >= 1.5.5-2 ocaml-ctypes
%endif
BuildRequires:	tcl
BuildRequires:	sed
BuildRequires:	zip
BuildRequires:	libstdc++-devel
BuildRequires:	pkgconfig(libffi)
BuildRequires:	pkgconfig(cloog-isl)
BuildRequires:	pkgconfig(isl) >= 0.13
BuildRequires:	pkgconfig(libtirpc)
BuildRequires:	python >= 3.4
BuildRequires:	cmake
BuildRequires:	ninja
%if %{with apidox}
BuildRequires:	doxygen
%endif
Requires:	libstdc++-devel
Obsoletes:	llvm-ocaml

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

%define LLVMLibs LLVMAArch64AsmParser LLVMAArch64AsmPrinter LLVMAArch64CodeGen LLVMAArch64Desc LLVMAArch64Disassembler LLVMAArch64Info LLVMAArch64Utils LLVMARMAsmParser LLVMARMAsmPrinter LLVMARMCodeGen LLVMARMDesc LLVMARMDisassembler LLVMARMInfo LLVMAnalysis LLVMAsmParser LLVMAsmPrinter LLVMBitReader LLVMBitWriter LLVMBPFAsmPrinter LLVMBPFCodeGen LLVMBPFDesc LLVMBPFInfo LLVMCodeGen LLVMCore LLVMCppBackendCodeGen LLVMCppBackendInfo LLVMDebugInfoDWARF LLVMDebugInfoPDB LLVMExecutionEngine LLVMHexagonCodeGen LLVMHexagonDesc LLVMHexagonDisassembler LLVMHexagonInfo LLVMIRReader LLVMInstCombine LLVMInstrumentation LLVMInterpreter LLVMLTO LLVMLineEditor LLVMLinker LLVMMC LLVMMCDisassembler LLVMMCJIT LLVMMCParser LLVMMIRParser LLVMMSP430AsmPrinter LLVMMSP430CodeGen LLVMMSP430Desc LLVMMSP430Info LLVMMipsAsmParser LLVMMipsAsmPrinter LLVMMipsCodeGen LLVMMipsDesc LLVMMipsDisassembler LLVMMipsInfo LLVMNVPTXAsmPrinter LLVMNVPTXCodeGen LLVMNVPTXDesc LLVMNVPTXInfo LLVMObjCARCOpts LLVMObject LLVMOption LLVMOrcJIT LLVMPasses LLVMPowerPCAsmParser LLVMPowerPCAsmPrinter LLVMPowerPCCodeGen LLVMPowerPCDesc LLVMPowerPCDisassembler LLVMPowerPCInfo LLVMProfileData LLVMR600AsmParser LLVMR600AsmPrinter LLVMR600CodeGen LLVMR600Desc LLVMR600Info LLVMRuntimeDyld LLVMScalarOpts LLVMSelectionDAG LLVMSparcAsmParser LLVMSparcAsmPrinter LLVMSparcCodeGen LLVMSparcDesc LLVMSparcDisassembler LLVMSparcInfo LLVMSupport LLVMSystemZAsmParser LLVMSystemZAsmPrinter LLVMSystemZCodeGen LLVMSystemZDesc LLVMSystemZDisassembler LLVMSystemZInfo LLVMTableGen LLVMTarget LLVMTransformUtils LLVMVectorize LLVMX86AsmParser LLVMX86AsmPrinter LLVMX86CodeGen LLVMX86Desc LLVMX86Disassembler LLVMX86Info LLVMX86Utils LLVMXCoreAsmPrinter LLVMXCoreCodeGen LLVMXCoreDesc LLVMXCoreDisassembler LLVMXCoreInfo LLVMipa LLVMipo

%define ClangLibs LTO clang clangARCMigrate clangAST clangASTMatchers clangAnalysis clangApplyReplacements clangBasic clangCodeGen clangDriver clangDynamicASTMatchers clangEdit clangFormat clangFrontend clangFrontendTool clangIndex clangLex clangParse clangQuery clangRename clangRewrite clangRewriteFrontend clangSema clangSerialization clangStaticAnalyzerCheckers clangStaticAnalyzerCore clangStaticAnalyzerFrontend clangTidy clangTidyGoogleModule clangTidyLLVMModule clangTidyMiscModule clangTidyReadabilityModule clangTidyUtils clangTooling clangToolingCore

%{expand:%(for i in %{LLVMLibs} %{ClangLibs}; do echo %%libpackage $i %{major1}; done)}
%libpackage modernizeCore %{major1}

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
# FIXME this is evil.. Just a temporary workaround
# for abf issues thinking mesa pre-requires LLVM 3.6 devel files
%if "%{_lib}" == "lib64"
Provides:	devel(libLLVM-3.6(64bit))
Provides:	libLLVM-3.6.so()(64bit)
%else
Provides:	devel(libLLVM-3.6)
Provides:	libLLVM-3.6.so()
%endif

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

%prep
%setup -q %{?with_clang:-a1 -a2 -a3 -a4} -n %{name}-%{version}.src
rm -rf tools/clang
%if %{with clang}
mv cfe-%{version}%{?prerel}.src tools/clang
mv polly-%{version}%{?prerel}.src tools/polly
mv clang-tools-extra-%{version}%{?prerel}.src tools/clang/tools/extra
mv compiler-rt-%{version}%{?prerel}.src projects/compiler-rt
cd tools/clang
%patch0 -p0 -b .soname~
%patch1 -p1 -b .mandriva~
%patch8 -p1 -b .fuseLd~
cd -
%patch2 -p1 -b .armhf~
%patch4 -p1 -b .64bitLongs~
%patch5 -p1 -b .EnableGlobalMerge~
%endif
%patch6 -p1 -b .detectHardfloat~
%patch7 -p1 -b .gcc49~
%patch9 -p1 -b .ddsan~

%patch20 -p1 -b .musl1~
%patch21 -p1 -b .musl2~
%patch22 -p1 -b .musl3~
%patch23 -p1 -b .musl4~
%patch26 -p1 -b .musl7~
%patch27 -p1 -b .musl8~
%patch29 -p1 -b .musl10~
%patch30 -p1 -b .musl11~
%patch31 -p1 -b .musl12~

# Fix bogus permissions
find . -type d |while read r; do chmod 0755 "$r"; done

%build
# Workaround for previous build having a problem with debug info
# generation
#export CFLAGS="%{optflags} -g0"
#export CXXFLAGS="%{optflags} -g0"

# Currently broken, but potentially interesting:
#	-DLLVM_ENABLE_MODULES:BOOL=ON

# compiler-rt doesn't support ix86 with x<6
%ifarch %ix86
export CFLAGS="%{optflags} -march=i686 -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
export CXXFLAGS="%{optflags} -march=i686 -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
%endif

%cmake \
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
	-DLLVM_BUILD_DOCS:BOOL=ON \
	-DOCAMLFIND=NOTFOUND \
	-DLLVM_LIBDIR_SUFFIX=$(echo %{_lib} |sed -e 's,^lib,,') \
	-DLLVM_OPTIMIZED_TABLEGEN:BOOL=ON \
	-DPOLLY_ENABLE_GPGPU_CODEGEN:BOOL=ON \
	-DWITH_POLLY:BOOL=ON \
%if %{with libcxx}
	-DLLVM_ENABLE_LIBCXX:BOOL=ON \
	-DLLVM_ENABLE_LIBCXXABI:BOOL=ON \
%endif
%if %{with apidox}
	-DLLVM_ENABLE_DOXYGEN:BOOL=ON \
%endif

%if ! %{cross_compiling}
export LD_LIBRARY_PATH="$(pwd)/%{_lib}":${LD_LIBRARY_PATH}
%endif
%make || make

%install
%if ! %{cross_compiling}
export LD_LIBRARY_PATH="$(pwd)/build/%{_lib}":${LD_LIBRARY_PATH}
%endif
%if %{with ocaml}
#cp bindings/ocaml/llvm/META.llvm bindings/ocaml/llvm/Release/
%endif
%makeinstall_std -C build

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
%endif

# Sample file not needed
rm %{buildroot}%{_libdir}/LLVMHello.so

# Files needed for make check, but harmful afterwards...
# (conflicts with upstream libgtest)
rm %{buildroot}%{_libdir}/libgtest*
