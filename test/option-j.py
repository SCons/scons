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

import string
import sys
import TestSCons

python = sys.executable

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
file = open(sys.argv[1], 'wb')
file.write(str(time.time()) + '\n')
time.sleep(1)
file.write(str(time.time()))
file.close()
""")

test.write('SConstruct', """
MyBuild = Builder(action = r'%s build.py $TARGETS')
env = Environment(BUILDERS = { 'MyBuild' : MyBuild })
env.MyBuild(target = 'f1', source = 'f1.in')
env.MyBuild(target = 'f2', source = 'f2.in')
""" % python)

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
 
