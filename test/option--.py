#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import os.path
import string
import sys

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
file = open(sys.argv[1], 'w')
file.write("build.py: %s\n" % sys.argv[1])
file.close()
""")

test.write('SConstruct', """
MyBuild = Builder(name = "MyBuild",
		  action = "python build.py %(target)s")
env = Environment(BUILDERS = [MyBuild])
env.MyBuild(target = '-f1.out', source = 'f1.in')
env.MyBuild(target = '-f2.out', source = 'f2.in')
""")

expect = "python build.py -f1.out\npython build.py -f2.out\n"

test.run(arguments = '-- -f1.out -f2.out', stdout = expect)
test.fail_test(not os.path.exists(test.workpath('-f1.out')))
test.fail_test(not os.path.exists(test.workpath('-f2.out')))

test.pass_test()

