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
Verify substition of the $TARGET string in progress output, including
overwriting it by setting the overwrite= keyword argument.
"""


import TestSCons

test = TestSCons.TestSCons(universal_newlines=None)

test.write('SConstruct', """\
env = Environment()
env['BUILDERS']['C'] = Builder(action=Copy('$TARGET', '$SOURCE'))
Progress('$TARGET\\r', overwrite=True)
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
S1.in\r     \rS1.out\rCopy("S1.out", "S1.in")
      \rS2.in\r     \rS2.out\rCopy("S2.out", "S2.in")
      \rS3.in\r     \rS3.out\rCopy("S3.out", "S3.in")
      \rS4.in\r     \rS4.out\rCopy("S4.out", "S4.in")
      \rSConstruct\r          \r.\r"""

test.run(arguments = '-Q .', stdout=expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
