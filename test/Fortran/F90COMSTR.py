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
    f90pp = 'f90'
else:
    f90pp = 'f90pp'


test.write('SConstruct', """
env = Environment(F90COM = r'%(python)s myfc.py f90 $TARGET $SOURCES',
                  F90COMSTR = 'Building f90 $TARGET from $SOURCES',
                  F90PPCOM = r'%(python)s myfc.py f90pp $TARGET $SOURCES',
                  F90PPCOMSTR = 'Building f90pp $TARGET from $SOURCES',
                  OBJSUFFIX='.obj')
env.Object(source = 'test01.f90')
env.Object(source = 'test02.F90')
""" % locals())

test.write('test01.f90',        "A .f90 file.\n#f90\n")
test.write('test02.F90',        "A .F90 file.\n#%s\n" % f90pp)

test.run(stdout = test.wrap_stdout("""\
Building f90 test01.obj from test01.f90
Building %(f90pp)s test02.obj from test02.F90
""" % locals()))

test.must_match('test01.obj', "A .f90 file.\n")
test.must_match('test02.obj', "A .F90 file.\n")

test.pass_test()
