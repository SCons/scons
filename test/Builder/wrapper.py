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
Test the ability to use a direct Python function to wrap
calls to other Builder(s).
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
DefaultEnvironment(tools=[])

import os.path
import string
def cat(target, source, env):
    with open(str(target[0]), 'wb') as fp:
        for s in map(str, source):
            with open(s, 'rb') as infp:
                fp.write(infp.read())
Cat = Builder(action=cat)
def Wrapper(env, target, source):
    if not target:
        target = [str(source[0]).replace('.in', '.wout')]
    t1 = 't1-'+str(target[0])
    source = 's-'+str(source[0])
    env.Cat(t1, source)
    t2 = 't2-'+str(target[0])
    env.Cat(t2, source)
env = Environment(tools=[],
                  BUILDERS = {'Cat' : Cat,
                              'Wrapper' : Wrapper})
env.Wrapper('f1.out', 'f1.in')
env.Wrapper('f2.in')
""")

test.write('s-f1.in', "s-f1.in\n")
test.write('s-f2.in', "s-f2.in\n")

test.run()

test.must_match('t1-f1.out', "s-f1.in\n")
test.must_match('t1-f2.wout', "s-f2.in\n")
test.must_match('t2-f1.out', "s-f1.in\n")
test.must_match('t2-f2.wout', "s-f2.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
