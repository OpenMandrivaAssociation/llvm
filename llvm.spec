%define debug_package %{nil}
%define _disable_ld_no_undefined 0

# clang header paths are hard-coded at compile time
# and need adjustment whenever there's a new GCC version
%define gcc_version %(gcc -dumpversion)

%define default_compiler 1

%define compile_apidox 0
%{?_with_apidox: %{expand: %%global compile_apidox 1}}

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

%define _requires_exceptions devel\(libffi\)

Summary:	Low Level Virtual Machine (LLVM)
Name:		llvm
Version:	3.7.0
Release:	0.238333.1
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
# Patches for musl support, (partially) stolen from Alpine Linux and ported
Patch20:	llvm-3.7-musl.patch
Patch21:	llvm-3.7-musl-triple.patch
Patch22:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/compiler-rt-sanitizer-off_t.patch
Patch23:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/compiler-rt-3.6-musl-no-dlvsym.patch
# http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.6-remove-lgcc-when-using-compiler-rt.patch breaks
# exception handling -- removes gcc_eh
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
%if %{compile_apidox}
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
%doc LICENSE.TXT
%{_bindir}/FileCheck
%{_bindir}/bugpoint
%{_bindir}/count
%{_bindir}/llc
%{_bindir}/lli
%{_bindir}/opt
%{_bindir}/lli-child-target
%{_bindir}/llvm-ar
%{_bindir}/llvm-as
%{_bindir}/llvm-bcanalyzer
%{_bindir}/llvm-diff
%{_bindir}/llvm-dis
%{_bindir}/llvm-dsymutil
%{_bindir}/llvm-extract
%{_bindir}/llvm-link
%{_bindir}/llvm-mc
%{_bindir}/llvm-nm
%{_bindir}/llvm-objdump
%{_bindir}/llvm-ranlib
%{_bindir}/llvm-readobj
%{_bindir}/llvm-cov
%{_bindir}/llvm-dwarfdump
%{_bindir}/llvm-mcmarkup
%{_bindir}/llvm-profdata
%{_bindir}/llvm-rtdyld
%{_bindir}/llvm-size
%{_bindir}/llvm-stress
%{_bindir}/llvm-symbolizer
%{_bindir}/llvm-tblgen
%{_bindir}/llvm-cxxdump
%{_bindir}/llvm-pdbdump
%{_bindir}/pp-trace
%{_bindir}/verify-uselistorder
%{_bindir}/obj2yaml
%{_bindir}/yaml2obj
%{_bindir}/macho-dump
%{_bindir}/not
%dir %{_libdir}/llvm

#-----------------------------------------------------------

%define major %(echo %{version} |cut -d. -f1-2)
%define libname %mklibname %{name} %{major}

%package -n %{libname}
Summary:	LLVM shared libraries
Group:		System/Libraries
Conflicts:	llvm < 3.0-4
Obsoletes:	%{mklibname %{name} 3.5.0}

%description -n %{libname}
Shared libraries for the LLVM compiler infrastructure. This is needed by
programs that are dynamically linked against libLLVM.

%files -n %{libname}
%{_libdir}/libLLVM-[0-9].*.so

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
%{_libdir}/libLLVM.so
%{_includedir}/%{name}
%{_includedir}/%{name}-c
%{_libdir}/%{name}/BugpointPasses.so
%{_libdir}/%{name}/libLLVM*.a
%{_libdir}/%{name}/libLLVM*.so
%{_libdir}/%{name}/libLTO.a
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
%if %{compile_apidox}
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
%{_libdir}/llvm/LLVMPolly.so

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
%define libclang %mklibname clang %version

# TODO: %{_bindir}/clang is linked against static libclang.a, could it be
# linked against libclang.so instead, like llvm-* are against livLLVM.so?

%package -n clang
Summary:	A C language family front-end for LLVM
License:	NCSA
Group:		Development/Other
# TODO: is this requires:llvm needed, or just legacy from fedora pkg layout?
Requires:	llvm%{?_isa} = %{EVRD}
# clang requires gcc, clang++ requires libstdc++-devel
Requires:	gcc
Requires:	libstdc++-devel >= %{gcc_version}

%description -n clang
clang: noun
    1. A loud, resonant, metallic sound.
    2. The strident call of a crane or goose.
    3. C-language family front-end toolkit.

The goal of the Clang project is to create a new C, C++, Objective C
and Objective C++ front-end for the LLVM compiler. Its tools are built
as libraries and designed to be loosely-coupled and extensible.

%files -n clang
%doc clang-docs/*
%{_bindir}/clang*
%{_libdir}/llvm/libmodernizeCore.a
%{_libdir}/llvm/LLVMgold.so
%{_libdir}/llvm/libLTO.so
%{_libdir}/LLVMgold.so
%{_libdir}/libLTO.so
%{_bindir}/c-index-test
%{_prefix}/lib/clang
%doc %{_mandir}/man1/clang.1.*
%if %{default_compiler}
%{_bindir}/cc
%{_bindir}/c89
%{_bindir}/c99
%{_bindir}/c++
%endif

%package -n %{libclang}
Summary:	Shared library for clang
Group:		System/Libraries
Obsoletes:	%mklibname clang %{major} < %{EVRD}

%description -n %{libclang}
Shared libraries for the clang compiler. This is needed by
programs that are dynamically linked against libclang.

%files -n %{libclang}
%{_libdir}/libclang-%version.so

#-----------------------------------------------------------

%define devclang %mklibname -d clang

%package -n %{devclang}
Summary:	Development files for clang
Group:		Development/Other
Requires:	%{libclang} = %{EVRD}
Provides:	clang-devel = %{EVRD}
Conflicts:	llvm-devel < 3.1
Obsoletes:	clang-devel < 3.1

%description -n %{devclang}
This package contains header files and libraries needed for using
libclang.

%files -n %{devclang}
%{_includedir}/clang
%{_includedir}/clang-c
%{_libdir}/libclang.so
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/libclang*.a
%{_libdir}/%{name}/libclang*.so

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
%{_bindir}/scan-build
%{_bindir}/scan-view
%{_libdir}/clang-analyzer


%package -n clang-doc
Summary:	Documentation for Clang
Group:		Books/Computer books
BuildArch:	noarch
Requires:	%{name} = %{EVRD}

%description -n clang-doc
Documentation for the Clang compiler front-end.

%files -n clang-doc
%doc clang-docs-full/*

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

%patch20 -p1 -b .musl1~
%patch21 -p1 -b .musl2~
%patch22 -p1 -b .musl3~
%patch23 -p1 -b .musl4~
%patch26 -p1 -b .musl7~
%patch27 -p1 -b .musl8~
%patch29 -p1 -b .musl10~
%patch30 -p1 -b .musl11~
%patch31 -p1 -b .musl12~

# Upstream tends to forget to remove "rc" and "svn" markers from version
# numbers before making releases
sed -i -re 's|^(AC_INIT[^,]*,\[)([0-9.]*)([^]])*(.*)|\1\2\4|' autoconf/configure.ac
sed -i -re "s|(PACKAGE_VERSION='[0-9.]*)([^']*)(.*)|\1\3|g;s|(PACKAGE_STRING='LLVM [0-9.]*)([^']*)(.*)|\1\3|g" configure
sed -i -re "s|^LLVM_VERSION_SUFFIX=.*|LLVM_VERSION_SUFFIX=|g" autoconf/configure.ac configure
chmod +x configure autoconf/*
find . -type d |while read r; do chmod 0755 "$r"; done

%build
# Workaround for previous build having a problem with debug info
# generation
export CFLAGS="%{optflags} -g0"
export CXXFLAGS="%{optflags} -g0"

%configure \
	--libdir=%{_libdir}/%{name} \
	--datadir=%{_datadir}/%{name} \
	--enable-shared \
	--enable-polly \
	--enable-cxx11 \
	--enable-jit \
	--enable-libffi \
	--enable-optimized \
	--enable-keep-symbols \
	--enable-targets=all \
	--enable-experimental-targets=R600 \
	--disable-expensive-checks \
	--enable-debug-runtime \
	--disable-assertions \
	--enable-threads \
	--with-cloog=%{_prefix} \
	--with-isl=%{_prefix} \
	--with-binutils-include=%{_includedir} \
%if %{compile_apidox}
	--enable-doxygen
%endif

sed -i -e 's|^#define CLANG_LIBDIR_SUFFIX.*|#define CLANG_LIBDIR_SUFFIX \"64\"|' include/llvm/Config/config.h

# FIXME file this
# configure does not properly specify libdir
sed -i 's|(PROJ_prefix)/lib|(PROJ_prefix)/%{_lib}/%{name}|g' Makefile.config

# FIXME upstream need to fix this
# llvm-config.cpp hardcodes lib in it
sed -i 's|ActiveLibDir = ActivePrefix + "/lib"|ActiveLibDir = ActivePrefix + "/%{_lib}/%{name}"|g' tools/llvm-config/llvm-config.cpp

%make

%install
%if %{with ocaml}
cp bindings/ocaml/llvm/META.llvm bindings/ocaml/llvm/Release/
%endif
%makeinstall_std \
	KEEP_SYMBOLS=1 \
	PROJ_docsdir=%{_docdir}/%{name} \
	PROJ_etcdir=%{_sysconfdir}/%{name} \
	PROJ_libdir=%{_libdir}/%{name}

# Invalid dir 
rm -rf %{buildroot}%{_bindir}/.dir

# wrong rpath entries (Anssi 11/2011)
file %{buildroot}/%{_bindir}/* | awk -F: '$2~/ELF/{print $1}' | xargs -r chrpath -d
file %{buildroot}/%{_libdir}/llvm/*.so | awk -F: '$2~/ELF/{print $1}' | xargs -r chrpath -d

# move shared libraries to standard library path and add devel symlink (Anssi 11/2011)
mv %{buildroot}%{_libdir}/llvm/libLLVM-[0-9].*.so %{buildroot}%{_libdir}
ln -s libLLVM-%{version}.so %{buildroot}%{_libdir}/libLLVM.so
ln -s llvm/LLVMgold.so %{buildroot}%{_libdir}/
ln -s llvm/libLTO.so %{buildroot}%{_libdir}/
# Also, create shared library symlinks corresponding to all the static library
# names, so that using e.g. "-lLLVMBitReader" will cause the binary to be linked
# against the shared library instead of static library by default. (Anssi 08/2012)
for staticlib in %{buildroot}%{_libdir}/llvm/libLLVM*.a; do
	sharedlib="${staticlib%.a}.so"
	[ -e "$sharedlib" ] && exit 1
	ln -s ../libLLVM.so "$sharedlib"
done

%if %with clang
# Versionize libclang.so (patch0 makes the same change to soname) and move it to standard path.
mv %{buildroot}%{_libdir}/llvm/libclang.so %{buildroot}%{_libdir}/libclang-%{version}.so
ln -s libclang-%version.so %{buildroot}%{_libdir}/libclang.so
ln -s ../libclang.so %{buildroot}%{_libdir}/llvm/libclang.so

# NOTE: We don't create devel symlinks for the libclang.so for libclang*.a libraries
# like for libLLVM above, because libclang.so actually exports much less symbols
# - some are not linked in (tools/libclang/Makefile) and others are restricted
# by tools/libclang/libclang.exports. - Anssi 09/2012
%endif

# Since the static libraries are very huge, strip them of debug symbols as well
# (Anssi 08/2012)
strip --strip-debug %{buildroot}%{_libdir}/llvm/*.a

%if %{with clang}

# Static analyzer not installed by default:
# http://clang-analyzer.llvm.org/installation#OtherPlatforms
mkdir -p %{buildroot}%{_libdir}/clang-analyzer
# create launchers
for f in scan-{build,view}; do
  ln -s %{_libdir}/clang-analyzer/$f/$f %{buildroot}%{_bindir}/$f
done

(cd tools/clang/tools && cp -pr scan-{build,view} \
 %{buildroot}%{_libdir}/clang-analyzer/)

# And prepare Clang documentation
#
rm -rf clang-docs
mkdir clang-docs
for f in LICENSE.TXT NOTES.txt README.txt; do # TODO.txt; do
  ln tools/clang/$f clang-docs/
done
rm -rf clang-docs-full
cp -al tools/clang/docs clang-docs-full
rm -rf clang-docs-full/{doxygen*,Makefile*,*.graffle,tools}

# Polly bits as described on
# http://polly.llvm.org/example_load_Polly_into_clang.html
cat >%{buildroot}%{_bindir}/pollycc <<'EOF'
#!/bin/sh
exec %{_bindir}/clang -O3 -Xclang -load -Xclang %{_libdir}/llvm/LLVMPolly.so "$@"
EOF
cat >%{buildroot}%{_bindir}/pollyc++ <<'EOF'
#!/bin/sh
exec %{_bindir}/clang++ -O3 -Xclang -load -Xclang %{_libdir}/llvm/LLVMPolly.so "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/pollycc %{buildroot}%{_bindir}/pollyc++

%endif

# Get rid of erroneously installed example files.
rm %{buildroot}%{_libdir}/%{name}/LLVMHello.so

# Fix bogus permissions
find %{buildroot} -perm 0640 -o -name "*.a" |xargs chmod 0644

%if %{default_compiler}
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
