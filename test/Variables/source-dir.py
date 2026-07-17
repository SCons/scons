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
Test that a Variables() saved-variables file (e.g. custom.py) is read from
the source tree when it is not present in the build directory, i.e. when
building against a separate source directory via Repository() (issue #816).
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('repository', 'work')

opts = "-Y " + test.workpath('repository')

# The saved-variables file lives only in the source tree (the repository),
# not in the 'work' directory where SCons is actually invoked.
test.write(['repository', 'custom.py'], """\
MY_VARIABLE = 'from_source_tree'
""")

test.write(['repository', 'SConstruct'], """\
DefaultEnvironment(tools=[])
vars = Variables('custom.py')
vars.Add('MY_VARIABLE', 'a test variable', 'default_value')
env = Environment(variables=vars, tools=[])
print("MY_VARIABLE =", env['MY_VARIABLE'])
""")

# Before the issue #816 fix, custom.py was looked up relative to the build
# directory only, so it was not found here and the default value was used.
test.run(chdir='work', options=opts, arguments='.')

expect = "MY_VARIABLE = from_source_tree"
if expect not in test.stdout():
    test.fail_test()

test.pass_test()
