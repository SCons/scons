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

else:

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

test.write('myg77.py', r"""
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
    if l[:4] != '#g77':
	outfile.write(l)
sys.exit(0)
""")



test.write('SConstruct', """
env = Environment(LINK = r'%s mylink.py',
                  LINKFLAGS = [],
                  F77 = r'%s myg77.py',
                  F77FLAGS = '-x')
env.Program(target = 'test01', source = 'test01.f')
env.Program(target = 'test02', source = 'test02.F')
env.Program(target = 'test03', source = 'test03.for')
env.Program(target = 'test04', source = 'test04.FOR')
env.Program(target = 'test05', source = 'test05.ftn')
env.Program(target = 'test06', source = 'test06.FTN')
env.Program(target = 'test07', source = 'test07.fpp')
env.Program(target = 'test08', source = 'test08.FPP')
env.Program(target = 'test09', source = 'test09.f77')
env.Program(target = 'test10', source = 'test10.F77')
""" % (python, python))

test.write('test01.f',   "This is a .f file.\n#link\n#g77\n")
test.write('test02.F',   "This is a .F file.\n#link\n#g77\n")
test.write('test03.for', "This is a .for file.\n#link\n#g77\n")
test.write('test04.FOR', "This is a .FOR file.\n#link\n#g77\n")
test.write('test05.ftn', "This is a .ftn file.\n#link\n#g77\n")
test.write('test06.FTN', "This is a .FTN file.\n#link\n#g77\n")
test.write('test07.fpp', "This is a .fpp file.\n#link\n#g77\n")
test.write('test08.FPP', "This is a .FPP file.\n#link\n#g77\n")
test.write('test09.f77', "This is a .f77 file.\n#link\n#g77\n")
test.write('test10.F77', "This is a .F77 file.\n#link\n#g77\n")

test.run(arguments = '.', stderr = None)

test.must_match('test01' + _exe, " -x -c\nThis is a .f file.\n")
test.must_match('test02' + _exe, " -x -c\nThis is a .F file.\n")
test.must_match('test03' + _exe, " -x -c\nThis is a .for file.\n")
test.must_match('test04' + _exe, " -x -c\nThis is a .FOR file.\n")
test.must_match('test05' + _exe, " -x -c\nThis is a .ftn file.\n")
test.must_match('test06' + _exe, " -x -c\nThis is a .FTN file.\n")
test.must_match('test07' + _exe, " -x -c\nThis is a .fpp file.\n")
test.must_match('test08' + _exe, " -x -c\nThis is a .FPP file.\n")
test.must_match('test09' + _exe, " -x -c\nThis is a .f77 file.\n")
test.must_match('test10' + _exe, " -x -c\nThis is a .F77 file.\n")



g77 = test.detect('F77', 'g77')
FTN_LIB = TestSCons.fortran_lib

if g77:

    test.write("wrapper.py",
"""import os
import string
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """
foo = Environment(LIBS = %s)
f77 = foo.Dictionary('F77')
bar = foo.Copy(F77 = r'%s wrapper.py ' + f77, F77FLAGS = '-Ix')
foo.Program(target = 'foo', source = 'foo.f')
bar.Program(target = 'bar', source = 'bar.f')
""" % (FTN_LIB, python))

    test.write('foo.f', r"""
      PROGRAM FOO
      PRINT *,'foo.f'
      STOP
      END
""")

    test.write('bar.f', r"""
      PROGRAM BAR
      PRINT *,'bar.f'
      STOP
      END
""")


    test.run(arguments = 'foo' + _exe, stderr = None)

    test.run(program = test.workpath('foo'), stdout =  " foo.f\n")

    test.must_not_exist('wrapper.out')

    test.run(arguments = 'bar' + _exe)

    test.run(program = test.workpath('bar'), stdout =  " bar.f\n")

    test.must_match('wrapper.out', "wrapper.py\n")

test.pass_test()
