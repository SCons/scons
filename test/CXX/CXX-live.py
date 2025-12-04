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
Test the C compiler name variable $CC.
This is a live test, calling the detected C compiler via a wrapper.
"""

import sys
import TestSCons

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()

test.file_fixture('wrapper.py')

test.write('SConstruct', f"""\
DefaultEnvironment(tools=[])
foo = Environment()

cxx = foo.Dictionary('CXX')
bar = Environment(CXX=r'{_python_} wrapper.py ' + cxx)
foo.Program(target='foo', source='foo.cxx')
bar.Program(target='bar', source='bar.cxx')
""" % locals())

test.write('foo.cxx', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = (char *)"--";
        printf("foo.cxx\n");
        exit (0);
}
""")

test.write('bar.cxx', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = (char *)"--";
        printf("foo.cxx\n");
        exit (0);
}
""")

test.run(arguments='foo' + _exe)
test.must_not_exist(test.workpath('wrapper.out'))

test.run(arguments='bar' + _exe)
test.must_match('wrapper.out', "wrapper.py\n", mode='r')

test.pass_test()
