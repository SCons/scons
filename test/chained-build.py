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

test.write('SConstruct1', """
def build(env, target, source):
    open(str(target[0]), 'wt').write(open(str(source[0]), 'rt').read())

env=Environment(BUILDERS={'B' : Builder(action=build)})
env.B('foo.mid', 'foo.in')
""")

test.write('SConstruct2', """
def build(env, target, source):
    open(str(target[0]), 'wt').write(open(str(source[0]), 'rt').read())

env=Environment(BUILDERS={'B' : Builder(action=build)})
env.B('foo.out', 'foo.mid')
""")

test.write('foo.in', "foo.in")

test.run(arguments="--max-drift=0 -f SConstruct1 foo.mid",
         stdout = test.wrap_stdout('build("foo.mid", "foo.in")\n'))
test.run(arguments="--max-drift=0 -f SConstruct2 foo.out",
         stdout = test.wrap_stdout('build("foo.out", "foo.mid")\n'))

test.run(arguments="--max-drift=0 -f SConstruct1 foo.mid",
         stdout = test.wrap_stdout('scons: "foo.mid" is up to date.\n'))
test.run(arguments="--max-drift=0 -f SConstruct2 foo.out",
         stdout = test.wrap_stdout('scons: "foo.out" is up to date.\n'))

test.write('foo.in', "foo.in 2")

test.run(arguments="--max-drift=0 -f SConstruct1 foo.mid",
         stdout = test.wrap_stdout('build("foo.mid", "foo.in")\n'))
test.run(arguments="--max-drift=0 -f SConstruct2 foo.out",
         stdout = test.wrap_stdout('build("foo.out", "foo.mid")\n'))

test.run(arguments="--max-drift=0 -f SConstruct1 foo.mid",
         stdout = test.wrap_stdout('scons: "foo.mid" is up to date.\n'))
test.run(arguments="--max-drift=0 -f SConstruct2 foo.out",
         stdout = test.wrap_stdout('scons: "foo.out" is up to date.\n'))

test.pass_test()
