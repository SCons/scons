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
Test that external subdirs are searched if --external is given:

    python runtest.py --external ext/test/subdir

"""

import os

import TestRuntest

test = TestRuntest.TestRuntest()
test.subdir('ext/test/subdir')

pythonstring = TestRuntest.pythonstring
pythonflags = TestRuntest.pythonflags

one = os.path.join('ext', 'test', 'subdir', 'test_one.py')
two = os.path.join('ext', 'test', 'subdir', 'two.py')
three = os.path.join('ext', 'test', 'test_three.py')

test.write_passing_test(one)
test.write_passing_test(two)
test.write_passing_test(three)

expect_stderr_noarg = """\
usage: runtest.py [OPTIONS] [TEST ...]

error: no tests matching the specification were found.
       See "Test selection options" in the help for details on
       how to specify and/or exclude tests.
"""

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
    arguments='--no-progress ext/test/subdir',
    status=1,
    stdout=None,
    stderr=expect_stderr_noarg,
)

test.run(
    arguments='--no-progress --external ext/test/subdir',
    status=0,
    stdout=expect_stdout,
    stderr=None,
)

test.pass_test()
