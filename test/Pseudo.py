#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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
Test the Pseudo method
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
env = Environment()
foo = env.Command('foo.out', [], '@echo boo')
bar = env.Command('bar.out', [], Touch('$TARGET'))
env.Pseudo(foo, bar)

gfoo = Command('foo.glb', [], '@echo boo')
gbar = Command('bar.glb', [], Touch('$TARGET'))
Pseudo(gfoo, gbar)
""")

# foo.out build does not create file, should generate no errors
test.run(arguments='-Q foo.out', stdout='boo\n')
# missing target warning triggers if requested
test.run(arguments='-Q foo.out --warning=target-not-built', stdout="boo\n")
# bar.out build creates file, error if it exists after the build
test.run(arguments='-Q bar.out', stdout='Touch("bar.out")\n', stderr=None, status=2)
test.must_contain_all_lines(
    test.stderr(),
    'scons:  *** Pseudo target bar.out must not exist',
)
# warning must not appear since target created
test.run(
    arguments='-Q bar.out --warning=target-not-built',
    stdout='Touch("bar.out")\n',
    stderr=None,
    status=2,
)
test.must_contain_all_lines(
    test.stderr(),
    'scons:  *** Pseudo target bar.out must not exist',
)

# repeat the process for the global function form (was missing initially)
test.run(arguments='-Q foo.glb', stdout='boo\n')
test.run(arguments='-Q foo.glb --warning=target-not-built', stdout="boo\n")
test.run(arguments='-Q bar.glb', stdout='Touch("bar.glb")\n', stderr=None, status=2)
test.must_contain_all_lines(
    test.stderr(),
    'scons:  *** Pseudo target bar.glb must not exist',
)
test.run(
    arguments='-Q bar.glb --warning=target-not-built',
    stdout='Touch("bar.glb")\n',
    stderr=None,
    status=2,
)
test.must_contain_all_lines(
    test.stderr(),
    'scons:  *** Pseudo target bar.glb must not exist',
)

test.pass_test()
