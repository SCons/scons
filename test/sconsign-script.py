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

# Check for the sconsign script before we instantiate TestSCons(),
# because that will change directory on us.
if os.path.exists('sconsign.py'):
    sconsign = 'sconsign.py'
elif os.path.exists('sconsign'):
    sconsign = 'sconsign'
else:
    print "Can find neither 'sconsign.py' nor 'sconsign' scripts."
    test.no_result(1)

def sort_match(test, lines, expect):
    lines = string.split(lines, '\n')
    lines.sort()
    expect = string.split(expect, '\n')
    expect.sort()
    return test.match_re(lines, expect)

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
         program = sconsign,
         arguments = "sub1/.sconsign",
         stdout = """\
hello.exe: None \S+ None
hello.obj: None \S+ None
""")

test.run(interpreter = TestSCons.python,
         program = sconsign,
         arguments = "-v sub1/.sconsign",
         stdout = """\
hello.exe:
    timestamp: None
    bsig: \S+
    csig: None
hello.obj:
    timestamp: None
    bsig: \S+
    csig: None
""")

test.run(interpreter = TestSCons.python,
         program = sconsign,
         arguments = "-b -v sub1/.sconsign",
         stdout = """\
hello.exe:
    bsig: \S+
hello.obj:
    bsig: \S+
""")

test.run(interpreter = TestSCons.python,
         program = sconsign,
         arguments = "-c -v sub1/.sconsign",
         stdout = """\
hello.exe:
    csig: None
hello.obj:
    csig: None
""")

test.run(interpreter = TestSCons.python,
         program = sconsign,
         arguments = "-e hello.obj sub1/.sconsign",
         stdout = """\
hello.obj: None \S+ None
""")

test.run(interpreter = TestSCons.python,
         program = sconsign,
         arguments = "-e hello.obj -e hello.exe -e hello.obj sub1/.sconsign",
         stdout = """\
hello.obj: None \S+ None
hello.exe: None \S+ None
hello.obj: None \S+ None
""")

test.run(interpreter = TestSCons.python,
         program = sconsign,
         arguments = "sub2/.sconsign",
         stdout = """\
hello.exe: None \S+ None
hello.obj: None \S+ None
        %s
        %s
""" % (string.replace(os.path.join('sub2', 'inc1.h'), '\\', '\\\\'),
       string.replace(os.path.join('sub2', 'inc2.h'), '\\', '\\\\')))

test.run(interpreter = TestSCons.python,
         program = sconsign,
         arguments = "-i -v sub2/.sconsign",
         stdout = """\
hello.exe:
hello.obj:
    implicit:
        %s
        %s
""" % (string.replace(os.path.join('sub2', 'inc1.h'), '\\', '\\\\'),
       string.replace(os.path.join('sub2', 'inc2.h'), '\\', '\\\\')))

test.run(interpreter = TestSCons.python,
         program = sconsign,
         arguments = "-e hello.obj sub2/.sconsign sub1/.sconsign",
         stdout = """\
hello.obj: None \S+ None
        %s
        %s
hello.obj: None \S+ None
""" % (string.replace(os.path.join('sub2', 'inc1.h'), '\\', '\\\\'),
       string.replace(os.path.join('sub2', 'inc2.h'), '\\', '\\\\')))

test.run(arguments = '--clean .')

test.write('SConstruct', """
SourceSignatures('timestamp')
TargetSignatures('content')
env1 = Environment(PROGSUFFIX = '.exe', OBJSUFFIX = '.obj')
env1.Program('sub1/hello.c')
env2 = env1.Copy(CPPPATH = ['sub2'])
env2.Program('sub2/hello.c')
""")

import time
time.sleep(1)

test.run(arguments = '. --max-drift=1')

test.run(interpreter = TestSCons.python,
         program = sconsign,
         arguments = "sub1/.sconsign")

test.fail_test(not sort_match(test, test.stdout(), """\
hello.exe: None \S+ None
hello.c: \d+ None \d+
hello.obj: None \S+ None
"""))

test.run(interpreter = TestSCons.python,
         program = sconsign,
         arguments = "-r sub1/.sconsign")

test.fail_test(not sort_match(test, test.stdout(), """\
hello.exe: None \S+ None
hello.c: '\S+ \S+ [ \d]\d \d\d:\d\d:\d\d \d\d\d\d' None \d+
hello.obj: None \S+ None
"""))

test.pass_test()
