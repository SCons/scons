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
Verify that config files specified with the -f and --file options
affect how the time subcommand processes things.
"""

import TestSCons_time

test = TestSCons_time.TestSCons_time()

test.fake_logfile('foo-001-0.log')

test.fake_logfile('foo-002-0.log')


test.write('st1.conf', """\
prefix = 'foo-001'
""")

expect1 = """\
       Total  SConscripts        SCons     commands
   11.123456    22.234567    33.345678    44.456789    foo-001-0.log
"""

test.run(arguments = 'time -f st1.conf', stdout = expect1)


test.write('st2.conf', """\
prefix = 'foo'
title = 'ST2.CONF TITLE'
vertical_bars = (
    ( 1.5, 7, None ),
)
""")

expect2 = \
r"""set title "ST2.CONF TITLE"
set key bottom left
plot '-' title "Startup" with lines lt 1, \
     '-' notitle with lines lt 7
# Startup
1 11.123456
2 11.123456
e
1.5 0
1.5 12
e
"""

test.run(arguments = 'time --file st2.conf --fmt gnuplot', stdout = expect2)


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
