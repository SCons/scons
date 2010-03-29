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
This configuration times searching long lists of CPPPATH directories.

We create $DIR_COUNT on-disk directories.  A single checked-in .h file
exists in the 'include' directory.  The SConstruct sets CPPPATH to a
list of Dir Nodes for the created directories, followed by 'include'.
A checked-in .c file #includes the .h file to be found in the last
directory in the list.
"""

import TestSCons

# Full-build time of just under 10 seconds on ubuntu-timings slave,
# as determined by bin/calibrate.py on 9 December 2009:
#
# run   1:   2.235:  DIR_COUNT=50
# run   2:   3.976:  DIR_COUNT=223
# run   3:   7.353:  DIR_COUNT=560
# run   4:   9.569:  DIR_COUNT=761
# run   5:   9.353:  DIR_COUNT=761
# run   6:   9.972:  DIR_COUNT=813
# run   7:   9.930:  DIR_COUNT=813
# run   8:   9.983:  DIR_COUNT=813

test = TestSCons.TimeSCons(variables={'DIR_COUNT':813})

for d in range(test.variables['DIR_COUNT']):
    test.subdir('inc_%04d' % d)

test.main()

test.pass_test()
