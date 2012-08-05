#!/bin/sh

if [ $# -lt 2 ]; then
	echo Usage: $0 VERSION SF_USERNAME
	exit 1
fi

VERSION=$1; shift
SF_USER=$1; shift

RSYNC='rsync'
RSYNCOPTS='-v -e ssh'
SF_MACHINE='frs.sourceforge.net'
SF_TOPDIR='/home/frs/project/scons'

# the build products are here:
cd build/dist
cp -f ../../src/CHANGES.txt ../../src/RELEASE.txt ../../src/Announce.txt .

set -x

# Upload main scons release files:
$RSYNC $RSYNCOPTS \
  scons-$VERSION-1.noarch.rpm \
  scons-$VERSION-1.src.rpm \
  scons-$VERSION-setup.exe \
  scons-$VERSION.tar.gz \
  scons-$VERSION.zip \
  Announce.txt CHANGES.txt RELEASE.txt \
  $SF_USER@$SF_MACHINE:$SF_TOPDIR/scons/$VERSION/

# Local packages:
$RSYNC $RSYNCOPTS \
  scons-local-$VERSION.tar.gz \
  scons-local-$VERSION.zip \
  Announce.txt CHANGES.txt RELEASE.txt \
  $SF_USER@$SF_MACHINE:$SF_TOPDIR/scons-local/$VERSION/

# Source packages:
$RSYNC $RSYNCOPTS \
  scons-src-$VERSION.tar.gz \
  scons-src-$VERSION.zip \
  Announce.txt CHANGES.txt RELEASE.txt \
  $SF_USER@$SF_MACHINE:$SF_TOPDIR/scons-src/$VERSION/


#
# scons.org stuff:
# 
# Doc: copy the doc tgz over; we'll unpack later
$RSYNC $RSYNCOPTS \
  scons-doc-$VERSION.tar.gz \
  scons@scons.org:public_html/production/doc/$VERSION/
# Copy the changelog
$RSYNC $RSYNCOPTS \
  CHANGES.txt \
  scons@scons.org:public_html/production/
# Note that Announce.txt gets copied over to RELEASE.txt.
# This should be fixed at some point.
$RSYNC $RSYNCOPTS \
  Announce.txt \
  scons@scons.org:public_html/production/RELEASE.txt
# Unpack the doc and repoint doc symlinks:
ssh scons@scons.org "
  cd public_html/production/doc
  cd $VERSION
  tar xvf scons-doc-$VERSION.tar.gz
  cd ..
  rm latest; ln -s $VERSION latest
  rm production; ln -s $VERSION production
"
echo '*****'
echo '***** Now manually update index.php, includes/versions.php and news-raw.xhtml on scons.org.'
echo '*****'
