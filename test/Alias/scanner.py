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
Test that an Alias of a node with a Scanner works.
"""


import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
DefaultEnvironment(tools=[])
def cat(env, source, target):
    with open(target[0], "wb") as f:
        for src in source:
            with open(src, "rb") as ifp:
                f.write(ifp.read())

XBuilder = Builder(action = cat, src_suffix = '.x', suffix = '.c')
env = Environment(tools=[])
env.Append(BUILDERS = { 'XBuilder': XBuilder })
f = env.XBuilder(source = ['file.x'], target = ['file.c'])
env.Alias(target = ['cfiles'], source = f)
Default(['cfiles'])
""")

test.write('file.x', "file.x\n")

test.run()

test.fail_test(test.read('file.c') != b"file.x\n")

test.pass_test()
