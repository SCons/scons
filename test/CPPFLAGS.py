#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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

if sys.platform == 'win32':
    _exe = '.exe'
    _obj = '.obj'
else:
    _exe = ''
    _obj = '.o'

test = TestSCons.TestSCons()

# Writing this to accomodate both our in-line tool chain and the
# MSVC command lines is too hard, and will be completely unnecessary
# some day when we separate our tests.  Punt for now.
test.no_result(sys.platform == 'win32')



if sys.platform == 'win32':

    test.write('mylink.py', r"""
import getopt
import os
import sys
args = sys.argv[1:]
while args:
    a = args[0]
    if a[0] != '/':
        break
    args.pop(0)
    if a[:5] == '/OUT:': out = a[5:]
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:5] != '#link':
	outfile.write(l)
sys.exit(0)
""")

else:

    test.write('mylink.py', r"""
import getopt
import os
import sys
opts, args = getopt.getopt(sys.argv[1:], 'o:s:')
for opt, arg in opts:
    if opt == '-o': out = arg
outfile = open(out, 'wb')
for f in args:
    infile = open(f, 'rb')
    for l in infile.readlines():
        if l[:5] != '#link':
            outfile.write(l)
sys.exit(0)
""")

test.write('mygcc.py', r"""
import getopt
import os
import sys
compiler = sys.argv[1]
clen = len(compiler) + 1
opts, args = getopt.getopt(sys.argv[2:], 'co:xf:')
for opt, arg in opts:
    if opt == '-o': out = arg
    elif opt == '-x': open('mygcc.out', 'ab').write(compiler + "\n")
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:clen] != '#' + compiler:
	outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(CPPFLAGS = '-x',
                  LINK = r'%s mylink.py',
                  CC = r'%s mygcc.py cc',
                  CXX = r'%s mygcc.py c++',
                  F77 = r'%s mygcc.py g77')
env.Program(target = 'foo', source = Split('test1.c test2.cpp test3.F'))
""" % (python, python, python, python))

test.write('test1.c', r"""test1.c
#cc
#link
""")

test.write('test2.cpp', r"""test2.cpp
#c++
#link
""")

test.write('test3.F', r"""test3.F
#g77
#link
""")

test.run(arguments = '.', stderr = None)

test.fail_test(test.read('test1' + _obj) != "test1.c\n#link\n")

test.fail_test(test.read('test2' + _obj) != "test2.cpp\n#link\n")

test.fail_test(test.read('test3' + _obj) != "test3.F\n#link\n")

test.fail_test(test.read('foo' + _exe) != "test1.c\ntest2.cpp\ntest3.F\n")

test.fail_test(test.read('mygcc.out') != "cc\nc++\ng77\n")

test.write('SConstruct', """
env = Environment(CPPFLAGS = '-x',
                  SHLINK = r'%s mylink.py',
                  CC = r'%s mygcc.py cc',
                  CXX = r'%s mygcc.py c++',
                  F77 = r'%s mygcc.py g77')
env.SharedLibrary(target = File('foo.bar'),
                  source = Split('test1.c test2.cpp test3.F'))
""" % (python, python, python, python))

test.write('test1.c', r"""test1.c
#cc
#link
""")

test.write('test2.cpp', r"""test2.cpp
#c++
#link
""")

test.write('test3.F', r"""test3.F
#g77
#link
""")

test.unlink('mygcc.out')

test.run(arguments = '.', stderr = None)

test.fail_test(test.read('test1' + _obj) != "test1.c\n#link\n")

test.fail_test(test.read('test2' + _obj) != "test2.cpp\n#link\n")

test.fail_test(test.read('test3' + _obj) != "test3.F\n#link\n")

test.fail_test(test.read('foo.bar') != "test1.c\ntest2.cpp\ntest3.F\n")

test.fail_test(test.read('mygcc.out') != "cc\nc++\ng77\n")

test.pass_test()
