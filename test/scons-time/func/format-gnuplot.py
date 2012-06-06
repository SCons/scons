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
Verify the func --format=gnuplot option.
"""

import TestSCons_time

test = TestSCons_time.TestSCons_time(match = TestSCons_time.match_re,
                                     diff = TestSCons_time.diff_re)

try:
    import pstats
except ImportError:
    test.skip_test('No pstats module, skipping test.\n')

content = """\
def _main():
    pass
"""

test.profile_data('foo-000-0.prof', 'prof.py', '_main', content)
test.profile_data('foo-000-1.prof', 'prof.py', '_main', content)
test.profile_data('foo-000-2.prof', 'prof.py', '_main', content)

test.profile_data('foo-001-0.prof', 'prof.py', '_main', content)
test.profile_data('foo-001-1.prof', 'prof.py', '_main', content)
test.profile_data('foo-001-2.prof', 'prof.py', '_main', content)

expect_notitle = r"""set key bottom left
plot '-' title "Startup" with lines lt 1, \\
     '-' title "Full build" with lines lt 2, \\
     '-' title "Up-to-date build" with lines lt 3
# Startup
0 \d.\d\d\d
1 \d.\d\d\d
e
# Full build
0 \d.\d\d\d
1 \d.\d\d\d
e
# Up-to-date build
0 \d.\d\d\d
1 \d.\d\d\d
e
"""

expect_title = 'set title "TITLE"\n' + expect_notitle

test.run(arguments = 'func --fmt gnuplot', stdout=expect_notitle)

test.run(arguments = 'func --fmt=gnuplot --title TITLE', stdout=expect_title)

test.run(arguments = 'func --format gnuplot --title TITLE', stdout=expect_title)

test.run(arguments = 'func --format=gnuplot', stdout=expect_notitle)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
