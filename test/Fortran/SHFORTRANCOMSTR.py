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
env = Environment(SHFORTRANCOM = r'%(_python_)s myfc.py fortran $TARGET $SOURCES',
                  SHFORTRANCOMSTR = 'Building fortran $TARGET from $SOURCES',
                  SHFORTRANPPCOM = r'%(_python_)s myfc.py fortranpp $TARGET $SOURCES',
                  SHFORTRANPPCOMSTR = 'Building fortranpp $TARGET from $SOURCES',
                  SHOBJPREFIX='', SHOBJSUFFIX='.shobj')
env.SharedObject(source = 'test01.f')
env.SharedObject(source = 'test02.F')
env.SharedObject(source = 'test03.for')
env.SharedObject(source = 'test04.FOR')
env.SharedObject(source = 'test05.ftn')
env.SharedObject(source = 'test06.FTN')
env.SharedObject(source = 'test07.fpp')
env.SharedObject(source = 'test08.FPP')
env.SharedObject(source = 'test09.f77')
env.SharedObject(source = 'test10.F77')
env.SharedObject(source = 'test11.f90')
env.SharedObject(source = 'test12.F90')
env.SharedObject(source = 'test13.f95')
env.SharedObject(source = 'test14.F95')
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
Building fortran test01.shobj from test01.f
Building %(fortranpp)s test02.shobj from test02.F
Building fortran test03.shobj from test03.for
Building %(fortranpp)s test04.shobj from test04.FOR
Building fortran test05.shobj from test05.ftn
Building %(fortranpp)s test06.shobj from test06.FTN
Building fortranpp test07.shobj from test07.fpp
Building fortranpp test08.shobj from test08.FPP
Building fortran test09.shobj from test09.f77
Building %(fortranpp)s test10.shobj from test10.F77
Building fortran test11.shobj from test11.f90
Building %(fortranpp)s test12.shobj from test12.F90
Building fortran test13.shobj from test13.f95
Building %(fortranpp)s test14.shobj from test14.F95
""" % locals()))

test.must_match('test01.shobj', "A .f file.\n")
test.must_match('test02.shobj', "A .F file.\n")
test.must_match('test03.shobj', "A .for file.\n")
test.must_match('test04.shobj', "A .FOR file.\n")
test.must_match('test05.shobj', "A .ftn file.\n")
test.must_match('test06.shobj', "A .FTN file.\n")
test.must_match('test07.shobj', "A .fpp file.\n")
test.must_match('test08.shobj', "A .FPP file.\n")
test.must_match('test09.shobj', "A .f77 file.\n")
test.must_match('test10.shobj', "A .F77 file.\n")
test.must_match('test11.shobj', "A .f90 file.\n")
test.must_match('test12.shobj', "A .F90 file.\n")
test.must_match('test13.shobj', "A .f95 file.\n")
test.must_match('test14.shobj', "A .F95 file.\n")

test.pass_test()
