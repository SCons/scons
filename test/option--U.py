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
import os.path
import sys

import TestSCons

test = TestSCons.TestSCons()

python = TestSCons.python

test.subdir('sub1', 'sub2', 'sub3')

test.write('build.py', r"""
import sys
contents = open(sys.argv[2], 'rb').read()
file = open(sys.argv[1], 'wb')
file.write(contents)
file.close()
""")

test.write('SConstruct', r"""
import SCons.Defaults
env = Environment()
env['BUILDERS']['B'] = Builder(action=r'%s build.py $TARGET $SOURCES', multi=1)
Default(env.B(target = 'sub1/foo.out', source = 'sub1/foo.in'))
Export('env')
SConscript('sub2/SConscript')
Default(env.B(target = 'sub3/baz.out', source = 'sub3/baz.in'))
BuildDir('sub2b', 'sub2')
SConscript('sub2b/SConscript')
Default(env.B(target = 'sub2/xxx.out', source = 'xxx.in'))
SConscript('SConscript')
""" % python)

test.write(['sub2', 'SConscript'], """
Import('env')
bar = env.B(target = 'bar.out', source = 'bar.in')
Default(bar)
env.Alias('bar', bar)
Default(env.B(target = '../bar.out', source = 'bar.in'))
""")


test.write(['sub1', 'foo.in'], "sub1/foo.in\n")
test.write(['sub2', 'bar.in'], "sub2/bar.in\n")
test.write(['sub3', 'baz.in'], "sub3/baz.in\n")
test.write('xxx.in', "xxx.in\n")

test.write('SConscript', """assert GetLaunchDir() == r'%s'\n"""%test.workpath('sub1'))
test.run(arguments = '-U foo.out', chdir = 'sub1')

test.fail_test(not os.path.exists(test.workpath('sub1', 'foo.out')))
test.fail_test(os.path.exists(test.workpath('sub2', 'bar.out')))
test.fail_test(os.path.exists(test.workpath('sub2b', 'bar.out')))
test.fail_test(os.path.exists(test.workpath('sub3', 'baz.out')))
test.fail_test(os.path.exists(test.workpath('bar.out')))
test.fail_test(os.path.exists(test.workpath('sub2/xxx.out')))

test.unlink(['sub1', 'foo.out'])

test.write('SConscript', """\
env = Environment()
assert env.GetLaunchDir() == r'%s'
"""%test.workpath('sub1'))
test.run(arguments = '-U',
         chdir = 'sub1',
         stderr = "scons: *** No targets specified and no Default() targets found.  Stop.\n",
         status = 2)
test.fail_test(os.path.exists(test.workpath('sub1', 'foo.out')))
test.fail_test(os.path.exists(test.workpath('sub2', 'bar.out')))
test.fail_test(os.path.exists(test.workpath('sub2b', 'bar.out')))
test.fail_test(os.path.exists(test.workpath('sub3', 'baz.out')))
test.fail_test(os.path.exists(test.workpath('bar.out')))
test.fail_test(os.path.exists(test.workpath('sub2/xxx.out')))


if sys.platform == 'win32':
    test.write('SConscript', """assert GetLaunchDir() == r'%s'"""%test.workpath('SUB2'))
    test.run(chdir = 'SUB2', arguments = '-U')
else:
    test.write('SConscript', """assert GetLaunchDir() == r'%s'"""%test.workpath('sub2'))
    test.run(chdir = 'sub2', arguments = '-U')
test.fail_test(os.path.exists(test.workpath('sub1', 'foo.out')))
test.fail_test(not os.path.exists(test.workpath('sub2', 'bar.out')))
test.fail_test(not os.path.exists(test.workpath('sub2b', 'bar.out')))
test.fail_test(os.path.exists(test.workpath('sub3', 'baz.out')))
test.fail_test(not os.path.exists(test.workpath('bar.out')))
test.fail_test(os.path.exists(test.workpath('sub2/xxx.out')))

test.unlink(['sub2', 'bar.out'])
test.unlink(['sub2b', 'bar.out'])
test.unlink('bar.out')

test.write('SConscript', """assert GetLaunchDir() == r'%s'"""%test.workpath())
test.run(arguments='-U')
test.fail_test(not os.path.exists(test.workpath('sub1', 'foo.out')))
test.fail_test(os.path.exists(test.workpath('sub2', 'bar.out')))
test.fail_test(os.path.exists(test.workpath('sub2b', 'bar.out')))
test.fail_test(not os.path.exists(test.workpath('sub3', 'baz.out')))
test.fail_test(os.path.exists(test.workpath('bar.out')))
test.fail_test(not os.path.exists(test.workpath('sub2/xxx.out')))

test.unlink(['sub1', 'foo.out'])
test.unlink(['sub3', 'baz.out'])
test.unlink(['sub2', 'xxx.out'])

test.write('SConscript', """assert GetLaunchDir() == r'%s'"""%test.workpath('sub3'))
test.run(chdir = 'sub3', arguments='-U bar')
test.fail_test(os.path.exists(test.workpath('sub1', 'foo.out')))
test.fail_test(not os.path.exists(test.workpath('sub2', 'bar.out')))
test.fail_test(not os.path.exists(test.workpath('sub2b', 'bar.out')))
test.fail_test(os.path.exists(test.workpath('sub3', 'baz.out')))
test.fail_test(os.path.exists(test.workpath('bar.out')))
test.fail_test(os.path.exists(test.workpath('sub2/xxx.out')))

# Make sure that a Default() directory doesn't cause an exception.
test.subdir('sub4')

test.write(['sub4', 'SConstruct'], """
Default('.')
""")

test.run(chdir = 'sub4', arguments = '-U')

# Make sure no Default() targets doesn't cause an exception.
test.subdir('sub5')

test.write(['sub5', 'SConstruct'], "\n")

test.run(chdir = 'sub5',
         arguments = '-U',
         stderr = "scons: *** No targets specified and no Default() targets found.  Stop.\n",
         status = 2)

#
test.write('SConstruct', """
Default('not_a_target.in')
""")

test.run(arguments = '-U', status=2, stderr="""\
scons: *** Do not know how to make target `not_a_target.in'.  Stop.
""")

# Make sure explicit targets beginning with ../ get built.
test.subdir('sub6', ['sub6', 'dir'])

test.write(['sub6', 'SConstruct'], """\
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(BUILDERS={'Cat':Builder(action=cat)})
env.Cat('foo.out', 'foo.in')
SConscript('dir/SConscript', "env")
""")

test.write(['sub6', 'foo.in'], "foo.in\n")

test.write(['sub6', 'dir', 'SConscript'], """\
Import("env")
bar = env.Cat('bar.out', 'bar.in')
Default(bar)
""")

test.write(['sub6', 'dir', 'bar.in'], "bar.in\n")

test.run(chdir = 'sub6/dir', arguments = '-U ../foo.out')

test.fail_test(not os.path.exists(test.workpath('sub6', 'foo.out')))
test.fail_test(os.path.exists(test.workpath('sub6', 'dir', 'bar.out')))

test.pass_test()
