#!/usr/bin/env python
#
# __COPYRIGHT__
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

"""
XXX Put a description of the test here.
"""

import string

import TestSCons

test = TestSCons.TestSCons()

# Make sure $_CPPDEFFLAGS doesn't barf when CPPDEFINES isn't defined.
test.write('SConstruct', """\
env = Environment()
print env.subst('$_CPPDEFFLAGS')
""")

expect = test.wrap_stdout(build_str="scons: `.' is up to date.\n", 
                          read_str = "\n")

test.run(arguments = '.', stdout=expect)

# Test CPPDEFINES as a string and a list.
test.write('SConstruct', """\
test_list = [
    'xyz',
    ['x', 'y', 'z'],
    ['x', ['y', 123], 'z'],
    { 'c' : 3, 'b': None, 'a' : 1 },
]
env = Environment(CPPDEFPREFIX='-D', CPPDEFSUFFIX='')
for i in test_list:
    print env.Copy(CPPDEFINES=i).subst('$_CPPDEFFLAGS')
env = Environment(CPPDEFPREFIX='|', CPPDEFSUFFIX='|')
for i in test_list:
    print env.Copy(CPPDEFINES=i).subst('$_CPPDEFFLAGS')
""")

expect = test.wrap_stdout(build_str="scons: `.' is up to date.\n", 
                          read_str = """\
-Dxyz
-Dx -Dy -Dz
-Dx -Dy=123 -Dz
-Da=1 -Db -Dc=3
|xyz|
|x| |y| |z|
|x| |y=123| |z|
|a=1| |b| |c=3|
""")

test.run(arguments = '.', stdout=expect)

test.write('SConstruct', """\
foo = Environment(CPPDEFINES = ['FOO', ('VAL', 7)])
bar = Environment(CPPDEFINES = {'BAR':None, 'VAL':8})
baz = Environment(CPPDEFINES = ['BAZ', ('VAL', 9)])
f = foo.Object(target = 'foo', source = 'prog.c')
b = bar.Object(target = 'bar', source = 'prog.c')
foo.Program(target = 'foo', source = f)
bar.Program(target = 'bar', source = b)
baz.Program(target = 'baz', source = 'baz.cpp')
""")

test.write('prog.c', r"""
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
#ifdef FOO
	printf("prog.c:  FOO %d\n", VAL);
#endif
#ifdef BAR
	printf("prog.c:  BAR %d\n", VAL);
#endif
	exit (0);
}
""")

test.write('baz.cpp', r"""\
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
#ifdef  BAZ
        printf("baz.cpp:  BAZ %d\n", VAL);
#endif
        return(0);
}
""")


test.run(arguments = '.')

test.run(program = test.workpath('foo'), stdout = "prog.c:  FOO 7\n")
test.run(program = test.workpath('bar'), stdout = "prog.c:  BAR 8\n")
test.run(program = test.workpath('baz'), stdout = "baz.cpp:  BAZ 9\n")

test.pass_test()
