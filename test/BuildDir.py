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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os.path
import sys
import time
import TestSCons

if sys.platform == 'win32':
    _exe = '.exe'
else:
    _exe = ''

test = TestSCons.TestSCons()

foo11 = test.workpath('build', 'var1', 'foo1' + _exe)
foo12 = test.workpath('build', 'var1', 'foo2' + _exe)
foo21 = test.workpath('build', 'var2', 'foo1' + _exe)
foo22 = test.workpath('build', 'var2', 'foo2' + _exe)
foo31 = test.workpath('build', 'var3', 'foo1' + _exe)
foo32 = test.workpath('build', 'var3', 'foo2' + _exe)

test.write('SConstruct', """
src = Dir('src')
var2 = Dir('build/var2')
var3 = Dir('build/var3')

BuildDir('build/var1', src)
BuildDir(var2, src)
BuildDir(var3, src, duplicate=0)

env = Environment()
SConscript('build/var1/SConscript', "env")
SConscript('build/var2/SConscript', "env")

env = Environment(CPPPATH=src)
SConscript('build/var3/SConscript', "env")
""") 

test.subdir('src')
test.write('src/SConscript', """
import os
import os.path

def buildIt(target, source, env):
    if not os.path.exists('build'):
        os.mkdir('build')
    f1=open(str(source[0]), 'r')
    f2=open(str(target[0]), 'w')
    f2.write(f1.read())
    f2.close()
    f1.close()
    return 0
Import("env")
env.Command(target='f2.c', source='f2.in', action=buildIt)
env.Program(target='foo2', source='f2.c')
env.Program(target='foo1', source='f1.c')
""")

test.write('src/f1.c', r"""
#include "f1.h"

int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf(F1_STR);
	exit (0);
}
""")

test.write('src/f2.in', r"""
#include "f2.h"

int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf(F2_STR);
	exit (0);
}
""")

test.write('src/f1.h', r"""
#define F1_STR "f1.c\n"
""")

test.write('src/f2.h', r"""
#define F2_STR "f2.c\n"
""")

test.run(arguments = '.')

test.run(program = foo11, stdout = "f1.c\n")
test.run(program = foo12, stdout = "f2.c\n")
test.run(program = foo21, stdout = "f1.c\n")
test.run(program = foo22, stdout = "f2.c\n")
test.run(program = foo31, stdout = "f1.c\n")
test.run(program = foo32, stdout = "f2.c\n")

# Make sure we didn't duplicate the source files in build/var3.
test.fail_test(os.path.exists(test.workpath('build', 'var3', 'f1.c')))
test.fail_test(os.path.exists(test.workpath('build', 'var3', 'f2.in')))

test.pass_test()
