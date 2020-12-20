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
""" Test manipulating FORTRANPPFILESUFFIXES. """

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons



_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()

test.file_fixture('mylink.py')

test.write('myfortran.py', r"""
import getopt
import sys

comment = ('#' + sys.argv[1]).encode()
length = len(comment)
args = sys.argv[2:]
# First parse defines, since getopt won't have it
defines = []
for a in args[:]:
    if a.startswith("-D") or a.startswith("/D"):
        defines.append(a[2:])
        args.remove(a)

opts, args = getopt.getopt(args, 'co:')
for opt, arg in opts:
    if opt == '-o': out = arg
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for d in defines:
    outfile.write(("#define %s\n" % (d,)).encode())
for l in infile.readlines():
    if l[:length] != comment:
        outfile.write(l)
sys.exit(0)
""")

# Test non default file suffix: .f, .f90 and .f95 for FORTRAN
test.write('SConstruct', """
env = Environment(LINK=r'%(_python_)s mylink.py',
                  LINKFLAGS=[],
                  CPPDEFINES=["mosdef"],
                  F77=r'%(_python_)s myfortran.py g77',
                  FORTRAN=r'%(_python_)s myfortran.py fortran',
                  FORTRANPPFILESUFFIXES=['.f', '.fpp'],
                  tools=['default', 'fortran'])
env.Program(target = 'test01', source = 'test01.f')
env.Program(target = 'test02', source = 'test02.fpp')
""" % locals())

test.write('test01.f',   "This is a .f file.\n#link\n#fortran\n")
test.write('test02.fpp',   "This is a .fpp file.\n#link\n#fortran\n")

test.run(arguments='.', stderr=None)

test.must_match('test01' + _exe, "#define mosdef\nThis is a .f file.\n")
test.must_match('test02' + _exe, "#define mosdef\nThis is a .fpp file.\n")

test.pass_test()
