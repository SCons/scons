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
Verify that setting the $TEMPFILESUFFIX variable will cause
it to appear at the end of name of the generated tempfile
used for long command lines.
"""


import TestSCons

test = TestSCons.TestSCons(match=TestSCons.match_re)

test.write('SConstruct', """
import os

env = Environment(
    BUILDCOM='${TEMPFILE("xxx.py $TARGET $SOURCES")}',
    MAXLINELENGTH=16,
    TEMPFILESUFFIX='.foo',
)
env.AppendENVPath('PATH', os.curdir)
env.Command('foo.out', 'foo.in', '$BUILDCOM')
""")

test.write('foo.in', "foo.in\n")
test.run(
    arguments='-n -Q .',
    stdout="""\
Using tempfile \\S+ for command line:
xxx.py foo.out foo.in
xxx.py \\S+
""")

test.write('SConstruct', """
import os

def print_cmd_line(s, targets, sources, env):
    pass

env = Environment(
    BUILDCOM='${TEMPFILE("xxx.py $TARGET $SOURCES")}',
    MAXLINELENGTH=16,
    TEMPFILESUFFIX='.foo',
    PRINT_CMD_LINE_FUNC=print_cmd_line,
)
env.AppendENVPath('PATH', os.curdir)
env.Command('foo.out', 'foo.in', '$BUILDCOM')
""")

test.run(arguments = '-n -Q .',
         stdout = """""")

test.write('SConstruct', """
import os
from SCons.Platform import TempFileMunge

class TestTempFileMunge(TempFileMunge):
    def __init__(self, cmd, cmdstr=None):
        super().__init__(cmd, cmdstr)

    def _print_cmd_str(self, target, source, env, cmdstr):
        super()._print_cmd_str(target, source, None, cmdstr)

env = Environment(
    TEMPFILE=TestTempFileMunge,
    BUILDCOM='${TEMPFILE("xxx.py $TARGET $SOURCES")}',
    MAXLINELENGTH=16,
    TEMPFILESUFFIX='.foo',
)
env.AppendENVPath('PATH', os.curdir)
env.Command('foo.out', 'foo.in', '$BUILDCOM')
""")

test.run(
    arguments='-n -Q .',
    stdout="""\
Using tempfile \\S+ for command line:
xxx.py foo.out foo.in
xxx.py \\S+
""")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
