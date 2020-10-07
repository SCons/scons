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

import sys
import TestSCons

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()



if sys.platform == 'win32':

    test.write('mylink.py', r"""
import sys
args = sys.argv[1:]
while args:
    a = args[0]
    if a == '-o':
        out = args[1]
        args = args[2:]
        continue
    if not a[0] in '/-':
        break
    args = args[1:]
    if a[:5].lower() == '/out:': out = a[5:]
infile = open(args[0], 'r')
outfile = open(out, 'w')
for l in infile.readlines():
    if l[:8] != '/*link*/':
        outfile.write(l)
sys.exit(0)
""")

    test.write('myc++.py', r"""
import sys
args = sys.argv[1:]
inf = None
while args:
    a = args[0]
    if a == '-o':
        out = args[1]
        args = args[2:]
        continue
    args = args[1:]
    if not a[0] in '/-':
        if not inf:
            inf = a
        continue
    if a[:3] == '/Fo': out = a[3:]
infile = open(inf, 'r')
outfile = open(out, 'w')
for l in infile.readlines():
    if l[:7] != '/*c++*/':
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
infile = open(args[0], 'r')
outfile = open(out, 'w')
for l in infile.readlines():
    if l[:8] != '/*link*/':
        outfile.write(l)
sys.exit(0)
""")

    test.write('myc++.py', r"""
import getopt
import sys
opts, args = getopt.getopt(sys.argv[1:], 'co:')
for opt, arg in opts:
    if opt == '-o': out = arg
infile = open(args[0], 'r')
outfile = open(out, 'w')
for l in infile.readlines():
    if l[:7] != '/*c++*/':
        outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(LINK = r'%(_python_)s mylink.py',
                  LINKFLAGS = [],
                  CXX = r'%(_python_)s myc++.py',
                  CXXFLAGS = [])
env.Program(target = 'test1', source = 'test1.cc')
env.Program(target = 'test2', source = 'test2.cpp')
env.Program(target = 'test3', source = 'test3.cxx')
env.Program(target = 'test4', source = 'test4.c++')
env.Program(target = 'test5', source = 'test5.C++')
""" % locals())

test.write('test1.cc', r"""This is a .cc file.
/*c++*/
/*link*/
""")

test.write('test2.cpp', r"""This is a .cpp file.
/*c++*/
/*link*/
""")

test.write('test3.cxx', r"""This is a .cxx file.
/*c++*/
/*link*/
""")

test.write('test4.c++', r"""This is a .c++ file.
/*c++*/
/*link*/
""")

test.write('test5.C++', r"""This is a .C++ file.
/*c++*/
/*link*/
""")

test.run(arguments = '.', stderr = None)

test.must_match('test1' + _exe, "This is a .cc file.\n", mode='r')

test.must_match('test2' + _exe, "This is a .cpp file.\n", mode='r')

test.must_match('test3' + _exe, "This is a .cxx file.\n", mode='r')

test.must_match('test4' + _exe, "This is a .c++ file.\n", mode='r')

test.must_match('test5' + _exe, "This is a .C++ file.\n", mode='r')

if TestSCons.case_sensitive_suffixes('.c', '.C'):

    test.write('SConstruct', """
env = Environment(LINK = r'%(_python_)s mylink.py',
                  LINKFLAGS = [],
                  CXX = r'%(_python_)s myc++.py',
                  CXXFLAGS = [])
env.Program(target = 'test6', source = 'test6.C')
""" % locals())

    test.write('test6.C', r"""This is a .C file.
/*c++*/
/*link*/
""")

    test.run(arguments = '.', stderr = None)

    test.must_match('test6' + _exe, "This is a .C file.\n", mode='r')




test.file_fixture('wrapper.py')

test.write('SConstruct', """
foo = Environment()
cxx = foo.Dictionary('CXX')
bar = Environment(CXX = r'%(_python_)s wrapper.py ' + cxx)
foo.Program(target = 'foo', source = 'foo.cxx')
bar.Program(target = 'bar', source = 'bar.cxx')
""" % locals())

test.write('foo.cxx', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = (char *)"--";
        printf("foo.cxx\n");
        exit (0);
}
""")

test.write('bar.cxx', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = (char *)"--";
        printf("foo.cxx\n");
        exit (0);
}
""")


test.run(arguments = 'foo' + _exe)

test.must_not_exist(test.workpath('wrapper.out'))

test.run(arguments = 'bar' + _exe)

test.must_match('wrapper.out', "wrapper.py\n", mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
