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
Verify that the sconsign script works when using a .sconsign file in
each subdirectory (SConsignFile(None)) written with the non-default
SourceSignatures() and TargetSignatures() values (timestamp and content,
respectively).
"""

import TestSConsign

test = TestSConsign.TestSConsign(match = TestSConsign.match_re)

def re_sep(*args):
    import os.path
    import re
    return re.escape(apply(os.path.join, args))

test.subdir('sub1', 'sub2')

test.write('SConstruct', """
SConsignFile(None)
SourceSignatures('timestamp')
TargetSignatures('content')
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

test.sleep()

test.run(arguments = '. --max-drift=1')

test.run_sconsign(arguments = "-e hello.exe -e hello.obj sub1/.sconsign",
         stdout = """\
hello.exe: \S+ None \d+ \d+
        hello.obj: \S+
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
""")

test.run_sconsign(arguments = "-e hello.exe -e hello.obj -r sub1/.sconsign",
         stdout = """\
hello.exe: \S+ None '\S+ \S+ [ \d]\d \d\d:\d\d:\d\d \d\d\d\d' \d+
        hello.obj: \S+
hello.obj: \S+ None '\S+ \S+ [ \d]\d \d\d:\d\d:\d\d \d\d\d\d' \d+
        hello.c: \S+
""")

test.pass_test()
