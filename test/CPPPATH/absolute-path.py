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
Verify the ability to #include a file with an absolute path name.  (Which
is not strictly a test of using $CPPPATH, but it's in the ball park...)
"""

import os

import TestSCons

test = TestSCons.TestSCons()

test.subdir('include', 'work')

inc1_h = test.workpath('include', 'inc1.h')
inc2_h = test.workpath('include', 'inc2.h')
does_not_exist_h = test.workpath('include', 'does_not_exist.h')

# Verify that including an absolute path still works even if they
# double the separators in the input file.  This can happen especially
# on Windows if they use \\ to represent an escaped backslash.
inc2_h = inc2_h.replace(os.sep, os.sep+os.sep)

test.write(['work', 'SConstruct'], """\
Program('prog.c')
""")

test.write(['work', 'prog.c'], """\
#include <stdio.h>
#include "%(inc1_h)s"
#include "%(inc2_h)s"
#if     0
#include "%(does_not_exist_h)s"
#endif

int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    printf("%%s\\n", STRING1);
    printf("%%s\\n", STRING2);
    return 0;
}
""" % locals())

test.write(['include', 'inc1.h'], """\
#define STRING1  "include/inc1.h A\\n"
""")

test.write(['include', 'inc2.h'], """\
#define STRING2  "include/inc2.h A\\n"
""")

test.run(chdir = 'work', arguments = '.')

test.up_to_date(chdir = 'work', arguments = '.')

test.write(['include', 'inc1.h'], """\
#define STRING1  "include/inc1.h B\\n"
""")

test.not_up_to_date(chdir = 'work', arguments = '.')

test.write(['include', 'inc2.h'], """\
#define STRING2  "include/inc2.h B\\n"
""")

test.not_up_to_date(chdir = 'work', arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
