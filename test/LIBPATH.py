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

import TestSCons
import sys
import os.path
import time

if sys.platform == 'win32':
    _exe = '.exe'
else:
    _exe = ''
    
test = TestSCons.TestSCons()

prog1 = test.workpath('prog') + _exe
prog2 = test.workpath('prog2') + _exe

test.write('SConstruct', """
env = Environment(LIBS = [ 'foo1' ],
                  LIBPATH = [ './libs' ])
env.Program(target = 'prog', source = 'prog.c')
env.Library(target = './libs/foo1', source = 'f1.c')

env2 = Environment(LIBS = 'foo2',
                   LIBPATH = '.')
env2.Program(target = 'prog2', source = 'prog.c')
env2.Library(target = 'foo2', source = 'f1.c')
""")

test.write('f1.c', r"""
void
f1(void)
{
	printf("f1.c\n");
}
""")

test.write('prog.c', r"""
void f1(void);
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	f1();
	printf("prog.c\n");
        return 0;
}
""")

test.run(arguments = '.')

test.run(program = prog1,
         stdout = "f1.c\nprog.c\n")
test.run(program = prog2,
         stdout = "f1.c\nprog.c\n")

oldtime1 = os.path.getmtime(prog1)
oldtime2 = os.path.getmtime(prog2)
time.sleep(2)
test.run(arguments = '.')

test.fail_test(oldtime1 != os.path.getmtime(prog1))
test.fail_test(oldtime2 != os.path.getmtime(prog2))

test.write('f1.c', r"""
void
f1(void)
{
	printf("f1.cnew\n");
}
""")

test.run(arguments = '.')
test.run(program = prog1,
         stdout = "f1.cnew\nprog.c\n")
test.run(program = prog2,
         stdout = "f1.cnew\nprog.c\n")

test.up_to_date(arguments = '.')

# Change LIBPATH and make sure we don't rebuild because of it.
test.write('SConstruct', """
env = Environment(LIBS = [ 'foo1' ],
                  LIBPATH = [ './libs', './lib2' ])
env.Program(target = 'prog', source = 'prog.c')
env.Library(target = './libs/foo1', source = 'f1.c')
""")

test.up_to_date(arguments = '.', stderr = None)

test.pass_test()
