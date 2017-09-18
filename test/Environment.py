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

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('SConstruct', """
env=Environment(BAR='#bar.in', BLAT='subdir/../blat blat')
target = env.Command('foo.out',
                     'foo.in',
                     r'%(_python_)s build.py $SOURCE $TARGET ${File(BAR)} ${Dir(BLAT)}')

target = target[0]
assert target == Dir('.').File('foo.out')
assert Dir('.') == Dir('.').Dir('.')
assert target == target.File('foo.out')

e2 = env.Environment(XXX='$BAR', YYY='$BLAT')
print(e2['XXX'])
print(e2['YYY'])
""" % locals())

test.write('build.py', """
import sys
assert sys.argv[1] == 'foo.in', sys.argv[1]
assert sys.argv[2] == 'foo.out', sys.argv[2]
assert sys.argv[3] == 'bar.in', sys.argv[3]
assert sys.argv[4] == 'blat blat', sys.argv[4]
""")

test.write('foo.in', "foo.in\n")

test.run(arguments='foo.out')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
