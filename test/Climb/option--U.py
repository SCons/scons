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

import sys

import TestSCons

test = TestSCons.TestSCons()

_python_ = TestSCons._python_

test.subdir('sub1', 'sub2', 'sub3')

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as ofp, open(sys.argv[2], 'rb') as ifp:
    ofp.write(ifp.read())
""")

test.write('SConstruct', r"""
DefaultEnvironment(tools=[])
import SCons.Defaults
env = Environment(tools=[])
env['BUILDERS']['B'] = Builder(action=r'%(_python_)s build.py $TARGET $SOURCES', multi=1)
Default(env.B(target = 'sub1/foo.out', source = 'sub1/foo.in'))
Export('env')
SConscript('sub2/SConscript')
Default(env.B(target = 'sub3/baz.out', source = 'sub3/baz.in'))
VariantDir('sub2b', 'sub2')
SConscript('sub2b/SConscript')
Default(env.B(target = 'sub2/xxx.out', source = 'xxx.in'))
SConscript('SConscript')
""" % locals())

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

test.must_exist(test.workpath('sub1', 'foo.out'))
test.must_not_exist(test.workpath('sub2', 'bar.out'))
test.must_not_exist(test.workpath('sub2b', 'bar.out'))
test.must_not_exist(test.workpath('sub3', 'baz.out'))
test.must_not_exist(test.workpath('bar.out'))
test.must_not_exist(test.workpath('sub2/xxx.out'))

test.unlink(['sub1', 'foo.out'])

test.write('SConscript', """\
env = Environment(tools=[], )
assert env.GetLaunchDir() == r'%s'
"""%test.workpath('sub1'))
test.run(arguments = '-U',
         chdir = 'sub1',
         stderr = "scons: *** No targets specified and no Default() targets found.  Stop.\n",
         status = 2)
test.must_not_exist(test.workpath('sub1', 'foo.out'))
test.must_not_exist(test.workpath('sub2', 'bar.out'))
test.must_not_exist(test.workpath('sub2b', 'bar.out'))
test.must_not_exist(test.workpath('sub3', 'baz.out'))
test.must_not_exist(test.workpath('bar.out'))
test.must_not_exist(test.workpath('sub2/xxx.out'))


if sys.platform == 'win32':
    sub2 = 'SUB2'
else:
    sub2 = 'sub2'
test.write('SConscript', """assert GetLaunchDir() == r'%s'"""%test.workpath(sub2))
test.run(chdir = sub2, arguments = '-U')
test.must_not_exist(test.workpath('sub1', 'foo.out'))
test.must_exist(test.workpath('sub2', 'bar.out'))
test.must_exist(test.workpath('sub2b', 'bar.out'))
test.must_not_exist(test.workpath('sub3', 'baz.out'))
test.must_exist(test.workpath('bar.out'))
test.must_not_exist(test.workpath('sub2/xxx.out'))

test.unlink(['sub2', 'bar.out'])
test.unlink(['sub2b', 'bar.out'])
test.unlink('bar.out')

test.write('SConscript', """assert GetLaunchDir() == r'%s'"""%test.workpath())
test.run(arguments='-U')
test.must_exist(test.workpath('sub1', 'foo.out'))
test.must_not_exist(test.workpath('sub2', 'bar.out'))
test.must_not_exist(test.workpath('sub2b', 'bar.out'))
test.must_exist(test.workpath('sub3', 'baz.out'))
test.must_not_exist(test.workpath('bar.out'))
test.must_exist(test.workpath('sub2/xxx.out'))

test.unlink(['sub1', 'foo.out'])
test.unlink(['sub3', 'baz.out'])
test.unlink(['sub2', 'xxx.out'])

test.write('SConscript', """assert GetLaunchDir() == r'%s'"""%test.workpath('sub3'))
test.run(chdir = 'sub3', arguments='-U bar')
test.must_not_exist(test.workpath('sub1', 'foo.out'))
test.must_exist(test.workpath('sub2', 'bar.out'))
test.must_exist(test.workpath('sub2b', 'bar.out'))
test.must_not_exist(test.workpath('sub3', 'baz.out'))
test.must_not_exist(test.workpath('bar.out'))
test.must_not_exist(test.workpath('sub2/xxx.out'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
