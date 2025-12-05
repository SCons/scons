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
Test that setting illegal construction variables fails in ways that are
useful to the user.
"""

import TestSCons

test = TestSCons.TestSCons()

SConstruct_path = test.workpath('SConstruct')
SConscript_path = test.workpath('SConscript')

test.write(SConstruct_path, """\
_ = DefaultEnvironment(tools=[])
env = Environment(tools=[])
env['foo-bar'] = 1
""")

expect_stderr = """
scons: *** Illegal construction variable 'foo-bar'
""" + test.python_file_line(SConstruct_path, 3)

test.run(arguments='.', status=2, stderr=expect_stderr)



test.write(SConstruct_path, """\
SConscript('SConscript')
""")

test.write('SConscript', """\
_ = DefaultEnvironment(tools=[])
env = Environment(tools=[])
env['foo(bar)'] = 1
""")


expect_stderr = """
scons: *** Illegal construction variable 'foo(bar)'
""" + test.python_file_line(SConscript_path, 3)

test.run(arguments='.', status=2, stderr=expect_stderr)

test.pass_test()
