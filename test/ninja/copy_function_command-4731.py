#!/usr/bin/env python
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
Regression test for issue #4731: almost the same as copy_function_command,
but uses a list action where the first command is Copy,
as opposed to a simple function action. This was failing.
"""

import os

import TestSCons
from TestCmd import IS_WINDOWS

test = TestSCons.TestSCons()

try:
    import ninja
except ImportError:
    test.skip_test("Could not find module in python")

_python_ = TestSCons._python_
_exe = TestSCons._exe

ninja_bin = TestSCons.NINJA_BINARY

test.dir_fixture('ninja-fixture')

test.write('SConstruct', """\
SetOption('experimental', 'ninja')
DefaultEnvironment(tools=[])
env = Environment()
env.Tool('ninja')
env.Command('foo2.c', ['foo.c'], [Copy('$TARGET', '$SOURCE'), Chmod('$TARGET', 0x755)])
env.Program(target='foo', source='foo2.c')
""",
)

# generate simple build
test.run(stdout=None)
test.must_contain_all_lines(test.stdout(), ['Generating: build.ninja'])
test.must_contain_all(test.stdout(), 'Executing:')
test.must_contain_all(test.stdout(), f'ninja{_exe} -f')
test.run(program=test.workpath('foo'), stdout="foo.c")

# clean build and ninja files
test.run(arguments='-c', stdout=None)
test.must_contain_all_lines(test.stdout(), [
    'Removed foo2.o',
    'Removed foo2.c',
    'Removed foo' + _exe,
    'Removed build.ninja']
)

# only generate the ninja file
test.run(arguments='--disable-execute-ninja', stdout=None)
test.must_contain_all_lines(test.stdout(), ['Generating: build.ninja'])
test.must_not_exist(test.workpath('foo'))

# run ninja independently
program = test.workpath('run_ninja_env.bat') if IS_WINDOWS else ninja_bin
test.run(program=program, stdout=None)
test.run(program=test.workpath('foo'), stdout="foo.c")

test.pass_test()
