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
Regression test: an AddPostAction() on a Program must still run after the
ninja file has been regenerated several times following a ninja build.

Before the fix, the target's executor was released once it was up to date, so
the next regeneration lost the post action and the link edge ran without it.
"""

import TestSCons
from TestCmd import IS_WINDOWS

test = TestSCons.TestSCons()

try:
    import ninja  # noqa: F401  (import only checks that ninja is installed)
except ImportError:
    test.skip_test("Could not find module in python")

_exe = TestSCons._exe

ninja_bin = TestSCons.NINJA_BINARY

test.dir_fixture('ninja-fixture')

test.write('SConstruct', """\
SetOption('experimental', 'ninja')
DefaultEnvironment(tools=[])
env = Environment()
env.Tool('ninja')
prog = env.Program(target='foo', source='foo.c')
env.AddPostAction(prog, 'echo post > post.marker')
""",
)

# Generate, build with ninja, then regenerate repeatedly.
test.run(arguments='--disable-execute-ninja', stdout=None)
test.must_contain_all_lines(test.stdout(), ['Generating: build.ninja'])

program = test.workpath('run_ninja_env.bat') if IS_WINDOWS else ninja_bin
test.run(program=program, stdout=None)
test.must_exist('foo' + _exe)
test.must_exist('post.marker')

for _ in range(3):
    test.run(arguments='--disable-execute-ninja', stdout=None)

# The post action must still be part of the build after regeneration.
test.unlink('post.marker')
test.unlink('foo' + _exe)
test.run(program=program, stdout=None)
test.must_exist('foo' + _exe)
test.must_exist('post.marker')

test.pass_test()
