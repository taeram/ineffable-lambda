#!/bin/bash

set -ex -u
set -o pipefail

echo "*** Install system dependencies"
yum update -y
yum install -y gcc

echo "*** Download and compile ImageMagick"
IMAGEMAGICK_DIR=$( mktemp --directory )
yum -y install libpng-devel \
               libjpeg-devel \
               libtiff-devel
curl http://www.imagemagick.org/download/ImageMagick.tar.gz | tar zx --strip-components=1 -C $IMAGEMAGICK_DIR
cd $IMAGEMAGICK_DIR
./configure --enable-shared=no --enable-static=yes
make

echo "*** Download FFMPEG"
FFMPEG_DIR=$( mktemp --directory )
curl http://johnvansickle.com/ffmpeg/builds/ffmpeg-git-64bit-static.tar.xz | tar xJ --strip-components=1 -C $FFMPEG_DIR

echo "*** Zip everything up"
ZIP_FILE=$( mktemp --suffix=.zip --dry-run )
cd $IMAGEMAGICK_DIR/utilities
zip -r9 -X $ZIP_FILE convert
rm -rf $IMAGEMAGICK_DIR

cd $FFMPEG_DIR
zip -r9 -X $ZIP_FILE ffmpeg
rm -rf $FFMPEG_DIR

echo "*** Created package in $ZIP_FILE"
