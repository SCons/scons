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
Verify that we can use the any() function (in any supported Python
version we happen to be testing).

This test can be retired at some point in the distant future when Python
2.5 becomes the minimum version supported by SCons.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
print all([True, 1]) and "YES" or "NO"
print all([0]) and "YES" or "NO"
SConscript('SConscript')
""")

test.write('SConscript', """\
print all([1, False]) and "YES" or "NO"
print all([True, None]) and "YES" or "NO"
""")

expect = """\
YES
NO
NO
NO
"""

test.run(arguments = '-Q -q', stdout = expect)

test.pass_test()
