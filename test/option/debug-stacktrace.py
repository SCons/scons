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
Test the --debug=stacktrace option.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
DefaultEnvironment(tools=[])

def kfile_scan(node, env, target):
    raise Exception("kfile_scan error")

kscan = Scanner(name='kfile', function=kfile_scan, skeys=['.k'])
env = Environment(tools=[])
env.Append(SCANNERS = [kscan])

env.Command('foo', 'foo.k', Copy('$TARGET', '$SOURCE'))
""")
test.write('foo.k', "foo.k\n")

test.run(status = 2, stderr = "scons: *** [foo] Exception : kfile_scan error\n")
test.run(arguments="--debug=stacktrace", status=2, stderr=None)
lines = [
    "scons: *** [foo] Exception : kfile_scan error",
    "scons: internal stack trace:",
    'raise Exception("kfile_scan error")',
]
test.must_contain_all_lines(test.stderr(), lines)

# Test that --debug=stacktrace works for UserError exceptions,
# which are handled by different code than other exceptions.

test.write('SConstruct', """\
import SCons.Errors
raise SCons.Errors.UserError("explicit UserError!")
""")

test.run(arguments='--debug=stacktrace', status=2, stderr=None)
user_error_lines = [
    'UserError: explicit UserError!',
    'scons: *** explicit UserError!',
]
traceback_lines = ["Traceback (most recent call last)",]
test.must_contain_all_lines(test.stderr(), user_error_lines)
test.must_contain_all_lines(test.stderr(), traceback_lines)

# Test that full path names to SConscript files show up in stack traces.

test.write('SConstruct', """\
1/0
""")

test.run(arguments='--debug=stacktrace', status=2, stderr=None)
lines = ['  File "%s", line 1:' % test.workpath('SConstruct'),]
test.must_contain_all_lines(test.stderr(), lines)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
