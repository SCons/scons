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
Test that the $M4COMSTR construction variable allows you to customize
the displayed string when m4 is called.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()



test.write('mym4.py', """
import sys
with open(sys.argv[1], 'wb') as ofp:
    for f in sys.argv[2:]:
        with open(f, 'rb') as ifp:
            for l in [l for l in ifp.readlines() if l != b'/*m4*/\\n']:
                ofp.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(tools=['m4'],
                  M4COM = r'%(_python_)s mym4.py $TARGET $SOURCES',
                  M4COMSTR = 'M4ing $TARGET from $SOURCE')
env.M4(target = 'aaa.out', source = 'aaa.in')
""" % locals())

test.write('aaa.in', "aaa.in\n/*m4*/\n")

test.run(stdout = test.wrap_stdout("""\
M4ing aaa.out from aaa.in
"""))

test.must_match('aaa.out', "aaa.in\n")



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
