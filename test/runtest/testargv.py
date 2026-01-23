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
Test subdir args for runtest.py, for example:

    python runtest.py test/subdir

"""

import os

import TestRuntest

test = TestRuntest.TestRuntest()
test.subdir('test', ['test', 'subdir'])

pythonstring = TestRuntest.pythonstring
pythonflags = TestRuntest.pythonflags

one = os.path.join('test', 'subdir', 'test_one.py')
two = os.path.join('test', 'subdir', 'two.py')
three = os.path.join('test', 'test_three.py')

test.write_passing_test(['test', 'subdir', 'test_one.py'])
test.write_passing_test(['test', 'subdir', 'two.py'])
test.write_passing_test(['test', 'test_three.py'])

expect_stdout = f"""\
{pythonstring}{pythonflags} {one}
PASSING TEST STDOUT
PASSING TEST STDERR

{pythonstring}{pythonflags} {two}
PASSING TEST STDOUT
PASSING TEST STDERR

Summary: 2 selected, 0 failed, 0 no result
"""

test.run(
    arguments='--no-progress test/subdir',
    status=0,
    stdout=expect_stdout,
    stderr=None,
)

test.pass_test()
