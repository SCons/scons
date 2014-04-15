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
This configuration is for timing how we evaluate long chains of
dependencies, specifically when -j is used.

We set up a chain of $TARGET_COUNT targets that get built from a
Python function action with no source files (equivalent to "echo junk >
$TARGET").  Each target explicitly depends on the next target in turn,
so the Taskmaster will do a deep walk of the dependency graph.

This test case was contributed by Kevin Massey.  Prior to revision 1468,
we had a serious O(N^2) problem in the Taskmaster when handling long
dependency chains like this.  That was fixed by adding reference counts
to the Taskmaster so it could be smarter about not re-evaluating Nodes.
"""

import TestSCons

# Full-build time of just under 10 seconds on ubuntu-timings slave,
# as determined by bin/calibrate.py on 9 December 2009:
#
# run   1:   3.211:  TARGET_COUNT=50
# run   2:  11.920:  TARGET_COUNT=155
# run   3:   9.182:  TARGET_COUNT=130
# run   4:  10.185:  TARGET_COUNT=141
# run   5:   9.945:  TARGET_COUNT=138
# run   6:  10.035:  TARGET_COUNT=138
# run   7:   9.898:  TARGET_COUNT=137
# run   8:   9.840:  TARGET_COUNT=137
# run   9:  10.054:  TARGET_COUNT=137
# run  10:   9.747:  TARGET_COUNT=136
# run  11:   9.778:  TARGET_COUNT=136
# run  12:   9.743:  TARGET_COUNT=136
#
# The fact that this varies so much suggests that it's pretty
# non-deterministic, which makes sense for a test involving -j.

test = TestSCons.TimeSCons(variables={'TARGET_COUNT':136})

test.main()

test.pass_test()
