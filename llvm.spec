# Barfs because of python2 files
%define _python_bytecompile_build 0

%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif
%if %{with compat32}
%bcond_with bootstrap32
%endif

# (tpg) set snapshot date
%define date 20220207

# Allow empty debugsource package for some subdirs
%define _empty_manifest_terminate_build 0

%define build_lto 1
%define _disable_ld_no_undefined 1
%define _disable_lto 1

# (tpg) optimize it a bit
# And reduce debug level to save some space
%global optflags %(echo %{optflags} |sed -e 's,-m64,,g') -O3 -fpic -fno-semantic-interposition -Qunused-arguments -Wl,-Bsymbolic-functions -g1
%global build_ldflags %{build_ldflags} -fno-semantic-interposition -Wl,-Bsymbolic-functions

%ifarch %{riscv}
# Workaround for broken previous version
%global optflags %{optflags} -fpermissive
%endif

# clang header paths are hard-coded at compile time
# and need adjustment whenever there's a new GCC version
%define gcc_version %(gcc -dumpversion)

%bcond_without default_compiler

# apidox are *huge* (> 8 GB)
# Enabling this option will take forever and create
# a giant package that might even cause timeouts when
# uploading to ABF...
%bcond_with apidox
%bcond_without clang
%bcond_without bolt
# flang needs MLIR, MLIR is broken in 13.0.0-rc3
%bcond_without flang
# libc is broken in 13.0.0-rc3 (doesn't compile)
%bcond_with libc
# MLIR is broken in 13.0.0-rc3 (doesn't compile)
%bcond_without mlir
%ifarch armv7hnl riscv64
# RISC-V and armv7 don't have a working ocaml compiler yet
%bcond_with ocaml
# No graphviz yet either
%bcond_with bootstrap
%else
%bcond_with ocaml
%bcond_without bootstrap
%endif
%bcond_without ffi
# Force gcc to compile, in case previous clang is busted
%ifarch %{riscv} i686
%bcond_without bootstrap_gcc
%else
%bcond_with bootstrap_gcc
%endif
%if %{with bootstrap_gcc}
# gcc and clang don't fully agree about function name
# pretty printing, causing lldb to bomb out when built
# with gcc format checking
%global Werror_cflags %{nil}
# libcxx fails to bootstrap with gcc
%bcond_with libcxx
%else
%ifarch %{ix86}
# FIXME libc++ seems to be broken on x86_32
%bcond_with libcxx
%else
%bcond_without libcxx
%endif
%endif
%ifarch %{riscv}
# Disabled until we get a RISC-V implementation of NativeRegisterContext
# lldb/source/Plugins/Process/Linux/NativeRegisterContext*
%bcond_with lldb
%else
%bcond_without lldb
%endif
%bcond_without openmp
%bcond_without unwind
%bcond_without lld

# Use libcxx instead of libstdc++. Good, but
# don't do this if you care about binary compatibility...
%bcond_with use_libcxx

# If enabled, prefer compiler-rt over libgcc
%bcond_with default_compilerrt

# Clang's libLLVMgold.so shouldn't trigger devel(*) dependencies
%define __requires_exclude 'devel.*'

%define ompmajor 1
%define ompname %mklibname omp %{ompmajor}

%bcond_with upstream_tarballs

%define major %(echo %{version} |cut -d. -f1-2)
%define major1 %(echo %{version} |cut -d. -f1)
#define is_main 1

%bcond_without crosscrt

# We set LLVM_VERSION_SUFFIX affects the soname of libraries. If unset,
# LLVM_VERSION_SUFFIX is set to "git", resulting in libraries like
# libLLVMSupport.so.13git - a major of "13git" that is different from
# the major for the release ("13"). Better to set LLVM_VERSION_SUFFIX
# to something beginning with a ., leaving the major untouched.
#define SOMINOR .%(echo %{version}|cut -d. -f2-)%{?date:.%{date}}
# As of 13.0-rc1, the build system doesn't set a .so.13 symlink
# even if the soname is .so.13.0 or so, so let's set SOMINOR to nothing
# for now
%define SOMINOR %{nil}

Summary:	Low Level Virtual Machine (LLVM)
Name:		llvm
Version:	14.0.0
License:	Apache 2.0 with linking exception
Group:		Development/Other
Url:		http://llvm.org/
%if 0%{?date:1}
# git archive-d from https://github.com/llvm/llvm-project
Source0:	https://github.com/llvm/llvm-project/archive/%{?is_main:main}%{!?is_main:release/%{major1}.x}/llvm-%{major1}-%{date}.tar.gz
Release:	0.%{date}.1
%else
Release:	1
%if %{with upstream_tarballs}
Source0:	http://llvm.org/releases/%{version}/llvm-%{version}.src.tar.xz
Source1:	http://llvm.org/releases/%{version}/cfe-%{version}.src.tar.xz
Source2:	http://llvm.org/releases/%{version}/clang-tools-extra-%{version}.src.tar.xz
Source3:	http://llvm.org/releases/%{version}/polly-%{version}.src.tar.xz
Source4:	http://llvm.org/releases/%{version}/compiler-rt-%{version}.src.tar.xz
Source5:	http://llvm.org/releases/%{version}/libcxx-%{version}.src.tar.xz
Source6:	http://llvm.org/releases/%{version}/libcxxabi-%{version}.src.tar.xz
Source7:	http://llvm.org/releases/%{version}/libunwind-%{version}.src.tar.xz
Source8:	http://llvm.org/releases/%{version}/lldb-%{version}.src.tar.xz
Source9:	http://llvm.org/releases/%{version}/lld-%{version}.src.tar.xz
Source10:	http://llvm.org/releases/%{version}/openmp-%{version}.src.tar.xz
Source11:	http://llvm.org/releases/%{version}/libclc-%{version}.src.tar.xz
%else
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/llvm-project-%{version}.src.tar.xz
%endif
%endif
# llvm-spirv-translator and friends
Source20:	https://github.com/KhronosGroup/SPIRV-LLVM-Translator/archive/refs/heads/master.tar.gz#/spirv-llvm-translator-%{date}.tar.gz
# HEAD as of 2022/01/20
Source21:	https://github.com/KhronosGroup/SPIRV-Headers/archive/b8047fbe45f426f5918fadc67e8408f5b108c3c9.tar.gz
Source22:	https://github.com/KhronosGroup/SPIRV-Tools/archive/v2021.4.tar.gz
# For compatibility with the nongnu.org libunwind
Source50:	libunwind.pc.in
Source1000:	llvm.rpmlintrc
# Adjust search paths to match the OS
Patch1:		0000-clang-openmandriva-triples.patch
# ARM hardfloat hack
# see http://llvm.org/bugs/show_bug.cgi?id=15557
# and https://bugzilla.redhat.com/show_bug.cgi?id=803433
Patch2:		clang-hardfloat-hack.patch
# Default to a newer -fgnuc-version to get better performance
# out of stuff that does the likes of
# #if __GNUC__ > 5
# // assume SSE and friends are supported
# #else
# // slow workaround
# #endif
Patch3:		clang-default-newer-gnuc-version.patch
# Patches from AOSP
Patch5:		0001-llvm-Make-EnableGlobalMerge-non-static-so-we-can-modify-i.patch
# End AOSP patch section
Patch6:		llvm-11-compiler-rt-cmake-verbose.patch
# Set _GXX_ABI_VERSION correctly while pretending to be a newer gcc
Patch7:		clang-gcc-compat.patch
# Support -fuse-ld=XXX properly
Patch8:		clang-fuse-ld.patch
Patch9:		lld-10.0.1-format.patch
Patch10:	lldb-9.0.0-swig-compile.patch
#Patch12:	llvm-3.8.0-sonames.patch
# Silently turn -O9 into -O3 etc. for increased gcc compatibility
Patch13:	llvm-3.8.0-fix-optlevel.patch
Patch14:	llvm-10.0-fix-m32.patch
Patch16:	clang-rename-fix-linkage.patch
#Patch17:	lld-4.0.0-fix-build-with-libstdc++.patch
# Enable --no-undefined, --as-needed, --enable-new-dtags,
# --hash-style=gnu, --warn-common, --icf=safe, --build-id=sha1,
# -O by default
Patch19:	lld-default-settings.patch
# Patches for musl support, (partially) stolen from Alpine Linux and ported
Patch20:	llvm-3.7-musl.patch
Patch22:	lld-9.0-error-on-option-conflict.patch
Patch23:	llvm-9.0-lld-workaround.patch
Patch24:	llvm-11-flang-missing-docs.patch
#Patch25:	llvm-7.0-compiler-rt-arches.patch
Patch27:	compiler-rt-7.0.0-workaround-i386-build-failure.patch
# http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.6-remove-lgcc-when-using-compiler-rt.patch
# breaks exception handling -- removes gcc_eh
Patch29:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.6-fix-unwind-chain-inclusion.patch
Patch31:	http://git.alpinelinux.org/cgit/aports/plain/main/llvm/clang-3.5-fix-stdint.patch
Patch40:	libc++-3.7.0-musl-compat.patch
# Make it possible to override CLANG_LIBDIR_SUFFIX
# (that is used only to find LLVMgold.so)
# https://llvm.org/bugs/show_bug.cgi?id=23793
Patch43:	clang-0002-cmake-Make-CLANG_LIBDIR_SUFFIX-overridable.patch
# Fix library versioning
Patch46:	llvm-4.0.1-libomp-versioning.patch
# Fix mcount name for arm and armv8
# https://llvm.org/bugs/show_bug.cgi?id=27248
Patch48:	llvm-3.8.0-mcount-name.patch
# Show more information when aborting because posix_spawn failed
# (happened in some qemu aarch64 chroots)
Patch51:	llvm-4.0.1-debug-posix_spawn.patch
# Polly LLVM OpenMP backend
Patch56:	polly-8.0-default-llvm-backend.patch
#Patch57:	tsan-realpath-redefinition.patch
# libomp needs to link to libm so it can see
# logbl and fmaxl when using compiler-rt
Patch58:	llvm-10-omp-needs-libm.patch
# Use ELFv2 ABI even for big-endian PPC64
# for compatibility with LLD
Patch59:	llvm-12.0-ppc64-elfv2-abi.patch
# Really a patch -- but we want to apply it conditionally
# and we use %%autosetup for other patches...
Source62:	llvm-10-default-compiler-rt.patch
# Another patch, applied conditionally
Source63:	llvm-riscv-needs-libatomic-linkage.patch
# SPIR-V fixes
Patch90:	spirv-fix-warnings.patch
Patch91:	SPRIV-Tools-soname.patch
BuildRequires:	bison
BuildRequires:	binutils-devel
BuildRequires:	chrpath
BuildRequires:	flex
BuildRequires:	pkgconfig(libedit)
BuildRequires:	pkgconfig(libelf)
BuildRequires:	pkgconfig(lua)
%if %{without bootstrap}
BuildRequires:	graphviz
# Without this, generating man pages fails
# Handler <function process_automodsumm_generation at 0x7fa70fc2a5e0> for event 'builder-inited' threw an exception (exception: No module named 'lldb')
BuildRequires:	lldb
%endif
BuildRequires:	chrpath
BuildRequires:	groff
BuildRequires:	libtool
BuildRequires:	pkgconfig(ncursesw)
BuildRequires:	python-sphinx
# For sphinx plugins
BuildRequires:	python-recommonmark
BuildRequires:	python-sphinxcontrib-websupport
BuildRequires:	python-sphinx-automodapi
BuildRequires:	python-setuptools
BuildRequires:	python-requests
%if %{with ocaml}
BuildRequires:	ocaml-compiler
BuildRequires:	ocaml-compiler-libs
BuildRequires:	ocaml-camlp4
BuildRequires:	ocaml-findlib >= 1.5.5-2
BuildRequires:	ocaml-ctypes
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
BuildRequires:	pkgconfig(icu-i18n)
%ifnarch riscv64
BuildRequires:	atomic-devel
%endif
BuildRequires:	python >= 3.4
BuildRequires:	python3dist(pyyaml)
BuildRequires:	python3dist(pygments)
# Make sure lld doesn't install its own copy
BuildRequires:	python-six
BuildRequires:	cmake
BuildRequires:	ninja
%if %{with apidox}
BuildRequires:	doxygen
%endif
Obsoletes:	llvm-ocaml < 14.0.0
# Some cmake files try to look up the commit hash
BuildRequires:	git-core
# For lldb
BuildRequires:	swig
BuildRequires:	pkgconfig(python3)
BuildRequires:	gcc
BuildRequires:	pkgconfig(libtirpc)
%if !%{with lld}
BuildRequires:	lld < %{EVRD}
%endif
%if %{with openmp}
Requires:	%{ompname} = %{EVRD}
%endif
%if %{with compat32}
BuildRequires:	devel(libffi)
BuildRequires:	devel(libxml2)
BuildRequires:	devel(libelf)
# For Polly
BuildRequires:	devel(libgmp)
BuildRequires:	devel(libisl)
%endif
%ifarch %{armx} %{ix86} %{riscv}
# Temporary workaround for missing libunwind.so
BuildRequires:	llvm-devel
%ifarch %{ix86}
BuildRequires:	libunwind-devel
%endif
%endif
# for libGPURuntime in Polly
%ifnarch %{riscv}
BuildRequires:	pkgconfig(OpenCL)
BuildRequires:	mesa-opencl-devel
%endif
%if %{with compat32} && ! %{with bootstrap32}
BuildRequires:	devel(libOpenCL)
BuildRequires:	devel(libMesaOpenCL)
BuildRequires:	libunwind-devel
%endif

Obsoletes:	%{mklibname LLVMRISCVCodeGen 5} < %{EVRD}
Obsoletes:	%{mklibname LLVMRISCVDesc 5} < %{EVRD}
Obsoletes:	%{mklibname LLVMRISCVInfo 5} < %{EVRD}
Obsoletes:	%{mklibname lldConfig 5} < %{EVRD}

%if %{with crosscrt}
%ifnarch %{aarch64}
BuildRequires:	cross-aarch64-openmandriva-linux-gnu-binutils
BuildRequires:	cross-aarch64-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-aarch64-openmandriva-linux-gnu-libc
BuildRequires:	cross-aarch64-openmandriva-linux-gnu-kernel-headers
%endif
%ifnarch %{arm}
BuildRequires:	cross-armv7hnl-openmandriva-linux-gnueabihf-binutils
BuildRequires:	cross-armv7hnl-openmandriva-linux-gnueabihf-gcc-bootstrap
BuildRequires:	cross-armv7hnl-openmandriva-linux-gnueabihf-libc
BuildRequires:	cross-armv7hnl-openmandriva-linux-gnueabihf-kernel-headers
%endif
%ifnarch %{ix86}
BuildRequires:	cross-i686-openmandriva-linux-gnu-binutils
BuildRequires:	cross-i686-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-i686-openmandriva-linux-gnu-libc
BuildRequires:	cross-i686-openmandriva-linux-gnu-kernel-headers
%endif
%ifnarch ppc64le
BuildRequires:	cross-ppc64le-openmandriva-linux-gnu-binutils
BuildRequires:	cross-ppc64le-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-ppc64le-openmandriva-linux-gnu-libc
BuildRequires:	cross-ppc64le-openmandriva-linux-gnu-kernel-headers
%endif
%ifnarch ppc64
BuildRequires:	cross-ppc64-openmandriva-linux-gnu-binutils
BuildRequires:	cross-ppc64-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-ppc64-openmandriva-linux-gnu-libc
BuildRequires:	cross-ppc64-openmandriva-linux-gnu-kernel-headers
%endif
%ifnarch %{riscv64}
BuildRequires:	cross-riscv64-openmandriva-linux-gnu-binutils
BuildRequires:	cross-riscv64-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-riscv64-openmandriva-linux-gnu-libc
BuildRequires:	cross-riscv64-openmandriva-linux-gnu-kernel-headers
%endif
%ifnarch %{x86_64}
BuildRequires:	cross-x86_64-openmandriva-linux-gnu-binutils
BuildRequires:	cross-x86_64-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-x86_64-openmandriva-linux-gnu-libc
BuildRequires:	cross-x86_64-openmandriva-linux-gnu-kernel-headers
%endif
%endif

%description
LLVM is a robust system, particularly well suited for developing new mid-level
language-independent analyses and optimizations of all sorts, including those
that require  extensive interprocedural analysis. LLVM is also a great target
for front-end development for conventional or research programming languages,
including those which require compile-time, link-time, or run-time optimization 
for effective implementation, proper tail calls or garbage collection.

%files
%{_bindir}/FileCheck
%{_bindir}/bugpoint
%{_bindir}/count
%{_bindir}/c-index-test
%{_bindir}/dsymutil
%{_bindir}/git-clang-format
%{_bindir}/llc
%{_bindir}/lli
%{_bindir}/lli-child-target
%{_bindir}/opt
%{_bindir}/llvm-addr2line
%{_bindir}/llvm-ar
%{_bindir}/llvm-as
%{_bindir}/llvm-bcanalyzer
%{_bindir}/llvm-cat
%{_bindir}/llvm-c-test
%{_bindir}/llvm-cfi-verify
%{_bindir}/llvm-cvtres
%{_bindir}/llvm-cxxfilt
%{_bindir}/llvm-cxxmap
%{_bindir}/llvm-diff
%{_bindir}/llvm-dis
%{_bindir}/llvm-dwp
%{_bindir}/llvm-exegesis
%{_bindir}/llvm-extract
%{_bindir}/llvm-gsymutil
%{_bindir}/llvm-ifs
%{_bindir}/llvm-install-name-tool
%{_bindir}/llvm-reduce
%{_bindir}/llvm-jitlink
%{_bindir}/llvm-lib
%{_bindir}/llvm-link
%{_bindir}/llvm-lipo
%{_bindir}/llvm-lto
%{_bindir}/llvm-lto2
%{_bindir}/llvm-mc
%{_bindir}/llvm-mca
%{_bindir}/llvm-ml
%{_bindir}/llvm-nm
%{_bindir}/llvm-objdump
%{_bindir}/llvm-objcopy
%{_bindir}/llvm-omp-device-info
%{_bindir}/llvm-otool
%{_bindir}/llvm-sim
%{_bindir}/llvm-tapi-diff
%{_bindir}/llvm-windres
%{_bindir}/llvm-bitcode-strip
%{_bindir}/llvm-jitlink-executor
%{_bindir}/llvm-libtool-darwin
%{_bindir}/llvm-profgen
%{_bindir}/llvm-debuginfod-find
%{_bindir}/llvm-tli-checker
%{_bindir}/split-file
%{_bindir}/llvm-pdbutil
%{_bindir}/llvm-ranlib
%{_bindir}/llvm-rc
%{_bindir}/llvm-readelf
%{_bindir}/llvm-readobj
%{_bindir}/llvm-split
%{_bindir}/llvm-strip
%{_bindir}/llvm-undname
%{_bindir}/llvm-cov
%{_bindir}/llvm-dwarfdump
%{_bindir}/llvm-modextract
%{_bindir}/llvm-opt-report
%{_bindir}/llvm-PerfectShuffle
%{_bindir}/llvm-profdata
%{_bindir}/llvm-rtdyld
%{_bindir}/llvm-size
%{_bindir}/llvm-stress
%{_bindir}/llvm-strings
%{_bindir}/llvm-symbolizer
%{_bindir}/llvm-tblgen
%{_bindir}/llvm-cxxdump
%{_bindir}/llvm-xray
%if !%{with lld}
%{_bindir}/llvm-dlltool
%{_bindir}/llvm-mt
%{_bindir}/llvm-readelf
%endif

%{_bindir}/sancov
%{_bindir}/sanstats
%{_bindir}/verify-uselistorder
%{_bindir}/obj2yaml
%{_bindir}/wasm-ld
%{_bindir}/yaml2obj
%{_bindir}/yaml-bench
%{_bindir}/not

%doc %{_mandir}/man1/FileCheck.1*
%doc %{_mandir}/man1/bugpoint.1*

%doc %{_mandir}/man1/dsymutil.1*
%doc %{_mandir}/man1/lit.1*
%doc %{_mandir}/man1/llc.1*
%doc %{_mandir}/man1/lli.1*
%doc %{_mandir}/man1/llvm-*.1*
%doc %{_mandir}/man1/opt.1*

%doc %{_mandir}/man1/tblgen.1*
%doc %{_mandir}/man1/mlir-tblgen.1*

#-----------------------------------------------------------
%define LLVMLibs LLVMAArch64AsmParser LLVMAArch64CodeGen LLVMAArch64Desc LLVMAArch64Disassembler LLVMAArch64Info LLVMAArch64Utils LLVMAggressiveInstCombine LLVMARMAsmParser LLVMARMCodeGen LLVMARMDesc LLVMARMDisassembler LLVMARMInfo LLVMARMUtils LLVMAnalysis LLVMAsmParser LLVMAsmPrinter LLVMBPFAsmParser LLVMBitReader LLVMBitstreamReader LLVMBitWriter LLVMBPFCodeGen LLVMBPFDesc LLVMBPFDisassembler LLVMBPFInfo LLVMBinaryFormat LLVMCodeGen LLVMCore LLVMDebugInfoCodeView LLVMCoroutines LLVMDebugInfoDWARF LLVMDebugInfoMSF LLVMDebugInfoPDB LLVMDemangle LLVMDlltoolDriver LLVMExecutionEngine LLVMFuzzMutate LLVMHexagonAsmParser LLVMHexagonCodeGen LLVMHexagonDesc LLVMHexagonDisassembler LLVMHexagonInfo LLVMIRReader LLVMInstCombine LLVMInstrumentation LLVMInterpreter LLVMLanaiAsmParser LLVMLanaiCodeGen LLVMLanaiDesc LLVMLanaiDisassembler LLVMLanaiInfo LLVMLTO LLVMLibDriver LLVMLineEditor LLVMLinker LLVMMC LLVMMCDisassembler LLVMMCJIT LLVMMCParser LLVMMIRParser LLVMMSP430CodeGen LLVMMSP430Desc LLVMMSP430Info LLVMMipsAsmParser LLVMMipsCodeGen LLVMMipsDesc LLVMMipsDisassembler LLVMMipsInfo LLVMNVPTXCodeGen LLVMNVPTXDesc LLVMNVPTXInfo LLVMObjCARCOpts LLVMObject LLVMOption LLVMOrcJIT LLVMPasses LLVMPowerPCAsmParser LLVMPowerPCCodeGen LLVMPowerPCDesc LLVMPowerPCDisassembler LLVMPowerPCInfo LLVMProfileData LLVMAMDGPUAsmParser LLVMAMDGPUCodeGen LLVMAMDGPUDesc LLVMAMDGPUDisassembler LLVMAMDGPUInfo LLVMAMDGPUUtils LLVMRuntimeDyld LLVMScalarOpts LLVMSelectionDAG LLVMSparcAsmParser LLVMSparcCodeGen LLVMSparcDesc LLVMSparcDisassembler LLVMSparcInfo LLVMSupport LLVMSymbolize LLVMSystemZAsmParser LLVMSystemZCodeGen LLVMSystemZDesc LLVMSystemZDisassembler LLVMSystemZInfo LLVMTableGen LLVMTarget LLVMTransformUtils LLVMVectorize LLVMWindowsManifest LLVMX86AsmParser LLVMX86CodeGen LLVMX86Desc LLVMX86Disassembler LLVMX86Info LLVMXCoreCodeGen LLVMXCoreDesc LLVMXCoreDisassembler LLVMXCoreInfo LLVMXRay LLVMipo LLVMCoverage LLVMGlobalISel LLVMObjectYAML LLVMMCA LLVMMSP430AsmParser LLVMMSP430Disassembler LLVMRemarks LLVMTextAPI LLVMWebAssemblyAsmParser LLVMWebAssemblyCodeGen LLVMWebAssemblyDesc LLVMWebAssemblyDisassembler LLVMWebAssemblyInfo Remarks LLVMRISCVAsmParser LLVMRISCVCodeGen LLVMRISCVDesc LLVMRISCVDisassembler LLVMRISCVInfo LLVMDebugInfoGSYM LLVMJITLink LLVMCFGuard LLVMDWARFLinker LLVMFrontendOpenMP LLVMAVRAsmParser LLVMAVRCodeGen LLVMAVRDesc LLVMAVRDisassembler LLVMAVRInfo LLVMExtensions LLVMFrontendOpenACC LLVMFileCheck LLVMInterfaceStub LLVMOrcShared LLVMOrcTargetProcess Polly LLVMCFIVerify LLVMDWP LLVMExegesis LLVMExegesisAArch64 LLVMExegesisMips LLVMExegesisPowerPC LLVMExegesisX86 LLVMTableGenGlobalISel LLVMWebAssemblyUtils LLVMSPIRVLib LLVMAMDGPUTargetMCA LLVMDebuginfod LLVMDiff LLVMVEAsmParser LLVMVECodeGen LLVMVEDesc LLVMVEDisassembler LLVMVEInfo LLVMX86TargetMCA
# Removed in 14: LLVMMCACustomBehaviourAMDGPU

%define LLVM64Libs findAllSymbols

%define ClangLibs LTO clang clang-cpp clangAnalysisFlowSensitive clangAnalysis clangAPINotes clangARCMigrate clangASTMatchers clangAST clangBasic clangCodeGen clangCrossTU clangDependencyScanning clangDirectoryWatcher clangDriver clangDynamicASTMatchers clangEdit clangFormat clangFrontend clangFrontendTool clangHandleCXX clangHandleLLVM clangIndexSerialization clangIndex clangInterpreter clangLex clangParse clangRewriteFrontend clangRewrite clangSema clangSerialization clangStaticAnalyzerCheckers clangStaticAnalyzerCore clangStaticAnalyzerFrontend clangTesting clangToolingASTDiff clangToolingCore clangToolingInclusions clangToolingRefactoring clangTooling clangToolingSyntax clangTransformer

%define Clang64Libs clangApplyReplacements clangChangeNamespace clangDaemon clangDaemonTweaks clangDoc clangIncludeFixer clangIncludeFixerPlugin clangMove clangQuery clangReorderFields clangTidy clangTidyPlugin clangTidyAbseilModule clangTidyAlteraModule clangTidyAndroidModule clangTidyBoostModule clangTidyBugproneModule clangTidyCERTModule clangTidyCppCoreGuidelinesModule clangTidyConcurrencyModule clangTidyDarwinModule clangTidyFuchsiaModule clangTidyGoogleModule clangTidyHICPPModule clangTidyLLVMModule clangTidyLinuxKernelModule clangTidyMiscModule clangTidyModernizeModule clangTidyMPIModule clangTidyObjCModule clangTidyOpenMPModule clangTidyPortabilityModule clangTidyReadabilityModule clangTidyPerformanceModule clangTidyZirconModule clangTidyUtils clangTidyLLVMLibcModule clangTidyMain clangdRemoteIndex clangdSupport

%define FlangLibs FIRBuilder FIRCodeGen FIRDialect FIRSupport FIRTransforms FortranCommon FortranDecimal FortranEvaluate FortranLower FortranParser FortranRuntime FortranSemantics flangFrontend flangFrontendTool
# Removed in 14: FIROptimizer

%define BOLTLibs Core Passes Profile Rewrite RuntimeLibs TargetAArch64 TargetX86 Utils

%if %{with mlir}
%define MLIRLibs MLIRAffineAnalysis MLIRAffineBufferizableOpInterfaceImpl MLIRAffine MLIRAffineToStandard MLIRAffineTransforms MLIRAffineTransformsTestPasses MLIRAffineUtils MLIRAMX MLIRAMXToLLVMIRTranslation MLIRAMXTransforms MLIRAnalysis MLIRArithmetic MLIRArithmeticToLLVM MLIRArithmeticToSPIRV MLIRArithmeticTransforms MLIRArmNeon2dToIntr MLIRArmNeon MLIRArmNeonToLLVMIRTranslation MLIRArmSVE MLIRArmSVEToLLVMIRTranslation MLIRArmSVETransforms MLIRAsync MLIRAsyncToLLVM MLIRAsyncTransforms MLIRBufferization MLIRBufferizationToMemRef MLIRBufferizationTransforms MLIRCallInterfaces MLIRCAPIAsync MLIRCAPIConversion MLIRCAPIDebug MLIRCAPIExecutionEngine MLIRCAPIGPU MLIRCAPIInterfaces MLIRCAPIIR MLIRCAPILinalg MLIRCAPILLVM MLIRCAPIPDL MLIRCAPIQuant MLIRCAPIRegistration MLIRCAPISCF MLIRCAPIShape MLIRCAPISparseTensor MLIRCAPIStandard MLIRCAPITensor MLIRCAPITransforms MLIRCastInterfaces MLIRComplex MLIRComplexToLLVM MLIRComplexToStandard MLIRControlFlowInterfaces MLIRCopyOpInterface MLIRDataLayoutInterfaces MLIRDerivedAttributeOpInterface MLIRDialect MLIRDialectUtils MLIRDLTI MLIRDLTITestPasses MLIREmitC MLIRExecutionEngine MLIRGPUOps MLIRGPUTestPasses MLIRGPUToGPURuntimeTransforms MLIRGPUToNVVMTransforms MLIRGPUToROCDLTransforms MLIRGPUToSPIRV MLIRGPUToVulkanTransforms MLIRGPUTransforms MLIRInferTypeOpInterface MLIRIR MLIRJitRunner MLIRLinalgAnalysis MLIRLinalgBufferizableOpInterfaceImpl MLIRLinalg MLIRLinalgTestPasses MLIRLinalgToLLVM MLIRLinalgToSPIRV MLIRLinalgToStandard MLIRLinalgTransforms MLIRLinalgUtils MLIRLLVMCommonConversion MLIRLLVMIR MLIRLLVMIRTransforms MLIRLLVMToLLVMIRTranslation MLIRLoopLikeInterface MLIRLspServerLib MLIRMath MLIRMathTestPasses MLIRMathToLibm MLIRMathToLLVM MLIRMathToSPIRV MLIRMathTransforms MLIRMemRef MLIRMemRefToLLVM MLIRMemRefToSPIRV MLIRMemRefTransforms MLIRMemRefUtils MLIRMlirOptMain MLIRNVVMIR MLIRNVVMToLLVMIRTranslation MLIROpenACC MLIROpenACCToLLVMIRTranslation MLIROpenACCToLLVM MLIROpenACCToSCF MLIROpenMP MLIROpenMPToLLVMIRTranslation MLIROpenMPToLLVM MLIROptLib MLIRParser MLIRPass MLIRPDLInterp MLIRPDLLAST MLIRPDLLParser MLIRPDL MLIRPDLToPDLInterp MLIRPresburger MLIRQuant MLIRReconcileUnrealizedCasts MLIRReduceLib MLIRReduce MLIRRewrite MLIRROCDLIR MLIRROCDLToLLVMIRTranslation MLIRSCF MLIRSCFTestPasses MLIRSCFToGPU MLIRSCFToOpenMP MLIRSCFToSPIRV MLIRSCFToStandard MLIRSCFTransforms MLIRShapeOpsTransforms MLIRShape MLIRShapeTestPasses MLIRShapeToStandard MLIRSideEffectInterfaces MLIRSparseTensor MLIRSparseTensorTransforms MLIRSparseTensorUtils MLIRSPIRVBinaryUtils MLIRSPIRVConversion MLIRSPIRVDeserialization MLIRSPIRVModuleCombiner MLIRSPIRVSerialization MLIRSPIRV MLIRSPIRVTestPasses MLIRSPIRVToLLVM MLIRSPIRVTransforms MLIRSPIRVTranslateRegistration MLIRSPIRVUtils MLIRStandardOpsTestPasses MLIRStandardOpsTransforms MLIRStandard MLIRStandardToLLVM MLIRStandardToSPIRV MLIRSupportIndentedOstream MLIRSupport MLIRTargetCpp MLIRTargetLLVMIRExport MLIRTargetLLVMIRImport MLIRTensorInferTypeOpInterfaceImpl MLIRTensor MLIRTensorTransforms MLIRTestAnalysis MLIRTestDialect MLIRTestIR MLIRTestPass MLIRTestReducer MLIRTestRewrite MLIRTestStandardToLLVM MLIRTestTransforms MLIRTilingInterface MLIRToLLVMIRTranslationRegistration MLIRTosa MLIRTosaTestPasses MLIRTosaToLinalg MLIRTosaToSCF MLIRTosaToStandard MLIRTosaTransforms MLIRTransforms MLIRTransformUtils MLIRTranslation MLIRVectorInterfaces MLIRVector MLIRVectorTestPasses MLIRVectorToGPU MLIRVectorToLLVM MLIRVectorToROCDL MLIRVectorToSCF MLIRVectorToSPIRV MLIRViewLikeInterface MLIRX86Vector MLIRX86VectorToLLVMIRTranslation MLIRX86VectorTransforms mlir_async_runtime mlir_c_runner_utils mlir_runner_utils MLIRModuleBufferization MLIRTensorTilingInterfaceImpl MLIRTensorUtils MLIRMemRefTestPasses MLIRSCFUtils MLIRSparseTensorPipelines MLIRVectorTransforms MLIRVectorUtils

# Removed in 14: MLIRLoopAnalysis
%else
%define MLIRLibs %{nil}
%endif

%if %{with lld}
%define LLDLibs lldCOFF lldCommon lldELF lldMachO lldMinGW lldWasm
%else
%define LLDLibs %{nil}
%endif
# Removed as of 14: lldCore lldDriver lldMachO2 lldReaderWriter lldYAML

%if %{with lldb}
%define LLDBLibs lldb lldbIntelFeatures
%else
%define LLDBLibs %{nil}
%endif

%{expand:%(for i in %{LLVMLibs} %{LLVM64Libs} %{ClangLibs} %{Clang64Libs} %{LLDLibs} %{LLDBLibs} %{MLIRLibs}; do echo %%libpackage $i %{major1}; [ "$i" = "clang" ] && echo "%{_libdir}/libclang.so.13"; done)}

%if %{with flang}
%{expand:%(for i in %{FlangLibs}; do echo %%libpackage $i %{major1}; done)}
%endif

%if %{with bolt}
%{expand:%(for i in %{BOLTLibs}; do echo %%libpackage LLVMBOLT$i %{major1}; done)}
%endif

%if %{with compat32}
%{expand:%(for i in %{LLVMLibs} %{ClangLibs}; do cat <<EOF
%%package -n lib${i}%{major1}
Summary:	32-bit LLVM ${i} library
Group:		Development/C

%%description -n lib${i}%{major1}
32-bit LLVM ${i} library.

%%files -n lib${i}%{major1}
%%{_prefix}/lib/lib${i}.so.%{major1}*
EOF
[ "$i" = "clang" ] && echo %{_prefix}/lib/libclang.so.13
done)}
%endif

%if %{with unwind}
%define libunwind_major 1.0
%define libunwind %mklibname unwind %{libunwind_major}
%define devunwind %mklibname -d unwind

%package -n %{libunwind}
Summary:	The LLVM unwind library
Group:		System/Libraries

%description -n %{libunwind}
The unwind library, a part of llvm.

%files -n %{libunwind}
%{_libdir}/libunwind.so.%{libunwind_major}
%{_libdir}/libunwind.so.1

%package -n %{devunwind}
Summary:	Development files for libunwind
Group:		Development/C
Requires:	%{libunwind} = %{EVRD}

%description -n %{devunwind}
Development files for libunwind.

%files -n %{devunwind}
%doc %{_docdir}/LLVM/libunwind
%{_libdir}/libunwind.a
%{_libdir}/libunwind.so
%if %{with default_compilerrt}
%{_libdir}/pkgconfig/libunwind.pc
%else
%{_libdir}/pkgconfig/libunwind-llvm.pc
%endif
%{_includedir}/unwind.h
%{_includedir}/libunwind.h
%{_includedir}/__libunwind_config.h
%endif

#-----------------------------------------------------------
%if %{with libcxx}
%libpackage c++ 1
%libpackage c++abi 1
%{_libdir}/libc++abi.so
%{_libdir}/libc++.a

%define cxxdevname %mklibname c++ -d
%define cxxabistatic %mklibname c++abi -d -s

%package -n %{cxxdevname}
Summary:	Development files for libc++, an alternative implementation of the STL
Group:		Development/C
Requires:	%{mklibname c++ 1} = %{EVRD}
Requires:	%{mklibname c++abi 1} = %{EVRD}
Provides:	c++-devel = %{EVRD}

%description -n %{cxxdevname}
Development files for libc++, an alternative implementation of the STL.

%files -n %{cxxdevname}
%doc %{_docdir}/LLVM/libcxx
%{_includedir}/c++
%{_includedir}/__pstl*
%{_includedir}/pstl
%{_prefix}/lib/cmake/ParallelSTL
%{_libdir}/libc++experimental.a

%package -n %{cxxabistatic}
Summary:	Static library for libc++ C++ ABI support
Group:		Development/C
Requires:	%{cxxdevname} = %{EVRD}

%description -n %{cxxabistatic}
Static library for libc++'s C++ ABI library.

%files -n %{cxxabistatic}
%{_libdir}/libc++abi.a
%endif

#-----------------------------------------------------------
%define libname %mklibname %{name} %{major}

%package -n %{libname}
Summary:	LLVM shared libraries
Group:		System/Libraries
Conflicts:	llvm < 3.0-4
Obsoletes:	%{mklibname %{name} 3.5.0} < 14.0.0
Obsoletes:	%{mklibname %{name} 3.6.0} < 14.0.0
%{expand:%(for i in %{LLVMLibs} %{LLVM64Libs}; do echo Requires:	%%{mklibname $i %{major1}} = %{EVRD}; done)}
Obsoletes:	%{mklibname LLVMCppBackendCodeGen 3} < 14.0.0
Obsoletes:	%{mklibname LLVMCppBackendInfo 3} < 14.0.0
Obsoletes:	%{mklibname LLVMAArch64AsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMARMAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMLanaiAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMMSP430AsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMMipsAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMNVPTXAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMPowerPCAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMAMDGPUAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMSparcAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMSystemZAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMX86AsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMXCoreAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMWebAssemblyAsmPrinter 9} < 14.0.0
Obsoletes:	%{mklibname LLVMRISCVAsmPrinter 9} < 14.0.0
%rename		%{mklibname LLVMLTO 11}
%rename		%{mklibname clangCodeGen 11}
Obsoletes:	%{mklibname clang-cpp 11} < 14.0.0
Obsoletes:	%{mklibname LLVMExtensions 11} < 14.0.0

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
# Have to do those manually because we filter
# devel(*) deps for clang
Requires:	pkgconfig(libedit)
Requires:	ffi-devel
Requires:	pkgconfig(ncursesw)
Requires:	stdc++-devel
Requires:	pkgconfig(zlib)
%if %{with mlir}
# Required because of references in LLVMExports.cmake
Requires:	llvm-mlir-tools = %{EVRD}
%endif
# Back to regular dependencies
%if %{with openmp}
Provides:	openmp-devel = %{EVRD}
Requires:	%{ompname} = %{EVRD}
%if "%{_lib}" == "lib64"
Provides:	devel(libomp(64bit))
%else
Provides:	devel(libomp)
%endif
%endif
%ifnarch %{riscv}
Requires:	%{_lib}gpuruntime
BuildRequires:	%{_lib}gpuruntime
%endif

%description -n %{devname}
This package contains the development files for LLVM.

%files -n %{devname}
%{_bindir}/%{name}-config
%{_includedir}/%{name}
%{_includedir}/%{name}-c
%{_libdir}/cmake/%{name}
%{_libdir}/lib*.so
# FIXME this needs a real soname
%exclude %{_libdir}/libSPIRV-Tools-shared.so
%ifnarch %{riscv}
%exclude %{_libdir}/libGPURuntime.so
%endif
%ifnarch %{arm}
%{_libdir}/libarcher_static.a
%endif
%if %{with openmp}
%exclude %{_libdir}/libomp.so
%endif
%if %{with libcxx}
%exclude %{_libdir}/libc++abi.so
%endif
# Stuff from clang
%exclude %{_libdir}/libclang*.so
%exclude %{_libdir}/libLTO.so
%exclude %{_libdir}/libPolly.so
%exclude %{_libdir}/libPollyISL.so
%exclude %{_libdir}/libPollyPPCG.so

#-----------------------------------------------------------
%if %{with openmp}
%package -n %{ompname}
Summary:	LLVM OpenMP shared libraries
Group:		System/Libraries
# For libomp.so compatibility (see comment in file list)
%if "%{_lib}" == "lib64"
Provides:	libomp.so()(64bit)
Provides:	libomp.so(GOMP_1.0)(64bit)
Provides:	libomp.so(GOMP_2.0)(64bit)
Provides:	libomp.so(GOMP_3.0)(64bit)
Provides:	libomp.so(GOMP_4.0)(64bit)
Provides:	libomp.so(OMP_1.0)(64bit)
Provides:	libomp.so(OMP_2.0)(64bit)
Provides:	libomp.so(OMP_3.0)(64bit)
Provides:	libomp.so(OMP_3.1)(64bit)
Provides:	libomp.so(OMP_4.0)(64bit)
Provides:	libomp.so(VERSION)(64bit)
%else
Provides:	libomp.so
Provides:	libomp.so(GOMP_1.0)
Provides:	libomp.so(GOMP_2.0)
Provides:	libomp.so(GOMP_3.0)
Provides:	libomp.so(GOMP_4.0)
Provides:	libomp.so(OMP_1.0)
Provides:	libomp.so(OMP_2.0)
Provides:	libomp.so(OMP_3.0)
Provides:	libomp.so(OMP_3.1)
Provides:	libomp.so(OMP_4.0)
Provides:	libomp.so(VERSION)
%endif

%description -n %{ompname}
Shared libraries for LLVM OpenMP support.

%files -n %{ompname}
%doc %{_docdir}/LLVM/openmp
# (Slightly) nonstandard behavior: We package the .so
# file in the library package.
# This is because upstream doesn't assign sonames, and
# by keeping the .so we can keep compatible with binaries
# built against upstream libomp
%{_libdir}/libomp.so*
%ifnarch armv7hnl
%{_includedir}/ompt-multiplex.h
%endif
# FIXME why isn't this in %{_libdir}?
%{_prefix}/lib/libomptarget.rtl.amdgpu.so
%doc %{_mandir}/man1/llvmopenmp.1*
%{_libdir}/libomptarget-*.bc
%endif

#-----------------------------------------------------------

%package doc
Summary:	Documentation for LLVM
Group:		Books/Computer books
Requires:	%{name} = %{version}
BuildArch:	noarch
Obsoletes:	llvm-doc-devel < 6.0.0

%description doc
Documentation for the LLVM compiler infrastructure.

%files doc
%doc %dir %{_docdir}/LLVM
%doc %{_docdir}/LLVM/llvm

#-----------------------------------------------------------
%package polly
Summary:	Polyhedral optimizations for LLVM
License:	MIT
Group:		Development/Other
Obsoletes:	llvm-devel < 4.0.1
Obsoletes:	%{_lib}llvm-devel < 4.0.1
Conflicts:	%{_lib}llvm-devel < 4.0.1

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
%{_libdir}/LLVMPolly.so
# Unversioned library, not -devel file
%{_libdir}/libPollyISL.so
%{_libdir}/libPollyPPCG.so
%doc %{_mandir}/man1/polly.1*

#-----------------------------------------------------------
%package polly-devel
Summary:	Development files for Polly
License:	MIT
Group:		Development/Other
Requires:	%{name}-polly = %{EVRD}

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
%doc %{_docdir}/LLVM/polly
%{_includedir}/polly
%{_libdir}/cmake/polly
%{_libdir}/libPolly.so
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
%if %{with unwind} && %{with default_compilerrt}
Requires:	%{_lib}unwind1.0 = %{EVRD}
Requires:	%{devunwind} = %{EVRD}
%else
%ifnarch %{riscv}
%ifarch %{ix86}
# Workaround for missing previous packaging change
BuildRequires:	pkgconfig(libunwind)
%else
BuildRequires:	pkgconfig(libunwind-llvm)
%endif
%endif
%endif
Obsoletes:	%{mklibname clang 3.7.0} < 14.0.0
Obsoletes:	%{mklibname clang_shared 9} < 14.0.0
%{expand:%(for i in %{ClangLibs} %{Clang64Libs}; do echo Requires:	%%{mklibname $i %{major1}} = %{EVRD}; done)}

%description -n clang
clang: noun
    1. A loud, resonant, metallic sound.
    2. The strident call of a crane or goose.
    3. C-language family front-end toolkit.

The goal of the Clang project is to create a new C, C++, Objective C
and Objective C++ front-end for the LLVM compiler. Its tools are built
as libraries and designed to be loosely-coupled and extensible.

%files -n clang
%{_bindir}/clang
%{_bindir}/clang-linker-wrapper
%{_bindir}/clang-nvlink-wrapper
%{_bindir}/clang++
%{_bindir}/clang-%{major1}

%{_bindir}/clang-cpp
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
%doc %{_mandir}/man1/clang.1*

#-----------------------------------------------------------

%if %{with bolt}
%package bolt
Summary:	Binary optimizer for LLVM
License:	NCSA
Group:		Development/Other
%{expand:%(for i in %{BOLTLibs}; do echo Requires:	%%{mklibname LLVMBOLT$i %{major1}} = %{EVRD}; done)}

%description bolt
Binary Optimization and Layout Tool - A linux command-line utility used for
optimizing performance of binaries

%files bolt
%doc %{_docdir}/LLVM/bolt
%{_bindir}/llvm-bolt
%{_bindir}/llvm-bolt-heatmap
%{_bindir}/llvm-boltdiff
%{_bindir}/merge-fdata
%{_bindir}/perf2bolt
%ifarch %{x86_64}
# FIXME shouldn't those be in %{_libdir}?
# They're definitely 64 bit
# And is the _osx.a one useful on a real OS at all?
%{_prefix}/lib/libbolt_rt_hugify.a
%{_prefix}/lib/libbolt_rt_instr.a
%{_prefix}/lib/libbolt_rt_instr_osx.a
%endif
#doc %{_docdir}/bolt
%endif

#-----------------------------------------------------------

%package -n clang-tools
Summary:	Various tools for LLVM/clang
Group:		Development/Other
Requires:	clang = %{EVRD}

%description -n clang-tools
A various tools for LLVM/clang.

%files -n clang-tools
%{_bindir}/clang-apply-replacements
%{_bindir}/clang-change-namespace
%{_bindir}/clang-check
%{_bindir}/clang-cl
%{_bindir}/clang-doc
%{_bindir}/clang-extdef-mapping
%{_bindir}/clang-format
%{_bindir}/clang-include-fixer
%{_bindir}/clang-move
%{_bindir}/clang-offload-bundler
%{_bindir}/clang-offload-wrapper
%{_bindir}/clang-query
%{_bindir}/clang-refactor
%{_bindir}/clang-rename
%{_bindir}/clang-repl
%{_bindir}/clang-reorder-fields
%{_bindir}/clang-scan-deps
%{_bindir}/clang-tidy
%{_bindir}/run-clang-tidy
%{_bindir}/clangd
%{_bindir}/diagtool
%{_bindir}/find-all-symbols
%{_bindir}/hmaptool
%{_bindir}/modularize
%{_bindir}/pp-trace
%doc %{_mandir}/man1/diagtool.1*
%doc %{_mandir}/man1/extraclangtools.1*

%define devclang %mklibname -d clang

%package -n %{devclang}
Summary:	Development files for clang
Group:		Development/Other
Requires:	clang = %{EVRD}
Requires:	clang-tools = %{EVRD}
Provides:	clang-devel = %{EVRD}
Conflicts:	llvm-devel < 3.1
Obsoletes:	clang-devel < 3.1
Conflicts:	llvm < 8.0.1-0.359209.2

%description -n %{devclang}
This package contains header files and libraries needed for using
libclang.

%files -n %{devclang}
%{_includedir}/clang
%{_includedir}/clang-c
%{_includedir}/clang-tidy
%{_libdir}/libclang*.so
%{_libdir}/cmake/clang
%{_libdir}/cmake/openmp/FindOpenMPTarget.cmake
%doc %{_mandir}/man1/clang-tblgen.1*

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
%{_datadir}/opt-viewer
%{_bindir}/analyze-build
%{_bindir}/intercept-build
%{_bindir}/scan-build
%{_bindir}/scan-build-py
%{_prefix}/lib/libscanbuild
%{_prefix}/lib/libear
%{_bindir}/scan-view
%{_libexecdir}/ccc-analyzer
%{_libexecdir}/c++-analyzer
%{_libexecdir}/analyze-c++
%{_libexecdir}/analyze-cc
%{_libexecdir}/intercept-c++
%{_libexecdir}/intercept-cc
%{_datadir}/scan-build
%{_datadir}/scan-view
%doc %{_mandir}/man1/scan-build.1*

%package -n clang-doc
Summary:	Documentation for Clang
Group:		Books/Computer books
BuildArch:	noarch
Requires:	%{name} = %{EVRD}

%description -n clang-doc
Documentation for the Clang compiler front-end.

%files -n clang-doc
%doc %{_docdir}/LLVM/clang-tools
%doc %{_docdir}/LLVM/clang
%endif

%if %{with ocaml}
%package -n ocaml-%{name}
Summary:	Objective-CAML bindings for LLVM
Group:		Development/Other
Requires:	%{name} = %{EVRD}

%description -n ocaml-%{name}
Objective-CAML bindings for LLVM.

%files -n ocaml-%{name}
%{_libdir}/ocaml/*
%endif
#-----------------------------------------------------------

%if %{with flang}
%package -n flang
Summary:	A Fortran language front-end for LLVM
License:	NCSA
Group:		Development/Other
Requires:	clang = %{EVRD}
%if %{with unwind}
Requires:	%{_lib}unwind1.0 = %{EVRD}
Requires:	%{devunwind} = %{EVRD}
%endif

%description -n flang
A Fortran language front-end for LLVM

%files -n flang
%{_bindir}/bbc
%{_bindir}/flang
%{_bindir}/flang-new
%{_bindir}/fir-opt
%{_bindir}/f18-parse-demo
%{_bindir}/tco

%define flangdev %mklibname -d flang

%package -n %{flangdev}
Summary:	Development files for Flang, the LLVM Fortran compiler
Group:		Development/Fortran

%description -n %{flangdev}
Development files for Flang, the LLVM Fortran compiler.

%files -n %{flangdev}
%{_includedir}/flang
%{_libdir}/cmake/flang
%endif

#-----------------------------------------------------------

%if %{with lldb}
%package -n lldb
Summary:	Debugger from the LLVM toolchain
Group:		Development/Other
Requires:	python-six
%{expand:%(for i in %{LLDBLibs}; do echo Requires:	%%{mklibname $i %{major1}} = %{EVRD}; done)}

%description -n lldb
Debugger from the LLVM toolchain.

%files -n lldb
%{_bindir}/lldb*
%{_libdir}/python*/site-packages/lldb
%{_prefix}/lib/lua/*/lldb.so
%doc %{_mandir}/man1/lldb.1*
%doc %{_mandir}/man1/lldb-server.1*
%doc %{_mandir}/man1/lldb-tblgen.1*
%doc %{_docdir}/LLVM/lldb

%define lldbdev %mklibname -d lldb

%package -n %{lldbdev}
Summary:	Development files for the LLDB debugger
Group:		Development/Other
Requires:	lldb = %{EVRD}

%description -n %{lldbdev}
Development files for the LLDB debugger.

%files -n %{lldbdev}
%{_includedir}/lldb
%endif

#-----------------------------------------------------------
%if %{with lld}
%package -n lld
Summary:	The linker from the LLVM project
License:	NCSA
Group:		Development/Other
%{expand:%(for i in %{LLDLibs}; do echo Requires:	%%{mklibname $i %{major1}} = %{EVRD}; done)}
# Stuff from lld 3.8 that has been removed in 3.9
Obsoletes:	%{mklibname lldAArch64ELFTarget 3} < 14.0.0
Obsoletes:	%{mklibname lldARMELFTarget 3} < 14.0.0
Obsoletes:	%{mklibname lldELF2 3} < 14.0.0
Obsoletes:	%{mklibname lldExampleSubTarget 3} < 14.0.0
Obsoletes:	%{mklibname lldHexagonELFTarget 3} < 14.0.0
Obsoletes:	%{mklibname lldMipsELFTarget 3} < 14.0.0
Obsoletes:	%{mklibname lldX86ELFTarget 3} < 14.0.0
Obsoletes:	%{mklibname lldX86_64ELFTarget 3} < 14.0.0
# Stuff from lld 5.0 that has been removed in 6.0
Obsoletes:	%{mklibname lldELF 5} < 14.0.0
Obsoletes:	%{mklibname lldConfig 5} < 14.0.0

%description -n lld
The linker from the LLVM project.

%files -n lld
#doc %{_docdir}/lld
%{_bindir}/ld.lld
%{_bindir}/ld64.lld
%{_bindir}/lld
%{_bindir}/lld-link
%{_bindir}/llvm-dlltool
%{_bindir}/llvm-mt
%doc %{_mandir}/man1/ld.lld.1*

#-----------------------------------------------------------

%define devlld %mklibname -d lld

%package -n %{devlld}
Summary:	Development files for lld
Group:		Development/Other
Requires:	lld = %{EVRD}

%description -n %{devlld}
This package contains header files and libraries needed for
writing lld plugins.

%files -n %{devlld}
%doc %{_docdir}/LLVM/lld
%{_includedir}/lld
%{_libdir}/cmake/lld
%endif
#-----------------------------------------------------------

%package -n python-clang
Summary:	Python bindings to parts of the Clang library
Group:		Development/Python

%description -n python-clang
Python bindings to parts of the Clang library

%files -n python-clang
%{python_sitelib}/clang
#-----------------------------------------------------------

%package -n %{_lib}gpuruntime
Summary:	GPU runtime library
Group:		System/Libraries

%description -n %{_lib}gpuruntime
GPU runtime library.

%ifnarch %{riscv}
%files -n %{_lib}gpuruntime
%{_libdir}/libGPURuntime.so
%endif

#-----------------------------------------------------------

%if %{with compat32}
%package -n libllvm-devel
Summary:	32-bit LLVM development files
Group:		Development/C
%{expand:%(for i in %{LLVMLibs}; do echo Requires:	lib${i}%{major1} = %{EVRD}; done)}

%description -n libllvm-devel
32-bit LLVM development files.

%files -n libllvm-devel
%{_prefix}/lib/cmake/clang
%{_prefix}/lib/cmake/llvm
%{_prefix}/lib/libLLVM*.so
%{_prefix}/lib/libLTO.so
%{_prefix}/lib/libRemarks.so
%{_prefix}/lib/libarcher.so
%{_prefix}/lib/libarcher_static.a

%package -n libclang-devel
Summary:	32-bit Clang development files
Group:		Development/C
%{expand:%(for i in %{ClangLibs}; do echo Requires:	lib${i}%{major1} = %{EVRD}; done)}

%description -n libclang-devel
32-bit Clang development files.

%files -n libclang-devel
%{_prefix}/lib/libclang*.so

%package -n libgpuruntime
Summary:	32-bit GPU runtime library
Group:		System/Libraries

%description -n libgpuruntime
32-bit GPU runtime library.

%ifnarch %{riscv}
%if ! %{with bootstrap32}
%files -n libgpuruntime
%{_prefix}/lib/libGPURuntime.so
%endif
%endif

%package -n libomp1
Summary:	32-bit OpenMP runtime
Group:		System/Libraries

%description -n libomp1
32-bit OpenMP runtime.

%files -n libomp1
%{_prefix}/lib/libomp.so.1*
# FIXME does this need a SOVERSION?
%{_prefix}/lib/libompd.so

%package -n libomp-devel
Summary:	Development files for the 32-bit OpenMP runtime
Group:		Development/C

%description -n libomp-devel
Development files for the 32-bit OpenMP runtime.

%files -n libomp-devel
%{_prefix}/lib/libgomp.so
%{_prefix}/lib/libiomp5.so
%{_prefix}/lib/libomp.so
%{_prefix}/lib/libomptarget.so
%{_prefix}/lib/cmake/openmp/FindOpenMPTarget.cmake

%package polly32
Summary:	Polyhedral optimizations for LLVM (32-bit)
License:	MIT
Group:		Development/Other

%description polly32
Polly is a polyhedral optimizer for LLVM.

Using an abstract mathematical representation it analyzes and optimizes
the memory access pattern of a program. This includes data-locality
optimizations for cache locality as well as automatic parallelization
for thread-level and SIMD parallelism.

Our overall goal is an integrated optimizer for data-locality and
parallelism that takes advantage of multi-cores, cache hierarchies,
short vector instructions as well as dedicated accelerators.

%files polly32
%{_prefix}/lib/libPolly.so.*
# Unversioned libraries, not -devel files
%{_prefix}/lib/LLVMPolly.so
%{_prefix}/lib/libPollyISL.so
%{_prefix}/lib/libPollyPPCG.so

%package polly32-devel
Summary:	Development files for Polly (32-bit)
License:	MIT
Group:		Development/Other
Requires:	%{name}-polly32 = %{EVRD}
Requires:	%{name}-polly-devel = %{EVRD}

%description polly32-devel
Development files for Polly.

Polly is a polyhedral optimizer for LLVM.

Using an abstract mathematical representation it analyzes and optimizes
the memory access pattern of a program. This includes data-locality
optimizations for cache locality as well as automatic parallelization
for thread-level and SIMD parallelism.

Our overall goal is an integrated optimizer for data-locality and
parallelism that takes advantage of multi-cores, cache hierarchies,
short vector instructions as well as dedicated accelerators.

%files polly32-devel
%{_prefix}/lib/libPolly.so
%{_prefix}/lib/cmake/polly

%define lib32unwind libunwind%{libunwind_major}
%define dev32unwind libunwind-devel

%package -n %{lib32unwind}
Summary:	The LLVM unwind library (32-bit)
Group:		System/Libraries

%description -n %{lib32unwind}
The unwind library, a part of llvm.

%files -n %{lib32unwind}
%{_prefix}/lib/libunwind.so.%{libunwind_major}
%{_prefix}/lib/libunwind.so.1

%package -n %{dev32unwind}
Summary:	Development files for libunwind (32-bit)
Group:		Development/C
Requires:	%{lib32unwind} = %{EVRD}
Requires:	%{devunwind} = %{EVRD}

%description -n %{dev32unwind}
Development files for libunwind.

%files -n %{dev32unwind}
%{_prefix}/lib/libunwind.a
%{_prefix}/lib/libunwind.so
%if %{with default_compilerrt}
%{_prefix}/lib/pkgconfig/libunwind.pc
%else
%{_prefix}/lib/pkgconfig/libunwind-llvm.pc
%endif
%endif

%if %{with mlir}
#-----------------------------------------------------------
%package mlir-tools
Summary:	Tools for working with MLIR (Multi-Level Intermediate Representation)
Group:		Development/C

%description mlir-tools
Tools for working with MLIR (Multi-Level Intermediate Representation)

The MLIR project is a novel approach to building reusable and extensible
compiler infrastructure. MLIR aims to address software fragmentation,
improve compilation for heterogeneous hardware, significantly reduce
the cost of building domain specific compilers, and aid in connecting
existing compilers together.

%files mlir-tools
%{_bindir}/mlir-*
#-----------------------------------------------------------

%define mlirdev %{mklibname -d mlir}
%package -n %{mlirdev}
Summary:	Development files for MLIR
Group:		Development/C

%description -n %{mlirdev}
Development files for MLIR

The MLIR project is a novel approach to building reusable and extensible
compiler infrastructure. MLIR aims to address software fragmentation,
improve compilation for heterogeneous hardware, significantly reduce
the cost of building domain specific compilers, and aid in connecting
existing compilers together.

%files -n %{mlirdev}
%{_includedir}/mlir
%{_includedir}/mlir-c
%{_libdir}/cmake/mlir
%{_libdir}/libMLIRTableGen.a
#-----------------------------------------------------------
%endif

%package -n libclc
Summary:	Core library of the OpenCL language runtime
Group:		Development/Other
Url:		http://libclc.llvm.org/

%description -n libclc
Core library of the OpenCL language runtime.

%package -n libclc-spirv
Summary:	SPIR-V (Vulkan) backend for the libclc OpenCL library
Group:		System/Libraries
Requires:	libclc = %{EVRD}

%description -n libclc-spirv
SPIR-V (Vulkan) backend for the libclc OpenCL library.

%package -n libclc-r600
Summary:	Radeon 600 (older ATI/AMD GPU) backend for the libclc OpenCL library
Group:		System/Libraries
Requires:	libclc = %{EVRD}

%description -n libclc-r600
Radeon 600 (older ATI/AMD GPU) backend for the libclc OpenCL library.

%package -n libclc-amdgcn
Summary:	AMD GCN (newer ATI/AMD GPU) backend for the libclc OpenCL library
Group:		System/Libraries
Requires:	libclc = %{EVRD}

%description -n libclc-amdgcn
AMD GCN (newer ATI/AMD GPU) backend for the libclc OpenCL library.

%package -n libclc-nvptx
Summary:	Nvidia PTX backend for the libclc OpenCL library
Group:		System/Libraries
Requires:	libclc = %{EVRD}

%description -n libclc-nvptx
Nvidia PTX backend for the libclc OpenCL library.

%if %{without bootstrap}
%files -n libclc
%{_includedir}/clc
%dir %{_datadir}/clc
%{_datadir}/pkgconfig/libclc.pc
# Should this be a separate package? It's an
# OpenCL to Vulkan compute shader compiler.
%{_datadir}/clc/clspv--.bc
%{_datadir}/clc/clspv64--.bc

%files -n libclc-spirv
%{_datadir}/clc/spirv*

%files -n libclc-r600
%{_datadir}/clc/*-r600-*

%files -n libclc-nvptx
%{_datadir}/clc/nvptx*

%files -n libclc-amdgcn
%{_datadir}/clc/*amdgcn*
%endif

%package -n spirv-headers
Summary:	Headers for working with SPIR-V, a language for running on GPUs
Group:		Development/Tools
BuildArch:	noarch

%description -n spirv-headers
This package contains machine-readable files for the SPIR-V Registry.

This includes:

* Header files for various languages.
* JSON files describing the grammar for the SPIR-V core instruction
  set and the extended instruction sets.
* The XML registry file.
* A tool to build the headers from the JSON grammar.

Headers are provided in the include directory, with up-to-date
headers in the unified1 subdirectory. Older headers are provided
according to their version.

%files -n spirv-headers
%{_includedir}/spirv
%dir %{_datadir}/cmake/SPIRV-Headers
%{_datadir}/cmake/SPIRV-Headers/*.cmake
%{_datadir}/pkgconfig/SPIRV-Headers.pc

%package -n spirv-llvm-translator
Summary:	Library for bi-directional translation between SPIR-V and LLVM IR
Group:		Development/Tools

%description -n spirv-llvm-translator
Library for bi-directional translation between SPIR-V and LLVM IR.

%files -n spirv-llvm-translator
%{_bindir}/llvm-spirv

%define libspirv %mklibname LLVMSPIRVLib %{major1}
%define devspirv %mklibname -d LLVMSPIRVLib

%package -n %{devspirv}
Summary:	Library for bi-directional translation between SPIR-V and LLVM IR
Group:		Development/Tools
Requires:	%{libspirv} = %{EVRD}

%description -n %{devspirv}
Library for bi-directional translation between SPIR-V and LLVM IR.

%files -n %{devspirv}
%{_includedir}/LLVMSPIRVLib
%{_libdir}/libLLVMSPIRVLib.so
%{_libdir}/pkgconfig/LLVMSPIRVLib.pc

%package -n spirv-tools
Summary:	Tools for working with SPIR-V, a language for running on GPUs
Group:		Development/Tools

%description -n spirv-tools
Tools for working with SPIR-V, a language for running on GPUs.

%files -n spirv-tools
%{_bindir}/spirv-as
%{_bindir}/spirv-cfg
%{_bindir}/spirv-dis
%{_bindir}/spirv-lesspipe.sh
%{_bindir}/spirv-link
%{_bindir}/spirv-lint
%{_bindir}/spirv-opt
%{_bindir}/spirv-reduce
%{_bindir}/spirv-val

%define libspirvtools %mklibname spirv-tools %{major1}
%define devspirvtools %mklibname -d spirv-tools

%package -n %{libspirvtools}
Summary:	Libraries needed for SPIRV-Tools
Group:		System/Libraries

%description -n %{libspirvtools}
Libraries needed for SPIRV-Tools.

%files -n %{libspirvtools}
%{_libdir}/libSPIRV-Tools-shared.so.*

%package -n %{devspirvtools}
Summary:	Development files for SPIRV-Tools
Group:		Development/C++ and C
Requires:	%{libspirvtools} = %{EVRD}
Requires:	spirv-tools = %{EVRD}

%description -n %{devspirvtools}
Development files for SPIRV-Tools.

%files -n %{devspirvtools}
%{_includedir}/spirv-tools
%{_libdir}/cmake/SPIRV-Tools*
%{_libdir}/libSPIRV-Tools*.a
%{_libdir}/libSPIRV-Tools*.so
%{_libdir}/pkgconfig/SPIRV-Tools*.pc

%if %{with compat32}
%define lib32spirv libLLVMSPIRVLib%{major1}
%define dev32spirv libLLVMSPIRVLib-devel
%define lib32spirvtools %mklib32name spirv-tools %{major1}
%define dev32spirvtools %mklib32name -d spirv-tools

%package -n %{dev32spirv}
Summary:	Library for bi-directional translation between SPIR-V and LLVM IR (32-bit)
Group:		Development/Tools
Requires:	%{devspirv} = %{EVRD}
Requires:	%{lib32spirv} = %{EVRD}

%description -n %{dev32spirv}
Library for bi-directional translation between SPIR-V and LLVM IR (32-bit).

%files -n %{dev32spirv}
%{_prefix}/lib/libLLVMSPIRVLib.so
%{_prefix}/lib/pkgconfig/LLVMSPIRVLib.pc

%package -n %{lib32spirvtools}
Summary:	Libraries needed for SPIRV-Tools (32-bit)
Group:		System/Libraries

%description -n %{lib32spirvtools}
Libraries needed for SPIRV-Tools (32-bit).

%files -n %{lib32spirvtools}
%{_prefix}/lib/libSPIRV-Tools-shared.so.*

%package -n %{dev32spirvtools}
Summary:	Development files for SPIRV-Tools (32-bit)
Group:		Development/C++ and C
Requires:	%{devspirvtools} = %{EVRD}
Requires:	%{lib32spirvtools} = %{EVRD}
Provides:	libspirv-tools-devel = %{EVRD}

%description -n %{dev32spirvtools}
Development files for SPIRV-Tools.

%files -n %{dev32spirvtools}
%{_prefix}/lib/cmake/SPIRV-Tools*
%{_prefix}/lib/libSPIRV-Tools*.a
%{_prefix}/lib/libSPIRV-Tools*.so
%{_prefix}/lib/pkgconfig/SPIRV-Tools*.pc
%endif

%prep
%if 0%{?date:1}
%setup -q -n llvm-project-%{?is_main:main}%{!?is_main:release-%{major1}.x} -a 20 -a 21 -a 22
%else
%if %{with upstream_tarballs}
%setup -q -n %{name}-%{version}.src -c 0 -a 1 -a 2 -a 3 -a 4 -a 5 -a 6 -a 7 -a 8 -a 9 -a 10 -a 11 -a 20 -a 21 -a 22
mv llvm-%{version}.src llvm
mv cfe-%{version}.src clang
mv clang-tools-extra-%{version}.src clang-tools-extra
mv polly-%{version}.src polly
mv compiler-rt-%{version}.src compiler-rt
mv libcxx-%{version}.src libcxx
mv libcxxabi-%{version}.src libcxxabi
mv libunwind-%{version}.src libunwind
mv lld-%{version}.src lld
mv lldb-%{version}.src lldb
mv openmp-%{version}.src openmp
mv libclc-%{version}.src libclc
%else
%setup -q -n llvm-project-%{version}.src -a 20 -a 21 -a 22
%endif
%endif
mv SPIRV-LLVM-Translator-* llvm/projects/SPIRV-LLVM-Translator
mv SPIRV-Headers-* llvm/projects/SPIRV-Headers
mv SPIRV-Tools-* llvm/projects/SPIRV-Tools
%autopatch -p1
%if %{with default_compilerrt}
patch -p1 -b -z .crt~ <%{S:62}
%endif
%ifarch %{riscv}
patch -p1 -b -z .rvatomic~ <%{S:63}
%endif
git init
git config user.email build@openmandriva.org
git config user.name "OpenMandriva builder"
git add * >/dev/null
git commit --quiet -am "Fake commit to make cmake files happy"

# Fix bogus permissions
find . -type d -exec chmod 0755 {} \;

# LLVM doesn't use autoconf, but it uses autoconf's config.guess
# to find target arch and friends (hidden away in cmake/).
# Let's make sure we replace its outdated copy (which doesn't
# know what riscv64 is) with a current version.
%config_update

%build
# Make sure libclc can find llvm-spirv
export PATH=$(pwd)/build/bin:$PATH

# FIXME do we need to enable cross-project-tests anywhere?
PROJECTS="llvm"
%if %{with bolt}
PROJECTS="$PROJECTS;bolt"
if [ -e bolt/docs/conf.py ]; then
    echo "Bolt config has been fixed, remove this workaround"
    exit 1
else
    sed -i -e 's,clang,bolt,g;s,Clang,Bolt,g' clang/docs/conf.py >bolt/docs/conf.py
    sed -e 's,^/// ,,' bolt/docs/doxygen-mainpage.dox >bolt/docs/index.rst
fi
%endif
%if %{with clang}
PROJECTS="$PROJECTS;clang;clang-tools-extra;polly;compiler-rt"
%endif
%if %{with mlir}
PROJECTS="$PROJECTS;mlir"
%endif
%if %{with flang}
PROJECTS="$PROJECTS;flang"
%endif
%if %{with unwind}
RUNTIMES="$RUNTIMES;libunwind"
%endif
%if %{with lldb}
PROJECTS="$PROJECTS;lldb"
%endif
%if %{with lld}
PROJECTS="$PROJECTS;lld"
%endif
%if %{with openmp}
RUNTIMES="$RUNTIMES;openmp"
%endif
%if %{with libcxx}
PROJECTS="$PROJECTS;pstl"
RUNTIMES="$RUNTIMES;libcxx;libcxxabi"
%endif
%if %{with libc}
PROJECTS="$PROJECTS;libc"
RUNTIMES="$RUNTIMES;libc"
%endif
PROJECTS="$PROJECTS;libclc"

%if %{with bootstrap_gcc}
export CC=gcc
export CXX=g++
%endif
TOP=$(pwd)

# compiler-rt assumes off_t is 64 bits -- make sure this is true even on 32 bit
# OSes
%ifarch %ix86
# compiler-rt doesn't support ix86 with x<6 either
export CFLAGS="%{optflags} -march=i686 -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
export CXXFLAGS="%{optflags} -march=i686 -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
%endif
%ifarch %armx sparc mips riscv64
export CFLAGS="%{optflags} -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
export CXXFLAGS="%{optflags} -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
%endif

if echo %{_target_platform} | grep -q musl; then
    sed -i -e 's,set(COMPILER_RT_HAS_SANITIZER_COMMON TRUE),set(COMPILER_RT_HAS_SANITIZER_COMMON FALSE),' compiler-rt/cmake/config-ix.cmake
fi

# Fix noexecstack
for i in compiler-rt/lib/builtins/i386/*.S; do
    cat >>$i <<'EOF'
#if defined(__linux__) && defined(__ELF__)
.section .note.GNU-stack,"",%progbits
#endif
EOF
done

# The "%if 1" below is just a quick way to get rid of the real
# 64-bit build to debug 32-bit build issues. No need to do a
# proper define/with condition here, the switch is useless for
# any regular use.
%if 1
# We set an RPATH in CMAKE_EXE_LINKER_FLAGS to make sure the newly built
# clang and friends use the just-built shared libraries -- there's no guarantee
# that the ABI remains compatible between a snapshot libclang.so.11 and the
# final libclang.so.11 at the moment.
# We strip out the rpath in %%install though - so we aren't really being evil.
#
# We should probably enable
#	-DLIBUNWIND_BUILD_32_BITS:BOOL=ON \
#	-DLIBCXXABI_BUILD_32_BITS:BOOL=ON \
#	-DLIBCXX_BUILD_32_BITS:BOOL=ON \
# at some point - but right now, builds are broken
#
%cmake \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
%ifarch %{armx} %{riscv}
	-DLLVM_PARALLEL_LINK_JOBS=1 \
	-DLLVM_PARALLEL_COMPILE_JOBS=1 \
%else
	-DLLVM_PARALLEL_LINK_JOBS=2 \
	-DLLVM_PARALLEL_COMPILE_JOBS=2 \
%endif
	-DLLVM_VERSION_SUFFIX="%{SOMINOR}" \
	-DLLVM_ENABLE_PROJECTS="$PROJECTS" \
	-DLLVM_ENABLE_RUNTIMES="$RUNTIMES" \
	-DCLANG_VENDOR="OpenMandriva %{version}-%{release}" \
	-DLLD_VENDOR="OpenMandriva %{version}-%{release}" \
	-DBUILD_SHARED_LIBS:BOOL=ON \
	-DLLVM_ENABLE_NEW_PASS_MANAGER:BOOL=ON \
	-DENABLE_X86_RELAX_RELOCATIONS:BOOL=ON \
	-DCLANG_DEFAULT_LINKER=lld \
	-DCLANG_DEFAULT_OBJCOPY=llvm-objcopy \
%if %{with default_compilerrt}
	-DCLANG_DEFAULT_RTLIB=compiler-rt \
	-DCOMPILER_RT_USE_BUILTINS_LIBRARY:BOOL=ON \
%else
	-DCLANG_DEFAULT_RTLIB=libgcc \
%endif
%if %{with ffi}
	-DLLVM_ENABLE_FFI:BOOL=ON \
%else
	-DLLVM_ENABLE_FFI:BOOL=OFF \
%endif
	-DLLVM_ENABLE_SPHINX:BOOL=ON \
	-DSPHINX_WARNINGS_AS_ERRORS:BOOL=OFF \
	-DLLVM_TARGETS_TO_BUILD=all \
	-DLLVM_ENABLE_CXX1Y:BOOL=ON \
	-DLLVM_ENABLE_RTTI:BOOL=ON \
	-DLLVM_ENABLE_PIC:BOOL=ON \
	-DLLVM_INCLUDE_DOCS:BOOL=ON \
	-DLLVM_ENABLE_EH:BOOL=ON \
	-DLLVM_INSTALL_UTILS:BOOL=ON \
	-DLLVM_BINUTILS_INCDIR=%{_includedir} \
	-DLLVM_BUILD_DOCS:BOOL=ON \
	-DLLVM_BUILD_EXAMPLES:BOOL=OFF \
	-DLLVM_BUILD_RUNTIME:BOOL=ON \
	-DLLVM_TOOL_COMPILER_RT_BUILD:BOOL=ON \
	-DCOMPILER_RT_BUILD_BUILTINS:BOOL=ON \
	-DCOMPILER_RT_BUILD_CRT:BOOL=ON \
	-DENABLE_LINKER_BUILD_ID:BOOL=ON \
	-DOCAMLFIND=NOTFOUND \
	-DLLVM_LIBDIR_SUFFIX=$(echo %{_lib} |sed -e 's,^lib,,') \
	-DCLANG_LIBDIR_SUFFIX=$(echo %{_lib} |sed -e 's,^lib,,') \
	-DLLVM_OPTIMIZED_TABLEGEN:BOOL=OFF \
%ifarch %{arm}
	-DLLVM_DEFAULT_TARGET_TRIPLE=%{product_arch}-%{_vendor}-%{_os}%{_gnu} \
%endif
	-DPOLLY_ENABLE_GPGPU_CODEGEN:BOOL=ON \
	-DWITH_POLLY:BOOL=ON \
	-DLINK_POLLY_INTO_TOOLS:BOOL=ON \
%if %{with use_libcxx}
	-DLLVM_ENABLE_LIBCXX:BOOL=ON \
	-DLLVM_ENABLE_LIBCXXABI:BOOL=ON \
%endif
	-DLIBCXX_CXX_ABI=libcxxabi \
	-DLIBCXX_ENABLE_CXX1Y:BOOL=ON \
	-DLIBCXXABI_ENABLE_SHARED:BOOL=ON \
	-DLIBCXXABI_ENABLE_STATIC:BOOL=ON \
	-DLIBCXX_ENABLE_SHARED:BOOL=ON \
	-DLIBCXX_ENABLE_STATIC:BOOL=ON \
	-DLIBCXXABI_LIBCXX_INCLUDES=${TOP}/libcxx/include \
	-DLIBCXX_CXX_ABI_INCLUDE_PATHS=${TOP}/libcxxabi/include \
	-DLIBCXXABI_LIBDIR_SUFFIX="$(echo %{_lib} | sed -e 's,^lib,,')" \
	-DLIBCXX_LIBDIR_SUFFIX="$(echo %{_lib} | sed -e 's,^lib,,')" \
	-DCMAKE_SHARED_LINKER_FLAGS="-L$(pwd)/%{_lib}" \
	-DCMAKE_EXE_LINKER_FLAGS="-Wl,--disable-new-dtags,-rpath,$(pwd)/%{_lib},-rpath,$(pwd)/lib" \
%if %{with apidox}
	-DLLVM_ENABLE_DOXYGEN:BOOL=ON \
%endif
%if %{cross_compiling}
	-DCMAKE_CROSSCOMPILING=True \
	-DLLVM_TABLEGEN=%{_bindir}/llvm-tblgen \
	-DCLANG_TABLEGEN=%{_bindir}/clang-tblgen \
	-DLLVM_DEFAULT_TARGET_TRIPLE=%{_target_platform} \
%endif
%if %{with default_compilerrt}
%if %{with unwind}
	-DLIBCXXABI_USE_LLVM_UNWINDER:BOOL=ON \
	-DCLANG_DEFAULT_UNWINDLIB=libunwind \
%endif
%else
	-DCLANG_DEFAULT_UNWINDLIB=libgcc \
%endif
	-G Ninja \
	../llvm

if ! %ninja_build; then
# With many threads, there's a chance of libc++ being built
# before libc++abi, causing linkage to fail. Simply trying
# again "fixes" it.
# flang also seems to have SMP build issues
    for i in $(seq 1 30); do
	if %ninja_build; then
	    break
	fi
    done
    %ninja_build -j1
fi

cd ..
%endif

%if %{with compat32}
TOP="$(pwd)"
cat >xc <<EOF
#!/bin/sh
%if %{with bootstrap32}
exec %{_bindir}/clang --rtlib=libgcc --unwindlib=libgcc -m32 "\$@"
%else
exec %{_bindir}/clang -m32 "\$@"
%endif
EOF
gccver="$(i686-openmandriva-linux-gnu-gcc --version |head -n1 |cut -d' ' -f3)"
cat >xc++ <<EOF
#!/bin/sh
%if %{with bootstrap32}
exec %{_bindir}/clang++ --rtlib=libgcc --unwindlib=libgcc -m32 -isystem %{_includedir}/c++/x86_64-openmandriva-linux-gnu/32 "\$@"
%else
exec %{_bindir}/clang++ -m32 -isystem %{_includedir}/c++/${gccver}/x86_64-openmandriva-linux-gnu/32 "\$@"
%endif
EOF
chmod +x xc xc++
cat >cmake-i686.toolchain <<EOF
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR i686)
set(CMAKE_C_COMPILER ${TOP}/xc)
set(CMAKE_CXX_COMPILER ${TOP}/xc++)
EOF
%endif

%if %{with compat32}
%cmake32 \
	-DCMAKE_BUILD_TYPE=MinSizeRel \
	-DLLVM_PARALLEL_LINK_JOBS=2 \
	-DLLVM_PARALLEL_COMPILE_JOBS=2 \
	-DLLVM_VERSION_SUFFIX="%{SOMINOR}" \
	-DCMAKE_TOOLCHAIN_FILE="${TOP}/cmake-i686.toolchain" \
	-DLLVM_CONFIG_PATH=$(pwd)/../build/bin/llvm-config \
	-DLLVM_ENABLE_PROJECTS="llvm;clang;polly;compiler-rt" \
	-DLLVM_ENABLE_RUNTIMES="libc;libunwind;openmp" \
	-DLLVM_ENABLE_NEW_PASS_MANAGER:BOOL=ON \
	-DENABLE_X86_RELAX_RELOCATIONS:BOOL=ON \
%if %{with default_compilerrt}
	-DCLANG_DEFAULT_RTLIB=compiler-rt \
%if ! %{with bootstrap32}
	-DCOMPILER_RT_USE_BUILTINS_LIBRARY:BOOL=ON \
%endif
%else
	-DCLANG_DEFAULT_RTLIB=libgcc \
%endif
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
	-DLLVM_BUILD_DOCS:BOOL=OFF \
	-DLLVM_BUILD_EXAMPLES:BOOL=OFF \
	-DLLVM_BUILD_RUNTIME:BOOL=ON \
	-DLLVM_TOOL_COMPILER_RT_BUILD:BOOL=ON \
	-DCOMPILER_RT_BUILD_BUILTINS:BOOL=ON \
	-DCOMPILER_RT_BUILD_CRT:BOOL=ON \
	-DENABLE_LINKER_BUILD_ID:BOOL=ON \
	-DOCAMLFIND=NOTFOUND \
	-DLLVM_OPTIMIZED_TABLEGEN:BOOL=OFF \
	-DLLVM_DEFAULT_TARGET_TRIPLE=i686-%{_vendor}-%{_os}%{_gnu} \
	-DPOLLY_ENABLE_GPGPU_CODEGEN:BOOL=ON \
	-DWITH_POLLY:BOOL=ON \
	-DLINK_POLLY_INTO_TOOLS:BOOL=ON \
%if %{with use_libcxx}
	-DLLVM_ENABLE_LIBCXX:BOOL=ON \
	-DLLVM_ENABLE_LIBCXXABI:BOOL=ON \
%endif
	-DLIBCXX_CXX_ABI=libcxxabi \
	-DLIBCXX_ENABLE_CXX1Y:BOOL=ON \
	-DLIBCXXABI_ENABLE_SHARED:BOOL=ON \
	-DLIBCXXABI_ENABLE_STATIC:BOOL=ON \
	-DLIBCXX_ENABLE_SHARED:BOOL=ON \
	-DLIBCXX_ENABLE_STATIC:BOOL=ON \
	-DLIBCXX_ENABLE_PARALLEL_ALGORITHMS:BOOL=ON \
	-DLIBCXX_HAS_MUSL_LIBC:BOOL=OFF \
	-DLIBCXXABI_LIBCXX_INCLUDES=${TOP}/libcxx/include \
	-DLIBCXX_CXX_ABI_INCLUDE_PATHS=${TOP}/libcxxabi/include \
	-DCMAKE_SHARED_LINKER_FLAGS="-L$(pwd)/lib" \
	-DCMAKE_EXE_LINKER_FLAGS="-Wl,--disable-new-dtags,-rpath,$(pwd)/lib" \
	-DLLVM_ENABLE_DOXYGEN:BOOL=OFF \
	-DLIBCXXABI_USE_LLVM_UNWINDER:BOOL=ON \
%if %{with default_compilerrt}
	-DCLANG_DEFAULT_UNWINDLIB=libunwind \
%else
	-DCLANG_DEFAULT_UNWINDLIB=libgcc \
%endif
	-DCOMPILER_RT_DEFAULT_TARGET_TRIPLE=i686-openmandriva-linux-gnu \
	-DLIBCXX_USE_COMPILER_RT:BOOL=ON \
	-DLIBCXXABI_USE_COMPILER_RT:BOOL=ON \
	-DLIBUNWIND_USE_COMPILER_RT:BOOL=ON \
	-DLLVM_ENABLE_PER_TARGET_RUNTIME:BOOL=ON \
	-DLLVM_HOST_TRIPLE=i686-openmandriva-linux-gnu \
	-DLLVM_TARGET_ARCH=i686 \
	-DLIBCXX_CXX_ABI=libcxxabi \
	-DLIBCXX_ENABLE_CXX1Y:BOOL=ON \
	-DLIBCXXABI_ENABLE_SHARED:BOOL=ON \
	-DLIBCXXABI_ENABLE_STATIC:BOOL=ON \
	-DLIBCXX_ENABLE_SHARED:BOOL=ON \
	-DLIBCXX_ENABLE_STATIC:BOOL=ON \
	-DLIBCXXABI_LIBCXX_INCLUDES=${TOP}/libcxx/include \
	-DLIBCXX_CXX_ABI_INCLUDE_PATHS=${TOP}/libcxxabi/include \
	-DLIBCXXABI_USE_LLVM_UNWINDER:BOOL=ON \
	-G Ninja \
	../llvm
%ninja_build
cd ..
%endif

# Where our just-built compilers can be found...
BINDIR=$(pwd)/build/bin
# The build process tries to use the just built
# libLLVMAnalysis.so.*
export LD_LIBRARY_PATH=$(pwd)/build/%{_lib}:$LD_LIBRARY_PATH

%if %{without bootstrap}
# libclc integration into the main build seems to be broken
mkdir build-libclc
cd build-libclc
#ln -sf %{_bindir}/llvm-spirv ../build/bin
cmake \
	../libclc \
	-G Ninja \
	-DLLVM_VERSION_SUFFIX="%{SOMINOR}" \
	-DCMAKE_INSTALL_PREFIX=%{_prefix} \
	-DCMAKE_AR=${BINDIR}/llvm-ar \
	-DCMAKE_NM=${BINDIR}/llvm-nm \
	-DCMAKE_RANLIB=${BINDIR}/llvm-ranlib \
	-DLLVM_CONFIG=${BINDIR}/llvm-config \
	-DCMAKE_C_COMPILER=${BINDIR}/clang
%ninja_build
cd ..
%endif

%if %{with crosscrt}
# Build compiler-rt for all potential crosscompiler targets
unset CFLAGS
unset CXXFLAGS
XCRTARCHES=""
%ifnarch %{arm}
XCRTARCHES="$XCRTARCHES armv7hnl"
%endif
%ifnarch %{aarch64}
XCRTARCHES="$XCRTARCHES aarch64"
%endif
%ifnarch %{ix86}
XCRTARCHES="$XCRTARCHES i686"
%endif
%ifnarch %{riscv64}
XCRTARCHES="$XCRTARCHES riscv64"
%endif
%ifnarch ppc64
XCRTARCHES="$XCRTARCHES ppc64"
%endif
%ifnarch ppc64le
XCRTARCHES="$XCRTARCHES ppc64le"
%endif
if [ -n "$XCRTARCHES" ]; then
	for arch in $XCRTARCHES; do
		if [ "$arch" = "armv7hnl" ]; then
			LIBC=gnueabihf
		else
			LIBC=gnu
		fi
		mkdir xbuild-crt-${arch}
		cd xbuild-crt-${arch}
		gccver="$(${arch}-openmandriva-linux-${LIBC}-gcc --version |head -n1 |cut -d' ' -f3)"
		LFLAGS="-O3 --sysroot=/usr/${arch}-openmandriva-linux-${LIBC} --gcc-toolchain=%{_prefix}"
		FLAGS="$LFLAGS -D_LARGEFILE_SOURCE=1 -D_LARGEFILE64_SOURCE=1 -D_FILE_OFFSET_BITS=64"
		if echo $arch |grep -q riscv; then
			# Workaround of lack of linker relaxation support in lld
			LFLAGS="$LFLAGS -fuse-ld=bfd"
		fi
		cmake \
			../compiler-rt \
			-G Ninja \
			-DCMAKE_BUILD_TYPE=MinSizeRel \
			-DLLVM_PARALLEL_LINK_JOBS=1 \
			-DLLVM_PARALLEL_COMPILE_JOBS=1 \
			-DLLVM_VERSION_SUFFIX="%{SOMINOR}" \
			-DCMAKE_CROSSCOMPILING:BOOL=ON \
			-DCMAKE_INSTALL_PREFIX=%{_libdir}/clang/%{version} \
			-DCMAKE_AR=${BINDIR}/llvm-ar \
			-DCMAKE_NM=${BINDIR}/llvm-nm \
			-DCMAKE_RANLIB=${BINDIR}/llvm-ranlib \
			-DCMAKE_ASM_COMPILER_TARGET=${arch}-openmandriva-linux-${LIBC} \
			-DCMAKE_C_COMPILER_TARGET=${arch}-openmandriva-linux-${LIBC} \
			-DCMAKE_CXX_COMPILER_TARGET=${arch}-openmandriva-linux-${LIBC} \
			-DCOMPILER_RT_DEFAULT_TARGET_TRIPLE=${arch}-openmandriva-linux-${LIBC} \
			-DCMAKE_C_COMPILER=${BINDIR}/clang \
			-DCMAKE_CXX_COMPILER=${BINDIR}/clang++ \
			-DCMAKE_ASM_FLAGS="$FLAGS" \
			-DCMAKE_C_FLAGS="$FLAGS" \
			-DCMAKE_CXX_FLAGS="$FLAGS -isystem %{_prefix}/${arch}-openmandriva-linux-${LIBC}/include/c++/${gccver}/${arch}-openmandriva-linux-${LIBC}" \
			-DCMAKE_EXE_LINKER_FLAGS="$LFLAGS" \
			-DCMAKE_MODULE_LINKER_FLAGS="$LFLAGS" \
			-DCMAKE_SHARED_LINKER_FLAGS="$LFLAGS" \
			-DCOMPILER_RT_BUILD_BUILTINS:BOOL=ON \
			-DCOMPILER_RT_BUILD_SANITIZERS:BOOL=OFF \
			-DCOMPILER_RT_BUILD_LIBFUZZER:BOOL=OFF \
			-DCOMPILER_RT_BUILD_MEMPROF:BOOL=OFF \
			-DCOMPILER_RT_BUILD_PROFILE:BOOL=OFF \
			-DCOMPILER_RT_BUILD_XRAY:BOOL=OFF \
			-DCOMPILER_RT_DEFAULT_TARGET_ONLY:BOOL=OFF
		%ninja_build
		cd ..
	done
fi
%endif


%install
%if %{with ocaml}
#cp bindings/ocaml/llvm/META.llvm bindings/ocaml/llvm/Release/
%endif

%if %{with compat32}
%ninja_install -C build32
# Get rid of compat32 stuff that isn't needed in a 64-bit
# environment
rm -rf \
    %{buildroot}%{_prefix}/lib/LLVMgold.so \
    %{buildroot}%{_prefix}/lib/clang \
    %{buildroot}%{_bindir}
%endif

%ninja_install -C build

%if %{without bootstrap}
%ninja_install -C build-libclc
%endif

%if %{with crosscrt}
XCRTARCHES=""
%ifnarch %{arm}
XCRTARCHES="$XCRTARCHES armv7hnl"
%endif
%ifnarch %{aarch64}
XCRTARCHES="$XCRTARCHES aarch64"
%endif
%ifnarch %{ix86}
XCRTARCHES="$XCRTARCHES i686"
%endif
%ifnarch %{riscv64}
XCRTARCHES="$XCRTARCHES riscv64"
%endif
%ifnarch ppc64
XCRTARCHES="$XCRTARCHES ppc64"
%endif
%ifnarch ppc64le
XCRTARCHES="$XCRTARCHES ppc64le"
%endif
if [ -n "$XCRTARCHES" ]; then
    for arch in $XCRTARCHES; do
	%ninja_install -C xbuild-crt-${arch}
    done
fi
%endif

# Nuke the internal copy, we have system python-six
rm -f %{buildroot}%{_libdir}/python*/site-packages/six.py

# https://bugs.llvm.org/show_bug.cgi?id=42455
cp lld/docs/ld.lld.1 %{buildroot}%{_mandir}/man1/

# Install the clang python bits
mkdir -p %{buildroot}%{python_sitelib}
cp -a clang/bindings/python/clang %{buildroot}%{python_sitelib}/

%if %{with default_compiler}
ln -s clang %{buildroot}%{_bindir}/cc
ln -s clang++ %{buildroot}%{_bindir}/c++
cat >%{buildroot}%{_bindir}/c89 <<'EOF'
#!/bin/sh

fl="-std=c89"
for opt; do
	case "$opt" in
		-ansi|-std=c89|-std=iso9899:1990) fl="";;
		-std=*) echo "$(basename $0) called with non ANSI/ISO C option $opt" >&2
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
		-std=*) echo "$(basename $0) called with non ISO C99 option $opt" >&2
			exit 1;;
	esac
done
exec %{_bindir}/clang $fl ${1+"$@"}
EOF
chmod 0755 %{buildroot}%{_bindir}/c89 %{buildroot}%{_bindir}/c99
%endif

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

# We get libgomp from gcc, so don't symlink libomp to it
rm -f %{buildroot}%{_libdir}/libgomp.so

# Fix bogus pointers to incorrect locations
%if "%{_lib}" != "lib"
# Weird, but for some reason those files seem to get installed only on x86
if [ -e %{buildroot}%{_prefix}/lib/cmake/clang/ClangTargets-*.cmake ]; then
    sed -i -e "s,/lib/,/%{_lib}/,g" %{buildroot}%{_prefix}/lib/cmake/clang/ClangTargets-*.cmake %{buildroot}%{_prefix}/lib/cmake/llvm/LLVMExports-*.cmake
fi
%endif

%if %{with unwind}
# Add more headers and a pkgconfig file so we can use the llvm
# unwinder instead of the traditional nongnu.org libunwind
cp libunwind/include/libunwind.h libunwind/include/__libunwind_config.h %{buildroot}%{_includedir}/
# And move unwind.h to where gcc can see it as well
mv %{buildroot}%{_libdir}/clang/%{version}/include/unwind.h %{buildroot}%{_includedir}/
mkdir -p %{buildroot}%{_libdir}/pkgconfig %{buildroot}%{_prefix}/lib/pkgconfig
%if %{with default_compilerrt}
sed -e 's,@LIBDIR@,%{_libdir},g;s,@VERSION@,%{version},g' %{S:50} >%{buildroot}%{_libdir}/pkgconfig/libunwind.pc
%if %{with compat32}
sed -e 's,@LIBDIR@,%{_prefix}/lib,g;s,@VERSION@,%{version},g' %{S:50} >%{buildroot}%{_prefix}/lib/pkgconfig/libunwind.pc
%endif
%else
sed -e 's,@LIBDIR@,%{_libdir},g;s,@VERSION@,%{version},g' %{S:50} >%{buildroot}%{_libdir}/pkgconfig/libunwind-llvm.pc
%if %{with compat32}
sed -e 's,@LIBDIR@,%{_prefix}/lib,g;s,@VERSION@,%{version},g' %{S:50} >%{buildroot}%{_prefix}/lib/pkgconfig/libunwind-llvm.pc
%endif
%endif
%endif

%if %{with apidocs}
mv %{buildroot}%{_prefix}/docs/html/html %{buildroot}%{_docdir}/llvm/doxygen-polly
rm -rf %{buildroot}%{_prefix}/docs
%endif

# This seems to be a build system glitch
rm -rf %{buildroot}%{_mandir}/man1/python.1*
# Not equally sure about this one... Are those object files installed on purpose?
# Let's see if anything doesn't work if we don't package them...
rm -rf %{buildroot}%{_libdir}/objects-Rel*
