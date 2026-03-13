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
Verify merging with MergeFlags to CPPPDEFINES with various data types.

Now uses a mocked pkg-config to avoid some weird problems,
but is still a "live" test because we do expansion on $_CPPDEFFLAGS,
which needs to have been set up with a compiler tool so have something
to subst into.
"""

import pathlib
import sys

import TestSCons
import TestCmd

test = TestSCons.TestSCons()
_python_ = TestSCons._python_

mock_pkg_config = test.workpath('mock-pkg-config.py')
test.write(mock_pkg_config, f"""\
import sys
if '--cflags' in sys.argv:
    print("-DSOMETHING -DVARIABLE=2")
sys.exit(0)
""")

# Since the mock pkg-config is a Python script, use the selected Python to
# run it to avoid execution problems (esp. on Windows)
pc_path = (_python_ + ' ' + mock_pkg_config).replace("\\", "/")

# We need a toolset:
if TestCmd.IS_WINDOWS:
    pc_tools = 'mingw'
else:
    pc_tools = 'default'

# these are no longer really needed, leave so it looks like a "real" pkg-config
pc_file = 'bug'
pc_cl_path = ""

test.write('SConstruct', f"""\
import os
import sys

DefaultEnvironment(tools=[])
# https://github.com/SCons/scons/issues/2671
# Passing test cases
env_1 = Environment(CPPDEFINES=[('DEBUG', '1'), 'TEST'], tools=['{pc_tools}'])
env_1.ParseConfig('{pc_path} {pc_cl_path} --cflags {pc_file}')
print(env_1.subst('$_CPPDEFFLAGS'))

env_2 = Environment(CPPDEFINES=[('DEBUG', '1'), 'TEST'], tools=['{pc_tools}'])
env_2.MergeFlags('-DSOMETHING -DVARIABLE=2')
print(env_2.subst('$_CPPDEFFLAGS'))

# Failing test cases
env_3 = Environment(CPPDEFINES=dict([('DEBUG', 1), ('TEST', None)]), tools=['{pc_tools}'])
env_3.ParseConfig('{pc_path} {pc_cl_path} --cflags {pc_file}')
print(env_3.subst('$_CPPDEFFLAGS'))

env_4 = Environment(CPPDEFINES=dict([('DEBUG', 1), ('TEST', None)]), tools=['{pc_tools}'])
env_4.MergeFlags('-DSOMETHING -DVARIABLE=2')
print(env_4.subst('$_CPPDEFFLAGS'))

# https://github.com/SCons/scons/issues/1738
env_1738_1 = Environment(tools=['{pc_tools}'])
env_1738_1.ParseConfig('{pc_path} {pc_cl_path} --cflags {pc_file}')
env_1738_1.Append(CPPDEFINES={{'value': '1'}})
print(env_1738_1.subst('$_CPPDEFFLAGS'))
""")

expect_print_output="""\
-DDEBUG=1 -DTEST -DSOMETHING -DVARIABLE=2
-DDEBUG=1 -DTEST -DSOMETHING -DVARIABLE=2
-DDEBUG=1 -DTEST -DSOMETHING -DVARIABLE=2
-DDEBUG=1 -DTEST -DSOMETHING -DVARIABLE=2
-DSOMETHING -DVARIABLE=2 -Dvalue=1
"""

build_output = "scons: `.' is up to date.\n"
expect = test.wrap_stdout(build_str=build_output, read_str=expect_print_output)
test.run(arguments='.', stdout=expect)

test.pass_test()
