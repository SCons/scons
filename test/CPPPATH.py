#!/usr/bin/env python
#
# Copyright (c) 2001 Steven Knight
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

import sys
import TestSCons

if sys.platform == 'win32':
    _exe = '.exe'
else:
    _exe = ''

prog = 'prog' + _exe

test = TestSCons.TestSCons()

test.write('foo.c',
"""#include "foo.h"
#include <stdio.h>

int main(void)
{
    printf(FOO_STRING);
    printf(BAR_STRING);
    return 0;
}
""")

test.subdir('include')

test.write('include/foo.h',
r"""
#define	FOO_STRING "foo.h 1\n"
#include "bar.h"
""")

test.write('include/bar.h',
r"""
#define BAR_STRING "bar.h 1\n"
""")

test.write('SConstruct', """
env = Environment(CPPPATH = ['include'])
env.Program(target='prog', source='foo.c')
""")

test.run(arguments = prog)

test.run(program = test.workpath(prog),
         stdout = "foo.h 1\nbar.h 1\n")

test.up_to_date(arguments = prog)

test.unlink('include/foo.h')
test.write('include/foo.h',
r"""
#define	FOO_STRING "foo.h 2\n"
#include "bar.h"
""")

test.run(arguments = prog)

test.run(program = test.workpath(prog),
         stdout = "foo.h 2\nbar.h 1\n")

test.up_to_date(arguments = prog)

test.unlink('include/bar.h')
test.write('include/bar.h',
r"""
#define BAR_STRING "bar.h 2\n"
""")

test.run(arguments = prog)

test.run(program = test.workpath(prog),
         stdout = "foo.h 2\nbar.h 2\n")

test.up_to_date(arguments = prog)

test.pass_test()
