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

import pstats
import string
import StringIO
import sys

import TestSCons

test = TestSCons.TestSCons()

scons_prof = test.workpath('scons.prof')

test.run(arguments = "--profile=%s -v " % scons_prof)
test.fail_test(string.find(test.stdout(), 'SCons by ') == -1)
test.fail_test(string.find(test.stdout(), 'Copyright') == -1)

stats = pstats.Stats(scons_prof)
stats.sort_stats('time')

sys.stdout = StringIO.StringIO()

stats.strip_dirs().print_stats()

s = sys.stdout.getvalue()

test.fail_test(string.find(s, '__init__.py') == -1)
test.fail_test(string.find(s, 'print_version') == -1)
test.fail_test(string.find(s, 'SCons.Script.main()') == -1)
test.fail_test(string.find(s, 'option_parser.py') == -1)


scons_prof = test.workpath('scons2.prof')

test.run(arguments = "--profile %s -v " % scons_prof)
test.fail_test(string.find(test.stdout(), 'SCons by ') == -1)
test.fail_test(string.find(test.stdout(), 'Copyright') == -1)

stats = pstats.Stats(scons_prof)
stats.sort_stats('time')

sys.stdout = StringIO.StringIO()

stats.strip_dirs().print_stats()

s = sys.stdout.getvalue()

test.fail_test(string.find(s, '__init__.py') == -1)
test.fail_test(string.find(s, 'print_version') == -1)
test.fail_test(string.find(s, 'SCons.Script.main()') == -1)
test.fail_test(string.find(s, 'option_parser.py') == -1)
 

test.pass_test()

