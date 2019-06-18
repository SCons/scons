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

"""
Test that Aliases with actions work.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
def cat(target, source, env):
    target = str(target[0])
    with open(target, "wb") as f:
        for src in source:
            with open(str(src), "rb") as ifp:
                f.write(ifp.read())

def foo(target, source, env):
    target = list(map(str, target))
    source = list(map(str, source))
    with open('foo', 'wb') as f:
        f.write(bytearray("foo(%s, %s)\\n" % (target, source),'utf-8'))

def bar(target, source, env):
    target = list(map(str, target))
    source = list(map(str, source))
    with open('bar', 'wb') as f:
        f.write(bytearray("bar(%s, %s)\\n" % (target, source),'utf-8'))

env = Environment(BUILDERS = {'Cat':Builder(action=cat)})
env.Alias(target = ['build-f1'], source = 'f1.out', action = foo)
f1 = env.Cat('f1.out', 'f1.in')
f2 = env.Cat('f2.out', 'f2.in')
f3 = env.Cat('f3.out', 'f3.in')
f4 = env.Cat('f4.out', 'f4.in')
f5 = env.Cat('f5.out', 'f5.in')
f6 = env.Cat('f6.out', 'f6.in')
env.Alias('build-all', [f1, f2, f3], foo)
env.Alias('build-add1', f3, foo)
env.Alias('build-add1', f2)
env.Alias('build-add2a',  f4)
env.Alias('build-add2b',  f5)
env.Alias(['build-add2a', 'build-add2b'], action=foo)
env.Alias('build-add3', f6)
env.Alias('build-add3', action=foo)
env.Alias('build-add3', action=bar)
""")

test.write('f1.in', "f1.in 1\n")
test.write('f2.in', "f2.in 1\n")
test.write('f3.in', "f3.in 1\n")
test.write('f4.in', "f4.in 1\n")
test.write('f5.in', "f5.in 1\n")
test.write('f6.in', "f6.in 1\n")

test.run(arguments = 'build-f1')

test.must_match('f1.out', "f1.in 1\n")
test.must_match('foo', "foo(['build-f1'], ['f1.out'])\n")

test.up_to_date(arguments = 'build-f1')

test.write('f1.in', "f1.in 2\n")
test.unlink('foo')

test.run(arguments = 'build-f1')

test.must_match('f1.out', "f1.in 2\n")
test.must_match('foo', "foo(['build-f1'], ['f1.out'])\n")

test.run(arguments = 'build-all')

test.must_match('f1.out', "f1.in 2\n")
test.must_match('f2.out', "f2.in 1\n")
test.must_match('f3.out', "f3.in 1\n")
test.must_match('foo', "foo(['build-all'], ['f1.out', 'f2.out', 'f3.out'])\n")

test.up_to_date(arguments = 'build-all')
test.up_to_date(arguments = 'build-add1')

test.write('f1.in', "f1.in 3\n")
test.write('f3.in', "f3.in 2\n")
test.unlink('foo')

test.run(arguments = 'build-add1')

test.must_match('f1.out', "f1.in 2\n")
test.must_match('f2.out', "f2.in 1\n")
test.must_match('f3.out', "f3.in 2\n")
test.must_match('foo', "foo(['build-add1'], ['f3.out', 'f2.out'])\n")

test.up_to_date(arguments = 'build-add1')

test.run(arguments = 'build-add2a')

test.must_match('f4.out', "f4.in 1\n")
test.must_not_exist('f5.out')
test.must_match('foo', "foo(['build-add2a'], ['f4.out'])\n")

test.run(arguments = 'build-add2b')

test.must_match('f5.out', "f5.in 1\n")
test.must_match('foo', "foo(['build-add2b'], ['f5.out'])\n")

test.run(arguments = 'build-add3')

test.must_match('f6.out', "f6.in 1\n")
test.must_match('foo', "foo(['build-add3'], ['f6.out'])\n")
test.must_match('bar', "bar(['build-add3'], ['f6.out'])\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
