#!/usr/bin/env sh
#
# Simple hack script to restore __revision__ and __COPYRIGHT_ lines
# to what gets checked in to source.  This comes in handy when people
# send in diffs based on the released source.
#

for i in `find src test -name '*.py'`; do
ed $i <<EOF
/__revision__ = /s/= .*/= "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"/p
/# Copyright (c) 2001/s/.*/# __COPYRIGHT__/p
w
q
EOF
done
