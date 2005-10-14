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

import os.path
import sys

import TestSCons
import TestCmd

test = TestSCons.TestSCons(match = TestCmd.match_re_dotall)

# How to warn about deprecated features (whenever we have one again).
#
#test.write("SConstruct","""
#b=Builder(name='b', action='foo')
#""")
#
#test.run(arguments='.', stderr=r"""
#scons: warning: The use of the 'name' parameter to Builder\(\) is deprecated\.
#File "SConstruct", line 2, in \?
#""")
#
#test.run(arguments='--warn=no-deprecated .', stderr='')
#
#test.run(arguments='--warn=no-all .', stderr='')
#
#test.run(arguments='--warn=no-all --warn=deprecated .', stderr=r"""
#scons: warning: The use of the 'name' parameter to Builder\(\) is deprecated\.
#File "SConstruct", line 2, in \?
#""")



test.write("SConstruct", """\
import SCons.Defaults

def build(target, source, env):
    pass

env=Environment()
env['BUILDERS']['test'] = Builder(action=build,
                                  source_scanner=SCons.Defaults.ObjSourceScan)
env.test(target='foo', source='foo.c')
""")

test.write("foo.c","""
#include "not_there.h"
""")

test.run(arguments='--warn=dependency .', stderr=r"""
scons: warning: No dependency generated for file: not_there\.h \(included from: foo\.c\) \-\- file not found
""" + TestSCons.file_expr)

test.run(arguments='--warn=all .', stderr=r"""
scons: warning: No dependency generated for file: not_there\.h \(included from: foo\.c\) \-\- file not found
""" + TestSCons.file_expr)

test.run(arguments='--warn=all --warn=no-dependency .', stderr="")

test.run(arguments='--warn=no-dependency --warn=all .', stderr=r"""
scons: warning: No dependency generated for file: not_there\.h \(included from: foo\.c\) \-\- file not found
""" + TestSCons.file_expr)



test.write("SConstruct", """\
def build(target, source, env):
    pass

env=Environment()
env['BUILDERS']['test'] = Builder(action=build)
env.test(target='foo', source='foo.c')
SConscript('no_such_file')
""")

test.run(arguments = '--warn=missing-sconscript .', stderr = r"""
scons: warning: Ignoring missing SConscript 'no_such_file'
""" + TestSCons.file_expr)

test.run(arguments = '--warn=no-missing-sconscript .', stderr = "")



test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env2 = env.Copy(DIFFERENT_VARIABLE = 'true')
env.B(target = 'file1.out', source = 'file1a.in')
env2.B(target = 'file1.out', source = 'file1b.in')
""")

test.write('file1a.in', 'file1a.in\n')
test.write('file1b.in', 'file1b.in\n')

test.run(arguments='file1.out', 
         stderr=r"""
scons: warning: Two different environments were specified for target file1.out,
\tbut they appear to have the same action: build\(target, source, env\)
""" + TestSCons.file_expr)

test.must_match('file1.out', "file1a.in\nfile1b.in\n")

test.run(arguments='--warn=duplicate-environment file1.out', 
         stderr=r"""
scons: warning: Two different environments were specified for target file1.out,
\tbut they appear to have the same action: build\(target, source, env\)
""" + TestSCons.file_expr)

test.run(arguments='--warn=no-duplicate-environment file1.out')



test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=1)
env = Environment(BUILDERS = { 'B' : B })
env.B(targets = 'file3a.out', source = 'file3a.in')
env.B(target = 'file3b.out', sources = 'file3b.in')
""")

test.write('file3a.in', 'file3a.in\n')
test.write('file3b.out', 'file3b.out\n')

test.run(arguments='.', 
         stderr=r"""
scons: warning: Did you mean to use `(target|source)' instead of `(targets|sources)'\?
""" + TestSCons.file_expr + r"""
scons: warning: Did you mean to use `(target|source)' instead of `(targets|sources)'\?
""" + TestSCons.file_expr)

test.must_match(['file3a'], 'file3a.in\n')
test.must_match(['file3b'], 'file3b.out\n')

test.run(arguments='--warn=misleading-keywords .', 
         stderr=r"""
scons: warning: Did you mean to use `(target|source)' instead of `(targets|sources)'\?
""" + TestSCons.file_expr + r"""\
scons: warning: Did you mean to use `(target|source)' instead of `(targets|sources)'\?
""" + TestSCons.file_expr)

test.run(arguments='--warn=no-misleading-keywords .')


test.pass_test()
