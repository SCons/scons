#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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
import os
import os.path

test = TestSCons.TestSCons()

test.write('SConstruct',"""
BuildDir('var1', 'src', duplicate=0)
BuildDir('var2', 'src', duplicate=1)
SConscript('src/SConscript')
SConscript('var1/SConscript')
SConscript('var2/SConscript')
""")

test.subdir('src')

test.write('src/f.in', 'f.in')

test.write('src/SConscript',"""
def build(target, source, env):
    for t in target:
        open(str(t), "wt").write(str(t))

def emitter(target, source, env):
    target.append(str(target[0])+".foo")
    return target,source

b = Builder(name='foo', action=build, emitter=emitter)

env=Environment(BUILDERS=[b])
env.foo('f.out', 'f.in')
""")

test.run(arguments='.')

test.fail_test(not os.path.exists(test.workpath('src', 'f.out')))
test.fail_test(not os.path.exists(test.workpath('src', 'f.out.foo')))
test.fail_test(not os.path.exists(test.workpath('var1', 'f.out')))
test.fail_test(not os.path.exists(test.workpath('var1', 'f.out.foo')))
test.fail_test(not os.path.exists(test.workpath('var2', 'f.out')))
test.fail_test(not os.path.exists(test.workpath('var2', 'f.out.foo')))

test.pass_test()
