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
Verify the behavior of passing our own function to Progress().
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
import sys
env = Environment()
env['BUILDERS']['C'] = Builder(action=Copy('$TARGET', '$SOURCE'))
def my_progress_function(node, *args, **kw):
    sys.stderr.write('mpf: %s\\n' % node)
Progress(my_progress_function)
env.C('S1.out', 'S1.in')
env.C('S2.out', 'S2.in')
env.C('S3.out', 'S3.in')
env.C('S4.out', 'S4.in')
""")

test.write('S1.in', "S1.in\n")
test.write('S2.in', "S2.in\n")
test.write('S3.in', "S3.in\n")
test.write('S4.in', "S4.in\n")

expect_stdout = """\
Copy("S1.out", "S1.in")
Copy("S2.out", "S2.in")
Copy("S3.out", "S3.in")
Copy("S4.out", "S4.in")
"""

expect_stderr = """\
mpf: S1.in
mpf: S1.out
mpf: S2.in
mpf: S2.out
mpf: S3.in
mpf: S3.out
mpf: S4.in
mpf: S4.out
mpf: SConstruct
mpf: .
"""

test.run(arguments = '-Q .', stdout=expect_stdout, stderr=expect_stderr)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
