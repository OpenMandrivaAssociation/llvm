#!/bin/sh
CUR="`pwd`"
TMP="`mktemp -d /tmp/llvmXXXXXX`"
VER=0
REV=0
if [ "$#" -ge 1 ]; then
	BRANCH="$1"
	if ! echo $BRANCH |grep -qE '(/|@)'; then
		BRANCH="branches/$BRANCH"
	fi
else
	BRANCH="trunk"
fi
cd "$TMP"
export LANG=C
export LC_ALL=C
for i in llvm cfe clang-tools-extra compiler-rt polly libcxx libcxxabi lldb openmp libunwind llgo lld; do
	if [ "$i" = "llgo" ]; then
		# llgo isn't versioned with the rest of llvm for now
		svn co http://llvm.org/svn/llvm-project/$i/trunk $i
	else
		svn co http://llvm.org/svn/llvm-project/$i/$BRANCH $i
	fi
	cd $i
	[ "$VER" = 0 ] && VER=`grep "^PACKAGE_VERSION=" configure |cut -d= -f2 |sed -e "s,',,g;s,svn,,g"`
	if [ -z "$VER" ]; then
		# 3.9 drops the configure system, but earlier versions
		# don't have reliable version info in CMakeLists.txt...
		VER=$(grep 'set(LLVM_VERSION_MAJOR' CMakeLists.txt |sed -e 's,[^0-9]*,,g').$(grep 'set(LLVM_VERSION_MINOR' CMakeLists.txt |sed -e 's,[^0-9]*,,g').$(grep 'set(LLVM_VERSION_PATCH' CMakeLists.txt |sed -e 's,[^0-9]*,,g')
	fi
	R=`svn info |grep "^Last Changed Rev" |cut -d: -f2`
	[ $R -gt $REV ] && REV=$R
	svn export . "$TMP"/$i-$VER.src
	cd ..
	tar cJf "$CUR"/$i-$VER.src.tar.xz $i-$VER.src
done
rm -rf "$TMP"
echo "Packaged revision $REV"
