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

import TestSCons

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()

test.file_fixture('mylex.py')

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(LEX=r'%(_python_)s mylex.py', tools=['default', 'lex'])
env.CFile(target='aaa', source='aaa.l')
env.CFile(target='bbb', source='bbb.lex')
env.CXXFile(target='ccc', source='ccc.ll')
env.CXXFile(target='ddd', source='ddd.lm')
""" % locals())

test.write('aaa.l', "aaa.l\nLEX\n")
test.write('bbb.lex', "bbb.lex\nLEX\n")
test.write('ccc.ll', "ccc.ll\nLEX\n")
test.write('ddd.lm', "ddd.lm\nLEX\n")

test.run(arguments='.', stderr=None)

# Read in with mode='r' because mylex.py implicitley wrote to stdout
# with mode='w'.
test.must_match('aaa.c', "aaa.l\nmylex.py\n", mode='r')
test.must_match('bbb.c', "bbb.lex\nmylex.py\n", mode='r')
test.must_match('ccc.cc', "ccc.ll\nmylex.py\n", mode='r')
test.must_match('ddd.m', "ddd.lm\nmylex.py\n", mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
