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
_exe   = TestSCons._exe

test = TestSCons.TestSCons()



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
    if l[:8] != '/*link*/':
        outfile.write(l)
sys.exit(0)
""")

    test.write('mycc.py', r"""
import sys
args = sys.argv[1:]
inf = None
while args:
    a = args[0]
    args = args[1:]
    if a[0] != '/':
        if not inf:
            inf = a
        continue
    if a[:3] == '/Fo': out = a[3:]
infile = open(inf, 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:6] != '/*cc*/':
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
    if l[:8] != '/*link*/':
        outfile.write(l)
sys.exit(0)
""")

    test.write('mycc.py', r"""
import getopt
import sys
opts, args = getopt.getopt(sys.argv[1:], 'co:')
for opt, arg in opts:
    if opt == '-o': out = arg
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:6] != '/*cc*/':
        outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
cc = Environment().Dictionary('CC')
env = Environment(LINK = r'%(_python_)s mylink.py',
                  LINKFLAGS = [],
                  CC = r'%(_python_)s mycc.py',
                  CXX = cc,
                  CXXFLAGS = [])
env.Program(target = 'test1', source = 'test1.c')
""" % locals())

test.write('test1.c', r"""This is a .c file.
/*cc*/
/*link*/
""")

test.run(arguments = '.', stderr = None)

test.fail_test(test.read('test1' + _exe) != "This is a .c file.\n")

if os.path.normcase('.c') == os.path.normcase('.C'):

    test.write('SConstruct', """
cc = Environment().Dictionary('CC')
env = Environment(LINK = r'%(_python_)s mylink.py',
                  CC = r'%(_python_)s mycc.py',
                  CXX = cc)
env.Program(target = 'test2', source = 'test2.C')
""" % locals())

    test.write('test2.C', r"""This is a .C file.
/*cc*/
/*link*/
""")

    test.run(arguments = '.', stderr = None)

    test.fail_test(test.read('test2' + _exe) != "This is a .C file.\n")




test.write("wrapper.py",
"""import os
import string
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

test.write('SConstruct', """
foo = Environment()
cc = foo.Dictionary('CC')
bar = Environment(CC = r'%(_python_)s wrapper.py ' + cc)
foo.Program(target = 'foo', source = 'foo.c')
bar.Program(target = 'bar', source = 'bar.c')
""" % locals())

test.write('foo.c', r"""
#include <stdio.h>
#include <stdlib.h>

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("foo.c\n");
        exit (0);
}
""")

test.write('bar.c', r"""
#include <stdio.h>
#include <stdlib.h>

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("foo.c\n");
        exit (0);
}
""")


test.run(arguments = 'foo' + _exe)

test.fail_test(os.path.exists(test.workpath('wrapper.out')))

test.up_to_date(arguments = 'foo' + _exe)

test.run(arguments = 'bar' + _exe)

test.fail_test(test.read('wrapper.out') != "wrapper.py\n")

test.up_to_date(arguments = 'bar' + _exe)

test.pass_test()
