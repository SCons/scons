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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Verify that all subcommands show up in the global help.

This makes sure that each do_*() function attached to the SConsTimer
class has a line in the help string.
"""

import TestSCons_time

test = TestSCons_time.TestSCons_time()

# Compile the scons-time script as a module.
c = compile(test.read(test.program, mode='r'), test.program, 'exec')

# Evaluate the module in a global name space so we can get at SConsTimer.
globals = {}
try: eval(c, globals)
except: pass

# Extract all subcommands from the the do_*() functions.
functions = list(globals['SConsTimer'].__dict__.keys())
do_funcs = [x for x in functions if x[:3] == 'do_']

subcommands = [x[3:] for x in do_funcs]

expect = ['    %s ' % x for x in subcommands]

test.run(arguments = 'help')

test.must_contain_all_lines(test.stdout(), expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
