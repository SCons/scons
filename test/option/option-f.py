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

test = TestSCons.TestSCons()

test.subdir('subdir')

subdir_BuildThis = os.path.join('subdir', 'Buildthis')

test.write('SConscript', """
import os

DefaultEnvironment(tools=[])
print("SConscript " + os.getcwd())
""")

test.write(subdir_BuildThis, """
import os

DefaultEnvironment(tools=[])
print("subdir/BuildThis " + os.getcwd())
""")

test.write('Build2', """
import os

DefaultEnvironment(tools=[])
print("Build2 " + os.getcwd())
""")

wpath = test.workpath()

test.run(
    arguments='-f SConscript .',
    stdout=test.wrap_stdout(
        read_str=f'SConscript {wpath}\n',
        build_str="scons: `.' is up to date.\n"
    ),
)

test.run(
    arguments=f'-f {subdir_BuildThis} .',
    stdout=test.wrap_stdout(
        read_str=f'subdir/BuildThis {wpath}\n',
        build_str="scons: `.' is up to date.\n",
    ),
)

test.run(
    arguments='--file=SConscript .',
    stdout=test.wrap_stdout(
        read_str=f'SConscript {wpath}\n',
        build_str="scons: `.' is up to date.\n"
    ),
)

test.run(
    arguments=f'--file={subdir_BuildThis} .',
    stdout=test.wrap_stdout(
        read_str=f'subdir/BuildThis {wpath}\n',
        build_str="scons: `.' is up to date.\n",
    ),
)

test.run(
    arguments='--makefile=SConscript .',
    stdout=test.wrap_stdout(
        read_str=f'SConscript {wpath}\n',
        build_str="scons: `.' is up to date.\n"
    ),
)

test.run(
    arguments=f'--makefile={subdir_BuildThis} .',
    stdout=test.wrap_stdout(
        read_str=f'subdir/BuildThis {wpath}\n',
        build_str="scons: `.' is up to date.\n",
    ),
)

test.run(
    arguments='--sconstruct=SConscript .',
    stdout=test.wrap_stdout(
        read_str=f'SConscript {wpath}\n',
        build_str="scons: `.' is up to date.\n"
    ),
)

test.run(
    arguments=f'--sconstruct={subdir_BuildThis} .',
    stdout=test.wrap_stdout(
        read_str=f'subdir/BuildThis {wpath}\n',
        build_str="scons: `.' is up to date.\n",
    ),
)

test.run(
    arguments='-f - .',
    stdin="""
DefaultEnvironment(tools=[])
import os
print("STDIN " + os.getcwd())
""",
    stdout=test.wrap_stdout(
        read_str=f'STDIN {wpath}\n',
        build_str="scons: `.' is up to date.\n"
    ),
)

expect = test.wrap_stdout(
    read_str=f'Build2 {wpath}\nSConscript {wpath}\n',
    build_str="scons: `.' is up to date.\n",
)
test.run(arguments='-f Build2 -f SConscript .', stdout=expect)

missing = "no_such_file"
test.run(arguments=f"-f {missing} .", status=2, stderr=None)
expect = [f"scons: *** missing SConscript file {missing!r}"]
test.must_contain_all_lines(test.stderr(), expect)

test.pass_test()
