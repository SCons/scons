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
This configuration times simple Java compilation.

We create $JAVA_COUNT on-disk Java files in a 'src' subdirectory,
and the SConstruct file builds them.  That's it.
"""

import TestSCons

# Full-build time of just under 10 seconds on ubuntu-timings slave,
# as determined by bin/calibrate.py on 21 May 2010:
#
# run   1:  14.564:  JAVA_COUNT=100
# run   2:   9.692:  JAVA_COUNT=68
# run   3:   9.654:  JAVA_COUNT=68
# run   4:   9.635:  JAVA_COUNT=68

test = TestSCons.TimeSCons(variables={'JAVA_COUNT':68})

test.subdir('src')

contents = """\
package src;
public class j%04d {}
"""

for d in range(test.variables['JAVA_COUNT']):
    test.write(['src', 'j%04d.java' % d], contents % d)

test.main()

test.pass_test()
