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
Make sure different path separators don't break things.
Backslashes should be okay on POSIX, forwards slashes on win32,
and combinations should cause no problems.
"""

import os.path

import TestRuntest

# the "expected" paths are generated os-native
test_one_py = os.path.join('test', 'subdir', 'test1.py')
test_two_py = os.path.join('test', 'subdir', 'test2.py')
test_three_py = os.path.join('test', 'subdir', 'test3.py')
test_four_py = os.path.join('test', 'subdir', 'test4.py')

test = TestRuntest.TestRuntest()
# create files for discovery
testdir = "test/subdir".split("/")
test.subdir(testdir[0], testdir)
test.write_passing_test(testdir + ['test1.py'])
test.write_passing_test(testdir + ['test2.py'])
test.write_passing_test(testdir + ['test3.py'])
test.write_passing_test(testdir + ['test4.py'])

# discover tests using testlist file with various combinations of slashes
test.write(
    'testlist.txt',
    r"""
test/subdir/test1.py
test\subdir/test2.py
test/subdir\test3.py
test\subdir\test4.py
""",
)

# expect the discovered files to all be os-native
expect_stdout = f"""\
{test_one_py}
{test_two_py}
{test_three_py}
{test_four_py}
"""

test.run(arguments="-k -l -f testlist.txt", stdout=expect_stdout, stderr=None)

test.pass_test()
