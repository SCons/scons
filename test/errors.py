#!/usr/bin/env python
#
# Copyright (c) 2001 Steven Knight
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

test = TestSCons.TestSCons(match = TestCmd.match_re)

test.write('SConstruct1', """
a ! x
""")

test.run(arguments='-f SConstruct1',
	 stdout = "",
	 stderr = """  File "SConstruct1", line 2

    a ! x

      \^

SyntaxError: invalid syntax

""")


test.write('SConstruct2', """
raise UserError, 'Depends() require both sources and targets.'
""")

test.run(arguments='-f SConstruct2',
	 stdout = "",
	 stderr = """
SCons error: Depends\(\) require both sources and targets.
File "SConstruct2", line 2, in \?
""")

test.write('SConstruct3', """
raise InternalError, 'error inside'
""")

test.run(arguments='-f SConstruct3',
	 stdout = "other errors\n",
	 stderr = r"""Traceback \((most recent call|innermost) last\):
  File ".*Script.py", line \d+, in main
    _main\(\)
  File ".*Script.py", line \d+, in _main
    exec file in globals\(\)
  File "SConstruct3", line \d+, in \?
    raise InternalError, 'error inside'
InternalError: error inside
""")

test.pass_test()
