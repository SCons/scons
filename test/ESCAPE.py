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
Test the ESCAPE construction variable.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('cat.py', """\
import sys
ofp = open(sys.argv[1], 'wb')
for s in sys.argv[2:]:
    ofp.write(open(s, 'rb').read())
ofp.close()
""")

test.write('SConstruct', """\
import string
# We still need to run this through the original ESCAPE function,
# because that's set up to work in tandem with the existing SHELL,
# which we're not replacing.
orig_escape = Environment()['ESCAPE']
def my_escape(s):
    s = string.replace(s, 'file.in', 'file.xxx')
    return orig_escape(s)
env = Environment(ESCAPE = my_escape)
env.Command('file.out', 'file.in', '%(_python_)s cat.py $TARGET $SOURCES')
""" % locals())

test.write('file.in', "file.in\n")
test.write('file.xxx', "file.xxx\n")

test.run()

test.must_match('file.out', "file.xxx\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
