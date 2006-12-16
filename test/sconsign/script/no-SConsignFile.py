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
Verify that the sconsign script works when using an individual
.sconsign file in each directory (SConsignFile(None)).
"""

import TestSConsign

test = TestSConsign.TestSConsign(match = TestSConsign.match_re)

def re_sep(*args):
    import os.path
    import re
    return re.escape(apply(os.path.join, args))

test.subdir('sub1', 'sub2')

test.write(['SConstruct'], """
SConsignFile(None)
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

test.run_sconsign(arguments = "sub1/.sconsign",
         stdout = """\
hello.exe: \S+ None \d+ \d+
        hello.obj: \S+
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
""")

test.run_sconsign(arguments = "--raw sub1/.sconsign",
         stdout = """\
hello.exe: {'bsig': '\S+', 'size': \d+L?, 'timestamp': \d+}
        hello.obj: \S+
hello.obj: {'bsig': '\S+', 'size': \d+L?, 'timestamp': \d+}
        hello.c: \S+
""")

test.run_sconsign(arguments = "-v sub1/.sconsign",
         stdout = """\
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
""")

test.run_sconsign(arguments = "-b -v sub1/.sconsign",
         stdout = """\
hello.exe:
    bsig: \S+
hello.obj:
    bsig: \S+
""")

test.run_sconsign(arguments = "-c -v sub1/.sconsign",
         stdout = """\
hello.exe:
    csig: None
hello.obj:
    csig: None
""")

test.run_sconsign(arguments = "-s -v sub1/.sconsign",
         stdout = """\
hello.exe:
    size: \d+
hello.obj:
    size: \d+
""")

test.run_sconsign(arguments = "-t -v sub1/.sconsign",
         stdout = """\
hello.exe:
    timestamp: \d+
hello.obj:
    timestamp: \d+
""")

test.run_sconsign(arguments = "-e hello.obj sub1/.sconsign",
         stdout = """\
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
""")

test.run_sconsign(arguments = "-e hello.obj -e hello.exe -e hello.obj sub1/.sconsign",
         stdout = """\
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
hello.exe: \S+ None \d+ \d+
        hello.obj: \S+
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
""")

# XXX NOT SURE IF THIS IS RIGHT!
sub2_inc1_h = re_sep('sub2', 'inc1.h')
sub2_inc2_h = re_sep('sub2', 'inc2.h')

test.run_sconsign(arguments = "sub2/.sconsign",
         stdout = """\
hello.exe: \S+ None \d+ \d+
        hello.obj: \S+
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
        inc1.h: \S+
        inc2.h: \S+
""")

#test.run_sconsign(arguments = "-i -v sub2/.sconsign",
#         stdout = """\
#hello.exe:
#    implicit:
#        hello.obj: \S+ None \d+ \d+
#hello.obj:
#    implicit:
#        hello.c: None \S+ \d+ \d+
#        inc1.h: None \S+ \d+ \d+
#        inc2.h: None \S+ \d+ \d+
#""")

test.run_sconsign(arguments = "-e hello.obj sub2/.sconsign sub1/.sconsign",
         stdout = """\
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
        inc1.h: \S+
        inc2.h: \S+
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
""")

test.pass_test()
