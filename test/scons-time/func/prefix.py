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
Verify that the func -p and --prefix options specify what log files to use.
"""

import os.path

import TestSCons_time

test = TestSCons_time.TestSCons_time(match = TestSCons_time.match_re)

try:
    import pstats
except ImportError:
    test.skip_test('No pstats module, skipping test.\n')

input = """\
def _main():
    pass
"""

foo_lines = []
bar_lines = []

for i in range(2):
    test.profile_data('foo-%s.prof' % i, 'prof.py', '_main', input)
    foo_lines.append(r'\d.\d\d\d prof\.py:1\(_main\)' + '\n')

for i in range(4):
    test.profile_data('bar-%s.prof' % i, 'prof.py', '_main', input)
    bar_lines.append(r'\d.\d\d\d prof\.py:1\(_main\)' + '\n')

foo_expect = ''.join(foo_lines)
bar_expect = ''.join(bar_lines)

test.run(arguments = 'func -p bar', stdout = bar_expect)

test.run(arguments = 'func --prefix=foo', stdout = foo_expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
