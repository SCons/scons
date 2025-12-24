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

"""
Test LIBLITERALPREFIX behavior.

Build a static library and shared library of the same name,
and make sure the requested syntax selects the static one.
Depends on a live compiler to build libraries and executable,
and actually runs the executable.
"""

import os
import sys

import TestSCons
from TestSCons import lib_, _lib

test = TestSCons.TestSCons()

if sys.platform == 'win32':
    import SCons.Tool.MSCommon as msc
    if msc.msvc_exists():
        test.skip_test("Functionality not available for msvc, skipping test.\n")

test.write('SConstruct', """\
LIBLITERALPREFIX = ":"
env = Environment(LIBLITERALPREFIX=LIBLITERALPREFIX, LIBPATH=".")
lib = env.Library(target='foo', source='foo.c')
shlib = env.SharedLibrary(target='foo', source='shfoo.c')
env.Program(target='prog', source=['prog.c'], LIBS=f"{LIBLITERALPREFIX}libfoo.a")
""")

test.write('shfoo.c', r"""
#include <stdio.h>

void
foo(void)
{
        printf("shared libfoo\n");
}
""")

test.write('foo.c', r"""
#include <stdio.h>

void
foo(void)
{
        printf("static libfoo\n");
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

test.run(arguments='.', stderr=TestSCons.noisy_ar, match=TestSCons.match_re_dotall)
test.fail_test(not os.path.exists(test.workpath(f"{lib_}foo{_lib}")))

test.run(program=test.workpath('prog'), stdout="static libfoo\nprog.c\n")

test.pass_test()
