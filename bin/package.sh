#!/bin/bash

set -ex -u
set -o pipefail

echo "*** Install system dependencies"
yum update -y
yum install -y \
	freetype-devel \
	gcc \
	lcms2-devel \
	libjpeg-devel \
	libtiff-devel \
	libzip-devel \
	tcl-devel \
	tk-devel

echo "*** Create the virtualenv"
VIRTUALENV_DIR=$( mktemp --directory )
/usr/bin/virtualenv \
	--python /usr/bin/python $VIRTUALENV_DIR \
	--always-copy
source $VIRTUALENV_DIR/bin/activate

echo "*** Install Python dependencies"
pip install --upgrade pip
pip install --verbose --use-wheel pillow
deactivate

echo "*** Download FFMPEG"
FFMPEG_DIR=$( mktemp --directory )
curl http://johnvansickle.com/ffmpeg/builds/ffmpeg-git-64bit-static.tar.xz | tar xJ --strip-components=1 -C $FFMPEG_DIR

echo "*** Zip everything up"
ZIP_FILE=$( mktemp --suffix=.zip --dry-run )
cd $VIRTUALENV_DIR/lib/python2.7/site-packages
zip -r9 $ZIP_FILE *
cd $VIRTUALENV_DIR/lib64/python2.7/site-packages
zip -r9 $ZIP_FILE *
cd $FFMPEG_DIR
zip -r9 $ZIP_FILE ffmpeg

echo "*** Created package in $ZIP_FILE"
