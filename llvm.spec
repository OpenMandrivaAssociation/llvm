%define _disable_ld_no_undefined 1

Name: llvm
Version: 2.3
Release: %mkrel 4
Summary: Low Level Virtual Machine (LLVM)
License: University of Illinois Open Source License
Group: Development/Other
URL: http://llvm.org/
Source0: http://llvm.org/releases/%{version}/llvm-%{version}.tar.gz
Patch0: llvm-X86JITInfo.cpp.pic.patch
Patch1: llvm-2.3-fix-sed.patch
BuildRoot: %_tmppath/%name-%version-%release-root
Obsoletes: llvm-devel
Obsoletes: llvm-ocaml
Requires: libstdc++-devel
BuildRequires: bison
BuildRequires: groff
BuildRequires: chrpath
BuildRequires: ocaml
BuildRequires: doxygen
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
%doc docs/*.css
%doc docs/*.html
%doc docs/img
%doc examples
%doc docs/doxygen

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
	--enable-doxygen \
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

