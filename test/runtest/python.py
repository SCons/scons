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

import TestRuntest

test = TestRuntest.TestRuntest()

mypython_py = test.workpath('mypython.py')
mypython_out = test.workpath('mypython.out')

test.subdir('test')

test.write_passing_test(['test', 'pass.py'])

test.write(mypython_py, """\
#!/usr/bin/env python
import os
import sys
import string
open(r'%s', 'a').write(string.join(sys.argv) + '\\n')
os.system(string.join([sys.executable] + sys.argv[1:]))
""" % mypython_out)

test.chmod(mypython_py, 0755)

# NOTE:  The "test/fail.py : FAIL" and "test/pass.py : PASS" lines both
# have spaces at the end.

expect = r"""qmtest.py run --output results.qmr --format none --result-stream=scons_tdb.AegisChangeStream --context python=%(mypython_py)s test
--- TEST RESULTS -------------------------------------------------------------

  test/pass.py                                  : PASS    

--- TESTS THAT DID NOT PASS --------------------------------------------------

  None.


--- STATISTICS ---------------------------------------------------------------

       1        tests total

       1 (100%%) tests PASS
""" % locals()

test.run(arguments = '--qmtest -P %s test' % mypython_py,
         stdout = expect)

test.must_match(mypython_out, """\
%s ./test/pass.py
""" % mypython_py)

test.pass_test()
