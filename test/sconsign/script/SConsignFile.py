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
Verify that the sconsign script works with files generated when
using the signatures in an SConsignFile().
"""

import TestSConsign

test = TestSConsign.TestSConsign(match = TestSConsign.match_re)

test.subdir('sub1', 'sub2')

test.write(['SConstruct'], """\
SConsignFile()
env1 = Environment(PROGSUFFIX = '.exe', OBJSUFFIX = '.obj')
env1.Program('sub1/hello.c')
env2 = env1.Clone(CPPPATH = ['sub2'])
env2.Program('sub2/hello.c')
""")

test.write(['sub1', 'hello.c'], r"""\
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("sub1/hello.c\n");
        exit (0);
}
""")

test.write(['sub2', 'hello.c'], r"""\
#include <stdio.h>
#include <stdlib.h>
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

test.run_sconsign(arguments = ".sconsign",
         stdout = """\
=== sub1:
hello.exe: \S+ None \d+ \d+
        hello.obj: \S+
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
=== sub2:
hello.exe: \S+ None \d+ \d+
        hello.obj: \S+
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
        inc1.h: \S+
        inc2.h: \S+
""")

test.run_sconsign(arguments = "--raw .sconsign",
         stdout = """\
=== sub1:
hello.exe: {'bsig': '\S+', 'size': \d+L?, 'timestamp': \d+}
        hello.obj: \S+
hello.obj: {'bsig': '\S+', 'size': \d+L?, 'timestamp': \d+}
        hello.c: \S+
=== sub2:
hello.exe: {'bsig': '\S+', 'size': \d+L?, 'timestamp': \d+}
        hello.obj: \S+
hello.obj: {'bsig': '\S+', 'size': \d+L?, 'timestamp': \d+}
        hello.c: \S+
        inc1.h: \S+
        inc2.h: \S+
""")

test.run_sconsign(arguments = "-v .sconsign",
         stdout = """\
=== sub1:
hello.exe:
    bsig: \S+
    csig: None
    timestamp: \d+
    size: \d+
    implicit:
        hello.obj: \S+
hello.obj:
    bsig: \S+
    csig: None
    timestamp: \d+
    size: \d+
    implicit:
        hello.c: \S+
=== sub2:
hello.exe:
    bsig: \S+
    csig: None
    timestamp: \d+
    size: \d+
    implicit:
        hello.obj: \S+
hello.obj:
    bsig: \S+
    csig: None
    timestamp: \d+
    size: \d+
    implicit:
        hello.c: \S+
        inc1.h: \S+
        inc2.h: \S+
""")

test.run_sconsign(arguments = "-b -v .sconsign",
         stdout = """\
=== sub1:
hello.exe:
    bsig: \S+
hello.obj:
    bsig: \S+
=== sub2:
hello.exe:
    bsig: \S+
hello.obj:
    bsig: \S+
""")

test.run_sconsign(arguments = "-c -v .sconsign",
         stdout = """\
=== sub1:
hello.exe:
    csig: None
hello.obj:
    csig: None
=== sub2:
hello.exe:
    csig: None
hello.obj:
    csig: None
""")

test.run_sconsign(arguments = "-s -v .sconsign",
         stdout = """\
=== sub1:
hello.exe:
    size: \d+
hello.obj:
    size: \d+
=== sub2:
hello.exe:
    size: \d+
hello.obj:
    size: \d+
""")

test.run_sconsign(arguments = "-t -v .sconsign",
         stdout = """\
=== sub1:
hello.exe:
    timestamp: \d+
hello.obj:
    timestamp: \d+
=== sub2:
hello.exe:
    timestamp: \d+
hello.obj:
    timestamp: \d+
""")

test.run_sconsign(arguments = "-e hello.obj .sconsign",
         stdout = """\
=== sub1:
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
=== sub2:
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
        inc1.h: \S+
        inc2.h: \S+
""")

test.run_sconsign(arguments = "-e hello.obj -e hello.exe -e hello.obj .sconsign",
         stdout = """\
=== sub1:
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
hello.exe: \S+ None \d+ \d+
        hello.obj: \S+
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
=== sub2:
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
        inc1.h: \S+
        inc2.h: \S+
hello.exe: \S+ None \d+ \d+
        hello.obj: \S+
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
        inc1.h: \S+
        inc2.h: \S+
""")

#test.run_sconsign(arguments = "-i -v .sconsign",
#         stdout = """\
#=== sub1:
#hello.exe:
#    implicit:
#        hello.obj: \S+
#hello.obj:
#    implicit:
#        hello.c: \S+
#=== sub2:
#hello.exe:
#    implicit:
#        hello.obj: \S+
#hello.obj:
#    implicit:
#        hello.c: \S+
#        inc1.h: \S+
#        inc2.h: \S+
#""")

test.pass_test()
