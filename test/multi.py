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

"""
Test various cases where a target is "built" by multiple builder calls.
"""

import TestCmd
import TestSCons
import os.path

test = TestSCons.TestSCons(match=TestCmd.match_re)


#
# A builder with "multi" set can be called multiple times and
# the source files are added to the list.
#

test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'file1.out', source = 'file1a.in')
env.B(target = 'file1.out', source = 'file1b.in')
""")

test.write('file1a.in', 'file1a.in\n')
test.write('file1b.in', 'file1b.in\n')

test.run(arguments='file1.out')

test.must_match('file1.out', "file1a.in\nfile1b.in\n")


#
# A builder with "multi" not set generates an error on the second call.
#

test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=0)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'file2.out', source = 'file2a.in')
env.B(target = 'file2.out', source = 'file2b.in')
""")

test.write('file2a.in', 'file2a.in\n')
test.write('file2b.in', 'file2b.in\n')

test.run(arguments='file2.out', 
         status=2, 
         stderr=TestSCons.re_escape("""
scons: *** Multiple ways to build the same target were specified for: file2.out  (from ['file2a.in'] and from ['file2b.in'])
""") + TestSCons.file_expr)


#
# The second call generates an error if the two calls have different
# overrides.
#

test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'file3.out', source = 'file3a.in', foo=1)
env.B(target = 'file3.out', source = 'file3b.in', foo=2)
""")

test.write('file3a.in', 'file3a.in\n')
test.write('file3b.in', 'file3b.in\n')

test.run(arguments='file3.out', 
         status=2, 
         stderr=TestSCons.re_escape("""
scons: *** Two different sets of overrides were specified for the same target: file3.out
""") + TestSCons.file_expr)


#
# Everything works if the two calls have the same overrides.
#

test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'file4.out', source = 'file4a.in', foo=3)
env.B(target = 'file4.out', source = 'file4b.in', foo=3)
""")

test.write('file4a.in', 'file4a.in\n')
test.write('file4b.in', 'file4b.in\n')

test.run(arguments='file4.out')

test.must_match('file4.out', "file4a.in\nfile4b.in\n")


#
# Two different environments can be used for the same target, so long
# as the actions have the same signature; a warning is generated.
#

test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env2 = env.Copy(DIFFERENT_VARIABLE = 'true')
env.B(target = 'file5.out', source = 'file5a.in')
env2.B(target = 'file5.out', source = 'file5b.in')
""")

test.write('file5a.in', 'file5a.in\n')
test.write('file5b.in', 'file5b.in\n')

test.run(arguments='file5.out', 
         stderr=TestSCons.re_escape("""
scons: warning: Two different environments were specified for target file5.out,
	but they appear to have the same action: build(["file5.out"], ["file5b.in"])
""") + TestSCons.file_expr)

test.must_match('file5.out', "file5a.in\nfile5b.in\n")


#
# Environments with actions that have different signatures generate
# an error.
#

test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=Action(build, varlist=['XXX']), multi=1)
env = Environment(BUILDERS = { 'B' : B }, XXX = 'foo')
env2 = env.Copy(XXX = 'var')
env.B(target = 'file6.out', source = 'file6a.in')
env2.B(target = 'file6.out', source = 'file6b.in')
""")

test.write('file6a.in', 'file6a.in\n')
test.write('file6b.in', 'file6b.in\n')

test.run(arguments='file6.out', 
         status=2,
         stderr=TestSCons.re_escape("""
scons: *** Two environments with different actions were specified for the same target: file6.out
""") + TestSCons.file_expr)


#
# A builder without "multi" set can still be called multiple times
# if the calls are the same.
#

test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=0)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'file7.out', source = 'file7.in')
env.B(target = 'file7.out', source = 'file7.in')
""")

test.write('file7.in', 'file7.in\n')

test.run(arguments='file7.out')

test.must_match('file7.out', "file7.in\n")


#
# Trying to call a target with two different "multi" builders
# generates an error.
#

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
env.B(target = 'file8.out', source = 'file8.in')
env.C(target = 'file8.out', source = 'file8.in')
""")

test.write('file8a.in', 'file8a.in\n')
test.write('file8b.in', 'file8b.in\n')

test.run(arguments='file8.out', 
         status=2, 
         stderr=TestSCons.re_escape("""
scons: *** Two different builders (B and C) were specified for the same target: file8.out
""") + TestSCons.file_expr)


#
# A "multi" builder can be called multiple times with the same target list
# if everything is identical.
#

test.write('SConstruct', """
def build(env, target, source):
    for t in target:
        file = open(str(t), 'wb')
        for s in source:
            file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = ['file9a.out', 'file9b.out'], source = 'file9a.in')
env.B(target = ['file9a.out', 'file9b.out'], source = 'file9b.in')
""")

test.write('file9a.in', 'file9a.in\n')
test.write('file9b.in', 'file9b.in\n')

test.run(arguments='file9b.out')

test.must_match('file9a.out', "file9a.in\nfile9b.in\n")
test.must_match('file9b.out', "file9a.in\nfile9b.in\n")


#
# A "multi" builder can NOT be called multiple times with target lists
# that have different orders.  This is intentional; the order of the
# targets matter to the builder because the build command can contain
# things like ${TARGET[0]}.
#

test.write('SConstruct', """
def build(env, target, source):
    for t in target:
        file = open(str(target[0]), 'wb')
        for s in source:
            file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = ['file10a.out', 'file10b.out'], source = 'file10.in')
env.B(target = ['file10b.out', 'file10a.out'], source = 'file10.in')
""")

test.write('file10.in', 'file10.in\n')

test.run(arguments='file10.out', 
         status=2, 
         stderr=TestSCons.re_escape("""
scons: *** Two different target sets have a target in common: file10b.out
""") + TestSCons.file_expr)


#
# A target file can't be in two different target lists.
#

# XXX It would be nice if the following two tests could be made to work
# by executing the action once for each unique set of targets. This
# would make it simple to deal with PDB files on Windows like so:
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
env.B(target = ['file11a.out', 'file11b.out'], source = 'file11a.in')
env.B(target = ['file11b.out', 'file11c.out'], source = 'file11b.in')
""")

test.write('file11a.in', 'file11a.in\n')
test.write('file11b.in', 'file11b.in\n')

test.run(arguments='file11.out', 
         status=2, 
         stderr=TestSCons.re_escape("""
scons: *** Two different target sets have a target in common: file11b.out
""") + TestSCons.file_expr)


#
# A target file can't be a lone target and in a list.
#

test.write('SConstruct', """
def build(env, target, source):
    for t in target:
        file = open(str(target[0]), 'wb')
        for s in source:
            file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = ['file12a.out', 'file12b.out'], source = 'file12a.in')
env.B(target = 'file12a.out', source = 'file12b.in')
""")

test.write('file12a.in', 'file12a.in\n')
test.write('file12b.in', 'file12b.in\n')

test.run(arguments='file12.out', 
         status=2, 
         stderr=TestSCons.re_escape("""
scons: *** Cannot build same target `file12a.out' as singular and list
""") + TestSCons.file_expr)



test.pass_test()
