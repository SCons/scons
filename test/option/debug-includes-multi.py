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
Test that the --debug=includes option prints the implicit
dependencies of a target.

A separate test to make sure it works if there is more than one source.
The main test uses a C compiler, and object builders there are
single-source, so we need a different scheme.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
import os
import os.path
import sys

DefaultEnvironment(tools=[])

def buildIt(env, target, source):
    with open(target[0], 'w') as ofp:
        for out in source:
            with open(source[0], 'r') as ifp:
                ofp.write(ifp.read())
    return 0

def source_scanner(node, env, path, builder):
    return [File('a.inc'), File('b.inc')]

env = Environment(tools=[])
env.Command(
    target="f.out",
    source=["f1.in", "f2.in"],
    action=buildIt,
    source_scanner=Scanner(
        lambda node, env, path: source_scanner(node, env, path, "w-env")
    )
)
""")

# the contents of these sources/includes don't matter
test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('a.inc', "a.inc\n")
test.write('b.inc', "b.inc\n")

expect = """
+-f1.in
  +-a.inc
  | +-[a.inc]
  | +-b.inc
  |   +-[a.inc]
  |   +-[b.inc]
  +-[b.inc]
+-f2.in
  +-a.inc
  | +-[a.inc]
  | +-b.inc
  |   +-[a.inc]
  |   +-[b.inc]
  +-[b.inc]
"""
test.run(arguments="-Q --debug=includes f.out")
test.must_contain_all_lines(test.stdout(), [expect])

test.pass_test()
