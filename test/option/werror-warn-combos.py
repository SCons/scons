#!/usr/bin/env python
#
# Copyright the SCons Foundation
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
Verify use of the --werror options, alone and combined with --warn.
"""

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)


test.write('SConstruct', """
WERROR = ARGUMENTS.get('WERROR')
if WERROR:
    SetOption('werror', WERROR)
WARN = ARGUMENTS.get('WARN')
if WARN:
    SetOption('warn', WARN)

def build(env, target, source):
    with open(str(target[0]), 'wb') as ofp:
        for s in source:
            with open(str(s), 'rb') as ifp:
                ofp.write(ifp.read())

DefaultEnvironment(tools=[])
B = Builder(action=build, multi=1)
env = Environment(tools=[], BUILDERS={'B': B})
env2 = env.Clone(DIFFERENT_VARIABLE='true')
env.B(target='file1.out', source='file1a.in')
env2.B(target='file1.out', source='file1b.in')
""")

test.write('file1a.in', 'file1a.in\n')
test.write('file1b.in', 'file1b.in\n')

expect_warn = r"""
scons: warning: Two different environments were specified for target file1.out,
\tbut they appear to have the same action: build\(target, source, env\)
""" + TestSCons.file_expr

expect_fail = r"""
scons: \*\*\* Two different environments were specified for target file1.out,
\tbut they appear to have the same action: build\(target, source, env\)
""" + TestSCons.file_expr

test.run(arguments='file1.out', status=0, stderr=expect_warn)
test.must_match('file1.out', "file1a.in\nfile1b.in\n")

test.run(
    arguments='--werror=duplicate-environment file1.out',
    status=2,
    stderr=expect_fail,
)
# This should warn, DuplicateEnvironment is a WarningsOnByDefault
test.run(
    arguments='--werror=no-duplicate-environment file1.out',
    status=0,
    stderr=expect_warn,
)
test.run(
    arguments='WERROR=duplicate-environment file1.out',
    status=2,
    stderr=expect_fail,
)
# This should warn, DuplicateEnvironment is a WarningsOnByDefault
test.run(
    arguments='WERROR=no-duplicate-environment file1.out',
    status=0,
    stderr=expect_warn,
)
# cmdline should "win": warning
test.run(
    arguments='--warn=duplicate-environment WERROR=duplicate-environment file1.out',
    status=0,
    stderr=expect_warn,
)
# cmdline should "win": error
test.run(
    arguments='--werror=duplicate-environment WARN=duplicate-environment file1.out',
    status=2,
    stderr=expect_fail,
)


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
