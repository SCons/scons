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

"""
Testing the gnu tool chain, i.e. the tools 'gcc', 'g++' and 'gnulink'.
"""

import TestSCons
import string
import sys
_python_ = TestSCons._python_
_exe = TestSCons._exe
_dll = TestSCons._dll
dll_ = TestSCons.dll_
test = TestSCons.TestSCons()

test.subdir('gnutools')

test.write(['gnutools','mygcc.py'], """
import getopt
import sys
cmd_opts, args = getopt.getopt(sys.argv[1:], 'f:s:co:', [])
output = None
opt_string = ''
for opt, arg in cmd_opts:
    if opt == '-o': output = open(arg, 'wb')
    else: opt_string = opt_string + ' ' + opt + arg
output.write('gcc ' + opt_string + '\\n')
for a in args:
    contents = open(a, 'rb').read()
    output.write(contents)
output.close()
sys.exit(0)
""")

test.write(['gnutools','myg++.py'], """
import getopt
import sys
cmd_opts, args = getopt.getopt(sys.argv[1:], 'f:s:co:', [])
output = None
opt_string = ''
for opt, arg in cmd_opts:
    if opt == '-o': output = open(arg, 'wb')
    else: opt_string = opt_string + ' ' + opt + arg
output.write('g++ ' + opt_string + '\\n')
for a in args:
    contents = open(a, 'rb').read()
    output.write(contents)
output.close()
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

def testObject(test, obj, command, flags):
    contents = test.read(test.workpath('work1', obj))
    line1 = string.split(contents,'\n')[0]
    items = string.split(line1, ' ')
    cmd = ''
    for i in items:
        if i != '':
            if cmd:
                cmd = cmd + ' ' + i
            else:
                cmd = i
    res = ((flags and (cmd == command + ' ' + flags)) or
           (not flags and (cmd == command)))
    if not res: print "'"+obj+command+flags+"'"+"!='"+str(line1)+"'"
    return res

if sys.platform == 'cygwin':
    fpic = ''
else:
    fpic = ' -fPIC'

test.fail_test(not testObject(test, 'cfile1.o', 'gcc', '-c') or
               not testObject(test, 'cfile2.o', 'gcc', '-c') or
               not testObject(test, 'cppfile1.o', 'g++', '-c') or
               not testObject(test, 'cppfile2.o', 'g++', '-c') or
               not testObject(test, 'cfile1.os', 'gcc', '-c' + fpic) or
               not testObject(test, 'cfile2.os', 'gcc', '-c' + fpic) or
               not testObject(test, 'cppfile1.os', 'g++', '-c' + fpic) or
               not testObject(test, 'cppfile2.os', 'g++', '-c' + fpic) or
               not testObject(test, 'c-only' + _exe, 'gcc', '') or
               not testObject(test, 'cpp-only' + _exe, 'g++', '') or
               not testObject(test, 'c-and-cpp' + _exe, 'g++', '') or
               not testObject(test, dll_ + 'c-only' + _dll, 'gcc', '-shared') or
               not testObject(test, dll_ + 'cpp-only' + _dll, 'g++', '-shared') or
               not testObject(test, dll_ + 'c-and-cpp' + _dll, 'g++', '-shared'))

test.pass_test()
