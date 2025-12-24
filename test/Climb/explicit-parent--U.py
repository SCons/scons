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
Make sure explicit targets beginning with ../ get built correctly.
by the -U option.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('subdir')

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
def cat(env, source, target):
    target = str(target[0])
    with open(target, 'wb') as ofp:
        for src in source:
            with open(src, 'rb') as ifp:
                ofp.write(ifp.read())
env = Environment(tools=[],
                  BUILDERS={'Cat':Builder(action=cat)})
env.Cat('foo.out', 'foo.in')
SConscript('subdir/SConscript', "env")
""")

test.write('foo.in', "foo.in\n")

test.write(['subdir', 'SConscript'], """\
Import("env")
bar = env.Cat('bar.out', 'bar.in')
Default(bar)
""")

test.write(['subdir', 'bar.in'], "subdir/bar.in\n")

test.run(chdir = 'subdir', arguments = '-U ../foo.out')

test.must_exist(test.workpath('foo.out'))
test.must_not_exist(test.workpath('subdir', 'bar.out'))

test.pass_test()
