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



test.write('myfc.py', r"""
import sys
fline = '#'+sys.argv[1]+'\n'
outfile = open(sys.argv[2], 'wb')
infile = open(sys.argv[3], 'rb')
for l in filter(lambda l, fl=fline: l != fl, infile.readlines()):
    outfile.write(l)
sys.exit(0)
""")

if os.path.normcase('.f') == os.path.normcase('.F'):
    fortranpp = 'fortran'
else:
    fortranpp = 'fortranpp'


test.write('SConstruct', """
env = Environment(FORTRANCOM = r'%(python)s myfc.py fortran $TARGET $SOURCES',
                  FORTRANCOMSTR = 'Building fortran $TARGET from $SOURCES',
                  FORTRANPPCOM = r'%(python)s myfc.py fortranpp $TARGET $SOURCES',
                  FORTRANPPCOMSTR = 'Building fortranpp $TARGET from $SOURCES',
                  OBJSUFFIX='.obj')
env.Object(source = 'test01.f')
env.Object(source = 'test02.F')
env.Object(source = 'test03.for')
env.Object(source = 'test04.FOR')
env.Object(source = 'test05.ftn')
env.Object(source = 'test06.FTN')
env.Object(source = 'test07.fpp')
env.Object(source = 'test08.FPP')
env.Object(source = 'test09.f77')
env.Object(source = 'test10.F77')
env.Object(source = 'test11.f90')
env.Object(source = 'test12.F90')
env.Object(source = 'test13.f95')
env.Object(source = 'test14.F95')
""" % locals())

test.write('test01.f',          "A .f file.\n#fortran\n")
test.write('test02.F',          "A .F file.\n#%s\n" % fortranpp)
test.write('test03.for',        "A .for file.\n#fortran\n")
test.write('test04.FOR',        "A .FOR file.\n#%s\n" % fortranpp)
test.write('test05.ftn',        "A .ftn file.\n#fortran\n")
test.write('test06.FTN',        "A .FTN file.\n#%s\n" % fortranpp)
test.write('test07.fpp',        "A .fpp file.\n#fortranpp\n")
test.write('test08.FPP',        "A .FPP file.\n#fortranpp\n")
test.write('test09.f77',        "A .f77 file.\n#fortran\n")
test.write('test10.F77',        "A .F77 file.\n#%s\n" % fortranpp)
test.write('test11.f90',        "A .f90 file.\n#fortran\n")
test.write('test12.F90',        "A .F90 file.\n#%s\n" % fortranpp)
test.write('test13.f95',        "A .f95 file.\n#fortran\n")
test.write('test14.F95',        "A .F95 file.\n#%s\n" % fortranpp)

test.run(stdout = test.wrap_stdout("""\
Building fortran test01.obj from test01.f
Building %(fortranpp)s test02.obj from test02.F
Building fortran test03.obj from test03.for
Building %(fortranpp)s test04.obj from test04.FOR
Building fortran test05.obj from test05.ftn
Building %(fortranpp)s test06.obj from test06.FTN
Building fortranpp test07.obj from test07.fpp
Building fortranpp test08.obj from test08.FPP
Building fortran test09.obj from test09.f77
Building %(fortranpp)s test10.obj from test10.F77
Building fortran test11.obj from test11.f90
Building %(fortranpp)s test12.obj from test12.F90
Building fortran test13.obj from test13.f95
Building %(fortranpp)s test14.obj from test14.F95
""" % locals()))

test.must_match('test01.obj', "A .f file.\n")
test.must_match('test02.obj', "A .F file.\n")
test.must_match('test03.obj', "A .for file.\n")
test.must_match('test04.obj', "A .FOR file.\n")
test.must_match('test05.obj', "A .ftn file.\n")
test.must_match('test06.obj', "A .FTN file.\n")
test.must_match('test07.obj', "A .fpp file.\n")
test.must_match('test08.obj', "A .FPP file.\n")
test.must_match('test09.obj', "A .f77 file.\n")
test.must_match('test10.obj', "A .F77 file.\n")
test.must_match('test11.obj', "A .f90 file.\n")
test.must_match('test12.obj', "A .F90 file.\n")
test.must_match('test13.obj', "A .f95 file.\n")
test.must_match('test14.obj', "A .F95 file.\n")

test.pass_test()
