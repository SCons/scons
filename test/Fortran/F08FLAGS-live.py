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

fc = 'f08'
if not test.detect_tool(fc):
    # gfortran names all variants the same, try it too
    fc = 'gfortran'
    if not test.detect_tool(fc):
        test.skip_test('Could not find an f08 tool; skipping test.\n')

test.subdir('x')
test.write(['x', 'dummy.i'], """\
# Exists only such that -Ix finds the directory...
""")
# ref: test/fixture/wrapper.py
test.file_fixture('wrapper.py')
test.write('SConstruct', """\
DefaultEnvironment(tools=[])
foo = Environment(F08='%(fc)s')
f08 = foo.Dictionary('F08')
bar = foo.Clone(F08=r'%(_python_)s wrapper.py ' + f08, F08FLAGS='-Ix')
foo.Program(target='foo', source='foo.f08')
bar.Program(target='bar', source='bar.f08')
""" % locals())

test.write('foo.f08', r"""
      PROGRAM FOO
      PRINT *,'foo.f08'
      END PROGRAM FOO
""")

test.write('bar.f08', r"""
      PROGRAM BAR
      PRINT *,'bar.f08'
      END PROGRAM BAR
""")

test.run(arguments='foo' + _exe, stderr=None)
test.run(program=test.workpath('foo'), stdout=" foo.f08\n")
test.must_not_exist('wrapper.out')

if sys.platform[:5] == 'sunos':
    test.run(arguments='bar' + _exe, stderr=None)
else:
    test.run(arguments='bar' + _exe)
test.run(program=test.workpath('bar'), stdout=" bar.f08\n")
test.must_match('wrapper.out', "wrapper.py\n")

test.pass_test()
