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
Test how we handle SConscript calls when using a Repository.
"""

import sys
from TestSCons import TestSCons

test = TestSCons()

test.subdir('work',
            ['work', 'src'],
            'rep1',
            ['rep1', 'src'],
            'rep2',
            ['rep2', 'build'],
            ['rep2', 'src'],
            ['rep2', 'src', 'sub'])

workpath_rep1 = test.workpath('rep1')
workpath_rep2 = test.workpath('rep2')

test.write(['work', 'SConstruct'], """
Repository(r'%s')
SConscript('src/SConscript')
""" % workpath_rep1)

test.write(['rep1', 'src', 'SConscript'], """\
def cat(env, source, target):
    target = str(target[0])
    with open(target, "w") as ofp:
        for src in source:
            with open(str(src), "r") as ifp:
                ofp.write(ifp.read())

env = Environment(BUILDERS={'Cat':Builder(action=cat)})
env.Cat(target = 'foo', source = ['aaa.in', 'bbb.in', 'ccc.in'])
""")

test.write(['rep1', 'src', 'aaa.in'], "rep1/src/aaa.in\n")
test.write(['rep1', 'src', 'bbb.in'], "rep1/src/bbb.in\n")
test.write(['rep1', 'src', 'ccc.in'], "rep1/src/ccc.in\n")

# Make the rep1 non-writable,
# so we'll detect if we try to write into it accidentally.
test.writable('rep1', 0)

test.run(chdir = 'work', arguments = ".")

test.must_match(['work', 'src', 'foo'], """\
rep1/src/aaa.in
rep1/src/bbb.in
rep1/src/ccc.in
""", mode='r')

test.up_to_date(chdir = 'work', arguments = ".")

#
test.write(['rep2', 'build', 'SConstruct'], """
env = Environment(REPOSITORY = r'%s')
env.Repository('$REPOSITORY')
SConscript('src/SConscript')
""" % workpath_rep2)

test.write(['rep2', 'src', 'SConscript'], """\
def cat(env, source, target):
    target = str(target[0])
    with open(target, "w") as ofp:
        for src in source:
            with open(str(src), "r") as ifp:
                ofp.write(ifp.read())

env = Environment(BUILDERS={'Cat':Builder(action=cat)})
env.Cat(target = 'foo', source = ['aaa.in', 'bbb.in', 'ccc.in'])
SConscript('sub/SConscript')
""")

test.write(['rep2', 'src', 'sub', 'SConscript'], """\
""")

test.write(['rep2', 'src', 'aaa.in'], "rep2/src/aaa.in\n")
test.write(['rep2', 'src', 'bbb.in'], "rep2/src/bbb.in\n")
test.write(['rep2', 'src', 'ccc.in'], "rep2/src/ccc.in\n")

test.run(chdir = 'rep2/build', arguments = ".")

test.must_match(['rep2', 'build', 'src', 'foo'], """\
rep2/src/aaa.in
rep2/src/bbb.in
rep2/src/ccc.in
""", mode='r')

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
