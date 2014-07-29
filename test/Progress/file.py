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
Verify that the file= argument to Progress() allows us to redirect the
progress output.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
env = Environment()
env['BUILDERS']['C'] = Builder(action=Copy('$TARGET', '$SOURCE'))
Progress('stderr: $TARGET\\n', file=open('progress.out', 'w'))
env.C('S1.out', 'S1.in')
env.C('S2.out', 'S2.in')
env.C('S3.out', 'S3.in')
env.C('S4.out', 'S4.in')
""")

test.write('S1.in', "S1.in\n")
test.write('S2.in', "S2.in\n")
test.write('S3.in', "S3.in\n")
test.write('S4.in', "S4.in\n")

expect = """\
Copy("S1.out", "S1.in")
Copy("S2.out", "S2.in")
Copy("S3.out", "S3.in")
Copy("S4.out", "S4.in")
"""

test.run(arguments = '-Q .', stdout=expect)

expect = """\
stderr: S1.in
stderr: S1.out
stderr: S2.in
stderr: S2.out
stderr: S3.in
stderr: S3.out
stderr: S4.in
stderr: S4.out
stderr: SConstruct
stderr: .
"""

if os.linesep != '\n':
    expect = expect.replace('\n', os.linesep)

test.must_match('progress.out', expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
