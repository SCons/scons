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
Test a list of tests in failed_tests.log to run with the --retry option
"""

import os.path

import TestRuntest

pythonstring = TestRuntest.pythonstring
pythonflags = TestRuntest.pythonflags
test_fail_py = os.path.join('test', 'fail.py')
test_pass_py = os.path.join('test', 'pass.py')

test = TestRuntest.TestRuntest()
test.subdir('test')
test.write_failing_test(test_fail_py)
test.write_passing_test(test_pass_py)

expect_stdout = f"""\
{pythonstring}{pythonflags} {test_fail_py}
FAILING TEST STDOUT
FAILING TEST STDERR

{pythonstring}{pythonflags} {test_pass_py}
PASSING TEST STDOUT
PASSING TEST STDERR

Summary: 2 selected, 1 failed, 0 no result

Failed the following test:
\t{test_fail_py}
"""

testlist = [
    test_fail_py,
    test_pass_py,
]

test.run(
    arguments='-k --faillog=fail.log %s' % ' '.join(testlist),
    status=1,
    stdout=expect_stdout,
    stderr=None,
)
test.must_exist('fail.log')
test.must_contain('fail.log', test_fail_py)
test.must_not_exist('failed_tests.log')

test.pass_test()
