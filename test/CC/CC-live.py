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
Test the C compiler name variable $CC.
This is a live test, calling the detected C compiler via a wrapper.
"""

import os
import sys
import TestSCons

_python_ = TestSCons._python_
_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.dir_fixture('CC-fixture')
test.file_fixture('wrapper.py')

test.write('SConstruct', f"""\
DefaultEnvironment(tools=[])
foo = Environment()
bar = Environment()

bar['CC'] = r'{_python_} wrapper.py ' + foo['CC']
foo.Program(target='foo', source='foo.c')
bar.Program(target='bar', source='bar.c')
""")

test.run(arguments='foo' + _exe)
test.must_not_exist(test.workpath('wrapper.out'))
test.up_to_date(arguments='foo' + _exe)

test.run(arguments='bar' + _exe)
test.must_match('wrapper.out', "wrapper.py\n", mode='r')
test.up_to_date(arguments='bar' + _exe)

test.pass_test()
