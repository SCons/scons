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
Test a combination of a passing test, failing test, and no-result
test with no argument on the command line.
"""

import os.path
import re

import TestCmd
import TestRuntest

test_fail_py = re.escape(os.path.join('test', 'fail.py'))
test_no_result_py = re.escape(os.path.join('test', 'no_result.py'))
test_pass_py = re.escape(os.path.join('test', 'pass.py'))

test = TestRuntest.TestRuntest(match = TestCmd.match_re)

test.subdir('test')

test.write_failing_test(['test', 'fail.py'])

test.write_no_result_test(['test', 'no_result.py'])

test.write_passing_test(['test', 'pass.py'])

# NOTE:  The "test/fail.py : FAIL" and "test/pass.py : PASS" lines both
# have spaces at the end.

expect = r"""qmtest.py run --output results.qmr --format none --result-stream="scons_tdb.AegisChangeStream\(print_time='1'\)" test
--- TEST RESULTS -------------------------------------------------------------

  %(test_fail_py)s                                  : FAIL    

    FAILING TEST STDOUT

    FAILING TEST STDERR

    Total execution time: \d+\.\d+ seconds

  %(test_no_result_py)s                             : NO_RESULT

    NO RESULT TEST STDOUT

    NO RESULT TEST STDERR

    Total execution time: \d+\.\d+ seconds

  %(test_pass_py)s                                  : PASS    

    Total execution time: \d+\.\d+ seconds

--- TESTS THAT DID NOT PASS --------------------------------------------------

  %(test_fail_py)s                                  : FAIL    

  %(test_no_result_py)s                             : NO_RESULT


--- STATISTICS ---------------------------------------------------------------

       3        tests total

       1 \( 33%%\) tests PASS
       1 \( 33%%\) tests FAIL
       1 \( 33%%\) tests NO_RESULT
""" % locals()

test.run(arguments = '-t test', status = 1, stdout = expect)

test.pass_test()
