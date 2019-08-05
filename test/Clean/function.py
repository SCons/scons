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
Verify use of the Clean() function.
"""

import os

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as ofp, open(sys.argv[2], 'rb') as ifp:
    ofp.write(ifp.read())
""")

test.subdir('subd')

subd_SConscript = os.path.join('subd', 'SConscript')
subd_foon_in = os.path.join('subd', 'foon.in')
subd_foox_in = os.path.join('subd', 'foox.in')

test.write('SConstruct', """
DefaultEnvironment(tools=[])
B = Builder(action = r'%(_python_)s build.py $TARGETS $SOURCES')
env = Environment(tools=[], BUILDERS = { 'B' : B }, FOO = 'foo2')
env.B(target = 'foo1.out', source = 'foo1.in')
env.B(target = 'foo2.out', source = 'foo2.xxx')
foo2_xxx = env.B(target = 'foo2.xxx', source = 'foo2.in')
env.B(target = 'foo3.out', source = 'foo3.in')
SConscript('subd/SConscript')
Clean(foo2_xxx, ['aux1.x'])
env.Clean(['${FOO}.xxx'], ['aux2.x'])
Clean('.', ['subd'])
""" % locals())

test.write(['subd', 'SConscript'], """
Clean('.', 'foox.in')
""")

test.write('foo1.in', "foo1.in\n")
test.write('foo2.in', "foo2.in\n")
test.write('foo3.in', "foo3.in\n")
test.write(['subd', 'foon.in'], "foon.in\n")
test.write(['subd', 'foox.in'], "foox.in\n")
test.write('aux1.x', "aux1.x\n")
test.write('aux2.x', "aux2.x\n")

test.run()

expect = test.wrap_stdout("""Removed foo2.xxx
Removed aux1.x
Removed aux2.x
""", cleaning=1)
test.run(arguments = '-c foo2.xxx', stdout=expect)
test.must_match(test.workpath('foo1.out'), "foo1.in\n")
test.must_not_exist(test.workpath('foo2.xxx'))
test.must_match(test.workpath('foo2.out'), "foo2.in\n")
test.must_match(test.workpath('foo3.out'), "foo3.in\n")

expect = test.wrap_stdout("Removed %s\n" % subd_foox_in, cleaning = 1)
test.run(arguments = '-c subd', stdout=expect)
test.must_not_exist(test.workpath('foox.in'))

expect = test.wrap_stdout("""Removed foo1.out
Removed foo2.xxx
Removed foo2.out
Removed foo3.out
Removed %(subd_SConscript)s
Removed %(subd_foon_in)s
Removed directory subd
""" % locals(), cleaning = 1)
test.run(arguments = '-c -n .', stdout=expect)

expect = test.wrap_stdout("""Removed foo1.out
Removed foo2.out
Removed foo3.out
Removed %(subd_SConscript)s
Removed %(subd_foon_in)s
Removed directory subd
""" % locals(), cleaning = 1)
test.run(arguments = '-c .', stdout=expect)
test.must_not_exist(test.workpath('subdir', 'foon.in'))
test.must_not_exist(test.workpath('subdir'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
