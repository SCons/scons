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

"""
Verify behavior of the -H and --help-options options.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import re

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', "DefaultEnvironment(tools=[])\n")

test.run(arguments = '-H')

expect = [
    '-H, --help-options',
    '--debug=TYPE',
]
test.must_contain_all_lines(test.stdout(), expect)

# Validate that the help output lists the options in case-insensitive
# alphabetical order.

# Don't include in the sorted comparison the options that are ignored
# for compatibility.  They're all printed at the top of the list.
ignored_re = re.compile('.*Ignored for compatibility\\.\n', re.S)
stdout = ignored_re.sub('', test.stdout())

lines = stdout.split('\n')
lines = [x for x in lines if x[:3] == '  -']
lines = [x[3:] for x in lines]
lines = [x[0] == '-' and x[1:] or x for x in lines]
options = [x.split()[0] for x in lines]
options = [x[-1] == ',' and x[:-1] or x for x in options]
lowered = [x.lower() for x in options]
ordered = sorted(lowered)
if lowered != ordered:
    print("lowered =", lowered)
    print("sorted =", ordered)
    test.fail_test()

test.pass_test()
 

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
