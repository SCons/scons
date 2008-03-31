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
Verify that various ways of getting at a an sconsign file written with
the default dblite module and default .dblite suffix work correctly.
"""

import TestSConsign

test = TestSConsign.TestSConsign(match = TestSConsign.match_re)

CC = test.detect('CC', norm=1)
LINK = test.detect('LINK', norm=1)
if LINK is None: LINK = CC

test.subdir('sub1', 'sub2')

# Note:  We don't use os.path.join() representations of the file names
# in the expected output because paths in the .sconsign files are
# canonicalized to use / as the separator.

sub1_hello_c    = 'sub1/hello.c'
sub1_hello_obj  = 'sub1/hello.obj'

test.write('SConstruct', """
SConsignFile('my_sconsign')
Decider('timestamp-newer')
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

sig_re = r'[0-9a-fA-F]{32}'
date_re = r'\S+ \S+ [ \d]\d \d\d:\d\d:\d\d \d\d\d\d'

expect = r"""=== sub1:
hello.exe: %(sig_re)s \d+ \d+
        %(sub1_hello_obj)s: %(sig_re)s \d+ \d+
        %(LINK)s: None \d+ \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s \d+ \d+
        %(sub1_hello_c)s: None \d+ \d+
        %(CC)s: None \d+ \d+
        %(sig_re)s \[.*\]
""" % locals()

expect_r = """=== sub1:
hello.exe: %(sig_re)s '%(date_re)s' \d+
        %(sub1_hello_obj)s: %(sig_re)s '%(date_re)s' \d+
        %(LINK)s: None '%(date_re)s' \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s '%(date_re)s' \d+
        %(sub1_hello_c)s: None '%(date_re)s' \d+
        %(CC)s: None '%(date_re)s' \d+
        %(sig_re)s \[.*\]
""" % locals()

common_flags = '-e hello.exe -e hello.obj -d sub1'

test.run_sconsign(arguments = "%s my_sconsign" % common_flags,
                  stdout = expect)

test.run_sconsign(arguments = "%s my_sconsign.dblite" % common_flags,
                  stdout = expect)

test.run_sconsign(arguments = "%s -f dblite my_sconsign" % common_flags,
                  stdout = expect)

test.run_sconsign(arguments = "%s -f dblite my_sconsign.dblite" % common_flags,
                  stdout = expect)

test.run_sconsign(arguments = "%s -r -f dblite my_sconsign" % common_flags,
                  stdout = expect_r)

test.run_sconsign(arguments = "%s -r -f dblite my_sconsign.dblite" % common_flags,
                  stdout = expect_r)

test.pass_test()
