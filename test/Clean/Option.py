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
Verify that {Set,Get}Option('clean') works correctly to control
cleaning behavior.
"""

import os

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as ofp, open(sys.argv[2], 'rb') as ifp:
    ofp.write(ifp.read())
""")

test.write('SConstruct', """
DefaultEnvironment(tools=[])
B = Builder(action = r'%(_python_)s build.py $TARGETS $SOURCES')
env = Environment(tools=[], BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')

mode = ARGUMENTS.get('MODE')
if mode == 'not':
    assert not GetOption('clean')
if mode == 'set-zero':
    assert GetOption('clean')
    SetOption('clean', 0)
    assert GetOption('clean')
if mode == 'set-one':
    assert not GetOption('clean')
    SetOption('clean', 1)
    assert GetOption('clean')
""" % locals())

test.write('foo.in', '"Foo", I say!\n')

test.run(arguments='foo.out MODE=not')
test.must_match(test.workpath('foo.out'), '"Foo", I say!\n')

test.run(arguments='-c foo.out MODE=set-zero')
test.must_not_exist(test.workpath('foo.out'))

test.run(arguments='foo.out MODE=none')
test.must_match(test.workpath('foo.out'), '"Foo", I say!\n')

test.run(arguments='foo.out MODE=set-one')
test.must_not_exist(test.workpath('foo.out'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
