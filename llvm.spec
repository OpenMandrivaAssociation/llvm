%define _disable_ld_no_undefined 0

# clang header paths are hard-coded at compile time
# and need adjustment whenever there's a new GCC version
%define gcc_version %(gcc -dumpversion)

%define compile_apidox 0
%{?_with_apidox: %{expand: %%global compile_apidox 1}}

%bcond_without clang
%bcond_without ocaml

%define _requires_exceptions devel\(libffi\)

Summary:	Low Level Virtual Machine (LLVM)
Name:		llvm
Version:	3.5
Release:	0.207952.1
License:	NCSA
Group:		Development/Other
Url:		http://llvm.org/
# There's a branch of LLVM maintained at
# git://people.freedesktop.org/~tstellar/llvm
# Ir is the working branch of the AMDGPU/R600 backend needed by Mesa (and is otherwise
# more or less identical to upstream llvm).
# At times it may be necessary to package this branch instead.
Source0:	http://llvm.org/releases/%{version}/llvm-%{version}.src.tar.gz
Source1:	http://llvm.org/releases/%{version}/clang-%{version}.src.tar.gz
Source2:	http://llvm.org/releases/%{version}/clang-tools-extra-%{version}.src.tar.gz
Source3:	http://llvm.org/releases/%{version}/polly-%{version}.src.tar.gz
Source4:	http://llvm.org/releases/%{version}/compiler-rt-%{version}.src.tar.gz
Source1000:	llvm.rpmlintrc
# Versionize libclang.so (Anssi 08/2012):
Patch0:		clang-soname.patch
# Adjust search paths to match the OS
Patch1:		0000-clang-mandriva.patch
# ARM hardfloat hack
# see http://llvm.org/bugs/show_bug.cgi?id=15557
# and https://bugzilla.redhat.com/show_bug.cgi?id=803433
Patch2:		clang-hardfloat-hack.patch
# XDR size is different with tirpc
Patch3:		compiler-rt-tirpc-xdr.patch
BuildRequires:	bison
BuildRequires:	chrpath
BuildRequires:	flex
BuildRequires:	graphviz
BuildRequires:	groff
BuildRequires:	libtool
%if %{with ocaml}
BuildRequires:	ocaml
%endif
BuildRequires:	tcl
BuildRequires:	sed
BuildRequires:	zip
BuildRequires:	libstdc++-devel
BuildRequires:	pkgconfig(libffi)
BuildRequires:	pkgconfig(cloog-isl)
BuildRequires:	pkgconfig(isl) >= 0.13
BuildRequires:	pkgconfig(libtirpc)
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
%{_bindir}/pp-trace
%{_bindir}/macho-dump
%{_bindir}/not
%if %{with ocaml}
%{_libdir}/ocaml/*
%endif

#-----------------------------------------------------------

%define major %{version}.0
%define libname %mklibname %{name} %{major}

%package -n %{libname}
Summary:	LLVM shared libraries
Group:		System/Libraries
Conflicts:	llvm < 3.0-4

%description -n %{libname}
Shared libraries for the LLVM compiler infrastructure. This is needed by
programs that are dynamically linked against libLLVM.

%files -n %{libname}
%{_libdir}/libLLVM-%{major}.so

#-----------------------------------------------------------

%define devname %mklibname -d %{name}

%package -n %{devname}
Summary:	Development files for LLVM
Group:		Development/Other
Provides:	llvm-devel = %{version}-%{release}
Requires:	%{libname} = %{version}-%{release}
Requires:	%{name} = %{version}-%{release}
Conflicts:	llvm < 3.0-7
Conflicts:	%{_lib}llvm3.0 < 3.0-9

%description -n %{devname}
This package contains the development files for LLVM;

%files -n %{devname}
%{_bindir}/%{name}-config
%{_libdir}/libLLVM.so
%{_includedir}/%{name}
%{_includedir}/%{name}-c
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/BugpointPasses.so
%{_libdir}/%{name}/libLLVM*.a
%{_libdir}/%{name}/libLLVM*.so
%{_libdir}/%{name}/libLTO.a
%{_libdir}/%{name}/libLTO.so
%{_libdir}/%{name}/libllvm*.a
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
%doc docs/*.css
%doc docs/*.html
%doc docs/tutorial
%if %{with ocaml}
%doc docs/ocamldoc
%endif
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
%define clang_major %{major}
%define libclang %mklibname clang %clang_major

# TODO: %{_bindir}/clang is linked against static libclang.a, could it be
# linked against libclang.so instead, like llvm-* are against livLLVM.so?

%package -n clang
Summary:	A C language family front-end for LLVM
License:	NCSA
Group:		Development/Other
# TODO: is this requires:llvm needed, or just legacy from fedora pkg layout?
Requires:	llvm%{?_isa} = %{version}-%{release}
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
%{_bindir}/c-index-test
%{_prefix}/lib/clang
%doc %{_mandir}/man1/clang.1.*

%package -n %{libclang}
Summary:	Shared library for clang
Group:		System/Libraries

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
Requires:	%{libclang} = %{version}-%{release}
Provides:	clang-devel = %{version}-%{release}
Conflicts:	llvm-devel < 3.1
Obsoletes:	clang-devel < 3.1

%description -n %{devclang}
This package contains header files and libraries needed for using
libclang.

%files -n %{devclang}
%{_includedir}/clang
%{_includedir}/clang-c
%{_libdir}/libclang.so
%{_libdir}/libclang-%{clang_major}.so
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/libclang*.a
%{_libdir}/%{name}/libclang*.so

%package -n clang-analyzer
Summary:	A source code analysis framework
License:	NCSA
Group:		Development/Other
Requires:	clang%{?_isa} = %{version}-%{release}
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
Requires:	%{name} = %{version}-%{release}

%description -n clang-doc
Documentation for the Clang compiler front-end.

%files -n clang-doc
%doc clang-docs-full/*

%endif

#-----------------------------------------------------------

%prep
%setup -qn %{name}-%{version} %{?with_clang:-a1 -a2 -a3 -a4}
rm -rf tools/clang
%if %{with clang}
mv clang-%{version}%{?prerel} tools/clang
mv polly-%{version}%{?prerel} tools/polly
mv clang-tools-extra-%{version}%{?prerel} tools/clang/tools/extra
mv compiler-rt-%{version}%{?prerel} projects/compiler-rt
cd tools/clang
%patch0 -p0
%patch1 -p1 -b .mandriva~
cd -
%patch2 -p1 -b .armhf~
%patch3 -p1 -b .tirpc~
%endif

# Upstream tends to forget to remove "rc" and "svn" markers from version
# numbers before making releases
sed -i -re 's|^(AC_INIT[^,]*,\[)([0-9.]*)([^]])*(.*)|\1\2\4|' autoconf/configure.ac
sed -i -re "s|(PACKAGE_VERSION='[0-9.]*)([^']*)(.*)|\1\3|g;s|(PACKAGE_STRING='LLVM [0-9.]*)([^']*)(.*)|\1\3|g" configure

%build
# Build with gcc/g++, not clang if it happens to be installed
# (blino) clang < 3.1 does not handle system headers from gcc 4.7
# http://llvm.org/bugs/show_bug.cgi?id=11916
export CC=%__cc
export CXX=%__cxx

%configure2_5x \
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
%if %{compile_apidox}
	--enable-doxygen
%endif

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

# move shared library to standard library path and add devel symlink (Anssi 11/2011)
mv %{buildroot}%{_libdir}/llvm/libLLVM-%{major}.so %{buildroot}%{_libdir}
ln -s libLLVM-%{major}.so %{buildroot}%{_libdir}/libLLVM.so
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
ln -s libclang-%clang_major.so %{buildroot}%{_libdir}/libclang.so
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
find %{buildroot} -name "*.a" -a -type f|xargs chmod 0644

# Fix symlinks pointing at the buildroot
cd %{buildroot}%{_libdir}/%{name}
if [ -L libLLVM-%{version}svn.so ]; then
	rm -f libLLVM-%{version}svn.so
	ln -s libLLVM-%{major}.so libLLVM-%{version}svn.so
fi
