#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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

import TestCmd
import TestSCons
import os
import string

test = TestSCons.TestSCons(match = TestCmd.match_re)

wpath = test.workpath()

test.write('SConstruct', r"""
Help("Help text.\n")
""")

expect = "Help text.\n\nUse scons -H for help about command-line options.\n"

os.environ['SCONSFLAGS'] = ''

test.run(arguments = '-h', stdout = expect)

os.environ['SCONSFLAGS'] = '-h'

test.run(stdout = expect)

test.run(arguments = "-H")

test.fail_test(string.find(test.stdout(), 'Help text.') >= 0)
test.fail_test(string.find(test.stdout(), '-H, --help-options') == -1)

os.environ['SCONSFLAGS'] = '-Z'

test.run(arguments = "-H", stderr = r"""
SCons warning: SCONSFLAGS option -Z not recognized
File "[^"]*", line \d+, in \S+
""")

test.fail_test(string.find(test.stdout(), '-H, --help-options') == -1)

test.pass_test()
