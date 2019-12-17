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
Verify that parallel builds work correctly when a Node is duplicated
in the children (once in the sources and once in the depends list).
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('cat.py', """\
import sys
with open(sys.argv[1], 'wb') as ofp:
    for fname in sys.argv[2:]:
        with open(fname, 'rb') as ifp:
            ofp.write(ifp.read())
""")

test.write('sleep.py', """\
import sys
import time
time.sleep(int(sys.argv[1]))
""")

test.write('SConstruct', """
# Test case for SCons issue #1608
# Create a file "foo.in" in the current directory before running scons.
env = Environment()
env.Command('foo.out', ['foo.in'], r'%(_python_)s cat.py $TARGET $SOURCE && %(_python_)s sleep.py 3')
env.Command('foobar', ['foo.out'], r'%(_python_)s cat.py $TARGET $SOURCES')
env.Depends('foobar', 'foo.out')
""" % locals())

test.write('foo.in', "foo.in\n")

test.run(arguments = '-j2 .')

test.must_match('foo.out', "foo.in\n")
test.must_match('foobar', "foo.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
