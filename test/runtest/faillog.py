#!/usr/bin/env python
#
# __COPYRIGHT__
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
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

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

expect_stdout = """\
%(pythonstring)s%(pythonflags)s %(test_fail_py)s
FAILING TEST STDOUT
%(pythonstring)s%(pythonflags)s %(test_pass_py)s
PASSING TEST STDOUT

Failed the following test:
\t%(test_fail_py)s
""" % locals()

expect_stderr = """\
FAILING TEST STDERR
PASSING TEST STDERR
"""

testlist = [
    test_fail_py,
    test_pass_py,
]

test.run(
    arguments='-k --faillog=fail.log %s' % ' '.join(testlist),
    status=1,
    stdout=expect_stdout,
    stderr=expect_stderr,
)
test.must_exist('fail.log')
test.must_contain('fail.log', test_fail_py)
test.must_not_exist('failed_tests.log')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
