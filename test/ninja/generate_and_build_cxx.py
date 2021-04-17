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

import TestSCons
from TestCmd import IS_WINDOWS

test = TestSCons.TestSCons()

try:
    import ninja
except ImportError:
    test.skip_test("Could not find module in python")

_python_ = TestSCons._python_
_exe = TestSCons._exe

ninja_bin = os.path.abspath(os.path.join(
    ninja.__file__,
    os.pardir,
    'data',
    'bin',
    'ninja' + _exe))

test.dir_fixture('ninja-fixture')

test.file_fixture('ninja_test_sconscripts/sconstruct_generate_and_build_cxx',
                  'SConstruct')

# generate simple build
test.run()
test.must_contain_all_lines(test.stdout(), ['Generating: build.ninja'])
test.must_contain_all(test.stdout(), 'Executing:')
test.must_contain_all(test.stdout(), 'ninja%(_exe)s -f' % locals())
test.run(program=test.workpath('test2' + _exe), stdout="print_function")

# clean build and ninja files
test.run(arguments='-c', stdout=None)
test.must_contain_all_lines(test.stdout(), [
    'Removed test2.o',
    'Removed test2',
    'Removed build.ninja'])

# only generate the ninja file
test.run(arguments='--disable-execute-ninja', stdout=None)
test.must_contain_all_lines(test.stdout(), ['Generating: build.ninja'])
test.must_not_exist(test.workpath('test2' + _exe))

# run ninja independently
program = test.workpath('run_ninja_env.bat') if IS_WINDOWS else ninja_bin
test.run(program=program, stdout=None)
test.run(program=test.workpath('test2' + _exe), stdout="print_function")

test.write('test2.hpp', """
#include <string>
#include <iostream>

class Foo
{
public:
    int print_function();
    int print_function2(){
        std::cout << "2";
        return 0;
    };
};
""")

# generate simple build
test.run(program=program, stdout=None)
test.run(program=test.workpath('test2' + _exe), stdout="print_function2")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
