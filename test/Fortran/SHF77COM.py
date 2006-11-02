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
_obj   = TestSCons._shobj

test = TestSCons.TestSCons()



test.write('myfortran.py', r"""
import sys
comment = '#' + sys.argv[1]
outfile = open(sys.argv[2], 'wb')
infile = open(sys.argv[3], 'rb')
for l in infile.readlines():
    if l[:len(comment)] != comment:
        outfile.write(l)
sys.exit(0)
""")



test.write('SConstruct', """
env = Environment(SHF77COM = r'%(_python_)s myfortran.py f77 $TARGET $SOURCES',
                  SHF77PPCOM = r'%(_python_)s myfortran.py f77pp $TARGET $SOURCES',
                  SHFORTRANCOM = r'%(_python_)s myfortran.py fortran $TARGET $SOURCES',
                  SHFORTRANPPCOM = r'%(_python_)s myfortran.py fortranpp $TARGET $SOURCES')
env.SharedObject(target = 'test01', source = 'test01.f')
env.SharedObject(target = 'test02', source = 'test02.F')
env.SharedObject(target = 'test03', source = 'test03.for')
env.SharedObject(target = 'test04', source = 'test04.FOR')
env.SharedObject(target = 'test05', source = 'test05.ftn')
env.SharedObject(target = 'test06', source = 'test06.FTN')
env.SharedObject(target = 'test07', source = 'test07.fpp')
env.SharedObject(target = 'test08', source = 'test08.FPP')
env.SharedObject(target = 'test09', source = 'test09.f77')
env.SharedObject(target = 'test10', source = 'test10.F77')
env.SharedObject(target = 'test11', source = 'test11.f90')
env.SharedObject(target = 'test12', source = 'test12.F90')
env.SharedObject(target = 'test13', source = 'test13.f95')
env.SharedObject(target = 'test14', source = 'test14.F95')
env2 = Environment(SHF77COM = r'%(_python_)s myfortran.py f77 $TARGET $SOURCES',
                   SHF77PPCOM = r'%(_python_)s myfortran.py f77pp $TARGET $SOURCES')
env2.SharedObject(target = 'test21', source = 'test21.f')
env2.SharedObject(target = 'test22', source = 'test22.F')
env2.SharedObject(target = 'test23', source = 'test23.for')
env2.SharedObject(target = 'test24', source = 'test24.FOR')
env2.SharedObject(target = 'test25', source = 'test25.ftn')
env2.SharedObject(target = 'test26', source = 'test26.FTN')
env2.SharedObject(target = 'test27', source = 'test27.fpp')
env2.SharedObject(target = 'test28', source = 'test28.FPP')
env2.SharedObject(target = 'test29', source = 'test29.f77')
env2.SharedObject(target = 'test30', source = 'test30.F77')
""" % locals())

test.write('test01.f',   "This is a .f file.\n#fortran\n")
test.write('test02.F',   "This is a .F file.\n#fortranpp\n")
test.write('test03.for', "This is a .for file.\n#fortran\n")
test.write('test04.FOR', "This is a .FOR file.\n#fortranpp\n")
test.write('test05.ftn', "This is a .ftn file.\n#fortran\n")
test.write('test06.FTN', "This is a .FTN file.\n#fortranpp\n")
test.write('test07.fpp', "This is a .fpp file.\n#fortranpp\n")
test.write('test08.FPP', "This is a .FPP file.\n#fortranpp\n")
test.write('test09.f77', "This is a .f77 file.\n#f77\n")
test.write('test10.F77', "This is a .F77 file.\n#f77pp\n")
test.write('test11.f90', "This is a .f90 file.\n#fortran\n")
test.write('test12.F90', "This is a .F90 file.\n#fortranpp\n")
test.write('test13.f95', "This is a .f95 file.\n#fortran\n")
test.write('test14.F95', "This is a .F95 file.\n#fortranpp\n")

test.write('test21.f',   "This is a .f file.\n#f77\n")
test.write('test22.F',   "This is a .F file.\n#f77pp\n")
test.write('test23.for', "This is a .for file.\n#f77\n")
test.write('test24.FOR', "This is a .FOR file.\n#f77pp\n")
test.write('test25.ftn', "This is a .ftn file.\n#f77\n")
test.write('test26.FTN', "This is a .FTN file.\n#f77pp\n")
test.write('test27.fpp', "This is a .fpp file.\n#f77pp\n")
test.write('test28.FPP', "This is a .FPP file.\n#f77pp\n")
test.write('test29.f77', "This is a .f77 file.\n#f77\n")
test.write('test30.F77', "This is a .F77 file.\n#f77pp\n")

test.run(arguments = '.', stderr = None)

test.must_match('test01' + _obj, "This is a .f file.\n")
test.must_match('test02' + _obj, "This is a .F file.\n")
test.must_match('test03' + _obj, "This is a .for file.\n")
test.must_match('test04' + _obj, "This is a .FOR file.\n")
test.must_match('test05' + _obj, "This is a .ftn file.\n")
test.must_match('test06' + _obj, "This is a .FTN file.\n")
test.must_match('test07' + _obj, "This is a .fpp file.\n")
test.must_match('test08' + _obj, "This is a .FPP file.\n")
test.must_match('test09' + _obj, "This is a .f77 file.\n")
test.must_match('test10' + _obj, "This is a .F77 file.\n")
test.must_match('test11' + _obj, "This is a .f90 file.\n")
test.must_match('test12' + _obj, "This is a .F90 file.\n")
test.must_match('test13' + _obj, "This is a .f95 file.\n")
test.must_match('test14' + _obj, "This is a .F95 file.\n")

test.must_match('test21' + _obj, "This is a .f file.\n")
test.must_match('test22' + _obj, "This is a .F file.\n")
test.must_match('test23' + _obj, "This is a .for file.\n")
test.must_match('test24' + _obj, "This is a .FOR file.\n")
test.must_match('test25' + _obj, "This is a .ftn file.\n")
test.must_match('test26' + _obj, "This is a .FTN file.\n")
test.must_match('test27' + _obj, "This is a .fpp file.\n")
test.must_match('test28' + _obj, "This is a .FPP file.\n")
test.must_match('test29' + _obj, "This is a .f77 file.\n")
test.must_match('test30' + _obj, "This is a .F77 file.\n")

test.pass_test()
