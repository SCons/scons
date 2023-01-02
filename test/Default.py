#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

"""
Verify various combinations of arguments to Default() work properly.
"""

import os

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

for dirname in ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']:
    test.subdir(dirname)
    test.write(os.path.join(dirname, 'foo.in'), dirname + "/foo.in\n")
    test.write(os.path.join(dirname, 'bar.in'), dirname + "/bar.in\n")

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'w') as f, open(sys.argv[2], 'r') as ifp:
    f.write(ifp.read())
""")

#
test.write(['one', 'SConstruct'], """
B = Builder(action = r'%(_python_)s ../build.py $TARGET $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
env.B(target = 'bar.out', source = 'bar.in')
Default('foo.out')
""" % locals())

test.write(['two', 'SConstruct'], """
B = Builder(action = r'%(_python_)s ../build.py $TARGET $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
env.B(target = 'bar.out', source = 'bar.in')
Default('foo.out', 'bar.out')
""" % locals())

test.write(['three', 'SConstruct'], """
B = Builder(action = r'%(_python_)s ../build.py $TARGET $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
env.B(target = 'bar.out', source = 'bar.in')
Default(Split('foo.out bar.out'))
""" % locals())

test.write(['four', 'SConstruct'], """
B = Builder(action = r'%(_python_)s ../build.py $TARGET $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(BUILDERS = { 'B' : B })
env.B(target = ['foo bar'], source = 'foo.in')
env.B(target = 'foo', source = 'foo.in')
env.B(target = 'bar', source = 'bar.in')
Default(['foo bar'])
""" % locals())

test.write(['five', 'SConstruct'], """
B = Builder(action = r'%(_python_)s ../build.py $TARGET $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(BUILDERS = { 'B' : B })
Default(env.B(target = 'foo.out', source = 'foo.in'))
Default(env.B(target = 'bar.out', source = 'bar.in'))
""" % locals())


for dirname in ['one', 'two', 'three', 'four', 'five']:
    test.run(chdir=dirname)       # no arguments, use the Default

test.must_match(test.workpath('one', 'foo.out'), "one/foo.in\n", mode='r')
test.fail_test(os.path.exists(test.workpath('one', 'bar')))

test.must_match(test.workpath('two', 'foo.out'), "two/foo.in\n", mode='r')
test.must_match(test.workpath('two', 'bar.out'), "two/bar.in\n", mode='r')

test.must_match(test.workpath('three', 'foo.out'), "three/foo.in\n", mode='r')
test.must_match(test.workpath('three', 'bar.out'), "three/bar.in\n", mode='r')

test.fail_test(os.path.exists(test.workpath('four', 'foo')))
test.fail_test(os.path.exists(test.workpath('four', 'bar')))
test.must_match(test.workpath('four', 'foo bar'), "four/foo.in\n", mode='r')

test.must_match(test.workpath('five', 'foo.out'), "five/foo.in\n", mode='r')
test.must_match(test.workpath('five', 'bar.out'), "five/bar.in\n", mode='r')


# Test how a None Default() argument works to disable/reset default targets.
test.write(['six', 'SConstruct'], """\
B = Builder(action = r'%(_python_)s ../build.py $TARGET $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(BUILDERS = { 'B' : B })
foo = env.B(target = 'foo.out', source = 'foo.in')
bar = env.B(target = 'bar.out', source = 'bar.in')
Default(None)
""" % locals())

test.run(chdir='six', status=2,
         stderr="scons: *** No targets specified and no Default() targets found.  Stop.\n")

test.write(['seven', 'SConstruct'], """\
B = Builder(action = r'%(_python_)s ../build.py $TARGET $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(BUILDERS = { 'B' : B })
foo = env.B(target = 'foo.out', source = 'foo.in')
bar = env.B(target = 'bar.out', source = 'bar.in')
Default(foo, bar, None)
""" % locals())

test.run(chdir='seven', status=2,
         stderr="scons: *** No targets specified and no Default() targets found.  Stop.\n")

test.write(['eight', 'SConstruct'], """\
B = Builder(action = r'%(_python_)s ../build.py $TARGET $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(BUILDERS = { 'B' : B })
foo = env.B(target = 'foo.out', source = 'foo.in')
bar = env.B(target = 'bar.out', source = 'bar.in')
Default(foo, None, bar)
""" % locals())

test.run(chdir='eight')       # no arguments, use the Default

test.fail_test(os.path.exists(test.workpath('eight', 'foo.out')))
test.must_match(test.workpath('eight', 'bar.out'), "eight/bar.in\n", mode='r')


test.subdir('nine', ['nine', 'sub1'])

test.write(['nine', 'SConstruct'], """\
B = Builder(action = r'%(_python_)s build.py $TARGET $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'xxx.out', source = 'xxx.in')
SConscript('sub1/SConscript')
""" % locals())

test.write(['nine', 'xxx.in'], "xxx.in\n")

test.write(['nine', 'sub1', 'SConscript'], """
B = Builder(action = r'%(_python_)s ../build.py $TARGET $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'xxx.out', source = 'xxx.in')
Default('xxx.out')
""" % locals())

test.write(['nine', 'sub1', 'xxx.in'], "sub1/xxx.in\n")

test.run(chdir='nine')        # no arguments, use the Default

test.fail_test(os.path.exists(test.workpath('nine', 'xxx.out')))
test.must_match(test.workpath('nine', 'sub1', 'xxx.out'), "sub1/xxx.in\n", mode='r')


test.subdir('ten', ['ten', 'sub2'])

test.write(['ten', 'SConstruct'], """\
Default('sub2')
B = Builder(action = r'%(_python_)s ../build.py $TARGET $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'xxx.out', source = 'xxx.in')
SConscript('sub2/SConscript')
""" % locals())

test.write(['ten', 'xxx.in'], "xxx.in\n")

test.write(['ten', 'sub2', 'SConscript'], """
B = Builder(action = r'%(_python_)s ../build.py $TARGET $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'xxx.out', source = 'xxx.in')
""" % locals())

test.write(['ten', 'sub2', 'xxx.in'], "sub2/xxx.in\n")

test.run(chdir='ten')  # no arguments, use the Default

test.fail_test(os.path.exists(test.workpath('ten', 'xxx.out')))
test.must_match(test.workpath('ten', 'sub2', 'xxx.out'), "sub2/xxx.in\n", mode='r')


test.subdir('eleven')

test.write(['eleven', 'SConstruct'], """
B = Builder(action = r'%(_python_)s ../build.py $TARGET $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(BUILDERS = { 'B' : B }, XXX = 'foo.out')
env.B(target = 'foo.out', source = 'foo.in')
env.B(target = 'bar.out', source = 'bar.in')
env.Default('$XXX')
""" % locals())

test.write(os.path.join('eleven', 'foo.in'), "eleven/foo.in\n")

test.write(os.path.join('eleven', 'bar.in'), "eleven/bar.in\n")

test.run(chdir='eleven')      # no arguments, use the Default

test.must_match(test.workpath('eleven', 'foo.out'), "eleven/foo.in\n", mode='r')
test.fail_test(os.path.exists(test.workpath('eleven', 'bar')))


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
