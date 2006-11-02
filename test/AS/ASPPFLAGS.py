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

import os
import string
import sys
import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()
_exe = TestSCons._exe


if sys.platform == 'win32':

    o = ' -x'

    o_c = ' -x'

    test.write('mylink.py', r"""
import string
import sys
args = sys.argv[1:]
while args:
    a = args[0]
    if a[0] != '/':
        break
    args = args[1:]
    if string.lower(a[:5]) == '/out:': out = a[5:]
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:5] != '#link':
        outfile.write(l)
sys.exit(0)
""")

    test.write('myas.py', r"""
import sys
args = sys.argv[1:]
inf = None
optstring = ''
while args:
    a = args[0]
    args = args[1:]
    if not a[0] in '/-':
        if not inf:
            inf = a
        continue
    if a[:2] == '/c':
        continue
    if a[:3] == '/Fo':
        out = a[3:]
        continue
    optstring = optstring + ' ' + a
infile = open(inf, 'rb')
outfile = open(out, 'wb')
outfile.write(optstring + "\n")
for l in infile.readlines():
    if l[:3] != '#as':
        outfile.write(l)
sys.exit(0)
""")

else:

    o = ' -x'

    o_c = ' -x -c'

    test.write('mylink.py', r"""
import getopt
import sys
opts, args = getopt.getopt(sys.argv[1:], 'o:')
for opt, arg in opts:
    if opt == '-o': out = arg
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:5] != '#link':
        outfile.write(l)
sys.exit(0)
""")

    test.write('myas.py', r"""
import getopt
import sys
opts, args = getopt.getopt(sys.argv[1:], 'co:x')
optstring = ''
for opt, arg in opts:
    if opt == '-o': out = arg
    else: optstring = optstring + ' ' + opt
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
outfile.write(optstring + "\n")
for l in infile.readlines():
    if l[:3] != '#as':
        outfile.write(l)
sys.exit(0)
""")



test.write('SConstruct', """
env = Environment(LINK = r'%(_python_)s mylink.py',
                  LINKFLAGS = [],
                  ASPP = r'%(_python_)s myas.py', ASPPFLAGS = '-x',
                  CC = r'%(_python_)s myas.py')
env.Program(target = 'test1', source = 'test1.spp')
env.Program(target = 'test2', source = 'test2.SPP')
""" % locals())

test.write('test1.spp', r"""This is a .spp file.
#as
#link
""")

test.write('test2.SPP', r"""This is a .SPP file.
#as
#link
""")

test.run(arguments = '.', stderr = None)

test.must_match('test1' + _exe, "%s\nThis is a .spp file.\n" % o_c)
test.must_match('test2' + _exe, "%s\nThis is a .SPP file.\n" % o_c)

test.pass_test()
