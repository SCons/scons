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
import TestSCons

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
contents = open(sys.argv[2], 'r').read()
file = open(sys.argv[1], 'w')
file.write(contents)
file.close()
sys.exit(0)
""")

test.write('SConstruct', """
B1 = Builder(name = 'B1', action = ["python build.py .temp %(source)s",
				    "python build.py %(target)s .temp"])
B2 = Builder(name = 'B2', action = "python build.py .temp %(source)s\\npython build.py %(target)s .temp")
env = Environment(BUILDERS = [B1, B2])
env.B1(target = 'foo1.out', source = 'foo1.in')
env.B2(target = 'foo2.out', source = 'foo2.in')
env.B1(target = 'foo3.out', source = 'foo3.in')
""")

test.write('foo1.in', "foo1.in\n")

test.write('foo2.in', "foo2.in\n")

test.write('foo3.in', "foo3.in\n")

test.run(arguments = 'foo1.out foo2.out foo3.out')

test.fail_test(test.read(test.workpath('foo1.out')) != "foo1.in\n")
test.fail_test(test.read(test.workpath('foo2.out')) != "foo2.in\n")
test.fail_test(test.read(test.workpath('foo3.out')) != "foo3.in\n")

test.pass_test()
 
