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
Test that the --qmtest option invokes tests directly via QMTest,
not directly via Python.
"""

import os.path

import TestRuntest

test = TestRuntest.TestRuntest()

test.subdir('test')

test_fail_py      = os.path.join('test', 'fail.py')
test_no_result_py = os.path.join('test', 'no_result.py')
test_pass_py      = os.path.join('test', 'pass.py')

workpath_fail_py      = test.workpath(test_fail_py)
workpath_no_result_py = test.workpath(test_no_result_py)
workpath_pass_py      = test.workpath(test_pass_py)

test.write_failing_test(test_fail_py)
test.write_no_result_test(test_no_result_py)
test.write_passing_test(test_pass_py)

# NOTE:  the FAIL and PASS lines below have trailing spaces.

expect_stdout = """\
qmtest run --output results.qmr --format none --result-stream="scons_tdb.AegisChangeStream" test/fail.py test/no_result.py test/pass.py
--- TEST RESULTS -------------------------------------------------------------

  test/fail.py                                  : FAIL    

    FAILING TEST STDOUT

    FAILING TEST STDERR

  test/no_result.py                             : NO_RESULT

    NO RESULT TEST STDOUT

    NO RESULT TEST STDERR

  test/pass.py                                  : PASS    

--- TESTS THAT DID NOT PASS --------------------------------------------------

  test/fail.py                                  : FAIL    

  test/no_result.py                             : NO_RESULT


--- STATISTICS ---------------------------------------------------------------

       3        tests total

       1 ( 33%) tests PASS
       1 ( 33%) tests FAIL
       1 ( 33%) tests NO_RESULT
"""

testlist = [
    test_fail_py,
    test_no_result_py,
    test_pass_py,
]

test.run(arguments='--qmtest %s' % ' '.join(testlist),
         status=1,
         stdout=expect_stdout)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
