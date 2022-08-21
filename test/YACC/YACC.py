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

import os
import sys
from TestCmd import IS_WINDOWS

import TestSCons

_python_ = TestSCons._python_
_exe = TestSCons._exe

if IS_WINDOWS:
    compiler = 'msvc'
    linker = 'mslink'
else:
    compiler = 'gcc'
    linker = 'gnulink'

test = TestSCons.TestSCons()

test.dir_fixture('YACC-fixture')

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(YACC=r'%(_python_)s myyacc.py', tools=['default', 'yacc'])
env.CFile(target='aaa', source='aaa.y')
env.CFile(target='bbb', source='bbb.yacc')
env.CXXFile(target='ccc', source='ccc.yy')
env.CFile(target='ddd', source='ddd.ym')
""" % locals())

test.run(arguments='.', stderr=None)

test.must_match('aaa.c', "aaa.y" + os.linesep + "myyacc.py" + os.linesep)
test.must_match('bbb.c', "bbb.yacc" + os.linesep + "myyacc.py" + os.linesep)
test.must_match('ccc.cc', "ccc.yacc" + os.linesep + "myyacc.py" + os.linesep)
test.must_match('ddd.m', "ddd.yacc" + os.linesep + "myyacc.py" + os.linesep)

test.run(arguments="-n -f SConstruct_YACC_before")
test.fail_test(
    'SOMETHING_DUMB' not in test.stdout(),
    "YACC is not overridden to be SOMETHING_DUMB"
)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
