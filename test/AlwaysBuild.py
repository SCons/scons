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

import os
import sys
import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
def bfunc(target, source, env):
    import shutil
    shutil.copyfile('f2.in', str(target[0]))

B = Builder(action=bfunc)
env = Environment(BUILDERS = { 'B' : B })
env.B('f1.out', source='f1.in')
env.AlwaysBuild('f1.out')
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "1")

test.run(arguments = ".")
test.fail_test(test.read('f1.out') != '1')

test.write('f2.in', "2")
test.run(arguments = ".")
test.fail_test(test.read('f1.out') != '2')

test.pass_test()
