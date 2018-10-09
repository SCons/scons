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
Verifies the Depends() function when used with Nodes that have no Builder.
"""

import TestSCons

test = TestSCons.TestSCons()

#
test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = Environment(tools=[])
file1 = File('file1')
file2 = File('file2')
env.Depends(file1, [[file2, 'file3']])
# Verify that a "hidden" file created by another action causes the
# action to run when an explicit Dependency is specified.
# https://github.com/SCons/scons/issues/2647
env.Depends('hidden', 'file4.out')
env.Command('file4.out', 'file4.in',
            [Copy('$TARGET', '$SOURCE'), Touch('hidden')])
""")

test.write('file2', "file2\n")
test.write('file3', "file3\n")
test.write('file4.in', "file4.in\n")

test.run(arguments = 'hidden')

test.must_exist('hidden')
test.must_match('file4.out', "file4.in\n")

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
