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
Verify that we can call add_src_builder() to add a builder to
another on the fly.

This used to trigger infinite recursion (issue 1681) because the
same src_builder list object was being re-used between all Builder
objects that weren't initialized with a separate src_builder.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
copy_out = Builder(action = Copy('$TARGET', '$SOURCE'),
                                 suffix = '.out',
                                 src_suffix = '.mid')

copy_mid = Builder(action = Copy('$TARGET', '$SOURCE'),
                                 suffix = '.mid', \
                                 src_suffix = '.in')

env = Environment(tools=[])
env['BUILDERS']['CopyOut'] = copy_out
env['BUILDERS']['CopyMid'] = copy_mid

copy_out.add_src_builder(copy_mid)

env.CopyOut('file1.out', 'file1.in')
""")

test.write('file1.in', "file1.in\n")

test.run()

test.must_match('file1.mid', "file1.in\n")
test.must_match('file1.out', "file1.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
