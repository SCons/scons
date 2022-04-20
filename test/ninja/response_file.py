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
#

import os
import sys
import json
from io import StringIO


import TestSCons
from TestCmd import IS_WINDOWS

test = TestSCons.TestSCons()

try:
    import ninja
except ImportError:
    test.skip_test("Could not find module in python")

_python_ = TestSCons._python_
_exe = TestSCons._exe
_obj = TestSCons._obj

ninja_bin = os.path.abspath(os.path.join(
    ninja.__file__,
    os.pardir,
    'data',
    'bin',
    'ninja' + _exe))

test.dir_fixture('ninja-fixture')

test.file_fixture('ninja_test_sconscripts/sconstruct_response_file', 'SConstruct')

# only generate the ninja file
test.run(arguments='--disable-execute-ninja', stdout=None)
test.must_contain_all_lines(test.stdout(), ['Generating: build.ninja'])
test.must_not_exist(test.workpath('foo' + _exe))

# run ninja independently
program = test.workpath('run_ninja_env.bat') if IS_WINDOWS else ninja_bin

# now we must extract the line length for a given command by print the command
# to a StringIO internal buffer and calculating the length of the resulting command.
test.run(program=[program, 'compiledb'], stdout=None)
command_length = None
with open('compile_commands.json') as f:
    comp_commands = json.loads(f.read())
    for cmd in comp_commands:
        if cmd['output'].endswith('1'):
            result = StringIO()
            old_stdout = sys.stdout
            sys.stdout = result
            print(cmd['command'])
            result_string = result.getvalue()
            sys.stdout = old_stdout
            if sys.platform == 'win32':
                command_length = len(result_string)
            else:
                command_length = len(result_string.split(';')[-1])

# now regen the ninja file with the MAXLINELENGTH so we can force the response file in one case.
test.run(arguments=['--disable-execute-ninja', 'MLL='+str(command_length)], stdout=None)
test.run(program=[program, '-v', '-d', 'keeprsp'], stdout=None)
test.must_not_exist(test.workpath('foo' + _obj + '1.rsp'))
test.must_exist(test.workpath('foo' + _obj + '2.rsp'))

test.run(program=test.workpath('foo' + _exe), stdout="foo.c")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
