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

import TestSCons

test = TestSCons.TestSCons()

test.write('foo.c',
"""#include "include/foo.h"
#include <stdio.h>

int main(void)
{
    printf(TEST_STRING);
    return 0;
}
""")

test.subdir('include')

test.write('include/foo.h',
"""
#define TEST_STRING "Bad news\n"
""")

test.write('SConstruct', """
env = Environment()
env.Program(target='prog', source='foo.c')
#env.Depends(target='foo.c', dependency='include/foo.h')
""")

test.run(arguments = 'prog')

test.run(program = test.workpath('prog'),
         stdout = "Bad news\n")

test.unlink('include/foo.h')
test.write('include/foo.h',
"""
#define TEST_STRING "Good news\n"
""")

test.run(arguments = 'prog')

test.run(program = test.workpath('prog'),
         stdout = "Good news\n")

test.pass_test()
