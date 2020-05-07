#!/usr/bin/env python
#
# __COPYRIGHT__
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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import sys
import TestSCons

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()

test.dir_fixture('ninja-fixture')

ninja = test.where_is('ninja', os.environ['PATH'])

if not ninja:
    test.skip_test("Could not find ninja in environment")

test.write('SConstruct', """
env = Environment()
env.Tool('ninja')

shared_lib = env.SharedLibrary(target = 'test_impl', source = 'test_impl.c')
env.Program(target = 'test', source = 'test1.c', LIBS=[shared_lib], LIBPATH=['.'], RPATH='.')

static_lib = env.StaticLibrary(target = 'test_impl_static', source = 'test_impl.c')
static_obj = env.Object(target = 'test_static.o', source = 'test1.c')
env.Program(target = 'test_static', source = static_obj, LIBS=[static_lib], LIBPATH=['.'])
""")
# generate simple build
test.run(stdout=None)
test.must_contain_all_lines(test.stdout(),
    ['Generating: build.ninja', 'Executing: build.ninja'])
test.run(program = test.workpath('test'), stdout="library_function" + os.linesep)
test.run(program = test.workpath('test_static'), stdout="library_function" + os.linesep)

# clean build and ninja files
test.run(arguments='-c', stdout=None)
test.must_contain_all_lines(test.stdout(), [
    'Removed test_impl.os',
    'Removed libtest_impl.so',
    'Removed test1.o',
    'Removed test',
    'Removed test_impl.o',
    'Removed libtest_impl_static.a',
    'Removed test_static.o',
    'Removed test_static',
    'Removed build.ninja'])

# only generate the ninja file
test.run(arguments='--disable-auto-ninja', stdout=None)
test.must_contain_all_lines(test.stdout(),
    ['Generating: build.ninja'])
test.must_not_contain_any_line(test.stdout(),
    ['Executing: build.ninja'])

# run ninja independently
test.run(program = ninja, stdout=None)
test.run(program = test.workpath('test'), stdout="library_function" + os.linesep)
test.run(program = test.workpath('test_static'), stdout="library_function" + os.linesep)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
