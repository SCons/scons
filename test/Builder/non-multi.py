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
Verify that a builder without "multi" set can still be called multiple
times if the calls are the same.
"""

import TestSCons

test = TestSCons.TestSCons(match=TestSCons.match_re)

test.write('SConstruct', """
def build(env, target, source):
    file = open(str(target[0]), 'wb')
    for s in source:
        file.write(open(str(s), 'rb').read())

B = Builder(action=build, multi=0)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'file7.out', source = 'file7.in')
env.B(target = 'file7.out', source = 'file7.in')
""")

test.write('file7.in', 'file7.in\n')

test.run(arguments='file7.out')

test.must_match('file7.out', "file7.in\n")

test.pass_test()
