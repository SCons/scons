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

import os.path
import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
contents = open(sys.argv[2], 'rb').read()
file = open(sys.argv[1], 'wb')
file.write(contents)
file.close()
""")

test.write('SConstruct', """
B = Builder(action = r'%s build.py $TARGETS $SOURCES')
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo1.out', source = 'foo1.in')
env.B(target = 'foo2.out', source = 'foo2.xxx')
env.B(target = 'foo2.xxx', source = 'foo2.in')
env.B(target = 'foo3.out', source = 'foo3.in')
import os
if hasattr(os, 'symlink'):
    def symlink1(env, target, source):
        # symlink to a file that exists
        os.symlink(str(source[0]), str(target[0]))
    env.Command(target = 'symlink1', source = 'foo1.in', action = symlink1)
    def symlink2(env, target, source):
        # force symlink to a file that doesn't exist
        os.symlink('does_not_exist', str(target[0]))
    env.Command(target = 'symlink2', source = 'foo1.in', action = symlink2)
""" % python)

test.write('foo1.in', "foo1.in\n")

test.write('foo2.in', "foo2.in\n")

test.write('foo3.in', "foo3.in\n")

test.run(arguments = 'foo1.out foo2.out foo3.out')

test.fail_test(test.read(test.workpath('foo1.out')) != "foo1.in\n")
test.fail_test(test.read(test.workpath('foo2.xxx')) != "foo2.in\n")
test.fail_test(test.read(test.workpath('foo2.out')) != "foo2.in\n")
test.fail_test(test.read(test.workpath('foo3.out')) != "foo3.in\n")

def wrap_clean_stdout(string):
    return "scons: Reading SConscript files ...\n" + \
           "scons: done reading SConscript files.\n" + \
           "scons: Cleaning targets ...\n" + \
           string + \
           "scons: done cleaning targets.\n"

test.run(arguments = '-c foo1.out',
         stdout = wrap_clean_stdout("Removed foo1.out\n"))

test.fail_test(os.path.exists(test.workpath('foo1.out')))
test.fail_test(not os.path.exists(test.workpath('foo2.xxx')))
test.fail_test(not os.path.exists(test.workpath('foo2.out')))
test.fail_test(not os.path.exists(test.workpath('foo3.out')))

test.run(arguments = '--clean foo2.out foo2.xxx',
         stdout = wrap_clean_stdout("Removed foo2.xxx\nRemoved foo2.out\n"))

test.fail_test(os.path.exists(test.workpath('foo1.out')))
test.fail_test(os.path.exists(test.workpath('foo2.xxx')))
test.fail_test(os.path.exists(test.workpath('foo2.out')))
test.fail_test(not os.path.exists(test.workpath('foo3.out')))

test.run(arguments = '--remove foo3.out',
         stdout = wrap_clean_stdout("Removed foo3.out\n"))

test.fail_test(os.path.exists(test.workpath('foo1.out')))
test.fail_test(os.path.exists(test.workpath('foo2.xxx')))
test.fail_test(os.path.exists(test.workpath('foo2.out')))
test.fail_test(os.path.exists(test.workpath('foo3.out')))

test.run(arguments = '.')

test.fail_test(test.read(test.workpath('foo1.out')) != "foo1.in\n")
test.fail_test(test.read(test.workpath('foo2.xxx')) != "foo2.in\n")
test.fail_test(test.read(test.workpath('foo2.out')) != "foo2.in\n")
test.fail_test(test.read(test.workpath('foo3.out')) != "foo3.in\n")

if hasattr(os, 'symlink'):
    test.fail_test(not os.path.islink(test.workpath('symlink1')))
    test.fail_test(not os.path.islink(test.workpath('symlink2')))

test.run(arguments = '-c foo2.xxx',
         stdout = wrap_clean_stdout("Removed foo2.xxx\n"))

test.fail_test(test.read(test.workpath('foo1.out')) != "foo1.in\n")
test.fail_test(os.path.exists(test.workpath('foo2.xxx')))
test.fail_test(test.read(test.workpath('foo2.out')) != "foo2.in\n")
test.fail_test(test.read(test.workpath('foo3.out')) != "foo3.in\n")

test.run(arguments = '-c .')

test.fail_test(os.path.exists(test.workpath('foo1.out')))
test.fail_test(os.path.exists(test.workpath('foo2.out')))
test.fail_test(os.path.exists(test.workpath('foo3.out')))

if hasattr(os, 'symlink'):
    test.fail_test(os.path.islink(test.workpath('symlink1')))
    test.fail_test(os.path.islink(test.workpath('symlink2')))

test.run(arguments = 'foo1.out foo2.out foo3.out')

expect = wrap_clean_stdout("""Removed foo1.out
Removed foo2.xxx
Removed foo2.out
Removed foo3.out
""")

test.run(arguments = '-c -n foo1.out foo2.out foo3.out', stdout = expect)

test.run(arguments = '-n -c foo1.out foo2.out foo3.out', stdout = expect)

test.fail_test(test.read(test.workpath('foo1.out')) != "foo1.in\n")
test.fail_test(test.read(test.workpath('foo2.xxx')) != "foo2.in\n")
test.fail_test(test.read(test.workpath('foo2.out')) != "foo2.in\n")
test.fail_test(test.read(test.workpath('foo3.out')) != "foo3.in\n")

test.writable('.', 0)
f = open(test.workpath('foo1.out'))
test.run(arguments = '-c foo1.out',
         stdout = wrap_clean_stdout("scons: Could not remove 'foo1.out': Permission denied\n"))
test.fail_test(not os.path.exists(test.workpath('foo1.out')))
f.close()
test.writable('.', 1)

test.subdir('subd')
test.write(['subd', 'foon.in'], "foon.in\n")
test.write(['subd', 'foox.in'], "foox.in\n")
test.write('aux1.x', "aux1.x\n")
test.write('aux2.x', "aux2.x\n")
test.write('SConstruct', """
B = Builder(action = r'%s build.py $TARGETS $SOURCES')
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo1.out', source = 'foo1.in')
env.B(target = 'foo2.out', source = 'foo2.xxx')
env.B(target = 'foo2.xxx', source = 'foo2.in')
env.B(target = 'foo3.out', source = 'foo3.in')
SConscript('subd/SConscript')
Clean('foo2.xxx', ['aux1.x'])
Clean('foo2.xxx', ['aux2.x'])
Clean('.', ['subd'])
""" % python)

test.write(['subd', 'SConscript'], """
Clean('.', 'foox.in')
""")

expect = wrap_clean_stdout("""Removed foo2.xxx
Removed aux1.x
Removed aux2.x
""")
test.run(arguments = '-c foo2.xxx', stdout=expect)
test.fail_test(test.read(test.workpath('foo1.out')) != "foo1.in\n")
test.fail_test(os.path.exists(test.workpath('foo2.xxx')))
test.fail_test(test.read(test.workpath('foo2.out')) != "foo2.in\n")
test.fail_test(test.read(test.workpath('foo3.out')) != "foo3.in\n")

expect = wrap_clean_stdout("Removed %s\n" % os.path.join('subd', 'foox.in'))
test.run(arguments = '-c subd', stdout=expect)
test.fail_test(os.path.exists(test.workpath('foox.in')))

expect = wrap_clean_stdout("""Removed foo1.out
Removed foo2.xxx
Removed foo2.out
Removed foo3.out
Removed %s
Removed %s
Removed directory subd
""" % (os.path.join('subd','SConscript'), os.path.join('subd', 'foon.in')))
test.run(arguments = '-c -n .', stdout=expect)

expect = wrap_clean_stdout("""Removed foo1.out
Removed foo2.out
Removed foo3.out
Removed %s
Removed %s
Removed directory subd
""" % (os.path.join('subd','SConscript'), os.path.join('subd', 'foon.in')))
test.run(arguments = '-c .', stdout=expect)
test.fail_test(os.path.exists(test.workpath('subdir', 'foon.in')))
test.fail_test(os.path.exists(test.workpath('subdir')))


# Ensure that Set/GetOption('clean') works correctly:
test.write('SConstruct', """
B = Builder(action = r'%s build.py $TARGETS $SOURCES')
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')

assert not GetOption('clean')
"""%python)

test.write('foo.in', '"Foo", I say!\n')

test.run(arguments='foo.out')
test.fail_test(test.read(test.workpath('foo.out')) != '"Foo", I say!\n')

test.write('SConstruct', """
B = Builder(action = r'%s build.py $TARGETS $SOURCES')
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')

assert GetOption('clean')
SetOption('clean', 0)
assert GetOption('clean')
"""%python)

test.run(arguments='-c foo.out')
test.fail_test(os.path.exists(test.workpath('foo.out')))

test.write('SConstruct', """
B = Builder(action = r'%s build.py $TARGETS $SOURCES')
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
"""%python)

test.run(arguments='foo.out')
test.fail_test(test.read(test.workpath('foo.out')) != '"Foo", I say!\n')

test.write('SConstruct', """
B = Builder(action = r'%s build.py $TARGETS $SOURCES')
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')

assert not GetOption('clean')
SetOption('clean', 1)
assert GetOption('clean')
"""%python)

test.run(arguments='foo.out')
test.fail_test(os.path.exists(test.workpath('foo.out')))

test.pass_test()


