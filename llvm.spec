%define		_disable_ld_no_undefined	0
%define		_requires_exceptions		devel(libLLVMSupport\\|devel(libclangARCMigrate\\|devel(libclangAST\\|devel(libclangBasic\\|devel(libclangFrontend\\|devel(libclangLex\\|devel(libclangSema\\|libclangBasic
%define		ffi_include_dir			%(pkg-config libffi --cflags-only-I | sed -e 's/-I//')
%define		c_include_dirs			%(echo `gcc -print-search-dirs | grep install | sed -e 's/install: //'`include:%{_includedir})
%define		version				3.0
%define		major				3
%define		libllvm				%mklibname llvm %{major}
%define		libllvm_devel			%mklibname -d llvm
%define		libclang			%mklibname clang %{major}
%define		libclang_devel			%mklibname -d clang

Name:		llvm
Version:	%{version}
Release:	3
Summary:	Low Level Virtual Machine (LLVM)
License:	NCSA
Group:		Development/Other
URL:		http://llvm.org/
Source0:	http://llvm.org/releases/%{version}/llvm-%{version}.tar.gz
Source1:	http://llvm.org/releases/%{version}/clang-%{version}.tar.gz
%rename llvm-doc
Requires:	%{libllvm} = %{EVRD}
Requires:	libstdc++-devel
BuildRequires:	bison
BuildRequires:	binutils-devel
BuildRequires:	cmake
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
Patch1:		llvm-3.0-soversion.patch

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
%exclude %{_bindir}/llvm-config
%exclude %{_bindir}/c-index-test
%doc LICENSE.TXT
%doc README.txt
%doc docs/*.css
%doc docs/*.html
%doc docs/img
%doc docs/tutorial
%doc examples

#-----------------------------------------------------------
%package	-n %{libllvm}
Summary:	LLVM %{version} shared libraries
Group:		System/Libraries

%description	-n %{libllvm}
%{summary}.

%files		-n %{libllvm}
%{_libdir}/*.so.%{major}*
%exclude %{_libdir}/lib*clang*.so.%{major}*

#-----------------------------------------------------------
%package	-n %{libllvm_devel}
Summary:	LLVM %{version} development files
Group:		Development/Other
Requires:	%{libllvm} = %{EVRD}
Requires:	llvm = %{EVRD}
%rename llvm-devel

%description	-n %{libllvm_devel}
%{summary}.

%files		-n %{libllvm_devel}
%{_bindir}/llvm-config
%{_libdir}/*.so
%exclude %{_libdir}/lib*clang*.so
%{_includedir}/llvm
%{_includedir}/llvm-c
%{_libdir}/cmake/llvm

#-----------------------------------------------------------
%package	-n clang
Summary:	C/C++/Objective-C Frontend Toolkit
Group:		Development/Other
Requires:	llvm = %{EVRD}
Requires:	%{libclang} = %{EVRD}
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
%{_libdir}/clang

#-----------------------------------------------------------
%package	-n %{libclang}
Summary:	Clang %{version} shared libraries
Group:		Development/Other

%description	-n %{libclang}
%{summary}.

%files		-n %{libclang}
%{_libdir}/lib*clang*.so.%{major}*

#-----------------------------------------------------------
%package	-n %{libclang_devel}
Summary:	Clang %{version} development files
Group:		Development/Other
Requires:	%{libclang} = %{EVRD}
Provides:	clang-devel = %{EVRD}

%description	-n %{libclang_devel}
%{summary}.

%files		-n %{libclang_devel}
%{_includedir}/clang
%{_includedir}/clang-c
%{_libdir}/lib*clang*.so

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
%patch1 -p1

%build
%cmake							\
	-DC_INCLUDE_DIRS:STRING=%{c_include_dirs}	\
	-DCLANG_VENDOR:STRING=%{vendor}			\
	-DFFI_INCLUDE_DIR:PATH=%{ffi_include_dir}	\
	-DLLVM_ENABLE_ASSERTIONS:BOOL=false		\
	-DLLVM_INCLUDE_EXAMPLES:BOOL=false		\
%ifarch x86_64
	-DLLVM_LIBDIR_SUFFIX:STRING=64			\
%endif
	-DLLVM_ENABLE_FFI:BOOL=true			\
	-DBUILD_SHARED_LIBS:BOOL=true			\
	-DBUILD_STATIC_LIBS:BOOL=false

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

rm -f %{buildroot}%{_libdir}/{BugpointPasses.so,LLVMHello.so,profile_rt.so}
