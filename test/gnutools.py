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

"""
Testing the gnu tool chain, i.e. the tools 'gcc', 'g++' and 'gnulink'.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import sys

_python_ = TestSCons._python_
_exe = TestSCons._exe

def dll(s):
    return TestSCons.dll_ + s + TestSCons._dll

test = TestSCons.TestSCons()

test.subdir('gnutools')

test.write(['gnutools','mygcc.py'], """
import getopt
import sys
try:
    cmd_opts, args = getopt.getopt(sys.argv[1:], 'f:s:co:', [])
except getopt.GetoptError:
    # we may be called with --version, just quit if so
    sys.exit(0)
out = None
opt_string = ''
for opt, arg in cmd_opts:
    if opt == '-o': out = arg
    else: opt_string = opt_string + ' ' + opt + arg
with open(out, 'w') as ofp:
    ofp.write('gcc ' + opt_string + '\\n')
    for a in args:
        with open(a, 'r') as ifp:
            ofp.write(ifp.read())
sys.exit(0)
""")

test.write(['gnutools','myg++.py'], """
import getopt
import sys
try:
    cmd_opts, args = getopt.getopt(sys.argv[1:], 'f:s:co:', [])
except getopt.GetoptError:
    # we may be called with --version, just quit if so
    sys.exit(0)
out = None
opt_string = ''
for opt, arg in cmd_opts:
    if opt == '-o': out = arg
    else: opt_string = opt_string + ' ' + opt + arg
with open(out, 'w') as ofp:
    ofp.write('g++ ' + opt_string + '\\n')
    for a in args:
        with open(a, 'r') as ifp:
            ofp.write(ifp.read())
sys.exit(0)
""")

test.subdir('work1')

test.write(['work1', 'cfile1.c'],"""
/* c file 1 */
""")

test.write(['work1', 'cfile2.c'],"""
/* c file 2 */
""")

test.write(['work1', 'cppfile1.cpp'],"""
/* cpp file 1 */
""")

test.write(['work1', 'cppfile2.cpp'],"""
/* cpp file 2 */
""")

mygcc_py = test.workpath('gnutools','mygcc.py')
mygxx_py = test.workpath('gnutools','myg++.py')

test.write(['work1', 'SConstruct'],"""
env = Environment(tools=['gcc','g++','gnulink'],
                  CC=r'%(_python_)s %(mygcc_py)s',
                  CXX=r'%(_python_)s %(mygxx_py)s',
                  OBJSUFFIX='.o',
                  SHOBJSUFFIX='.os')
env.Program('c-only', Split('cfile1.c cfile2.c'))
env.Program('cpp-only', Split('cppfile1.cpp cppfile2.cpp'))
env.Program('c-and-cpp', Split('cfile1.c cppfile1.cpp'))

env.SharedLibrary('c-only', Split('cfile1.c cfile2.c'))
env.SharedLibrary('cpp-only', Split('cppfile1.cpp cppfile2.cpp'))
env.SharedLibrary('c-and-cpp', Split('cfile1.c cppfile1.cpp'))
""" % locals())

test.run(chdir='work1')

def testObject(test, obj, expect):
    contents = test.read(test.workpath('work1', obj))
    line1 = contents.split(b'\n')[0]
    actual = b' '.join(line1.split())
    if not expect == actual:
        print("%s:  %s != %s\n" % (obj, repr(expect), repr(actual)))
        test.fail_test()

if sys.platform in ('win32', 'cygwin'):
    c_fpic = b''
else:
    c_fpic = b' -fPIC'

testObject(test, 'cfile1.o',            b'gcc -c')
testObject(test, 'cfile2.o',            b'gcc -c')
testObject(test, 'cppfile1.o',          b'g++ -c')
testObject(test, 'cppfile2.o',          b'g++ -c')
testObject(test, 'cfile1.os',           b'gcc -c' + c_fpic)
testObject(test, 'cfile2.os',           b'gcc -c' + c_fpic)
testObject(test, 'cppfile1.os',         b'g++ -c' + c_fpic)
testObject(test, 'cppfile2.os',         b'g++ -c' + c_fpic)
testObject(test, 'c-only' + _exe,       b'gcc')
testObject(test, 'cpp-only' + _exe,     b'g++')
testObject(test, 'c-and-cpp' + _exe,    b'g++')
testObject(test, dll('c-only'),         b'gcc -shared')
testObject(test, dll('cpp-only'),       b'g++ -shared')
testObject(test, dll('c-and-cpp'),      b'g++ -shared')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
