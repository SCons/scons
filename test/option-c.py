#!/usr/bin/env python
#
# Copyright (c) 2001 Steven Knight
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

import os.path
import sys
import TestSCons

python = sys.executable

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
contents = open(sys.argv[2], 'rb').read()
file = open(sys.argv[1], 'wb')
file.write(contents)
file.close()
""")

test.write('SConstruct', """
B = Builder(name = 'B', action = r'%s build.py $targets $sources')
env = Environment(BUILDERS = [B])
env.B(target = 'foo1.out', source = 'foo1.in')
env.B(target = 'foo2.out', source = 'foo2.in')
env.B(target = 'foo3.out', source = 'foo3.in')
""" % python)

test.write('foo1.in', "foo1.in\n")

test.write('foo2.in', "foo2.in\n")

test.write('foo3.in', "foo3.in\n")

test.run(arguments = 'foo1.out foo2.out foo3.out')

test.fail_test(test.read(test.workpath('foo1.out')) != "foo1.in\n")
test.fail_test(test.read(test.workpath('foo2.out')) != "foo2.in\n")
test.fail_test(test.read(test.workpath('foo3.out')) != "foo3.in\n")

test.run(arguments = '-c foo1.out', stdout = "Removed foo1.out\n")

test.fail_test(os.path.exists(test.workpath('foo1.out')))
test.fail_test(not os.path.exists(test.workpath('foo2.out')))
test.fail_test(not os.path.exists(test.workpath('foo3.out')))

test.run(arguments = '--clean foo2.out', stdout = "Removed foo2.out\n")

test.fail_test(os.path.exists(test.workpath('foo1.out')))
test.fail_test(os.path.exists(test.workpath('foo2.out')))
test.fail_test(not os.path.exists(test.workpath('foo3.out')))

test.run(arguments = '--remove foo3.out', stdout = "Removed foo3.out\n")

test.fail_test(os.path.exists(test.workpath('foo1.out')))
test.fail_test(os.path.exists(test.workpath('foo2.out')))
test.fail_test(os.path.exists(test.workpath('foo3.out')))

test.run(arguments = 'foo1.out foo2.out foo3.out')

test.fail_test(test.read(test.workpath('foo1.out')) != "foo1.in\n")
test.fail_test(test.read(test.workpath('foo2.out')) != "foo2.in\n")
test.fail_test(test.read(test.workpath('foo3.out')) != "foo3.in\n")

#XXXtest.run(arguments = '-c .',
test.run(arguments = '-c foo1.out foo2.out foo3.out',
         stdout = "Removed foo1.out\nRemoved foo2.out\nRemoved foo3.out\n")

test.fail_test(os.path.exists(test.workpath('foo1.out')))
test.fail_test(os.path.exists(test.workpath('foo2.out')))
test.fail_test(os.path.exists(test.workpath('foo3.out')))

test.pass_test()
 
