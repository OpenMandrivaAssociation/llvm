#!/bin/sh
CUR="`pwd`"
TMP="`mktemp -d /tmp/llvmXXXXXX`"
VER=0
REV=0
cd "$TMP"
export LANG=C
for i in llvm cfe clang-tools-extra compiler-rt polly; do
	svn co http://llvm.org/svn/llvm-project/$i/trunk $i
	cd $i
	[ "$VER" = 0 ] && VER=`grep "^PACKAGE_VERSION=" configure |cut -d= -f2 |sed -e "s,',,g;s,svn,,g"`
	R=`svn info |grep "^Last Changed Rev" |cut -d: -f2`
	[ $R -gt $REV ] && REV=$R
	svn export . "$TMP"/$i-$VER.src
	cd ..
	tar cJf "$CUR"/$i-$VER.src.tar.xz $i-$VER.src
done
echo "Packaged revision $REV"
