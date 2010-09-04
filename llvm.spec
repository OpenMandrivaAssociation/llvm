%define _disable_ld_no_undefined 0

%define compile_apidox 0
%{?_with_apidox: %{expand: %%global compile_apidox 1}}

Name: llvm
Version: 2.7
Release: %mkrel 2
Summary: Low Level Virtual Machine (LLVM)
License: University of Illinois Open Source License
Group: Development/Other
URL: http://llvm.org/
Source0: http://llvm.org/releases/%{version}/llvm-%{version}.tgz
Patch3:	llvm-2.6-configure.patch
BuildRoot: %_tmppath/%name-%version-%release-root
Obsoletes: llvm-devel
Obsoletes: llvm-ocaml
Requires: libstdc++-devel
BuildRequires: bison
BuildRequires: groff
BuildRequires: chrpath
BuildRequires: ocaml
BuildRequires: tcl
%if %{compile_apidox}
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
%{_bindir}/llc
%{_bindir}/lli
%{_bindir}/opt
%{_bindir}/llvm-ar
%{_bindir}/llvm-as
%{_bindir}/llvm-bcanalyzer
%{_bindir}/llvm-dis
%{_bindir}/llvm-extract
%{_bindir}/llvm-ld
%{_bindir}/llvm-link
%{_bindir}/llvm-nm
%{_bindir}/llvm-prof
%{_bindir}/llvm-ranlib
%{_bindir}/llvm-stub
%{_bindir}/llvmc
%{_bindir}/tblgen
%{_mandir}/man1/*
%{_libdir}/ocaml/*
%{_bindir}/llvm-config
%{_includedir}/*
%{_libdir}/%{name}

#-----------------------------------------------------------

%package doc
Summary: Documentation for LLVM
Group: Books/Computer books
Requires: %{name} = %{version}
Obsoletes: llvm-doc-evel

%description doc
Documentation for the LLVM compiler infrastructure.

%files doc
%defattr(-,root,root,-)
%doc README.txt
%doc docs/*.css
%doc docs/*.html
%doc docs/img
%doc docs/tutorial
%doc docs/ocamldoc
%doc examples
%if %{compile_apidox}
%doc docs/doxygen
%endif

#-----------------------------------------------------------

%prep
%setup -q
%patch3 -p1

%build
%configure2_5x \
	--libdir=%{_libdir}/%{name} \
	--datadir=%{_datadir}/%{name} \
	--enable-shared \
	--enable-jit \
	--enable-optimized \
	--enable-targets=host-only \
	--disable-expensive-checks \
	--enable-debug-runtime \
    --disable-assertions \
	--enable-threads \
%if %{compile_apidox}
	--enable-doxygen \
%endif
%if "%{_lib}" == "lib64" 
    --enable-pic
%else
    --enable-pic=no
%endif

%make

%install
%__rm -rf %buildroot
 
 
%makeinstall_std \
	KEEP_SYMBOLS=1 \
	PROJ_docsdir=%{_docdir}/%{name} \
	PROJ_etcdir=%{_sysconfdir}/%{name} \
	PROJ_libdir=%{_libdir}/%{name}

# Invalid dir 
rm -rf %buildroot%_bindir/.dir

# adjust library path
sed -i -e 's|ABS_RUN_DIR/lib"|ABS_RUN_DIR/%{_lib}/%{name}"|' %{buildroot}%_bindir/llvm-config

%clean
%__rm -rf %buildroot

