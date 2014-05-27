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
Verify the time --which option.
"""

import TestSCons_time

test = TestSCons_time.TestSCons_time()

test.fake_logfile('foo-000-0.log', 0)
test.fake_logfile('foo-000-1.log', 0)
test.fake_logfile('foo-000-2.log', 0)

test.fake_logfile('foo-001-0.log', 1)
test.fake_logfile('foo-001-1.log', 1)
test.fake_logfile('foo-001-2.log', 1)

expect = """\
set key bottom left
plot '-' title "Startup" with lines lt 1, \\
     '-' title "Full build" with lines lt 2, \\
     '-' title "Up-to-date build" with lines lt 3
# Startup
0 %(time)s
1 %(time)s
e
# Full build
0 %(time)s
1 %(time)s
e
# Up-to-date build
0 %(time)s
1 %(time)s
e
"""

total       = expect % {'time' : 11.123456}
SConscripts = expect % {'time' : 22.234567}
SCons       = expect % {'time' : 33.345678}
commands    = expect % {'time' : 44.456789}

test.run(arguments = 'time --fmt gnuplot --which total', stdout=total)

test.run(arguments = 'time --fmt gnuplot --which=SConscripts', stdout=SConscripts)

test.run(arguments = 'time --fmt gnuplot --which=SCons', stdout=SCons)

test.run(arguments = 'time --fmt gnuplot --which commands', stdout=commands)

expect = """\
scons-time: time: Unrecognized timer "unknown".
            Type "scons-time help time" for help.
"""

test.run(arguments = 'time --fmt gnuplot --which unknown',
         status = 1,
         stderr = expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
