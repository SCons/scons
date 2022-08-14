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
Test that setting the YACCHFILESUFFIX variable can reflect a yacc
utility that writes to an odd
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('myyacc.py', """\
import getopt
import os.path
import sys

opts, args = getopt.getopt(sys.argv[1:], 'do:')
for o, a in opts:
    if o == '-o':
        outfile = open(a, 'wb')
for f in args:
    with open(f, 'rb') as infile:
        for l in [l for l in infile.readlines() if l != b'/*yacc*/\\n']:
            outfile.write(l)
outfile.close()
base, ext = os.path.splitext(args[0])
with open(base + '.hsuffix', 'wb') as outfile:
    outfile.write((" ".join(sys.argv) + '\\n').encode())
sys.exit(0)
""")

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(
    tools=['default', 'yacc'],
    YACC=r'%(_python_)s myyacc.py',
    YACCFLAGS='-d',
    YACCHFILESUFFIX='.hsuffix',
)
env.CFile(target='aaa', source='aaa.y')
env.CFile(target='bbb', source='bbb.yacc')
""" % locals())

test.write('aaa.y', "aaa.y\n/*yacc*/\n")
test.write('bbb.yacc', "bbb.yacc\n/*yacc*/\n")

test.run(arguments='.')

test.must_match('aaa.c', "aaa.y\n")
test.must_contain('aaa.hsuffix', "myyacc.py -d -o aaa.c aaa.y\n")
test.must_match('bbb.c', "bbb.yacc\n")
test.must_contain('bbb.hsuffix', "myyacc.py -d -o bbb.c bbb.yacc\n")

test.up_to_date(arguments='.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
