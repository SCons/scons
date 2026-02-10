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

Uses system pkg-config with a stub pc file to generate the data.
Not entirely sure the motivation for this - it would be more "isolated"
to just paste in the data and not depend on pkg-config, but presumably
this test exists because of observed bugs, so leaving alone for now.

Ran into an interesting problem when we spun up a GitHub Windows Action:
it finds pre-installed Strawberry Perl's pkg-config over the mingw one,
which is also pre-installed. The Strawberry one is written in pure
Perl (after getting past the initial batch file), so requires perl.exe,
which won't be in the SCons env['ENV']['PATH'].  We try to detect it,
by somewhat hokey means: if pkg-config's path had "strawberry' in it,
assume we need to add the directory path to our execution env.

It ended up being more portable to use pkg-config's --with-path than
to set PKG_CONFIG_PATH, because the Windows cmd.exe can't accept
the standard calling style.
"""

import pathlib

import TestSCons
import TestCmd

test = TestSCons.TestSCons()

pkg_config_path = test.where_is('pkg-config')
if not pkg_config_path:
    test.skip_test("Could not find 'pkg-config' in PATH, skipping test.\n")
pkg_config_path = pkg_config_path.replace("\\", "/")

# Try to guess if this was Strawberry Perl's pkg-config
if 'strawberry' in pkg_config_path.lower():
    # as_posix() or the pasted paths in SConstruct will have escape problems
    # (or need to be raw strings)
    strawberry_perl_path = pathlib.PurePath(pkg_config_path).parent.as_posix()
else:
    strawberry_perl_path = ""

test.write('bug.pc', """\
prefix=/usr
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
includedir=${prefix}/include

Name: bug
Description: A test case .pc file
Version: 1.2
Cflags: -DSOMETHING -DVARIABLE=2
""")

test.write('main.c', """\
int main(int argc, char *argv[])
{
  return 0;
}
""")

if TestCmd.IS_WINDOWS:
    pkg_config_file = 'bug'
    pkg_config_tools = 'mingw'
else:
    pkg_config_file = 'bug.pc'
    pkg_config_tools = 'default'
pkg_config_cl_path = '--with-path=.'

test.write('SConstruct', f"""\
import os
import sys

DefaultEnvironment(tools=[])
# https://github.com/SCons/scons/issues/2671
# Passing test cases
env_1 = Environment(
    CPPDEFINES=[('DEBUG', '1'), 'TEST'],
    tools=['{pkg_config_tools}']
)
if '{strawberry_perl_path}':
    env_1.AppendENVPath('PATH', '{strawberry_perl_path}')
if sys.platform == 'win32':
    os.environ['PKG_CONFIG_PATH'] = env_1.Dir('.').abspath.replace("\\\\", "/")
env_1.ParseConfig('"{pkg_config_path}" {pkg_config_cl_path} --cflags {pkg_config_file}')
print(env_1.subst('$_CPPDEFFLAGS'))

env_2 = Environment(
    CPPDEFINES=[('DEBUG', '1'), 'TEST'],
    tools=['{pkg_config_tools}']
)
if '{strawberry_perl_path}':
    env_2.AppendENVPath('PATH', '{strawberry_perl_path}')
env_2.MergeFlags('-DSOMETHING -DVARIABLE=2')
print(env_2.subst('$_CPPDEFFLAGS'))

# Failing test cases
env_3 = Environment(
    CPPDEFINES=dict([('DEBUG', 1), ('TEST', None)]),
    tools=['{pkg_config_tools}'],
)
if '{strawberry_perl_path}':
    env_3.AppendENVPath('PATH', '{strawberry_perl_path}')
env_3.ParseConfig('"{pkg_config_path}" {pkg_config_cl_path} --cflags {pkg_config_file}')
print(env_3.subst('$_CPPDEFFLAGS'))

env_4 = Environment(
    CPPDEFINES=dict([('DEBUG', 1), ('TEST', None)]),
    tools=['{pkg_config_tools}'],
)
if '{strawberry_perl_path}':
    env_4.AppendENVPath('PATH', '{strawberry_perl_path}')
env_4.MergeFlags('-DSOMETHING -DVARIABLE=2')
print(env_4.subst('$_CPPDEFFLAGS'))

# https://github.com/SCons/scons/issues/1738
# TODO: the Perl pkg-config doesn't work right with both --cflags --libs
#   e.g.: pkg-config --with-path=. --libs --cflags bug
#   Exepct: -DSOMETHING -DVARIABLE=2
#   Strawberry:   (blank)
#   We don't have any libs in the stub pc file, so just drop that for now.
env_1738_1 = Environment(tools=['{pkg_config_tools}'])
if '{strawberry_perl_path}':
    env_1738_1.AppendENVPath('PATH', '{strawberry_perl_path}')
env_1738_1.ParseConfig(
    '"{pkg_config_path}" {pkg_config_cl_path} --cflags {pkg_config_file}'
)
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
