#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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

python = sys.executable

test = TestSCons.TestSCons()

test.subdir('subdir')

test.write('build.py', r"""
import sys
sys.exit(0)
""")

test.write('SConstruct', """
B = Builder(name = "B", action = r"%s build.py $TARGET $SOURCES")
env = Environment(BUILDERS = [B])
f1 = env.B(target = 'f1.out', source = 'f1.in')
env.B(target = 'f2.out', source = 'f2.in')
env.B(target = 'f3.out', source = 'f3.in')
env.Precious(f1, 'f2.out')
SConscript('subdir/SConscript', "env")
""" % python)

test.write(['subdir', 'SConscript'], """
Import("env")
env.B(target = 'f4.out', source = 'f4.in')
f5 = env.B(target = 'f5.out', source = 'f5.in')
env.B(target = 'f6.out', source = 'f6.in')
env.Precious(['f4.out', f5])
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")

test.write(['subdir', 'f4.in'], "subdir/f4.in\n")
test.write(['subdir', 'f5.in'], "subdir/f5.in\n")
test.write(['subdir', 'f6.in'], "subdir/f6.in\n")

test.write('f1.out', "SHOULD NOT BE REMOVED\n")
test.write('f2.out', "SHOULD NOT BE REMOVED\n")
test.write('f3.out', "SHOULD BE REMOVED\n")

test.write(['subdir', 'f4.out'], "SHOULD NOT BE REMOVED\n")
test.write(['subdir', 'f5.out'], "SHOULD NOT BE REMOVED\n")
test.write(['subdir', 'f6.out'], "SHOULD BE REMOVED\n")

test.run(arguments = '.')

test.fail_test(not os.path.exists(test.workpath('f1.out')))
test.fail_test(not os.path.exists(test.workpath('f2.out')))
test.fail_test(os.path.exists(test.workpath('f3.out')))

test.fail_test(not os.path.exists(test.workpath('subdir', 'f4.out')))
test.fail_test(not os.path.exists(test.workpath('subdir', 'f5.out')))
test.fail_test(os.path.exists(test.workpath('subdir', 'f6.out')))

test.write('f3.out', "SHOULD BE REMOVED\n")
test.write(['subdir', 'f6.out'], "SHOULD BE REMOVED\n")

test.run(arguments = '.')

test.fail_test(not os.path.exists(test.workpath('f1.out')))
test.fail_test(not os.path.exists(test.workpath('f2.out')))
test.fail_test(not os.path.exists(test.workpath('f3.out')))

test.fail_test(not os.path.exists(test.workpath('subdir', 'f4.out')))
test.fail_test(not os.path.exists(test.workpath('subdir', 'f5.out')))
test.fail_test(not os.path.exists(test.workpath('subdir', 'f6.out')))

test.write('f3.in', "f3.in 2\n")
test.write(['subdir', 'f6.in'], "subdir/f6.in 2\n")

test.run(arguments = '.')

test.fail_test(not os.path.exists(test.workpath('f1.out')))
test.fail_test(not os.path.exists(test.workpath('f2.out')))
test.fail_test(os.path.exists(test.workpath('f3.out')))

test.fail_test(not os.path.exists(test.workpath('subdir', 'f4.out')))
test.fail_test(not os.path.exists(test.workpath('subdir', 'f5.out')))
test.fail_test(os.path.exists(test.workpath('subdir', 'f6.out')))

test.pass_test()
