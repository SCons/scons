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
Test handling of the dialect-specific FLAGS variable for shared objects,
using a live compiler.
"""

import sys

import TestSCons

_python_ = TestSCons._python_
test = TestSCons.TestSCons()

# ref: test/Fortran/fixture/myfortran_flags.py
test.file_fixture(['fixture', 'myfortran_flags.py'])

fc = 'f03'
if not test.detect_tool(fc):
    fc = 'gfortran'
    if not test.detect_tool(fc):
        test.skip_test('Could not find a f03 tool; skipping test.\n')

test.subdir('x')
test.write(['x', 'dummy.i'], """\
# Exists only such that -Ix finds the directory...
""")
# ref: test/fixture/wrapper.py
test.file_fixture('wrapper.py')
test.write('SConstruct', """\
DefaultEnvironment(tools=[])
# foo = Environment(SHF03='%(fc)s')
foo = Environment()
shf03 = foo.Dictionary('SHF03')
bar = foo.Clone(SHF03=r'%(_python_)s wrapper.py ' + shf03)
bar.Append(SHF03FLAGS='-Ix')
foo.SharedLibrary(target='foo/foo', source='foo.f03')
bar.SharedLibrary(target='bar/bar', source='bar.f03')
""" % locals())

test.write('foo.f03', r"""
      PROGRAM FOO
      PRINT *,'foo.f03'
      STOP
      END
""")

test.write('bar.f03', r"""
      PROGRAM BAR
      PRINT *,'bar.f03'
      STOP
      END
""")

test.run(arguments='foo', stderr=None)
test.must_not_exist('wrapper.out')

if sys.platform.startswith('sunos'):
    test.run(arguments='bar', stderr=None)
else:
    test.run(arguments='bar')
test.must_match('wrapper.out', "wrapper.py\n")

test.pass_test()
