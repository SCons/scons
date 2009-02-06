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
Test that the -P option lets us specify a Python version to use.
"""

import os.path

if not hasattr(os.path, 'pardir'):
    os.path.pardir = '..'

import TestRuntest

test = TestRuntest.TestRuntest()

test_pass_py = os.path.join('test', 'pass.py')

head, python = os.path.split(TestRuntest.python)
head, dir = os.path.split(head)

mypython = os.path.join(head, dir, os.path.pardir, dir, python)

test.subdir('test')

test.write_passing_test(['test', 'pass.py'])

# NOTE:  The "test/pass.py : PASS" line has spaces at the end.

expect = r"""qmtest run --output results.qmr --format none --result-stream="scons_tdb.AegisChangeStream" --context python="%(mypython)s" test
--- TEST RESULTS -------------------------------------------------------------

  %(test_pass_py)s                                  : PASS    

--- TESTS THAT DID NOT PASS --------------------------------------------------

  None.


--- STATISTICS ---------------------------------------------------------------

       1        tests total

       1 (100%%) tests PASS
""" % locals()

test.run(arguments = ['-P', mypython, 'test'], stdout = expect)

test.pass_test()
