%define _disable_ld_no_undefined 0

# clang header paths are hard-coded at compile time
# and need adjustment whenever there's a new GCC version
%define gcc_version %(gcc -dumpversion)

%define compile_apidox 0
%{?_with_apidox: %{expand: %%global compile_apidox 1}}

%bcond_without clang

%define _requires_exceptions devel\(libffi\)

Name:		llvm
Version:	3.2
Release:	5
Summary:	Low Level Virtual Machine (LLVM)
License:	NCSA
Group:		Development/Other
URL:		http://llvm.org/
# For the time being, we're building tarballs from the branch hosted at
# git://people.freedesktop.org/~tstellar/llvm rather than direct upstream.
# This patch adds the AMDGPU/R600 backend needed by Mesa 9.1 (and is otherwise
# more or less identical to upstream llvm).
Source0:	http://llvm.org/releases/%{version}/llvm-%{version}.src.tar.gz
Source1:	http://llvm.org/releases/%{version}/clang-%{version}.src.tar.gz
Source2:	llvm.rpmlintrc
# Versionize libclang.so (Anssi 08/2012):
Patch0:		clang-soname.patch
# Adjust search paths to match the OS
Patch1:		llvm-3.2-mandriva.patch
Obsoletes:	llvm-ocaml
Requires:	libstdc++-devel
BuildRequires:	bison
BuildRequires:	groff
BuildRequires:	chrpath
BuildRequires:	ocaml
BuildRequires:	tcl
%if %{compile_apidox}
BuildRequires:	doxygen
%endif
BuildRequires:	flex
BuildRequires:	sed
BuildRequires:	graphviz
BuildRequires:	libstdc++-devel
BuildRequires:	libtool
BuildRequires:	zip
BuildRequires:	pkgconfig(libffi)
BuildRequires:	chrpath

%description
LVM is a robust system, particularly well suited for developing new mid-level
language-independent analyses and optimizations of all sorts, including those
that require  extensive interprocedural analysis. LLVM is also a great target
for front-end development for conventional or research programming languages,
including those which require compile-time, link-time, or run-time optimization 
for effective implementation, proper tail calls or garbage collection. 

%files
%doc LICENSE.TXT
%{_bindir}/bugpoint
%{_bindir}/llc
%{_bindir}/lli
%{_bindir}/opt
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
%{_bindir}/llvm-prof
%{_bindir}/llvm-ranlib
%{_bindir}/llvm-readobj
%{_bindir}/llvm-cov
%{_bindir}/llvm-dwarfdump
%{_bindir}/llvm-mcmarkup
%{_bindir}/llvm-rtdyld
%{_bindir}/llvm-size
%{_bindir}/llvm-stress
%{_bindir}/llvm-tblgen
%{_bindir}/macho-dump
%{_libdir}/ocaml/*

#-----------------------------------------------------------

%define major %version
%define libname %mklibname %name %major

%package -n %libname
Summary: LLVM shared libraries
Group: System/Libraries
Conflicts: llvm < 3.0-4

%description -n %libname
Shared libraries for the LLVM compiler infrastructure. This is needed by
programs that are dynamically linked against libLLVM.

%files -n %libname
%{_libdir}/libLLVM-%major.so

#-----------------------------------------------------------

%define libname_devel %mklibname -d %name

%package -n %{libname_devel}
Summary: Development files for LLVM
Group: Development/Other
Provides: llvm-devel = %version-%release
Requires: %libname = %version-%release
Requires: %name = %version-%release
Conflicts: llvm < 3.0-7
Conflicts: %{_lib}llvm3.0 < 3.0-9

%description -n %{libname_devel}
This package contains the development files for LLVM;

%files -n %{libname_devel}
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
%{_libdir}/%{name}/libprofile_rt.a
%{_libdir}/%{name}/libprofile_rt.so
%{_libdir}/%{name}/libllvm*.a

#-----------------------------------------------------------

%package doc
Summary: Documentation for LLVM
Group: Books/Computer books
Requires: %{name} = %{version}
BuildArch: noarch
Obsoletes: llvm-doc-devel

%description doc
Documentation for the LLVM compiler infrastructure.

%files doc
%defattr(-,root,root,-)
%doc README.txt
%doc docs/*.css
%doc docs/*.html
%doc docs/tutorial
%doc docs/ocamldoc
%doc examples
%if %{compile_apidox}
%doc docs/doxygen
%endif

#-----------------------------------------------------------

%if %{with clang}
%define clang_major %version
%define clang_libname %mklibname clang %clang_major

# TODO: %{_bindir}/clang is linked against static libclang.a, could it be
# linked against libclang.so instead, like llvm-* are against livLLVM.so?

%package -n clang
Summary:        A C language family front-end for LLVM
License:        NCSA
Group:          Development/Other
# TODO: is this requires:llvm needed, or just legacy from fedora pkg layout?
Requires:       llvm%{?_isa} = %{version}-%{release}
# clang requires gcc, clang++ requires libstdc++-devel
Requires:       gcc
Requires:       libstdc++-devel >= %{gcc_version}

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
%{_bindir}/c-index-test
%{_prefix}/lib/clang
%doc %{_mandir}/man1/clang.1.*

%package -n %clang_libname
Summary: Shared library for clang
Group: System/Libraries

%description -n %clang_libname
Shared libraries for the clang compiler. This is needed by
programs that are dynamically linked against libclang.

%files -n %clang_libname
%{_libdir}/libclang-%clang_major.so

#-----------------------------------------------------------

%define clang_libname_devel %mklibname -d clang

%package -n %{clang_libname_devel}
Summary:        Development files for clang
Group:          Development/Other
Requires:	%clang_libname = %version-%release
Provides:	clang-devel = %version-%release
Conflicts:	llvm-devel < 3.1
Obsoletes:	clang-devel < 3.1

%description -n %{clang_libname_devel}
This package contains header files and libraries needed for using
libclang.

%files -n %{clang_libname_devel}
%{_includedir}/clang
%{_includedir}/clang-c
%{_libdir}/libclang.so
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/libclang*.a
%{_libdir}/%{name}/libclang*.so

%package -n clang-analyzer
Summary:        A source code analysis framework
License:        NCSA
Group:          Development/Other
Requires:       clang%{?_isa} = %{version}-%{release}
# not picked up automatically since files are currently not instaled
# in standard Python hierarchies yet
Requires:       python

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
Summary:        Documentation for Clang
Group:          Books/Computer books
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}

%description -n clang-doc
Documentation for the Clang compiler front-end.

%files -n clang-doc
%doc clang-docs-full/*

%endif

#-----------------------------------------------------------

%prep
%setup -qn %{name}-%{version}.src %{?with_clang:-a1}
rm -rf tools/clang
%if %{with clang}
mv clang-%{version}%{?prerel}.src tools/clang
cd tools/clang
%patch0 -p1
cd -
%patch1 -p1 -b .mandriva~
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
	--enable-jit \
	--enable-libffi \
	--enable-optimized \
	--enable-targets=all \
	--enable-experimental-targets=R600 \
	--disable-expensive-checks \
	--enable-debug-runtime \
	--disable-assertions \
	--enable-threads \
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
cp bindings/ocaml/llvm/META.llvm bindings/ocaml/llvm/Release/
%makeinstall_std \
	KEEP_SYMBOLS=1 \
	PROJ_docsdir=%{_docdir}/%{name} \
	PROJ_etcdir=%{_sysconfdir}/%{name} \
	PROJ_libdir=%{_libdir}/%{name}

# Invalid dir 
rm -rf %buildroot%_bindir/.dir

# wrong rpath entries (Anssi 11/2011)
file %{buildroot}/%{_bindir}/* | awk -F: '$2~/ELF/{print $1}' | xargs -r chrpath -d
file %{buildroot}/%{_libdir}/llvm/*.so | awk -F: '$2~/ELF/{print $1}' | xargs -r chrpath -d

# move shared library to standard library path and add devel symlink (Anssi 11/2011)
mv %{buildroot}%{_libdir}/llvm/libLLVM-%major.so %{buildroot}%{_libdir}
ln -s libLLVM-%major.so %{buildroot}%{_libdir}/libLLVM.so
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
mv %{buildroot}%{_libdir}/llvm/libclang.so %{buildroot}%{_libdir}/libclang-%version.so
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

%endif

# Get rid of erroneously installed example files.
rm %{buildroot}%{_libdir}/%{name}/LLVMHello.so

# Fix bogus permissions
find %buildroot -name "*.a" -a -type f|xargs chmod 0644
