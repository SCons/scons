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
Verify the "obj" subcommand help.
"""

import TestSCons_time

test = TestSCons_time.TestSCons_time()

expect = [
    "Usage: scons-time obj [OPTIONS] OBJECT FILE [...]\n",
    "  -C DIR, --chdir=DIR           Change to DIR before looking for files\n",
    "  -h, --help                    Print this help and exit\n",
]

test.run(arguments = 'obj -h')

test.must_contain_all_lines(test.stdout(), expect)

test.run(arguments = 'obj -?')

test.must_contain_all_lines(test.stdout(), expect)

test.run(arguments = 'obj --help')

test.must_contain_all_lines(test.stdout(), expect)

test.run(arguments = 'help obj')

test.must_contain_all_lines(test.stdout(), expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
