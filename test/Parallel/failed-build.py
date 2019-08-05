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

"""
Verify that a failed build action with -j works as expected.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

python = TestSCons.python

try:
    import threading
except ImportError:
    # if threads are not supported, then
    # there is nothing to test
    TestCmd.no_result()
    sys.exit()


test = TestSCons.TestSCons()

# We want to verify that -j 2 starts precisely two jobs, the first of
# which fails and the second of which succeeds, and then stops processing
# due to the first build failure - the second build job does not just
# continue processing tasks.  To try to control the timing, the two
# created build scripts use a pair of marker directories.
#
# The failure script waits until it sees the 'mycopy.started' directory
# that indicates the successful script has, in fact, gotten started.
# If we don't wait, then SCons could detect our script failure early
# (typically if a high system load happens to delay SCons' ability to
# start the next script) and then not start the successful script at all.
#
# The successful script waits until it sees the 'myfail.exiting' directory
# that indicates the failure script has finished (with everything except
# the final sys.exit(), that is).  If we don't wait for that, then SCons
# could detect our successful exit first (typically if a high system
# load happens to delay the failure script) and start another job before
# it sees the failure from the first script.
#
# Both scripts are set to bail if they had to wait too long for what
# they expected to see.

test.write('myfail.py', """\
import os
import sys
import time
WAIT = 10
count = 0
while not os.path.exists('mycopy.started') and count < WAIT:
    time.sleep(1)
    count += 1
if count >= WAIT:
    sys.exit(99)
os.mkdir('myfail.exiting')
sys.exit(1)
""")

test.write('mycopy.py', """\
import os
import sys
import time
os.mkdir('mycopy.started')
with open(sys.argv[1], 'wb') as ofp, open(sys.argv[2], 'rb') as ifp:
    ofp.write(ifp.read())
WAIT = 10
count = 0
while not os.path.exists('myfail.exiting') and count < WAIT:
    time.sleep(1)
    count += 1
if count >= WAIT:
    sys.exit(99)
os.rmdir('mycopy.started')
sys.exit(0)
""")

test.write('SConstruct', """
MyCopy = Builder(action=[[r'%(python)s', 'mycopy.py', '$TARGET', '$SOURCE']])
Fail = Builder(action=[[r'%(python)s', 'myfail.py', '$TARGETS', '$SOURCE']])
env = Environment(BUILDERS={'MyCopy' : MyCopy, 'Fail' : Fail})
env.Fail(target='f3', source='f3.in')
env.MyCopy(target='f4', source='f4.in')
env.MyCopy(target='f5', source='f5.in')
env.MyCopy(target='f6', source='f6.in')
""" % locals())

test.write('f3.in', "f3.in\n")
test.write('f4.in', "f4.in\n")
test.write('f5.in', "f5.in\n")
test.write('f6.in', "f6.in\n")

test.run(arguments='-j 2 .',
         status=2,
         stderr="scons: *** [f3] Error 1\n")

test.must_not_exist(test.workpath('f3'))
test.must_match(test.workpath('f4'), 'f4.in\n')
test.must_not_exist(test.workpath('f5'))
test.must_not_exist(test.workpath('f6'))



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
