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
Test the C compiler name variable $CC, calling a mocked compiler.
"""

import os
import sys
import TestSCons

_python_ = TestSCons._python_
_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.dir_fixture('CC-fixture')
test.file_fixture('mylink.py')

test.write('SConstruct', f"""\
DefaultEnvironment(tools=[])
env = Environment(
    tools=['link', 'cc'],
    LINK=r'{_python_} mylink.py',
    LINKFLAGS=[],
    CC=r'{_python_} mycc.py',
)
env.Program(target='test1', source='test1.c')
""")

test.run(arguments='.', stderr=None)
test.must_match('test1' + _exe, "This is a .c file.\n", mode='r')

if os.path.normcase('.c') == os.path.normcase('.C'):
    test.write('SConstruct2', f"""
DefaultEnvironment(tools=[])
env = Environment(
    tools=['link', 'cc'],
    LINK=r'{_python_} mylink.py',
    CC=r'{_python_} mycc.py',
)
env.Program(target='test2', source='test2.C')
""")

    test.run(arguments=['-f', 'SConstruct2', '.'], stderr=None)
    test.must_match('test2' + _exe, "This is a .C file.\n", mode='r')

test.pass_test()
