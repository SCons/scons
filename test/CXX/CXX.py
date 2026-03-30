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
Test the C++ compiler name variable $CXX, calling a mocked compiler.
"""

import sys
import TestSCons

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()

test.file_fixture('mylink.py')
test.dir_fixture('CXX-fixture')

test.write('SConstruct', f"""\
DefaultEnvironment(tools=[])
env = Environment(
    LINK=r'{_python_} mylink.py',
    LINKFLAGS=[],
    CXX=r'{_python_} myc++.py',
    CXXFLAGS=[],
)

env.Program(target='test1', source='test1.cc')
env.Program(target='test2', source='test2.cpp')
env.Program(target='test3', source='test3.cxx')
env.Program(target='test4', source='test4.c++')
env.Program(target='test5', source='test5.C++')
""")

test.write('test1.cc', r"""This is a .cc file.
/*c++*/
#link
""")

test.write('test2.cpp', r"""This is a .cpp file.
/*c++*/
#link
""")

test.write('test3.cxx', r"""This is a .cxx file.
/*c++*/
#link
""")

test.write('test4.c++', r"""This is a .c++ file.
/*c++*/
#link
""")

test.write('test5.C++', r"""This is a .C++ file.
/*c++*/
#link
""")

test.run(arguments='.', stderr=None)
test.must_match('test1' + _exe, "This is a .cc file.\n", mode='r')
test.must_match('test2' + _exe, "This is a .cpp file.\n", mode='r')
test.must_match('test3' + _exe, "This is a .cxx file.\n", mode='r')
test.must_match('test4' + _exe, "This is a .c++ file.\n", mode='r')
test.must_match('test5' + _exe, "This is a .C++ file.\n", mode='r')

if TestSCons.case_sensitive_suffixes('.c', '.C'):
    test.write('SConstruct2', f"""\
DefaultEnvironment(tools=[])
env = Environment(
    LINK=r'{_python_} mylink.py',
    LINKFLAGS=[],
    CXX=r'{_python_} myc++.py',
    CXXFLAGS=[],
)

env.Program(target='test6', source='test6.C')
""")

    test.write('test6.C', r"""This is a .C file.
/*c++*/
#link
""")

    test.run(arguments=['-f', 'SConstruct2', '.'], stderr=None)
    test.must_match('test6' + _exe, "This is a .C file.\n", mode='r')

test.pass_test()
