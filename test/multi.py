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
import os.path

test = TestSCons.TestSCons()

test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
env.B(target = 'foo.out', source = 'bar.in')
""")

test.write('foo.in', 'foo.in\n')
test.write('bar.in', 'bar.in\n')

test.run(arguments='foo.out')

test.fail_test(not os.path.exists(test.workpath('foo.out')))
test.fail_test(not test.read('foo.out') == 'foo.in\nbar.in\n')

test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=0)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
env.B(target = 'foo.out', source = 'bar.in')
""")

test.run(arguments='foo.out', 
         status=2, 
         stderr="""
SCons error: Multiple ways to build the same target were specified for: foo.out
File "SConstruct", line 10, in ?
""")

test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in', foo=1)
env.B(target = 'foo.out', source = 'bar.in', foo=2)
""")

test.run(arguments='foo.out', 
         status=2, 
         stderr="""
SCons error: Two different sets of build arguments were specified for the same target: foo.out
File "SConstruct", line 10, in ?
""")

test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env2 = env.Copy(CCFLAGS='foo')
env.B(target = 'foo.out', source = 'foo.in')
env2.B(target = 'foo.out', source = 'bar.in')
""")

test.run(arguments='foo.out', 
         status=2, 
         stderr="""
SCons error: Two different environments were specified for the same target: foo.out
File "SConstruct", line 11, in ?
""")

test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=0)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
env.B(target = 'foo.out', source = 'foo.in')
""")

test.run(arguments='foo.out')
test.fail_test(not test.read('foo.out') == 'foo.in\n')

test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

def build2(env, target, source):
    build(env, target, source)

B = Builder(action=build, multi=1)
C = Builder(action=build2, multi=1)
env = Environment(BUILDERS = { 'B' : B, 'C' : C })
env.B(target = 'foo.out', source = 'foo.in')
env.C(target = 'foo.out', source = 'bar.in')
""")

test.run(arguments='foo.out', 
         status=2, 
         stderr="""
SCons error: Two different builders (B and C) were specified for the same target: foo.out
File "SConstruct", line 14, in ?
""")

test.write('SConstruct', """
def build(env, target, source):
    for t in target:
        file = open(str(t), 'wb')
        for s in source:
            file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = ['foo.out', 'bar.out'], source = 'foo.in')
env.B(target = ['foo.out', 'bar.out'], source = 'bar.in')
""")

test.run(arguments='bar.out')
test.fail_test(not os.path.exists(test.workpath('bar.out')))
test.fail_test(not test.read('bar.out') == 'foo.in\nbar.in\n')
test.fail_test(not os.path.exists(test.workpath('foo.out')))
test.fail_test(not test.read('foo.out') == 'foo.in\nbar.in\n')

test.write('SConstruct', """
def build(env, target, source):
    for t in target:
        file = open(str(target[0]), 'wb')
        for s in source:
            file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = ['foo.out', 'bar.out'], source = 'foo.in')
env.B(target = ['bar.out', 'foo.out'], source = 'bar.in')
""")

# This is intentional. The order of the targets matter to the
# builder because the build command can contain things like ${TARGET[0]}:
test.run(arguments='foo.out', 
         status=2, 
         stderr="""
SCons error: Two different target sets have a target in common: bar.out
File "SConstruct", line 11, in ?
""")

# XXX It would be nice if the following two tests could be made to 
# work by executing the action once for each unique set of
# targets. This would make it simple to deal with PDB files on Windows like so:
#
#     env.Object(['foo.obj', 'vc60.pdb'], 'foo.c')
#     env.Object(['bar.obj', 'vc60.pdb'], 'bar.c')

test.write('SConstruct', """
def build(env, target, source):
    for t in target:
        file = open(str(target[0]), 'wb')
        for s in source:
            file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = ['foo.out', 'bar.out'], source = 'foo.in')
env.B(target = ['bar.out', 'blat.out'], source = 'bar.in')
""")

test.run(arguments='foo.out', 
         status=2, 
         stderr="""
SCons error: Two different target sets have a target in common: bar.out
File "SConstruct", line 11, in ?
""")

test.write('SConstruct', """
def build(env, target, source):
    for t in target:
        file = open(str(target[0]), 'wb')
        for s in source:
            file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = ['foo.out', 'bar.out'], source = 'foo.in')
env.B(target = 'foo.out', source = 'bar.in')
""")

test.run(arguments='foo.out', 
         status=2, 
         stderr="""
SCons error: Two different builders (ListBuilder(B) and B) were specified for the same target: foo.out
File "SConstruct", line 11, in ?
""")




test.pass_test()
