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

python = TestSCons.python

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
env = Environment(LINK = r'%s mylink.py',
                  LINKFLAGS = [],
                  AS = r'%s myas.py', ASFLAGS = '-x',
                  CC = r'%s myas.py')
env.Program(target = 'test1', source = 'test1.s')
env.Program(target = 'test2', source = 'test2.S')
env.Program(target = 'test3', source = 'test3.asm')
env.Program(target = 'test4', source = 'test4.ASM')
env.Program(target = 'test5', source = 'test5.spp')
env.Program(target = 'test6', source = 'test6.SPP')
""" % (python, python, python))

test.write('test1.s', r"""This is a .s file.
#as
#link
""")

test.write('test2.S', r"""This is a .S file.
#as
#link
""")

test.write('test3.asm', r"""This is a .asm file.
#as
#link
""")

test.write('test4.ASM', r"""This is a .ASM file.
#as
#link
""")

test.write('test5.spp', r"""This is a .spp file.
#as
#link
""")

test.write('test6.SPP', r"""This is a .SPP file.
#as
#link
""")

test.run(arguments = '.', stderr = None)

test.fail_test(test.read('test1' + _exe) != "%s\nThis is a .s file.\n" % o)

test.fail_test(test.read('test2' + _exe) != "%s\nThis is a .S file.\n" % o_c)

test.fail_test(test.read('test3' + _exe) != "%s\nThis is a .asm file.\n" % o)

test.fail_test(test.read('test4' + _exe) != "%s\nThis is a .ASM file.\n" % o)

test.fail_test(test.read('test5' + _exe) != "%s\nThis is a .spp file.\n" % o_c)

test.fail_test(test.read('test6' + _exe) != "%s\nThis is a .SPP file.\n" % o_c)



test.pass_test()
