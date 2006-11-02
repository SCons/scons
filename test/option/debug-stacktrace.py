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

"""
Test the --debug=stacktrace option.
"""

import TestSCons
import sys
import string
import re
import time

test = TestSCons.TestSCons()

def must_contain_all_lines(content, lines):
    missing = filter(lambda l, c=content: string.find(c, l) == -1, lines)
    if missing:
        return [
                "Missing the following lines:\n",
                "\t" + string.join(missing, "\n\t") + "\n",
                "Output =====\n",
                content
                ]
    return None



test.write('SConstruct', """\
def kfile_scan(node, env, target):
    raise "kfile_scan error"

kscan = Scanner(name = 'kfile',
                function = kfile_scan,
                skeys = ['.k'])

env = Environment()
env.Append(SCANNERS = [kscan])

env.Command('foo', 'foo.k', Copy('$TARGET', '$SOURCE'))
""")

test.write('foo.k', "foo.k\n")

test.run(status = 2, stderr = "scons: *** kfile_scan error\n")

test.run(arguments = "--debug=stacktrace",
         status = 2,
         stderr = None)

lines = [
    "scons: *** kfile_scan error",
    "scons: internal stack trace:",
    'raise "kfile_scan error"',
]

err = must_contain_all_lines(test.stderr(), lines)
if err:
    print string.join(err, '')
    test.fail_test(1)



# Test that --debug=stacktrace works for UserError exceptions,
# which are handled by different code than other exceptions.

test.write('SConstruct', """\
import SCons.Errors
raise SCons.Errors.UserError, "explicit UserError!"
""")

test.run(arguments = '--debug=stacktrace',
         status = 2,
         stderr = None)

lines = [
    'UserError: explicit UserError!',
    'scons: *** explicit UserError!',
]

# The "(most recent call last)" message is used by more recent Python
# versions than the "(innermost last)" message, so that's the one
# we report if neither matches.
recent_lines = [ "Traceback (most recent call last)" ] + lines
inner_lines = [ "Traceback (innermost last)" ] + lines

err = must_contain_all_lines(test.stderr(), recent_lines)
if err and must_contain_all_lines(test.stderr(), inner_lines):
    print string.join(err, '')
    test.fail_test(1)



# Test that full path names to SConscript files show up in stack traces.

test.write('SConstruct', """\
1/0
""")

test.run(arguments = '--debug=stacktrace',
         status = 2,
         stderr = None)

lines = [
    '  File "%s", line 1:' % test.workpath('SConstruct'),
]

err = must_contain_all_lines(test.stderr(), lines)
if err:
    print string.join(err, '')
    test.fail_test(1)



test.pass_test()
