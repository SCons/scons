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
import os.path

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('subdir')

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'w') as f, open(sys.argv[2], 'r') as ifp:
    f.write(ifp.read())
""")

test.write('SConstruct', """
B = Builder(action = r'%(_python_)s build.py $TARGETS $SOURCES')
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'subdir/f1.out', source = 'subdir/f1.in')
env.B(target = 'subdir/f2.out', source = 'subdir/f2.in')
env.B(target = 'subdir/f3.out', source = 'subdir/f3.in')
env.B(target = 'subdir/f4.out', source = 'subdir/f4.in')
""" % locals())

test.write(['subdir', 'f1.in'], "f1.in\n")
test.write(['subdir', 'f2.in'], "f2.in\n")
test.write(['subdir', 'f3.in'], "f3.in\n")
test.write(['subdir', 'f4.in'], "f4.in\n")

test.run(arguments = 'subdir')

test.must_match(['subdir', 'f1.out'], "f1.in\n", mode='r')
test.must_match(['subdir', 'f2.out'], "f2.in\n", mode='r')
test.must_match(['subdir', 'f3.out'], "f3.in\n", mode='r')
test.must_match(['subdir', 'f4.out'], "f4.in\n", mode='r')

test.up_to_date(arguments = 'subdir')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
