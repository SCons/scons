#!/usr/bin/env python
#
# Copyright (c) 2001, 2002, 2003 Steven Knight
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

__revision__ = "/home/scons/scons/branch.0/baseline/test/sconsign.py 0.90.D001 2003/06/25 15:32:24 knight"

import os.path
import string

import TestCmd
import TestSCons

test = TestSCons.TestSCons(match = TestCmd.match_re)

test.subdir('sub1', 'sub2')

test.write('SConstruct', """
env1 = Environment(PROGSUFFIX = '.exe', OBJSUFFIX = '.obj')
env1.Program('sub1/hello.c')
env2 = env1.Copy(CPPPATH = ['sub2'])
env2.Program('sub2/hello.c')
""")

test.write(['sub1', 'hello.c'], r"""\
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("sub1/hello.c\n");
	exit (0);
}
""")

test.write(['sub2', 'hello.c'], r"""\
#include <inc1.h>
#include <inc2.h>
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("sub2/goodbye.c\n");
	exit (0);
}
""")

test.write(['sub2', 'inc1.h'], r"""\
#define STRING1 "inc1.h"
""")

test.write(['sub2', 'inc2.h'], r"""\
#define STRING2 "inc2.h"
""")

test.run(arguments = '--implicit-cache .')

test.run(interpreter = TestSCons.python,
         program = "sconsign",
         arguments = "sub1/.sconsign",
         stdout = """\
hello.exe: - \S+ -
hello.obj: - \S+ -
""")

test.run(interpreter = TestSCons.python,
         program = "sconsign",
         arguments = "-v sub1/.sconsign",
         stdout = """\
hello.exe:
    timestamp: -
    bsig: \S+
    csig: -
hello.obj:
    timestamp: -
    bsig: \S+
    csig: -
""")

test.run(interpreter = TestSCons.python,
         program = "sconsign",
         arguments = "-b -v sub1/.sconsign",
         stdout = """\
hello.exe:
    bsig: \S+
hello.obj:
    bsig: \S+
""")

test.run(interpreter = TestSCons.python,
         program = "sconsign",
         arguments = "-c -v sub1/.sconsign",
         stdout = """\
hello.exe:
    csig: -
hello.obj:
    csig: -
""")

test.run(interpreter = TestSCons.python,
         program = "sconsign",
         arguments = "-e hello.obj sub1/.sconsign",
         stdout = """\
hello.obj: - \S+ -
""")

test.run(interpreter = TestSCons.python,
         program = "sconsign",
         arguments = "-e hello.obj -e hello.exe -e hello.obj sub1/.sconsign",
         stdout = """\
hello.obj: - \S+ -
hello.exe: - \S+ -
hello.obj: - \S+ -
""")

test.run(interpreter = TestSCons.python,
         program = "sconsign",
         arguments = "sub2/.sconsign",
         stdout = """\
hello.exe: - \S+ -
hello.obj: - \S+ -
        %s
        %s
""" % (string.replace(os.path.join('sub2', 'inc1.h'), '\\', '\\\\'),
       string.replace(os.path.join('sub2', 'inc2.h'), '\\', '\\\\')))

test.run(interpreter = TestSCons.python,
         program = "sconsign",
         arguments = "-i -v sub2/.sconsign",
         stdout = """\
hello.exe:
hello.obj:
    implicit:
        %s
        %s
""" % (string.replace(os.path.join('sub2', 'inc1.h'), '\\', '\\\\'),
       string.replace(os.path.join('sub2', 'inc2.h'), '\\', '\\\\')))

test.pass_test()

test.run(interpreter = TestSCons.python,
         program = "sconsign",
         arguments = "-e hello.obj sub2/.sconsign sub1/.sconsign",
         stdout = """\
hello.obj: - \S+ -
        %s
        %s
hello.obj: - \S+ -
""" % (string.replace(os.path.join('sub2', 'inc1.h'), '\\', '\\\\'),
       string.replace(os.path.join('sub2', 'inc2.h'), '\\', '\\\\')))

test.pass_test()
