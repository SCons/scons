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


# Doc doesn't go to SF, but to scons.org.
$RSYNC $RSYNCOPTS \
  scons-doc-$VERSION.tar.gz \
  scons@scons.org:public_html/production/doc/$VERSION/

