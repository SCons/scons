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

test.subdir('w1', 'w2')

SConstruct1_contents = """\
def build(env, target, source):
    open(str(target[0]), 'wt').write(open(str(source[0]), 'rt').read())

env=Environment(BUILDERS={'B' : Builder(action=build)})
env.B('foo.mid', 'foo.in')
"""

SConstruct2_contents = """\
def build(env, target, source):
    open(str(target[0]), 'wt').write(open(str(source[0]), 'rt').read())

env=Environment(BUILDERS={'B' : Builder(action=build)})
env.B('foo.out', 'foo.mid')
"""

# Test with the default of saving explanation info.
test.write(['w1', 'SConstruct1'], SConstruct1_contents)
test.write(['w1', 'SConstruct2'], SConstruct2_contents)
test.write(['w1', 'foo.in'], "foo.in 1")

test.run(chdir='w1',
         arguments="--max-drift=0 -f SConstruct1 foo.mid",
         stdout = test.wrap_stdout('build("foo.mid", "foo.in")\n'))
test.run(chdir='w1',
         arguments="--max-drift=0 -f SConstruct2 foo.out",
         stdout = test.wrap_stdout('build("foo.out", "foo.mid")\n'))

test.up_to_date(chdir='w1',
                options="--max-drift=0 -f SConstruct1",
                arguments="foo.mid")
test.up_to_date(chdir='w1',
                options="--max-drift=0 -f SConstruct2",
                arguments="foo.out")

test.write(['w1', 'foo.in'], "foo.in 2")

test.run(chdir='w1',
         arguments="--max-drift=0 -f SConstruct1 foo.mid",
         stdout = test.wrap_stdout('build("foo.mid", "foo.in")\n'))
test.run(chdir='w1',
         arguments="--max-drift=0 -f SConstruct2 foo.out",
         stdout = test.wrap_stdout('build("foo.out", "foo.mid")\n'))

test.up_to_date(chdir='w1',
                options="--max-drift=0 -f SConstruct1",
                arguments="foo.mid")
test.up_to_date(chdir='w1',
                options="--max-drift=0 -f SConstruct2",
                arguments="foo.out")

# Now test when we're not saving explanation info.
preamble = "SetOption('save_explain_info', 0)\n"
test.write(['w2', 'SConstruct1'], preamble + SConstruct1_contents)
test.write(['w2', 'SConstruct2'], preamble + SConstruct2_contents)
test.write(['w2', 'foo.in'], "foo.in 1")

test.run(chdir='w2',
         arguments="--max-drift=0 -f SConstruct1 foo.mid",
         stdout = test.wrap_stdout('build("foo.mid", "foo.in")\n'))
test.run(chdir='w2',
         arguments="--max-drift=0 -f SConstruct2 foo.out",
         stdout = test.wrap_stdout('build("foo.out", "foo.mid")\n'))

test.up_to_date(chdir='w2',
                options="--max-drift=0 -f SConstruct1",
                arguments="foo.mid")
test.up_to_date(chdir='w2',
                options="--max-drift=0 -f SConstruct2",
                arguments="foo.out")

test.write(['w2', 'foo.in'], "foo.in 2")

test.run(chdir='w2',
         arguments="--max-drift=0 -f SConstruct1 foo.mid",
         stdout = test.wrap_stdout('build("foo.mid", "foo.in")\n'))
test.run(chdir='w2',
         arguments="--max-drift=0 -f SConstruct2 foo.out",
         stdout = test.wrap_stdout('build("foo.out", "foo.mid")\n'))

test.up_to_date(chdir='w2',
                options="--max-drift=0 -f SConstruct1",
                arguments="foo.mid")
test.up_to_date(chdir='w2',
                options="--max-drift=0 -f SConstruct2",
                arguments="foo.out")

test.pass_test()
