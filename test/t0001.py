#!/usr/bin/env python

__revision__ = "test/t0001.py __REVISION__ __DATE__ __DEVELOPER__"

from TestCmd import TestCmd
import string
import sys


try:
    import threading
except ImportError:
    # if threads are not supported, then
    # there is nothing to test
    test.pass_test()
    sys.exit()


test = TestCmd(program = 'scons.py',
               workdir = '',
               interpreter = 'python')

test.write('build.py', r"""
import time
import sys
file = open(sys.argv[1], 'w')
file.write(str(time.time()) + '\n')
time.sleep(1)
file.write(str(time.time()))
file.close()
""")

test.write('SConstruct', """
MyBuild = Builder(name = "MyBuild",
		  action = "python build.py %(target)s")
env = Environment(BUILDERS = [MyBuild])
env.MyBuild(target = 'f1', source = 'f1.in')
env.MyBuild(target = 'f2', source = 'f2.in')
""")

def RunTest(args):
    test.write('f1.in', 'f1.in')
    test.write('f2.in', 'f2.in')

    test.run(chdir = '.', arguments = args)

    str = test.read("f1")
    start1,finish1 = map(float, string.split(str, "\n"))

    str = test.read("f2")
    start2,finish2 = map(float, string.split(str, "\n"))

    return start2, finish1

start2, finish1 = RunTest('-j 2 f1 f2')

# fail if the second file was not started
# before the first one was finished
test.fail_test(not (start2 < finish1))

start2, finish1 = RunTest('f1 f2')

# fail if the second file was started
# before the first one was finished
test.fail_test(start2 < finish1)

test.pass_test()
 
