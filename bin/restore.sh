#!/usr/bin/env sh
#
# Simple hack script to restore __revision__, __COPYRIGHT_, __VERSION__
# and other similar variables to what gets checked in to source.  This
# comes in handy when people send in diffs based on the released source.
#

if test "X$*" = "X"; then
    DIRS="src test"
else
    DIRS="$*"
fi

SEPARATOR="================================================================================"

header() {
    arg_space="$1 "
    dots=`echo "$arg_space" | sed 's/./\./g'`
    echo "$SEPARATOR" | sed "s;$dots;$arg_space;"
}

for i in `find $DIRS -name '*.py'`; do
    header $i
    ed $i <<EOF
g/Copyright (c) 2001.*SCons Foundation/s//__COPYRIGHT__/p
w
/^__revision__ = /s/= .*/= "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"/p
w
q
EOF
done

for i in `find $DIRS -name 'scons.bat'`; do
    header $i
    ed $i <<EOF
g/Copyright (c) 2001.*SCons Foundation/s//__COPYRIGHT__/p
w
/^@REM src\/script\/scons.bat/s/@REM .* knight/@REM __FILE__ __REVISION__ __DATE__ __DEVELOPER__/p
w
q
EOF
done

for i in `find $DIRS -name '__init__.py' -o -name 'scons.py' -o -name 'sconsign.py'`; do
    header $i
    ed $i <<EOF
/^__version__ = /s/= .*/= "__VERSION__"/p
w
/^__build__ = /s/= .*/= "__BUILD__"/p
w
/^__buildsys__ = /s/= .*/= "__BUILDSYS__"/p
w
/^__date__ = /s/= .*/= "__DATE__"/p
w
/^__developer__ = /s/= .*/= "__DEVELOPER__"/p
w
q
EOF
done

for i in `find $DIRS -name 'setup.py'`; do
    header $i
    ed $i <<EOF
/^ *version = /s/= .*/= "__VERSION__",/p
w
q
EOF
done

for i in `find $DIRS -name '*.txt'`; do
    header $i
    ed $i <<EOF
g/Copyright (c) 2001.*SCons Foundation/s//__COPYRIGHT__/p
w
/# [^ ]* 0.96.[CD][0-9]* [0-9\/]* [0-9:]* knight$/s/.*/# __FILE__ __REVISION__ __DATE__ __DEVELOPER__/p
w
/Version [0-9][0-9]*\.[0-9][0-9]*/s//Version __VERSION__/p
w
q
EOF
done

for i in `find $DIRS -name '*.xml'`; do
    header $i
    ed $i <<EOF
g/Copyright (c) 2001.*SCons Foundation/s//__COPYRIGHT__/p
w
q
EOF
done
