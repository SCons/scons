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

#
# This test ensures that NoClean works correctly, even when it's applied to
# a single target in the return list of an multi-target Builder.
#
import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
def action(target, source, env):
    for t in target:
        with open(t.get_internal_path(), 'w'):
            pass
Command('1.out', 'SConstruct', action)
NoClean('1.out')
""")

test.write('SConstruct.force', """
def action(target, source, env):
    for t in target:
        with open(t.get_internal_path(), 'w'):
            pass
    with open('4.out', 'w'):
        pass
res = Command('3.out', 'SConstruct.force', action)
Clean('4.out', res)
NoClean('4.out')
""")

test.write('SConstruct.multi', """
def action(target, source, env):
    for t in target:
        with open(t.get_internal_path(), 'w'):
            pass
Command(['5.out', '6.out'], 'SConstruct.multi', action)
NoClean('6.out')
""")

#
# Basic check: NoClean keeps files
#
test.run()
test.run(arguments='-c')

test.must_exist('1.out')

#
# Check: NoClean overrides Clean
#
test.run(arguments=['-f', 'SConstruct.force'])
test.run(arguments=['-f', 'SConstruct.force', '-c'])

test.must_not_exist('3.out')
test.must_exist('4.out')

#
# Check: NoClean works for multi-target Builders
#
test.run(arguments=['-f', 'SConstruct.multi'])
test.run(arguments=['-f', 'SConstruct.multi', '-c'])

test.must_not_exist('5.out')
test.must_exist('6.out')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
