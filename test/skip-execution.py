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
Verify that a command that builds multiple targets doesn't get
skipped if the first target is up-to-date but the rest aren't.
Test (and fix for the bug) courtesy Patrick Mezard.
"""

import TestSCons

test = TestSCons.TestSCons()


test.write('SConstruct', """
env = Environment()
env.Command(['a', 'b', 'c'], ['source'], [Touch('a'),Touch('b'),Touch('c')])
""")

test.write('source', '')

test.run(arguments = '.')
test.must_exist('a')
test.must_exist('b')
test.must_exist('c')

test.unlink('c')
test.run(arguments = '.')
test.must_exist('c')

test.unlink('b')
test.run(arguments = '.')
test.must_exist('b')

test.unlink('a')
test.run(arguments = '.')
test.must_exist('a')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
