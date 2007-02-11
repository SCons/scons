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
Verify that the swig tool generates file names that we expect.
"""

import os
import string
import sys
import TestSCons

if sys.platform =='darwin':
    # change to make it work with stock OS X python framework
    # we can't link to static libpython because there isn't one on OS X
    # so we link to a framework version. However, testing must also
    # use the same version, or else you get interpreter errors.
    python = "/System/Library/Frameworks/Python.framework/Versions/Current/bin/python"
    _python_ = '"' + python + '"'
else:
    _python_ = TestSCons._python_
    
_exe   = TestSCons._exe
_obj   = TestSCons._obj

test = TestSCons.TestSCons()



test.write('myswig.py', r"""
import getopt
import sys
opts, args = getopt.getopt(sys.argv[1:], 'c:o:')
for opt, arg in opts:
    if opt == '-c': pass
    elif opt == '-o': out = arg
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:4] != 'swig':
        outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(tools=['default', 'swig'], SWIG = r'%(_python_)s myswig.py')
env.Program(target = 'test1', source = 'test1.i')
env.CFile(target = 'test2', source = 'test2.i')
env.Clone(SWIGFLAGS = '-c++').Program(target = 'test3', source = 'test3.i')
""" % locals())

test.write('test1.i', r"""
int
main(int argc, char *argv[]) {
        argv[argc++] = "--";
        printf("test1.i\n");
        exit (0);
}
swig
""")

test.write('test2.i', r"""test2.i
swig
""")

test.write('test3.i', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[]) {
        argv[argc++] = "--";
        printf("test3.i\n");
        exit (0);
}
swig
""")

test.run(arguments = '.', stderr = None)

test.run(program = test.workpath('test1' + _exe), stdout = "test1.i\n")
test.must_exist(test.workpath('test1_wrap.c'))
test.must_exist(test.workpath('test1_wrap' + _obj))

test.must_match('test2_wrap.c', "test2.i\n")

test.run(program = test.workpath('test3' + _exe), stdout = "test3.i\n")
test.must_exist(test.workpath('test3_wrap.cc'))
test.must_exist(test.workpath('test3_wrap' + _obj))

test.pass_test()
