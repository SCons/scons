#!/usr/bin/env python
#
# __COPYRIGHT__
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
import string
import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.subdir('one', 'two', 'three')

test.write('build.py', r"""
import sys
exitval = int(sys.argv[1])
if exitval == 0:
    contents = open(sys.argv[3], 'rb').read()
    file = open(sys.argv[2], 'wb')
    file.write(contents)
    file.close()
sys.exit(exitval)
""")

test.write(['one', 'SConstruct'], """
B0 = Builder(action = r'%s ../build.py 0 $TARGET $SOURCES')
B1 = Builder(action = r'%s ../build.py 1 $TARGET $SOURCES')
env = Environment(BUILDERS = { 'B0' : B0, 'B1' : B1 })
env.B1(target = 'f1.out', source = 'f1.in')
env.B0(target = 'f2.out', source = 'f2.in')
env.B0(target = 'f3.out', source = 'f3.in')
""" % (python, python))

test.write(['one', 'f1.in'], "one/f1.in\n")
test.write(['one', 'f2.in'], "one/f2.in\n")
test.write(['one', 'f3.in'], "one/f3.in\n")

test.run(chdir = 'one', arguments = "f1.out f2.out f3.out",
         stderr = "scons: *** [f1.out] Error 1\n", status = 2)

test.fail_test(os.path.exists(test.workpath('f1.out')))
test.fail_test(os.path.exists(test.workpath('f2.out')))
test.fail_test(os.path.exists(test.workpath('f3.out')))

test.write(['two', 'SConstruct'], """
B0 = Builder(action = r'%s ../build.py 0 $TARGET $SOURCES')
B1 = Builder(action = r'%s ../build.py 1 $TARGET $SOURCES')
env = Environment(BUILDERS = { 'B0': B0, 'B1' : B1 })
env.B0(target = 'f1.out', source = 'f1.in')
env.B1(target = 'f2.out', source = 'f2.in')
env.B0(target = 'f3.out', source = 'f3.in')
""" % (python, python))

test.write(['two', 'f1.in'], "two/f1.in\n")
test.write(['two', 'f2.in'], "two/f2.in\n")
test.write(['two', 'f3.in'], "two/f3.in\n")

test.run(chdir = 'two', arguments = "f1.out f2.out f3.out",
         stderr = "scons: *** [f2.out] Error 1\n", status = 2)

test.fail_test(test.read(['two', 'f1.out']) != "two/f1.in\n")
test.fail_test(os.path.exists(test.workpath('f2.out')))
test.fail_test(os.path.exists(test.workpath('f3.out')))

test.write(['three', 'SConstruct'], """
B0 = Builder(action = r'%s ../build.py 0 $TARGET $SOURCES')
B1 = Builder(action = r'%s ../build.py 1 $TARGET $SOURCES')
env = Environment(BUILDERS = { 'B0' : B0, 'B1': B1 })
env.B0(target = 'f1.out', source = 'f1.in')
env.B0(target = 'f2.out', source = 'f2.in')
env.B1(target = 'f3.out', source = 'f3.in')
""" % (python, python))

test.write(['three', 'f1.in'], "three/f1.in\n")
test.write(['three', 'f2.in'], "three/f2.in\n")
test.write(['three', 'f3.in'], "three/f3.in\n")

test.run(chdir = 'three', arguments = "f1.out f2.out f3.out",
         stderr = "scons: *** [f3.out] Error 1\n", status = 2)

test.fail_test(test.read(['three', 'f1.out']) != "three/f1.in\n")
test.fail_test(test.read(['three', 'f2.out']) != "three/f2.in\n")
test.fail_test(os.path.exists(test.workpath('f3.out')))

test.write('SConstruct', """
env=Environment()
if env['PLATFORM'] == 'posix':
    from SCons.Platform.posix import fork_spawn
    env['SPAWN'] = fork_spawn
env['ENV']['PATH'] = ''
env.Command(target='foo.out', source=[], action='not_a_program')
""")

test.run(status=2, stderr=None)
err = test.stderr()
test.fail_test(string.find(err, 'Exception') != -1 or \
               string.find(err, 'Traceback') != -1)

test.pass_test()
