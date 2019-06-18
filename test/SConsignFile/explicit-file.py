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
Verify the default behavior of SConsignFile(), called with no arguments.
"""

import TestSCons
import os.path

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('subdir')

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as ofp, open(sys.argv[2], 'rb') as ifp:
    ofp.write(ifp.read())
""")

#
test.write('SConstruct', """
e = Environment(XXX = 'scons')
e.SConsignFile('my_${XXX}ign')
B = Builder(action = r'%(_python_)s build.py $TARGETS $SOURCES')
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'f5.out', source = 'f5.in')
env.B(target = 'f6.out', source = 'f6.in')
env.B(target = 'subdir/f7.out', source = 'subdir/f7.in')
env.B(target = 'subdir/f8.out', source = 'subdir/f8.in')
""" % locals())

test.write('f5.in', "f5.in\n")
test.write('f6.in', "f6.in\n")
test.write(['subdir', 'f7.in'], "subdir/f7.in\n")
test.write(['subdir', 'f8.in'], "subdir/f8.in\n")

test.run()

test.must_exist(test.workpath('my_sconsign.dblite'))
test.must_not_exist(test.workpath('.sconsign'))
test.must_not_exist(test.workpath('subdir', '.sconsign'))

test.must_match('f5.out', "f5.in\n")
test.must_match('f6.out', "f6.in\n")
test.must_match(['subdir', 'f7.out'], "subdir/f7.in\n")
test.must_match(['subdir', 'f8.out'], "subdir/f8.in\n")

test.up_to_date(arguments = '.')

test.must_exist(test.workpath('my_sconsign.dblite'))
test.must_not_exist(test.workpath('.sconsign'))
test.must_not_exist(test.workpath('subdir', '.sconsign'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
