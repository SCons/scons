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
import TestSCons
from TestCmd import IS_WINDOWS

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
env.Program(target = 'foo', source = 'foo.c')

env2 = Environment()
env2.Tool('ninja')
env2.Program(target = 'bar', source = 'bar.c')
""")

# generate simple build
test.run(stdout=None)
test.must_contain_all_lines(test.stdout(),
    ['Generating: build.ninja', 'Executing: build.ninja'])
test.run(program = test.workpath('foo' + _exe), stdout="foo.c")
test.run(program = test.workpath('bar' + _exe), stdout="bar.c")

# clean build and ninja files
test.run(arguments='-c', stdout=None)
test.must_contain_all_lines(test.stdout(), [
    'Removed foo.o',
    'Removed foo' + _exe,
    'Removed bar.o',
    'Removed bar' + _exe,
    'Removed build.ninja'])

# only generate the ninja file
test.run(arguments='--disable-auto-ninja', stdout=None)
test.must_contain_all_lines(test.stdout(),
    ['Generating: build.ninja'])
test.must_not_contain_any_line(test.stdout(),
    ['Executing: build.ninja'])

# run ninja independently
program = ['ninja_env.bat', '&', ninja] if IS_WINDOWS else ninja
test.run(program = program, stdout=None)
test.run(program = test.workpath('foo' + _exe), stdout="foo.c")
test.run(program = test.workpath('bar' + _exe), stdout="bar.c")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
