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
import sys


test = TestSCons.TestSCons()


python = sys.executable

test.write('SConstruct', """
env = Environment(LIBS=['a'])
def build(target, source, env):
    assert env['CC'] == 'mycc'
    assert env['LIBS'] == ['a','b']
builder = Builder(action=build)
env['BUILDERS']['Build'] = builder

Default(env.Build('foo', 'bar', CC='mycc', LIBS = env['LIBS']+['b']))
""")

test.run()

test.write('SConstruct', """
env = Environment()
env.Program('hello', 'hello.c',
            CC=r'%s mycc.py',
            LINK=r'%s mylink.py',
            OBJSUFFIX='.not_obj',
            PROGSUFFIX='.not_exe')
"""%(python,python))

test.write('hello.c',"this ain't no c file!\n")

test.write('mycc.py',"""
open('hello.not_obj', 'wt').write('this is no object file!')
""")

test.write('mylink.py',"""
open('hello.not_exe', 'wt').write('this is not a program!')
""")

test.run(arguments='hello.not_exe')

assert test.read('hello.not_obj') == 'this is no object file!'
assert test.read('hello.not_exe') == 'this is not a program!'

test.up_to_date(arguments='hello.not_exe')

test.pass_test()


