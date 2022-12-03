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

import TestSCons
from TestCmd import IS_WINDOWS, IS_MACOS
from TestSCons import _exe, _lib, lib_, _dll, dll_

test = TestSCons.TestSCons()

try:
    import ninja
except ImportError:
    test.skip_test("Could not find ninja module. Skipping test.\n")

ninja_bin = os.path.abspath(os.path.join(
    ninja.__file__,
    os.pardir,
    'data',
    'bin',
    'ninja' + _exe))

test.dir_fixture('ninja-fixture')

win32 = ", 'WIN32'" if IS_WINDOWS else ""

test.write('SConstruct', """
SetOption('experimental', 'ninja')
DefaultEnvironment(tools=[])
env = Environment()
env.Tool('ninja')
env['NINJA'] = r"%(ninja_bin)s"

shared_lib = env.SharedLibrary(target='test_impl', source='test_impl.c', CPPDEFINES=['LIBRARY_BUILD'%(win32)s])
env.Program(target='test', source='test1.c', LIBS=['test_impl'], LIBPATH=['.'], RPATH='.')
static_obj = env.Object(target='test_impl_static', source='test_impl.c')
static_lib = env.StaticLibrary(target='test_impl_static', source=static_obj)
static_obj = env.Object(target='test_static', source='test1.c')
env.Program(target='test_static', source=static_obj, LIBS=[static_lib], LIBPATH=['.'])
""" % locals())

# generate simple build
test.run(stdout=None)
test.must_contain_all_lines(test.stdout(), ['Generating: build.ninja'])
test.must_contain_all(test.stdout(), 'Executing:')
test.must_contain_all(test.stdout(), 'ninja%(_exe)s -f' % locals())
test.run(program=test.workpath('test'), stdout="library_function")
test.run(program=test.workpath('test_static'), stdout="library_function")

# clean build and ninja files
test.run(arguments='-c', stdout=None)
test.must_contain_all_lines(
    test.stdout(),
    [
        ('Removed %stest_impl' % dll_) + _dll,
        'Removed test' + _exe,
        ('Removed %stest_impl_static' % lib_) + _lib,
        'Removed test_static' + _exe,
        'Removed build.ninja',
    ],
)

# only generate the ninja file
test.run(arguments='--disable-execute-ninja', stdout=None)
test.must_contain_all_lines(test.stdout(), ['Generating: build.ninja'])
test.must_not_exist(test.workpath('test'))
test.must_not_exist(test.workpath('test_static'))

# run ninja independently
program = test.workpath('run_ninja_env.bat') if IS_WINDOWS else ninja_bin
test.run(program=program, stdout=None)
test.run(program=test.workpath('test'), stdout="library_function")
test.run(program=test.workpath('test_static'), stdout="library_function")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
