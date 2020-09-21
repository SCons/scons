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

test.subdir('src')

test.write('SConstruct',"""
VariantDir('var1', 'src', duplicate=0)
VariantDir('var2', 'src', duplicate=1)
SConscript('src/SConscript')
SConscript('var1/SConscript')
SConscript('var2/SConscript')
""")

test.write('src/SConscript',"""
def build(target, source, env):
    for t in target:
        with open(str(t), "wt") as f:
            f.write(str(t))

def emitter(target, source, env):
    target.append(str(target[0])+".foo")
    return target,source

def emit1(t, s, e): return (t + ['emit.1'], s)
def emit2(t, s, e): return (t + ['emit.2'], s)

foo = Builder(action=build, emitter=emitter)
bar = Builder(action=build, emitter='$EMITTERS')

env=Environment(BUILDERS={ 'foo': foo, 'bar': bar },
                EMITTERS=[emit1, emit2])
env.foo('f.out', 'f.in')
env.foo(File('g.out'), 'g.in')
env.bar('h.out', 'h.in')
""")

test.write(['src', 'f.in'], 'f.in')
test.write(['src', 'g.in'], 'g.in')
test.write(['src', 'h.in'], 'h.in')

# Do 'src' last so that creation of the emitter files in there doesn't
# interfere with searching for them in the VariantDirs.

test.run(arguments='var2')

test.must_exist(test.workpath('var2', 'f.out'))
test.must_exist(test.workpath('var2', 'f.out.foo'))
test.must_exist(test.workpath('var2', 'g.out'))
test.must_exist(test.workpath('var2', 'g.out.foo'))
test.must_exist(test.workpath('var2', 'h.out'))
test.must_exist(test.workpath('var2', 'emit.1'))
test.must_exist(test.workpath('var2', 'emit.2'))

test.run(arguments = 'var1')

test.must_exist(test.workpath('var1', 'f.out'))
test.must_exist(test.workpath('var1', 'f.out.foo'))
test.must_exist(test.workpath('var1', 'g.out'))
test.must_exist(test.workpath('var1', 'g.out.foo'))
test.must_exist(test.workpath('var1', 'h.out'))
test.must_exist(test.workpath('var1', 'emit.1'))
test.must_exist(test.workpath('var1', 'emit.2'))

test.run(arguments = 'src')

test.must_exist(test.workpath('src', 'f.out'))
test.must_exist(test.workpath('src', 'f.out.foo'))
test.must_exist(test.workpath('src', 'g.out'))
test.must_exist(test.workpath('src', 'g.out.foo'))
test.must_exist(test.workpath('src', 'h.out'))
test.must_exist(test.workpath('src', 'emit.1'))
test.must_exist(test.workpath('src', 'emit.2'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
