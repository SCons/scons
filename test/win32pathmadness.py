#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

"""
This test verifies that the build command signatures do not depend on
the case of the drive letter on Windows. This is important because Windows is 
inconsistent about which case is used for the drive letter.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import sys
import TestCmd
import string
import os.path

test = TestSCons.TestSCons(match=TestCmd.match_re)

if sys.platform != 'win32':
    test.pass_test()

test.subdir('src', 'build', 'include', 'src2')

test.write('src/SConstruct', """
env=Environment(LIBS=['../build/foo'], CPPPATH=['../include'], CCCOM='$CC $CCFLAGS $CPPFLAGS $_CPPINCFLAGS /c ${SOURCES.abspath} /Fo$TARGET')
foo=env.Object('../build/foo', 'foo.c')
Default(env.Library('../build/foo', foo))
Default(env.SharedLibrary('../build/bar', 'bar.c'))
Default(env.Program('../build/bar', ['main.c', '../src2/blat.c', '../build/bar.lib']))
""")

test.write('src/foo.c', """
int foo(void) 
{ 
    return 1;
}
""")

test.write('src/bar.c', """
__declspec(dllexport) int bar(void) 
{ 
    return 1;
}
""")

test.write('src/main.c', """
#include <bar.h>
int main(void) 
{ 
    return 1;
}
""")

test.write('src2/blat.c', """
int blat(void) 
{ 
    return 1;
}
""")

test.write('include/bar.h', """
int foo(void);
int blat(void);
int bar(void);
""")

drive,rest = os.path.splitdrive(test.workpath('src'))
upper = os.path.join(string.upper(drive),rest)
lower = os.path.join(string.lower(drive),rest)

test.run(chdir=upper)
test.run(chdir=lower, stdout=test.wrap_stdout("""\
scons: .* is up to date.
scons: .* is up to date.
scons: .* is up to date.
"""))

test.write('SConstruct', """
env=Environment()
env.StaticLibrary('a', 'a.c')
env.StaticLibrary('b', 'b.c')
""")

test.write('a.c', '''
#include "a.h"
#include "b.h"
''')

test.write('b.c', '''
#include "a.h"
#include "B.h"
''')

test.write('a.h', """
#define A_H
""")

test.write('b.h', """
#define B_H
""")

test.run(arguments='a.lib b.lib')
test.run(arguments='b.lib a.lib', stdout=test.wrap_stdout("""\
scons: .* is up to date.
scons: .* is up to date.
"""))



test.pass_test()

