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
Verify that a specific snippet of backwards-compatibility code works.

"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """

# When the 0.96.93 release introduced the env.Clone() we advertised this
# code as the correct pattern for maintaining the backwards compatibility
# of SConstruct files to earlier release of SCons.  Going forward, make
# sure it still works (or at least doesn't blow up).
# Copy was removed for 3.1.2 but Clone will certainly be there -
# this test probably isn't needed any longer.
import SCons.Environment
try:
    SCons.Environment.Environment.Clone
except AttributeError:
    SCons.Environment.Environment.Clone = SCons.Environment.Environment.Copy

env1 = Environment(X = 1)
env2 = env1.Clone(X = 2)

print(env1['X'])
print(env2['X'])
""")

test.run(arguments = '-q -Q', stdout = "1\n2\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
