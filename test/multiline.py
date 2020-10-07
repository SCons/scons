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

python = TestSCons.python
_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as f, open(sys.argv[2], 'rb') as ifp:
    f.write(ifp.read())
sys.exit(0)
""")

test.write('SConstruct', """
B1 = Builder(action = [ [ r'%(python)s', 'build.py', '.temp', '$SOURCES' ],
                        [ r'%(python)s', 'build.py', '$TARGETS', '.temp'] ])
B2 = Builder(action = r'%(_python_)s' + ' build.py .temp $SOURCES\\n' + r'%(_python_)s' + " build.py $TARGETS .temp")
env = Environment(BUILDERS = { 'B1' : B1, 'B2' : B2 })
env.B1(target = 'foo1.out', source = 'foo1.in')
env.B2(target = 'foo2.out', source = 'foo2.in')
env.B1(target = 'foo3.out', source = 'foo3.in')
""" % locals())

test.write('foo1.in', "foo1.in\n")

test.write('foo2.in', "foo2.in\n")

test.write('foo3.in', "foo3.in\n")

test.run(arguments = 'foo1.out foo2.out foo3.out')

test.fail_test(test.read(test.workpath('foo1.out')) != b"foo1.in\n")
test.fail_test(test.read(test.workpath('foo2.out')) != b"foo2.in\n")
test.fail_test(test.read(test.workpath('foo3.out')) != b"foo3.in\n")

test.pass_test()
 

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
