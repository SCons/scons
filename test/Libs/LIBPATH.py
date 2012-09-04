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

import os.path
import time

import TestSCons

_exe = TestSCons._exe
_dll = TestSCons._dll
dll_ = TestSCons.dll_
    
test = TestSCons.TestSCons()

test.subdir('lib1', 'lib2')

prog1 = test.workpath('prog') + _exe
prog2 = test.workpath(dll_ + 'shlib') + _dll

test.write('SConstruct', """
env1 = Environment(LIBS = [ 'foo1' ],
                   LIBPATH = [ '$FOO' ],
                   FOO='./lib1')

f1 = env1.SharedObject('f1', 'f1.c')

env1.Program(target = 'prog', source = 'prog.c')
env1.Library(target = './lib1/foo1', source = f1)

env2 = Environment(LIBS = 'foo2',
                   LIBPATH = '.')
env2.SharedLibrary(target = 'shlib', source = 'shlib.c', no_import_lib = 1)
env2.Library(target = 'foo2', source = f1)
""")

test.write('f1.c', r"""
#include <stdio.h>

void
f1(void)
{
        printf("f1.c\n");
}
""")

test.write('shlib.c', r"""
void f1(void);
int
test()
{
    f1();
    return 0;
}
""")

test.write('prog.c', r"""
#include <stdio.h>

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

test.run(arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

test.run(program = prog1,
         stdout = "f1.c\nprog.c\n")

oldtime1 = os.path.getmtime(prog1)
oldtime2 = os.path.getmtime(prog2)
time.sleep(2)
test.run(arguments = '.')

test.fail_test(oldtime1 != os.path.getmtime(prog1))
test.fail_test(oldtime2 != os.path.getmtime(prog2))

test.write('f1.c', r"""
#include <stdio.h>

void
f1(void)
{
        printf("f1.c 1\n");
}
""")

test.run(arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)
test.run(program = prog1,
         stdout = "f1.c 1\nprog.c\n")
test.fail_test(oldtime2 == os.path.getmtime(prog2))
#test.up_to_date(arguments = '.')
# Change LIBPATH and make sure we don't rebuild because of it.
test.write('SConstruct', """
env1 = Environment(LIBS = [ 'foo1' ],
                  LIBPATH = [ './lib1', './lib2' ])

f1 = env1.SharedObject('f1', 'f1.c')

env1.Program(target = 'prog', source = 'prog.c')
env1.Library(target = './lib1/foo1', source = f1)

env2 = Environment(LIBS = 'foo2',
                   LIBPATH = Split('. ./lib2'))
env2.SharedLibrary(target = 'shlib', source = 'shlib.c', no_import_lib = 1)
env2.Library(target = 'foo2', source = f1)
""")

test.up_to_date(arguments = '.', stderr=None)

test.write('f1.c', r"""
#include <stdio.h>

void
f1(void)
{
        printf("f1.c 2\n");
}
""")

test.run(arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)
test.run(program = prog1,
         stdout = "f1.c 2\nprog.c\n")

test.up_to_date(arguments = '.')

# We need at least one file for some implementations of the Library
# builder, notably the SGI one.
test.write('empty.c', 'int a=0;\n')

# Check that a null-string LIBPATH doesn't blow up.
test.write('SConstruct', """
env = Environment(LIBPATH = '')
env.Library('foo', source = 'empty.c')
""")

test.run(arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
