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
Test that runtest.py falls back (with a warning) using --noqmtest
if it can't find qmtest on the $PATH.
"""

import os

import TestRuntest

pythonstring = TestRuntest.pythonstring
pythonflags = TestRuntest.pythonflags

test = TestRuntest.TestRuntest()

# qmtest may be in more than one location in your path
while test.where_is('qmtest'):
    qmtest=test.where_is('qmtest')
    dir = os.path.split(qmtest)[0]
    path = os.environ['PATH'].split(os.pathsep)
    path.remove(dir)
    os.environ['PATH'] = os.pathsep.join(path)

test.subdir('test')

test_fail_py      = os.path.join('test', 'fail.py')
test_no_result_py = os.path.join('test', 'no_result.py')
test_pass_py      = os.path.join('test', 'pass.py')

test.write_failing_test(test_fail_py)
test.write_no_result_test(test_no_result_py)
test.write_passing_test(test_pass_py)

expect_stdout = """\
%(pythonstring)s%(pythonflags)s %(test_fail_py)s
FAILING TEST STDOUT
%(pythonstring)s%(pythonflags)s %(test_no_result_py)s
NO RESULT TEST STDOUT
%(pythonstring)s%(pythonflags)s %(test_pass_py)s
PASSING TEST STDOUT

Failed the following test:
\t%(test_fail_py)s

NO RESULT from the following test:
\t%(test_no_result_py)s
""" % locals()

expect_stderr = """\
FAILING TEST STDERR
NO RESULT TEST STDERR
PASSING TEST STDERR
"""

testlist = [
    test_fail_py,
    test_no_result_py,
    test_pass_py,
]

test.run(arguments = '-k '+' '.join(testlist),
         status = 1,
         stdout = expect_stdout,
         stderr = expect_stderr)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
