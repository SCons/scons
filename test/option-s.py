#!/usr/bin/env python

__revision__ = "test/option-s.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import os.path
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

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
env.MyBuild(target = 'f1.out', source = 'f1.in')
env.MyBuild(target = 'f2.out', source = 'f2.in')
""")

test.run(chdir = '.', arguments = '-s f1.out f2.out')

test.fail_test(test.stdout() != "")
test.fail_test(test.stderr() != "")
test.fail_test(not os.path.exists(test.workpath('f1.out')))
test.fail_test(not os.path.exists(test.workpath('f2.out')))

os.unlink(test.workpath('f1.out'))
os.unlink(test.workpath('f2.out'))

test.run(chdir = '.', arguments = '--silent f1.out f2.out')

test.fail_test(test.stdout() != "")
test.fail_test(test.stderr() != "")
test.fail_test(not os.path.exists(test.workpath('f1.out')))
test.fail_test(not os.path.exists(test.workpath('f2.out')))

os.unlink(test.workpath('f1.out'))
os.unlink(test.workpath('f2.out'))

test.run(chdir = '.', arguments = '--quiet f1.out f2.out')

test.fail_test(test.stdout() != "")
test.fail_test(test.stderr() != "")
test.fail_test(not os.path.exists(test.workpath('f1.out')))
test.fail_test(not os.path.exists(test.workpath('f2.out')))

test.pass_test()
 
