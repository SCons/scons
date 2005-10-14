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

import os.path
import string
import time

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

def re_sep(*args):
    return string.replace(apply(os.path.join, args), '\\', '\\\\')



class MyTestSCons(TestSCons.TestSCons):
    # subclass with a method for running the sconsign script
    def __init__(self, *args, **kw):
        apply(TestSCons.TestSCons.__init__, (self,)+args, kw)
        self.my_kw = {
            'interpreter' : TestSCons.python,
            'program' : sconsign,
        }
    def run_sconsign(self, *args, **kw):
        kw.update(self.my_kw)
        return apply(self.run, args, kw)

test = MyTestSCons(match = TestCmd.match_re)




test.subdir('work1', ['work1', 'sub1'], ['work1', 'sub2'],
            'work2', ['work2', 'sub1'], ['work2', 'sub2'])

test.write(['work1', 'SConstruct'], """
SConsignFile(None)
env1 = Environment(PROGSUFFIX = '.exe', OBJSUFFIX = '.obj')
env1.Program('sub1/hello.c')
env2 = env1.Copy(CPPPATH = ['sub2'])
env2.Program('sub2/hello.c')
""")

test.write(['work1', 'sub1', 'hello.c'], r"""\
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("sub1/hello.c\n");
        exit (0);
}
""")

test.write(['work1', 'sub2', 'hello.c'], r"""\
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

test.write(['work1', 'sub2', 'inc1.h'], r"""\
#define STRING1 "inc1.h"
""")

test.write(['work1', 'sub2', 'inc2.h'], r"""\
#define STRING2 "inc2.h"
""")

test.run(chdir = 'work1', arguments = '--implicit-cache .')

test.run_sconsign(arguments = "work1/sub1/.sconsign",
         stdout = """\
hello.exe: \S+ None \d+ \d+
        hello.obj: \S+
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
""")

test.run_sconsign(arguments = "--raw work1/sub1/.sconsign",
         stdout = """\
hello.exe: {'bsig': '\S+', 'size': \d+L?, 'timestamp': \d+}
        hello.obj: \S+
hello.obj: {'bsig': '\S+', 'size': \d+L?, 'timestamp': \d+}
        hello.c: \S+
""")

test.run_sconsign(arguments = "-v work1/sub1/.sconsign",
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

test.run_sconsign(arguments = "-b -v work1/sub1/.sconsign",
         stdout = """\
hello.exe:
    bsig: \S+
hello.obj:
    bsig: \S+
""")

test.run_sconsign(arguments = "-c -v work1/sub1/.sconsign",
         stdout = """\
hello.exe:
    csig: None
hello.obj:
    csig: None
""")

test.run_sconsign(arguments = "-s -v work1/sub1/.sconsign",
         stdout = """\
hello.exe:
    size: \d+
hello.obj:
    size: \d+
""")

test.run_sconsign(arguments = "-t -v work1/sub1/.sconsign",
         stdout = """\
hello.exe:
    timestamp: \d+
hello.obj:
    timestamp: \d+
""")

test.run_sconsign(arguments = "-e hello.obj work1/sub1/.sconsign",
         stdout = """\
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
""")

test.run_sconsign(arguments = "-e hello.obj -e hello.exe -e hello.obj work1/sub1/.sconsign",
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

test.run_sconsign(arguments = "work1/sub2/.sconsign",
         stdout = """\
hello.exe: \S+ None \d+ \d+
        hello.obj: \S+
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
        inc1.h: \S+
        inc2.h: \S+
""")

#test.run_sconsign(arguments = "-i -v work1/sub2/.sconsign",
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

test.run_sconsign(arguments = "-e hello.obj work1/sub2/.sconsign work1/sub1/.sconsign",
         stdout = """\
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
        inc1.h: \S+
        inc2.h: \S+
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
""")

test.run(chdir = 'work1', arguments = '--clean .')

test.write(['work1', 'SConstruct'], """
SourceSignatures('timestamp')
TargetSignatures('content')
env1 = Environment(PROGSUFFIX = '.exe', OBJSUFFIX = '.obj')
env1.Program('sub1/hello.c')
env2 = env1.Copy(CPPPATH = ['sub2'])
env2.Program('sub2/hello.c')
""")

time.sleep(1)

test.run(chdir = 'work1', arguments = '. --max-drift=1 --debug=stacktrace')

test.run_sconsign(arguments = "-e hello.exe -e hello.obj work1/sub1/.sconsign",
         stdout = """\
hello.exe: \S+ None \d+ \d+
        hello.obj: \S+
hello.obj: \S+ None \d+ \d+
        hello.c: \S+
""")

test.run_sconsign(arguments = "-e hello.exe -e hello.obj -r work1/sub1/.sconsign",
         stdout = """\
hello.exe: \S+ None '\S+ \S+ [ \d]\d \d\d:\d\d:\d\d \d\d\d\d' \d+
        hello.obj: \S+
hello.obj: \S+ None '\S+ \S+ [ \d]\d \d\d:\d\d:\d\d \d\d\d\d' \d+
        hello.c: \S+
""")


##############################################################################

test.write(['work2', 'SConstruct'], """
SConsignFile()
env1 = Environment(PROGSUFFIX = '.exe', OBJSUFFIX = '.obj')
env1.Program('sub1/hello.c')
env2 = env1.Copy(CPPPATH = ['sub2'])
env2.Program('sub2/hello.c')
""")

test.write(['work2', 'sub1', 'hello.c'], r"""\
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("sub1/hello.c\n");
        exit (0);
}
""")

test.write(['work2', 'sub2', 'hello.c'], r"""\
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

test.write(['work2', 'sub2', 'inc1.h'], r"""\
#define STRING1 "inc1.h"
""")

test.write(['work2', 'sub2', 'inc2.h'], r"""\
#define STRING2 "inc2.h"
""")

test.run(chdir = 'work2', arguments = '--implicit-cache .')

test.run_sconsign(arguments = "work2/.sconsign")

test.run_sconsign(arguments = "work2/.sconsign",
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

test.run_sconsign(arguments = "--raw work2/.sconsign",
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

test.run_sconsign(arguments = "-v work2/.sconsign",
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

test.run_sconsign(arguments = "-b -v work2/.sconsign",
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

test.run_sconsign(arguments = "-c -v work2/.sconsign",
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

test.run_sconsign(arguments = "-s -v work2/.sconsign",
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

test.run_sconsign(arguments = "-t -v work2/.sconsign",
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

test.run_sconsign(arguments = "-e hello.obj work2/.sconsign",
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

test.run_sconsign(arguments = "-e hello.obj -e hello.exe -e hello.obj work2/.sconsign",
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

#test.run_sconsign(arguments = "-i -v work2/.sconsign",
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

test.run(chdir = 'work2', arguments = '--clean .')

test.write(['work2','SConstruct'], """
SConsignFile('my_sconsign')
SourceSignatures('timestamp')
TargetSignatures('content')
env1 = Environment(PROGSUFFIX = '.exe', OBJSUFFIX = '.obj')
env1.Program('sub1/hello.c')
env2 = env1.Copy(CPPPATH = ['sub2'])
env2.Program('sub2/hello.c')
""")

time.sleep(1)

test.run(chdir = 'work2', arguments = '. --max-drift=1')

test.run_sconsign(arguments = "-e hello.exe -e hello.obj -d sub1 -f dblite work2/my_sconsign",
         stdout = """\
=== sub1:
hello.exe: \d+ None \d+ \d+
        hello.obj: \d+
hello.obj: \d+ None \d+ \d+
        hello.c: \d+
""")

test.run_sconsign(arguments = "-e hello.exe -e hello.obj -d sub1 -f dblite work2/my_sconsign.dblite",
         stdout = """\
=== sub1:
hello.exe: \d+ None \d+ \d+
        hello.obj: \S+
hello.obj: \d+ None \d+ \d+
        hello.c: \S+
""")

test.run_sconsign(arguments = "-e hello.exe -e hello.obj -d sub1 -f dblite work2/my_sconsign",
         stdout = """\
=== sub1:
hello.exe: \d+ None \d+ \d+
        hello.obj: \d+
hello.obj: \d+ None \d+ \d+
        hello.c: \d+
""")

test.run_sconsign(arguments = "-e hello.exe -e hello.obj -d sub1 -f dblite work2/my_sconsign.dblite",
         stdout = """\
=== sub1:
hello.exe: \S+ None \d+ \d+
        hello.obj: \d+
hello.obj: \S+ None \d+ \d+
        hello.c: \d+
""")

test.run_sconsign(arguments = "-e hello.exe -e hello.obj -r -d sub1 -f dblite work2/my_sconsign",
         stdout = """\
=== sub1:
hello.exe: \d+ None '\S+ \S+ [ \d]\d \d\d:\d\d:\d\d \d\d\d\d' \d+
        hello.obj: \d+
hello.obj: \d+ None '\S+ \S+ [ \d]\d \d\d:\d\d:\d\d \d\d\d\d' \d+
        hello.c: \d+
""")

test.run_sconsign(arguments = "-e hello.exe -e hello.obj -r -d sub1 -f dblite work2/my_sconsign.dblite",
         stdout = """\
=== sub1:
hello.exe: \d+ None '\S+ \S+ [ \d]\d \d\d:\d\d:\d\d \d\d\d\d' \d+
        hello.obj: \d+
hello.obj: \d+ None '\S+ \S+ [ \d]\d \d\d:\d\d:\d\d \d\d\d\d' \d+
        hello.c: \d+
""")

##############################################################################

test.write('bad1', "bad1\n")
test.write('bad2.dblite', "bad2.dblite\n")
test.write('bad3', "bad3\n")

test.run_sconsign(arguments = "-f dblite no_sconsign",
         stderr = "sconsign: \[Errno 2\] No such file or directory: 'no_sconsign'\n")

test.run_sconsign(arguments = "-f dblite bad1",
         stderr = "sconsign: \[Errno 2\] No such file or directory: 'bad1.dblite'\n")

test.run_sconsign(arguments = "-f dblite bad1.dblite",
         stderr = "sconsign: \[Errno 2\] No such file or directory: 'bad1.dblite'\n")

test.run_sconsign(arguments = "-f dblite bad2",
         stderr = "sconsign: ignoring invalid `dblite' file `bad2'\n")

test.run_sconsign(arguments = "-f dblite bad2.dblite",
         stderr = "sconsign: ignoring invalid `dblite' file `bad2.dblite'\n")

test.run_sconsign(arguments = "-f sconsign no_sconsign",
         stderr = "sconsign: \[Errno 2\] No such file or directory: 'no_sconsign'\n")

test.run_sconsign(arguments = "-f sconsign bad3",
         stderr = "sconsign: ignoring invalid .sconsign file `bad3'\n")

test.pass_test()
