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
Test the PackageVariable canned Variable type.
"""

from __future__ import annotations

import os

import TestSCons

test = TestSCons.TestSCons()

SConstruct_path = test.workpath('SConstruct')

def check(expect: list[str]) -> None:
    result = test.stdout().split('\n')
    # skip first line and any lines beyond the length of expect
    assert result[1:len(expect)+1] == expect, (result[1:len(expect)+1], expect)

test.write(SConstruct_path, """\
from SCons.Variables.PackageVariable import PackageVariable as PV
from SCons.Variables import PackageVariable

opts = Variables(args=ARGUMENTS)
opts.AddVariables(
    PackageVariable('x11', 'use X11 installed here (yes = search some places', 'yes'),
    PV('package', 'help for package', 'yes'),
)

_ = DefaultEnvironment(tools=[])
env = Environment(variables=opts, tools=[])
Help(opts.GenerateHelpText(env))

print(env['x11'])
Default(env.Alias('dummy', None))
""")

test.run()
check([str(True)])

test.run(arguments='x11=no')
check([str(False)])

test.run(arguments='x11=0')
check([str(False)])

test.run(arguments=['x11=%s' % test.workpath()])
check([test.workpath()])

space_subdir = test.workpath('space subdir')
test.subdir(space_subdir)
test.run(arguments=[f'x11={space_subdir}'])
check([space_subdir])

expect_stderr = """
scons: *** Path does not exist for variable 'x11': '/non/existing/path/'
""" + test.python_file_line(SConstruct_path, 11)

test.run(arguments='x11=/non/existing/path/', stderr=expect_stderr, status=2)

# test that an enabling value produces the default value
# as long as that's a path string
tinycbor_path = test.workpath('path', 'to', 'tinycbor')
test.subdir(tinycbor_path)
SConstruct_pathstr = test.workpath('SConstruct.path')
test.write(SConstruct_pathstr, f"""\
from SCons.Variables import PackageVariable

vars = Variables(args=ARGUMENTS)
vars.Add(
    PackageVariable(
        'tinycbor',
        help="use 'tinycbor' at <path>",
        default=r'{tinycbor_path}'
    )
)

_ = DefaultEnvironment(tools=[])
env = Environment(variables=vars, tools=[])

print(env['tinycbor'])
Default(env.Alias('dummy', None))
""")

test.run(arguments=['-f', 'SConstruct.path', 'tinycbor=yes'])
check([tinycbor_path])

test.pass_test()
