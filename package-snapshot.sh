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
for i in llvm cfe clang-tools-extra compiler-rt polly libcxx libcxxabi lldb openmp libunwind; do
	if [ "$i" = "libunwind" ]; then
		# libunwind isn't branched with the rest of llvm for now
		svn co http://llvm.org/svn/llvm-project/$i/trunk $i
	else
		svn co http://llvm.org/svn/llvm-project/$i/$BRANCH $i
	fi
	cd $i
	[ "$VER" = 0 ] && VER=`grep "^PACKAGE_VERSION=" configure |cut -d= -f2 |sed -e "s,',,g;s,svn,,g"`
	R=`svn info |grep "^Last Changed Rev" |cut -d: -f2`
	[ $R -gt $REV ] && REV=$R
	svn export . "$TMP"/$i-$VER.src
	cd ..
	tar cJf "$CUR"/$i-$VER.src.tar.xz $i-$VER.src
done
echo "Packaged revision $REV"
