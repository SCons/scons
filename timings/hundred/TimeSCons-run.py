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
This configuration is for timing how we handle the NxM interaction when
we build a lot of targets from a lot of source files.

We create a list of $TARGET_COUNT target files that will each be built by
copying a file from a corresponding list of $TARGET_COUNT source files.
The source files themselves are each built by a Python function action
that's the equivalent of "echo contents > $TARGET".
"""

import TestSCons

# Full-build time of just under 10 seconds on ubuntu-timings slave,
# as determined by bin/calibrate.py on 9 December 2009:
#
# run   1:   3.124:  TARGET_COUNT=50
# run   2:  11.936:  TARGET_COUNT=160
# run   3:   9.175:  TARGET_COUNT=134
# run   4:  10.489:  TARGET_COUNT=146
# run   5:   9.798:  TARGET_COUNT=139
# run   6:   9.695:  TARGET_COUNT=139
# run   7:   9.670:  TARGET_COUNT=139

test = TestSCons.TimeSCons(variables={'TARGET_COUNT':139})

for t in range(test.variables['TARGET_COUNT']):
    with open('source_%04d' % t, 'w') as f:
        f.write('contents\n')

test.main()

test.pass_test()
