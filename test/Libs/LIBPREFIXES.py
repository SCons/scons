#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

import os
import sys

import TestSCons
from TestSCons import _lib

if sys.platform == 'win32':
    import SCons.Tool.MSCommon as msc
    if not msc.msvc_exists():
        _lib = '.a'

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment(LIBPREFIX = 'xxx-',
                  LIBPREFIXES = ['xxx-'])
lib = env.Library(target = 'foo', source = 'foo.c')
env.Program(target = 'prog', source = ['prog.c', lib])
""")

test.write('foo.c', r"""
#include <stdio.h>

void
foo(void)
{
        printf("foo.c\n");
}
""")

test.write('prog.c', r"""
#include <stdio.h>

void foo(void);
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        foo();
        printf("prog.c\n");
        return 0;
}
""")

test.run(arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

test.fail_test(not os.path.exists(test.workpath('xxx-foo' + _lib)))

test.run(program = test.workpath('prog'), stdout = "foo.c\nprog.c\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
