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
Verify basic operation of the -q (--question) option.
"""

import TestSCons

test = TestSCons.TestSCons()

_python_ = TestSCons._python_

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as f, open(sys.argv[2], 'rb') as ifp:
    f.write(ifp.read())
""")

test.write('SConstruct', """
B = Builder(action=r'%(_python_)s build.py $TARGET $SOURCES')
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'aaa.out', source = 'aaa.in')
env.B(target = 'bbb.out', source = 'bbb.in')
""" % locals())

test.write('aaa.in', "aaa.in\n")
test.write('bbb.in', "bbb.in\n")

test.run(arguments = '-q aaa.out', status = 1)

test.must_not_exist(test.workpath('aaa.out'))

test.run(arguments = 'aaa.out')

test.must_match('aaa.out', "aaa.in\n")

test.run(arguments = '-q aaa.out', status = 0)

test.run(arguments = '--question bbb.out', status = 1)

test.must_not_exist(test.workpath('bbb.out'))

test.run(arguments = 'bbb.out')

test.must_match('bbb.out', "bbb.in\n")

test.run(arguments = '--question bbb.out', status = 0)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
