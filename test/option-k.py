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

test.pass_test()	#XXX Short-circuit until this is supported.

test.write('succeed.py', r"""
import sys
file = open(sys.argv[1], 'wb')
file.write("succeed.py: %s\n" % sys.argv[1])
file.close()
sys.exit(0)
""")

test.write('fail.py', r"""
import sys
sys.exit(1)
""")

test.write('SConstruct', """
Succeed = Builder(name = "Succeed", action = r'%s succeed.py $targets')
Fail = Builder(name = "Fail", action = r'%s fail.py $targets')
env = Environment(BUILDERS = [Succeed, Fail])
env.Fail(target = 'aaa.1', source = 'aaa.in')
env.Succeed(target = 'aaa.out', source = 'aaa.1')
env.Succeed(target = 'bbb.out', source = 'bbb.in')
""" % (python, python))

test.run(arguments = '.')

test.fail_test(os.path.exists(test.workpath('aaa.1')))
test.fail_test(os.path.exists(test.workpath('aaa.out')))
test.fail_test(os.path.exists(test.workpath('bbb.out')))

test.run(arguments = '-k .')

test.fail_test(os.path.exists(test.workpath('aaa.1')))
test.fail_test(os.path.exists(test.workpath('aaa.out')))
test.fail_test(test.read('bbb.out') != "bbb.out\n")

test.unlink("bbb.out")

test.run(arguments = '--keep-going .')

test.fail_test(os.path.exists(test.workpath('aaa.1')))
test.fail_test(os.path.exists(test.workpath('aaa.out')))
test.fail_test(test.read('bbb.out') != "bbb.out\n")

test.pass_test()
 
