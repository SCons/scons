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
Test calling the --debug=nomemoizer option.
"""

import pstats
import string
import StringIO
import sys

import TestSCons

test = TestSCons.TestSCons()

scons_prof = test.workpath('scons.prof')

test.write('SConstruct', """
def cat(target, source, env):
    open(str(target[0]), 'wb').write(open(str(source[0]), 'rb').read())
env = Environment(BUILDERS={'Cat':Builder(action=Action(cat))})
env.Cat('file.out', 'file.in')
""")

test.write('file.in', "file.in\n")

test.run(arguments = "--profile=%s --debug=nomemoizer " % scons_prof)

stats = pstats.Stats(scons_prof)
stats.sort_stats('time')

try:
    save_stdout = sys.stdout
    sys.stdout = StringIO.StringIO()

    stats.strip_dirs().print_stats()

    s = sys.stdout.getvalue()
finally:
    sys.stdout = save_stdout

test.fail_test(string.find(s, '_MeMoIZeR_init') != -1)
test.fail_test(string.find(s, '_MeMoIZeR_reset') != -1)
test.fail_test(string.find(s, 'Count_cache_get') != -1)
test.fail_test(string.find(s, 'Count_cache_get_self') != -1)
test.fail_test(string.find(s, 'Count_cache_get_one') != -1)

test.pass_test()
