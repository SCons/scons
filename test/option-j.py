#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys


try:
    import threading
except ImportError:
    # if threads are not supported, then
    # there is nothing to test
    TestCmd.no_result()
    sys.exit()


test = TestSCons.TestSCons()

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

def RunTest(args, extra):
    """extra is used to make scons rebuild the output file"""
    test.write('f1.in', 'f1.in'+extra)
    test.write('f2.in', 'f2.in'+extra)

    test.run(arguments = args)

    str = test.read("f1")
    start1,finish1 = map(float, string.split(str, "\n"))

    str = test.read("f2")
    start2,finish2 = map(float, string.split(str, "\n"))

    return start2, finish1

start2, finish1 = RunTest('-j 2 f1 f2', "first")

# fail if the second file was not started
# before the first one was finished
test.fail_test(not (start2 < finish1))

s2, f1 = RunTest('-j 2 f1 f2', "first")

# re-run the test with the same input, fail if we don't
# get back the same times, which would indicate that
# SCons rebuilt the files even though nothing changed
test.fail_test(start2 != s2)
test.fail_test(finish1 != f1)

start2, finish1 = RunTest('f1 f2', "second")

# fail if the second file was started
# before the first one was finished
test.fail_test(start2 < finish1)

test.pass_test()
 
