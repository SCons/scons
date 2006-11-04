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

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment()

def copy1(env, source, target):
    open(str(target[0]), 'wb').write(open(str(source[0]), 'rb').read())

def copy2(env, source, target):
    return copy1(env, source, target)

env['BUILDERS']['Copy1'] = Builder(action=copy1)
env['BUILDERS']['Copy2'] = Builder(action=copy2)

env.Copy2('foo.mid', 'foo.in')
env.Copy1('foo.out', 'foo.mid')

env2 = env.Clone()
env2.TargetSignatures('build')
env2.Copy2('bar.mid', 'bar.in')
env2.Copy1('bar.out', 'bar.mid')

TargetSignatures('content')
""")

test.write('foo.in', 'foo.in')
test.write('bar.in', 'bar.in')

test.run(arguments="bar.out foo.out",
         stdout=test.wrap_stdout("""\
copy2(["bar.mid"], ["bar.in"])
copy1(["bar.out"], ["bar.mid"])
copy2(["foo.mid"], ["foo.in"])
copy1(["foo.out"], ["foo.mid"])
"""))

test.up_to_date(arguments='bar.out foo.out')

test.write('SConstruct', """
env = Environment()

def copy1(env, source, target):
    open(str(target[0]), 'wb').write(open(str(source[0]), 'rb').read())

def copy2(env, source, target):
    x = 2 # added this line
    return copy1(env, source, target)

env['BUILDERS']['Copy1'] = Builder(action=copy1)
env['BUILDERS']['Copy2'] = Builder(action=copy2)

env.Copy2('foo.mid', 'foo.in')
env.Copy1('foo.out', 'foo.mid')

env2 = env.Clone()
env2.TargetSignatures('build')
env2.Copy2('bar.mid', 'bar.in')
env2.Copy1('bar.out', 'bar.mid')

TargetSignatures('content')
""")

test.run(arguments="bar.out foo.out",
         stdout=test.wrap_stdout("""\
copy2(["bar.mid"], ["bar.in"])
copy1(["bar.out"], ["bar.mid"])
copy2(["foo.mid"], ["foo.in"])
scons: `foo.out' is up to date.
"""))

test.write('SConstruct', """
env = Environment()

def copy1(env, source, target):
    open(str(target[0]), 'wb').write(open(str(source[0]), 'rb').read())

def copy2(env, source, target):
    x = 2 # added this line
    return copy1(env, source, target)

env['BUILDERS']['Copy1'] = Builder(action=copy1)
env['BUILDERS']['Copy2'] = Builder(action=copy2)

env.Copy2('foo.mid', 'foo.in')
env.Copy1('foo.out', 'foo.mid')

env2 = env.Copy()
env2.TargetSignatures('content')
env2.Copy2('bar.mid', 'bar.in')
env2.Copy1('bar.out', 'bar.mid')

TargetSignatures('build')
""")

test.run(arguments="bar.out foo.out",
         stdout=test.wrap_stdout("""\
copy1(["bar.out"], ["bar.mid"])
copy1(["foo.out"], ["foo.mid"])
"""))

test.write('SConstruct', """
env = Environment()

def copy1(env, source, target):
    open(str(target[0]), 'wb').write(open(str(source[0]), 'rb').read())

def copy2(env, source, target):
    return copy1(env, source, target)

env['BUILDERS']['Copy1'] = Builder(action=copy1)
env['BUILDERS']['Copy2'] = Builder(action=copy2)

env.Copy2('foo.mid', 'foo.in')
env.Copy1('foo.out', 'foo.mid')

env2 = env.Copy()
env2.TargetSignatures('content')
env2.Copy2('bar.mid', 'bar.in')
env2.Copy1('bar.out', 'bar.mid')

TargetSignatures('build')
""")

test.run(arguments='bar.out foo.out',
         stdout=test.wrap_stdout("""\
copy2(["bar.mid"], ["bar.in"])
scons: `bar.out' is up to date.
copy2(["foo.mid"], ["foo.in"])
copy1(["foo.out"], ["foo.mid"])
"""))


test.pass_test()
