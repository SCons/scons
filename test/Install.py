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

foo1 = test.workpath('export/foo1' + _exe)
foo2 = test.workpath('export/foo2' + _exe)

test.write('SConstruct', """
env=Environment()
t=env.Program(target='foo1', source='f1.c')
env.Install(dir='export', source=t)
t=env.Program(target='foo2', source='f2.c')
env.Install(dir='export', source=t)
""")

test.write('f1.c', r"""
#include <stdio.h>

int main(void)
{
   printf("f1.c\n");
   return 0;
}
""")

test.write('f2.c', r"""
#include <stdio.h>

int main(void)
{
   printf("f2.c\n");
   return 0;
}
""")

test.run(arguments = '.')

test.run(program = foo1, stdout = "f1.c\n")
test.run(program = foo2, stdout = "f2.c\n")

# make sure the programs didn't get rebuilt, because nothing changed:
oldtime1 = os.path.getmtime(foo1)
oldtime2 = os.path.getmtime(foo2)

test.write('f1.c', r"""
#include <stdio.h>

int main(void)
{
   printf("f1.c again\n");
   return 0;
}
""")

time.sleep(2) # introduce a small delay, to make the test valid

test.run(arguments = '.')

test.fail_test(oldtime1 == os.path.getmtime(foo1))
test.fail_test(oldtime2 != os.path.getmtime(foo2))

test.pass_test()
