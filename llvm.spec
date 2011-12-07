%define		_disable_ld_no_undefined	0
%define		_requires_exceptions		devel(libLLVMSupport\\|devel(libclangARCMigrate\\|devel(libclangAST\\|devel(libclangBasic\\|devel(libclangFrontend\\|devel(libclangLex\\|devel(libclangSema\\|libclangBasic
%define		ffi_include_dir			%(pkg-config libffi --cflags-only-I | sed -e 's/-I//')
%define		c_include_dirs			%(echo `gcc -print-search-dirs | grep install | sed -e 's/install: //'`include:%{_includedir})

Name:		llvm
Version:	3.0
Release:	%mkrel 1
Summary:	Low Level Virtual Machine (LLVM)
License:	NCSA
Group:		Development/Other
URL:		http://llvm.org/
Source0:	http://llvm.org/releases/%{version}/llvm-%{version}.tar.gz
Source1:	http://llvm.org/releases/%{version}/clang-%{version}.tar.gz
%rename llvm-doc
%rename llvm-devel
Requires:	libstdc++-devel
BuildRequires:	bison
BuildRequires:	binutils-devel
BuildRequires:	chrpath
BuildRequires:	ffi-devel
BuildRequires:	flex
BuildRequires:	graphviz
BuildRequires:	groff
BuildRequires:	libstdc++-devel
BuildRequires:	libtool
BuildRequires:	sed
BuildRequires:	tcl
BuildRequires:	zip

Patch0:		llvm-3.0-mandriva.patch

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root

%description
LVM is a robust system, particularly well suited for developing new mid-level
language-independent analyses and optimizations of all sorts, including those
that require  extensive interprocedural analysis. LLVM is also a great target
for front-end development for conventional or research programming languages,
including those which require compile-time, link-time, or run-time optimization 
for effective implementation, proper tail calls or garbage collection. 

%files
%{_bindir}/*
%exclude %{_bindir}/clang*
%exclude %{_bindir}/c-index-test
%{_includedir}/llvm
%{_includedir}/llvm-c
%{_libdir}/*.so
%exclude %{_libdir}/libclang*.so
%exclude %{_libdir}/liblibclang*.so.*
%{_libdir}/cmake/llvm
%doc LICENSE.TXT
%doc README.txt
%doc docs/*.css
%doc docs/*.html
%doc docs/img
%doc docs/tutorial
%doc examples

#-----------------------------------------------------------
%package	-n clang
Summary:	C/C++/Objective-C Frontend Toolkit
Group:		Development/Other
Requires:	llvm = %{version}-%{release}
Requires:	gcc-c++

%description	-n clang
Clang is an LLVM front end for the C, C++, and Objective-C languages.
Clang aims to provide a better user experience through expressive
diagnostics, a high level of conformance to language standards, fast
compilation, and low memory use. Like LLVM, Clang provides a modular,
library-based architecture that makes it suitable for creating or
integrating with other development tools. Clang is considered a
production-quality compiler for C, Objective-C, C++ and Objective-C++
on x86 (32- and 64-bit), and for Darwin/ARM targets.

%files		-n clang
%{_bindir}/clang*
%{_bindir}/c-index-test
%{_includedir}/clang
%{_includedir}/clang-c
%{_libdir}/clang
%{_libdir}/libclang*.so
%{_libdir}/liblibclang*.so.*

#-----------------------------------------------------------
%prep
%setup -q -n %{name}-%{version}.src -a1
mv clang-%{version}.src tools/clang

cat > autoconf/config.guess <<EOF
#!/bin/sh
echo %{_target_platform}
EOF
chmod +x autoconf/config.guess

%patch0 -p1

%build
%cmake							\
	-DC_INCLUDE_DIRS:STRING=%{c_include_dirs}	\
	-DCLANG_VENDOR:STRING=%{vendor}			\
	-DFFI_INCLUDE_DIR:PATH=%{ffi_include_dir}	\
	-DLLVM_INCLUDE_EXAMPLES:BOOL=false		\
%ifarch x86_64
	-DLLVM_LIBDIR_SUFFIX:STRING=64			\
%endif
	-DLLVM_ENABLE_FFI:BOOL=true

LD_LIBRARY_PATH=$PWD/lib:$_LIBRARY_PATH			\
%make

#-----------------------------------------------------------
%install
%makeinstall_std -C build
mkdir -p %{buildroot}%{_libdir}/cmake
mv -f %{buildroot}%{_datadir}/llvm/cmake %{buildroot}%{_libdir}/cmake/llvm
rmdir %{buildroot}%{_datadir}/llvm

%ifarch x86_64
# adjust library path
sed -i -e 's|ABS_RUN_DIR/lib.*"|ABS_RUN_DIR/%{_lib}"|'	\
	%{buildroot}%{_bindir}/llvm-config
%endif
