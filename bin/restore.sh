#!/usr/bin/env sh
#
# Simple hack script to restore __revision__ and __COPYRIGHT_ lines
# to what gets checked in to source.  This comes in handy when people
# send in diffs based on the released source.
#

if test "X$*" = "X"; then
    DIRS="src test"
else
    DIRS="$*"
fi

for i in `find $DIRS -name '*.py'`; do
ed $i <<EOF
/^__revision__ = /s/= .*/= "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"/p
/Copyright (c) 2001.*SCons Foundation.*/s//__COPYRIGHT__/p
w
q
EOF
done

for i in `find $DIRS -name '*.txt'`; do
ed $i <<EOF
/# [^ ]* 0.96.[CD][0-9]* [0-9\/]* [0-9:]* knight$/s/.*/# __FILE__ __REVISION__ __DATE__ __DEVELOPER__/p
/Copyright (c) 2001.*SCons Foundation.*/s//__COPYRIGHT__/p
w
q
EOF
done

for i in `find $DIRS -name '*.xml'`; do
ed $i <<EOF
/^<!-- Copyright (c) 2001.*SCons Foundation -->$/s/.*/<!-- __COPYRIGHT__ -->/p
w
q
EOF
done
