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

import TestSCons

_python_ = TestSCons._python_

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
B0 = Builder(action = r'%(_python_)s ../build.py 0 $TARGET $SOURCES')
B1 = Builder(action = r'%(_python_)s ../build.py 1 $TARGET $SOURCES')
env = Environment(BUILDERS = { 'B0' : B0, 'B1' : B1 })
env.B1(target = 'f1.out', source = 'f1.in')
env.B0(target = 'f2.out', source = 'f2.in')
env.B0(target = 'f3.out', source = 'f3.in')
""" % locals())

test.write(['one', 'f1.in'], "one/f1.in\n")
test.write(['one', 'f2.in'], "one/f2.in\n")
test.write(['one', 'f3.in'], "one/f3.in\n")

test.run(chdir = 'one', arguments = "f1.out f2.out f3.out",
         stderr = "scons: *** [f1.out] Error 1\n", status = 2)

test.fail_test(os.path.exists(test.workpath('f1.out')))
test.fail_test(os.path.exists(test.workpath('f2.out')))
test.fail_test(os.path.exists(test.workpath('f3.out')))

test.write(['two', 'SConstruct'], """
B0 = Builder(action = r'%(_python_)s ../build.py 0 $TARGET $SOURCES')
B1 = Builder(action = r'%(_python_)s ../build.py 1 $TARGET $SOURCES')
env = Environment(BUILDERS = { 'B0': B0, 'B1' : B1 })
env.B0(target = 'f1.out', source = 'f1.in')
env.B1(target = 'f2.out', source = 'f2.in')
env.B0(target = 'f3.out', source = 'f3.in')
""" % locals())

test.write(['two', 'f1.in'], "two/f1.in\n")
test.write(['two', 'f2.in'], "two/f2.in\n")
test.write(['two', 'f3.in'], "two/f3.in\n")

test.run(chdir = 'two', arguments = "f1.out f2.out f3.out",
         stderr = "scons: *** [f2.out] Error 1\n", status = 2)

test.fail_test(test.read(['two', 'f1.out']) != "two/f1.in\n")
test.fail_test(os.path.exists(test.workpath('f2.out')))
test.fail_test(os.path.exists(test.workpath('f3.out')))

test.write(['three', 'SConstruct'], """
B0 = Builder(action = r'%(_python_)s ../build.py 0 $TARGET $SOURCES')
B1 = Builder(action = r'%(_python_)s ../build.py 1 $TARGET $SOURCES')
env = Environment(BUILDERS = { 'B0' : B0, 'B1': B1 })
env.B0(target = 'f1.out', source = 'f1.in')
env.B0(target = 'f2.out', source = 'f2.in')
env.B1(target = 'f3.out', source = 'f3.in')
""" % locals())

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
test.must_not_contain_any_line(test.stderr(), ['Exception', 'Traceback'])


# Test ETOOLONG (arg list too long).  This is not in exitvalmap,
# but that shouldn't cause a scons traceback.
long_cmd = 'xyz ' + "foobarxyz" * 100000
test.write('SConstruct', """
env=Environment()
if env['PLATFORM'] == 'posix':
    from SCons.Platform.posix import fork_spawn
    env['SPAWN'] = fork_spawn
env.Command(target='longcmd.out', source=[], action='echo %s')
"""%long_cmd)

test.run(status=2, stderr=None)

test.must_not_contain_any_line(test.stderr(), ['Exception', 'Traceback'])

# Python 1.5.2 on a FC3 system doesn't even get to the exitvalmap
# because it fails with "No such file or directory."  Just comment
# this out for now, there are plenty of other good tests below.
#expected = [
#    "too long", # posix
#    "nvalid argument", # win32
#]
#test.must_contain_any_line(test.stderr(), expected)


# Test bad shell ('./one' is a dir, so it can't be used as a shell).
# This will also give an exit status not in exitvalmap,
# with error "Permission denied" or "No such file or directory".
test.write('SConstruct', """
env=Environment()
if env['PLATFORM'] in ('posix', 'darwin'):
    from SCons.Platform.posix import fork_spawn
    env['SPAWN'] = fork_spawn
env['SHELL'] = 'one'
env.Command(target='badshell.out', source=[], action='foo')
""")

test.run(status=2, stderr=None)
test.must_not_contain_any_line(test.stderr(), ['Exception', 'Traceback'])
expect = [
    'No such file',
    'Permission denied',
    'permission denied',
]
test.must_contain_any_line(test.stderr(), expect)


# Test command with exit status -1.
# Should not give traceback.
test.write('SConstruct', """
import os
env = Environment(ENV = os.environ)
env.Command('dummy.txt', None, ['python -c "import sys; sys.exit(-1)"'])
""")

test.run(status=2, stderr=None)
test.must_not_contain_any_line(test.stderr(), ['Exception', 'Traceback'])


# Test SConscript with errors and an atexit function.
# Should not give traceback; the task error should get converted
# to a BuildError.
test.write('SConstruct', """
import atexit

env = Environment()
env2 = env.Clone()

env.Install("target", "dir1/myFile")
env2.Install("target", "dir2/myFile")

def print_build_failures():
    from SCons.Script import GetBuildFailures
    for bf in GetBuildFailures():
	print bf.action

atexit.register(print_build_failures)
""")

test.run(status=2, stderr=None)
test.must_not_contain_any_line(test.stderr(), ['Exception', 'Traceback'])


# No tests failed; OK.
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
