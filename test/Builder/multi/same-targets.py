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
Verify that a "multi" builder can be called multiple times with the same
target list if everything is identical.
"""

import TestSCons

test = TestSCons.TestSCons(match=TestSCons.match_re)

test.write('SConstruct', """\
DefaultEnvironment(tools=[])

def build(env, target, source):
    for t in target:
        with open(str(t), 'wb') as f:
            for s in source:
                with open(str(s), 'rb') as infp:
                    f.write(infp.read())

B = Builder(action=build, multi=1)
env = Environment(tools=[], BUILDERS = { 'B' : B })
env.B(target = ['file9a.out', 'file9b.out'], source = 'file9a.in')
env.B(target = ['file9a.out', 'file9b.out'], source = 'file9b.in')
""")

test.write('file9a.in', 'file9a.in\n')
test.write('file9b.in', 'file9b.in\n')

test.run(arguments='file9b.out')

test.must_match('file9a.out', "file9a.in\nfile9b.in\n")
test.must_match('file9b.out', "file9a.in\nfile9b.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
