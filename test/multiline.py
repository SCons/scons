#!/usr/bin/env python

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
 
