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

"""
Verify that a failed build action with -j works as expected.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

_python_ = TestSCons._python_

try:
    import threading
except ImportError:
    # if threads are not supported, then
    # there is nothing to test
    TestCmd.no_result()
    sys.exit()


test = TestSCons.TestSCons()

# We want to verify that -j 4 starts all four jobs, the first and last of
# which fail and the second and third of which succeed, and then stops
# processing due to the build failures.  To try to control the timing,
# the created build scripts use marker directories to avoid doing their
# processing until the previous script has finished.

contents = r"""\
import os.path
import sys
import time
wait_marker = sys.argv[1] + '.marker'
write_marker = sys.argv[2] + '.marker'
if wait_marker != '-.marker':
    while not os.path.exists(wait_marker):
        time.sleep(1)
if 'mypass.py' in sys.argv[0]:
    with open(sys.argv[3], 'wb') as ofp, open(sys.argv[4], 'rb') as ifp:
        ofp.write(ifp.read())
    exit_value = 0
elif 'myfail.py' in sys.argv[0]:
    exit_value = 1
if write_marker != '-.marker':
    os.mkdir(write_marker)
sys.exit(exit_value)
"""

test.write('mypass.py', contents)
test.write('myfail.py', contents)

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
Command('f3', 'f3.in', r'@%(_python_)s mypass.py -  f3 $TARGET $SOURCE')
Command('f4', 'f4.in', r'@%(_python_)s myfail.py f3 f4 $TARGET $SOURCE')
Command('f5', 'f5.in', r'@%(_python_)s myfail.py f4 f5 $TARGET $SOURCE')
Command('f6', 'f6.in', r'@%(_python_)s mypass.py f5 -  $TARGET $SOURCE')

def print_build_failures():
    from SCons.Script import GetBuildFailures
    for bf in sorted(GetBuildFailures(), key=lambda t: t.filename or 'None'):
        print("%%s failed:  %%s" %% (bf.node, bf.errstr))

import atexit
atexit.register(print_build_failures)
""" % locals())

test.write('f3.in', "f3.in\n")
test.write('f4.in', "f4.in\n")
test.write('f5.in', "f5.in\n")
test.write('f6.in', "f6.in\n")

test.run(arguments = '-Q -j 4 .',
         status = 2,
         stderr = None)

f4_error = "scons: *** [f4] Error 1\n"
f5_error = "scons: *** [f5] Error 1\n"

error_45 = f4_error + f5_error
error_54 = f5_error + f4_error

if test.stderr() not in [error_45, error_54]:
    print("Did not find the following output in list of expected strings:")
    print(test.stderr(), end=' ')
    test.fail_test()

# We jump through hoops above to try to make sure that the individual
# commands execute and exit in the order we want, but we still can't be
# 100% sure that SCons will actually detect and record the failures in
# that order; the thread for f5 may detect its command's failure before
# the thread for f4.  Just sidestep the issue by allowing the failure
# strings in the output to come in either order.  If there's a genuine
# problem in the way things get ordered, it'll show up in stderr.

f4_failed = "f4 failed:  Error 1\n"
f5_failed = "f5 failed:  Error 1\n"

failed_45 = f4_failed + f5_failed
failed_54 = f5_failed + f4_failed

if test.stdout() not in [failed_45, failed_54]:
    print("Did not find the following output in list of expected strings:")
    print(test.stdout(), end=' ')
    test.fail_test()

test.must_match(test.workpath('f3'), 'f3.in\n')
test.must_not_exist(test.workpath('f4'))
test.must_not_exist(test.workpath('f5'))
test.must_match(test.workpath('f6'), 'f6.in\n')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
