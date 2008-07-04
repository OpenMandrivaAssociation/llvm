%define _disable_ld_no_undefined 1

%define with_devdoc 0
%{?_with_devdoc: %{expand: %%global with_devdoc 1}}

%define with_ocaml 0
%{?_with_ocaml: %{expand: %%global with_ocaml 1}}

Name: llvm
Version: 2.3
Release: %mkrel 2
Summary: Low Level Virtual Machine (LLVM)
License: University of Illinois Open Source License
Group: Development/Other
URL: http://llvm.org/
Source0: http://llvm.org/releases/%{version}/llvm-%{version}.tar.gz
Patch0: llvm-X86JITInfo.cpp.pic.patch
Patch1: llvm-2.3-fix-sed.patch
BuildRoot: %_tmppath/%name-%version-%release-root
BuildRequires: bison
BuildRequires: groff
BuildRequires: chrpath
%if %{with_ocaml}
BuildRequires: ocaml
%endif
%if %{with_devdoc}
BuildRequires: doxygen
%endif
BuildRequires: flex
BuildRequires: sed
BuildRequires: graphviz
BuildRequires: libstdc++-devel
BuildRequires: libtool
BuildRequires: zip

%description
LVM is a robust system, particularly well suited for developing new mid-level
language-independent analyses and optimizations of all sorts, including those
that require  extensive interprocedural analysis. LLVM is also a great target
for front-end development for conventional or research programming languages,
including those which require compile-time, link-time, or run-time optimization 
for effective implementation, proper tail calls or garbage collection. 

%files
%defattr(-,root,root,-)
%doc LICENSE.TXT
%{_bindir}/bugpoint
%{_bindir}/gccas
%{_bindir}/gccld
%{_bindir}/llc
%{_bindir}/lli
%{_bindir}/opt
%{_bindir}/llvm-ar
%{_bindir}/llvm-as
%{_bindir}/llvm-bcanalyzer
%{_bindir}/llvm-db
%{_bindir}/llvm-dis
%{_bindir}/llvm-extract
%{_bindir}/llvm-ld
%{_bindir}/llvm-link
%{_bindir}/llvm-nm
%{_bindir}/llvm-prof
%{_bindir}/llvm-ranlib
%{_bindir}/llvm-stub
%{_bindir}/llvmc2
%{_mandir}/man1/*

#-----------------------------------------------------------

%if %{with_ocaml}
%package ocaml
Summary: llvm ocaml frontend
Group: Development/Other
Requires: %{name} = %{version}

%description ocaml
llvm ocaml frontend.

%files ocaml
%defattr(-,root,root,-)
%_libdir/ocaml/*

%endif

#-----------------------------------------------------------

%package devel
Summary: Libraries and header files for LLVM
Group: Development/Other
Requires: %{name} = %{version}
Requires: libstdc++-devel

%description devel
This package contains library and header files needed to develop
new native programs that use the LLVM infrastructure.

%files devel
%defattr(-,root,root,-)
%{_bindir}/llvm-config
%{_includedir}/*
%{_libdir}/%{name}

#-----------------------------------------------------------

%package doc
Summary: Documentation for LLVM
Group: Books/Computer books
Requires: %{name} = %{version}

%description doc
Documentation for the LLVM compiler infrastructure.

%files doc
%defattr(-,root,root,-)
%doc docs/*.css
%doc docs/*.html
%doc docs/img
%doc examples

#-----------------------------------------------------------

%if %{with_devdoc}

%package doc-devel
Summary: Documentation for development LLVM
Group: Books/Computer books
Requires: %{name} = %{version}

%description doc-devel
Documentation for the LLVM compiler infrastructure.

%files doc-devel
%defattr(-,root,root,-)
%doc docs/doxygen

%endif

#-----------------------------------------------------------

%prep
%setup -q
%patch0 -p0 -b .x86_64
%patch1 -p1 -b .sed

%build
%configure2_5x \
	--libdir=%{_libdir}/%{name} \
	--datadir=%{_datadir}/%{name} \
	--enable-shared \
	--enable-assertions \
	--enable-jit \
	--enable-optimized \
	--enable-targets=host-only \
	--disable-expensive-checks \
	--enable-debug-runtime \
	--enable-threads \
	%if %{with_devdoc}
	--enable-doxygen \
	%endif
	--enable-pic \
	--with-pic

make

%install
%makeinstall_std \
	KEEP_SYMBOLS=1 \
	PROJ_docsdir=%{buildroot}/%{_docdir}/%{name} \
	PROJ_etcdir=%{buildroot}/%{_sysconfdir}/%{name} \
	PROJ_libdir=%{buildroot}/%{_libdir}/%{name}

# Invalid dir 
rm -rf %buildroot%_bindir/.dir

# adjust library path
sed -i -e 's|ABS_RUN_DIR/lib"|ABS_RUN_DIR/%{_lib}/%{name}"|' %{buildroot}%_bindir/llvm-config

%clean
rm -rf %buildroot

