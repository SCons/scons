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
Verifies that the default name matching of optparse for long options
gets properly suppressed. We don't allow for partial matching
of argument names, because it would lead to trouble in the test
case below...
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
AddOption('--myargument', dest='myargument', type='string', default='gully')
AddOption('--myarg', dest='myarg', type='string', default='balla')
print("myargument: " + str(GetOption('myargument')))
print("myarg: " + str(GetOption('myarg')))
""")

test.run('-Q -q .',
         stdout="myargument: gully\nmyarg: balla\n")

test.run('-Q -q . --myargument=helloworld',
         stdout="myargument: helloworld\nmyarg: balla\n")

test.run('-Q -q . --myarg=helloworld',
         stdout="myargument: gully\nmyarg: helloworld\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
