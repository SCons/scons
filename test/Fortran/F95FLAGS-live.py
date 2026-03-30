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
Test handling of the dialect-specific FLAGS variable, using a live compiler.
"""

import sys

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()
_exe = TestSCons._exe

# ref: test/Fortran/fixture/myfortran_flags.py
test.file_fixture(['fixture', 'myfortran_flags.py'])

fc = 'f95'
if not test.detect_tool(fc):
    # gfortran names all variants the same, try it too
    fc = 'gfortran'
    if not test.detect_tool(fc):
        test.skip_test('Could not find an f95 tool; skipping test.\n')

test.subdir('x')
test.write(['x', 'dummy.i'], """\
# Exists only such that -Ix finds the directory...
""")
# ref: test/fixture/wrapper.py
test.file_fixture('wrapper.py')
test.write('SConstruct', """\
DefaultEnvironment(tools=[])
foo = Environment(F95='%(fc)s')
f95 = foo.Dictionary('F95')
bar = foo.Clone(F95=r'%(_python_)s wrapper.py ' + f95, F95FLAGS='-Ix')
foo.Program(target='foo', source='foo.f95')
bar.Program(target='bar', source='bar.f95')
""" % locals())

test.write('foo.f95', r"""
      PROGRAM FOO
      PRINT *,'foo.f95'
      STOP
      END
""")

test.write('bar.f95', r"""
      PROGRAM BAR
      PRINT *,'bar.f95'
      STOP
      END
""")

test.run(arguments='foo' + _exe, stderr=None)
test.run(program=test.workpath('foo'), stdout=" foo.f95\n")
test.must_not_exist('wrapper.out')

if sys.platform.startswith('sunos'):
    test.run(arguments='bar' + _exe, stderr=None)
else:
    test.run(arguments='bar' + _exe)
test.run(program=test.workpath('bar'), stdout=" bar.f95\n")
test.must_match('wrapper.out', "wrapper.py\n")

test.pass_test()
