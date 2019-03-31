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
Verify that a directory (Dir()) works as a SideEffect() "target."
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
import os.path
import os

def copy(source, target):
    with open(target, "wb") as ofp, open(source, "rb") as ifp:
        ofp.write(ifp.read())

def build(env, source, target):
    copy(str(source[0]), str(target[0]))
    if target[0].side_effects:
        try: os.mkdir('log')
        except: pass
        copy(str(target[0]), os.path.join('log', str(target[0])))

Build = Builder(action=build)
env = Environment(BUILDERS={'Build':Build})
env.Build('foo.out', 'foo.in')
env.Build('bar.out', 'bar.in')
env.Build('blat.out', 'blat.in')
env.SideEffect(Dir('log'), ['foo.out', 'bar.out', 'blat.out'])
""")

test.write('foo.in', "foo.in\n")
test.write('bar.in', "bar.in\n")
test.write('blat.in', "blat.in\n")

test.run(arguments='foo.out')

test.must_exist(test.workpath('foo.out'))
test.must_exist(test.workpath('log/foo.out'))
test.must_not_exist(test.workpath('log', 'bar.out'))
test.must_not_exist(test.workpath('log', 'blat.out'))

test.run(arguments='log')

test.must_exist(test.workpath('log', 'bar.out'))
test.must_exist(test.workpath('log', 'blat.out'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
