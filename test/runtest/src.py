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
Verify that we find tests under the src/ tree only if they end
with *Tests.py.
"""

import os.path

import TestRuntest

test = TestRuntest.TestRuntest(verbose=1)

test.subdir(['src'],
            ['src', 'suite'])

src_passTests_py = os.path.join('src', 'passTests.py')
src_suite_passTests_py = os.path.join('src', 'suite', 'passTests.py')

test.write_passing_test(['src', 'pass.py'])

test.write_passing_test(['src', 'passTests.py'])

test.write_passing_test(['src', 'suite', 'pass.py'])

test.write_passing_test(['src', 'suite', 'passTests.py'])

# NOTE:  The "test/pass.py : PASS" and "test/passTests.py : PASS" lines
# both have spaces at the end.

expect = r"""qmtest run --output results.qmr --format none --result-stream="scons_tdb.AegisChangeStream" src
--- TEST RESULTS -------------------------------------------------------------

  %(src_passTests_py)s                              : PASS    

  %(src_suite_passTests_py)s                        : PASS    

--- TESTS THAT DID NOT PASS --------------------------------------------------

  None.


--- STATISTICS ---------------------------------------------------------------

       2        tests total

       2 (100%%) tests PASS
""" % locals()

test.run(arguments = 'src', stdout = expect)

test.pass_test()
