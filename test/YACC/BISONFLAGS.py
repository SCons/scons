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
Test that detection of file-writing options in YACCFLAGS works.
Also test that the construction vars for the same purpose work.
"""

from pathlib import Path

import TestSCons
from TestCmd import IS_WINDOWS

_python_ = TestSCons._python_
_exe = TestSCons._exe

if IS_WINDOWS:
    compiler = 'msvc'
    linker = 'mslink'
else:
    compiler = 'gcc'
    linker = 'gnulink'

test = TestSCons.TestSCons()

test.subdir('sub1')
test.subdir('sub2')
test.subdir('sub3')

test.dir_fixture('YACCFLAGS-fixture')

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
SConscript(dirs=['sub1', 'sub2', 'sub3'])
""")

# this SConscript is for the options-in-flags version
test.write(['sub1', 'SConscript'], """\
import sys

env = Environment(
    YACC=r'%(_python_)s myyacc.py',
    YACCFLAGS='-x --header=header.h --graph=graph.g',
    tools=['yacc', '%(linker)s', '%(compiler)s'],
)
targs = env.CFile(target='aaa', source='aaa.y')
t = [str(target) for target in targs]
# fail ourselves if the two extra files were not detected
if not all((len(t) == 3, "header.h" in t, "graph.g" in t)):
    sys.exit(1)
""" % locals())
test.write(['sub1', 'aaa.y'], "aaa.y\nYACCFLAGS\n")

# this SConscript is for the construction var version
test.write(['sub2', 'SConscript'], """\
import sys

env = Environment(
    YACC=r'%(_python_)s myyacc.py',
    YACCFLAGS='-x',
    tools=['yacc', '%(linker)s', '%(compiler)s'],
)
env.CFile(
    target='aaa',
    source='aaa.y',
    YACC_HEADER_FILE='header.h',
    YACC_GRAPH_FILE='graph.g',
)
""" % locals())
test.write(['sub2', 'aaa.y'], "aaa.y\nYACCFLAGS\n")

# this SConscript is to try various other flag combos
test.write(['sub3', 'SConscript'], """\
import sys

env = Environment(
    YACC=r'%(_python_)s myyacc.py',
    YACCFLAGS='-x --header=header.h --graph=graph.g',
    tools=['yacc', '%(linker)s', '%(compiler)s'],
)

def check(targets, expected):
    t = [str(target) for target in targets]
    assert t == expected, t

targs1 = env.CFile('trg1', source='aaa.y', YACCFLAGS='-d')
check(targs1, ['trg1.c', 'trg1.h'])

targs2 = env.CXXFile('trg2', source='aaa.yy', YACCFLAGS='-d')
check(targs2, ['trg2.cc', 'trg2.hpp'])

targs3 = env.CFile('trg3', source='aaa.y', YACCFLAGS='--defines=zot.q')
check(targs3, ['trg3.c', 'zot.q'])

targs4 = env.CFile('trg4', source='aaa.y', YACCFLAGS='--header')
check(targs4, ['trg4.c', 'trg4.h'])

targs5 = env.CFile('trg5', source='aaa.y', YACCFLAGS='-H')
check(targs5, ['trg5.c', 'trg5.h'])

targs6 = env.CFile('trg6', source='aaa.y', YACCFLAGS='-g')
check(targs6, ['trg6.c', 'trg6.gv'])

targs7 = env.CFile('trg7', source='aaa.y', YACCFLAGS='-g -H')
check(targs7, ['trg7.c', 'trg7.h', 'trg7.gv'])

targs8 = env.CFile('trg8', source='aaa.y', YACCFLAGS='--graph --header')
check(targs8, ['trg8.c', 'trg8.h', 'trg8.gv'])
""" % locals())

test.write(['sub3', 'aaa.y'], "aaa.y\nYACCFLAGS\n")
test.write(['sub3', 'aaa.yy'], "aaa.yy\nYACCFLAGS\n")

test.run('.', stderr=None)
test.must_match(['sub1', 'aaa.c'], "aaa.y\n-x --header=header.h --graph=graph.g\n")

# NOTE: this behavior is "wrong" but we're keeping it for compat:
# the generated files should go into 'sub1', not the topdir.
test.must_match(['header.h'], 'yacc header\n')
test.must_match(['graph.g'], 'yacc graph\n')

# To confirm the files from the file-output options were tracked,
# we should do a clean and make sure they got removed.
# As noted, they currently don't go into the tracked location,
# so using the check in the SConscript instead.
#test.run(arguments='-c .')
#test.must_not_exist(test.workpath(['sub1', 'header.h']))
#test.must_not_exist(test.workpath(['sub1', 'graph.g']))

sub2 = Path('sub2')
headerfile = sub2 / 'header.h'
graphfile = sub2 / 'graph.g'
yaccflags = f"aaa.y\n-x --header={headerfile} --graph={graphfile}\n"
test.must_match(['sub2', 'aaa.c'], yaccflags)
test.must_match(['sub2', 'header.h'], 'yacc header\n')
test.must_match(['sub2', 'graph.g'], 'yacc graph\n')

# To confirm the files from the file-output options were tracked,
# do a clean and make sure they got removed. As noted, they currently
# don't go into the tracked location, so using the the SConscript check instead.
test.run(arguments='-c .')
test.must_not_exist(test.workpath('sub2', 'header.h'))
test.must_not_exist(test.workpath('sub2', 'graph.g'))

test.pass_test()
