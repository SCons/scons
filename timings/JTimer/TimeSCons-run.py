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

We set up a chain of 500 targets that get built from a Python function
action with no source files (equivalent to "echo junk > $TARGET").
Each target explicitly depends on the next target in turn, so the
Taskmaster will do a deep walk of the dependency graph.

This test case was contributed by Kevin Massey.  Prior to revision 1468,
we had a serious O(N^2) problem in the Taskmaster when handling long
dependency chains like this.  That was fixed by adding reference counts
to the Taskmaster so it could be smarter about not re-evaluating Nodes.
"""

import TestSCons

target_count = 500

TestSCons.TimeSCons().main(options='TARGET_COUNT=%d' % target_count)
