#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os.path
import TestSCons

test = TestSCons.TestSCons()

test.pass_test()	#XXX Short-circuit until this is supported.

test.write('succeed.py', r"""
import sys
file = open(sys.argv[1], 'w')
file.write("succeed.py: %s\n" % sys.argv[1])
file.close()
sys.exit(0)
""")

test.write('fail.py', r"""
import sys
sys.exit(1)
""")

test.write('SConstruct', """
Succeed = Builder(name = "Succeed", action = "python succeed.py %(target)s")
Fail = Builder(name = "Fail", action = "python fail.py %(target)s")
env = Environment(BUILDERS = [Succeed, Fail])
env.Fail(target = 'aaa.1', source = 'aaa.in')
env.Succeed(target = 'aaa.out', source = 'aaa.1')
env.Fail(target = 'bbb.1', source = 'bbb.in')
env.Succeed(target = 'bbb.out', source = 'bbb.1')
""")

test.run(arguments = '.')

test.fail_test(os.path.exists(test.workpath('aaa.1')))
test.fail_test(os.path.exists(test.workpath('aaa.out')))
test.fail_test(os.path.exists(test.workpath('bbb.1')))
test.fail_test(os.path.exists(test.workpath('bbb.out')))

test.run(arguments = '-i .')

test.fail_test(os.path.exists(test.workpath('aaa.1')))
test.fail_test(test.read('aaa.out') != "aaa.out\n")
test.fail_test(os.path.exists(test.workpath('bbb.1')))
test.fail_test(test.read('bbb.out') != "bbb.out\n")

test.unlink("aaa.out")
test.unlink("bbb.out")

test.run(arguments = '--ignore-errors .')

test.fail_test(os.path.exists(test.workpath('aaa.1')))
test.fail_test(test.read('aaa.out') != "aaa.out\n")
test.fail_test(os.path.exists(test.workpath('bbb.1')))
test.fail_test(test.read('bbb.out') != "bbb.out\n")

test.pass_test()
 
