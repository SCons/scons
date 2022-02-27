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

import TestSCons
from TestCmd import IS_WINDOWS
import SCons
from SCons.Platform.mingw import MINGW_DEFAULT_PATHS
from SCons.Platform.cygwin import CYGWIN_DEFAULT_PATHS

test = TestSCons.TestSCons()

if sys.platform not in ('cygwin', 'win32',):
    test.skip_test("Skipping mingw test on non-Windows platform %s." % sys.platform)

dp = MINGW_DEFAULT_PATHS + CYGWIN_DEFAULT_PATHS
gcc = SCons.Tool.find_program_path(test.Environment(), 'gcc', default_paths=dp)
if not gcc:
    test.skip_test("Skipping mingw test, no MinGW found.\n")

# ninja must have the os environment setup to work properly
os.environ["PATH"] += os.pathsep + os.path.dirname(gcc)

try:
    import ninja
except ImportError:
    test.skip_test("Could not find module in python")

_python_ = TestSCons._python_
_exe = TestSCons._exe

ninja_bin = os.path.abspath(os.path.join(
    ninja.BIN_DIR,
    'ninja' + _exe))

test.dir_fixture('ninja-fixture')

test.file_fixture('ninja_test_sconscripts/sconstruct_mingw_command_generator_action', 'SConstruct')

# generate simple build
test.run(stdout=None)
test.must_contain_all_lines(test.stdout(), ['Generating: build.ninja'])
test.must_contain_all(test.stdout(), 'Executing:')
test.must_contain_all(test.stdout(), 'ninja%(_exe)s -f' % locals())
test.run(program=test.workpath('test' + _exe), stdout="library_function")

# clean build and ninja files
test.run(arguments='-c', stdout=None)

# only generate the ninja file
test.run(arguments='--disable-execute-ninja', stdout=None)
test.must_contain_all_lines(test.stdout(), ['Generating: build.ninja'])
test.must_not_exist(test.workpath('test' + _exe))

# run ninja independently
program = test.workpath('run_ninja_env.bat') if IS_WINDOWS else ninja_bin
test.run(program=program, stdout=None)
test.run(program=test.workpath('test' + _exe), stdout="library_function")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
