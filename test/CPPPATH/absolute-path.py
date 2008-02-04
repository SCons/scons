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

import TestSCons

test = TestSCons.TestSCons()

test.subdir('include', 'work')

inc_h = test.workpath('include', 'inc.h')
does_not_exist_h = test.workpath('include', 'does_not_exist.h')

test.write(['work', 'SConstruct'], """\
Program('prog.c')
""")

test.write(['work', 'prog.c'], """\
#include <stdio.h>
#include "%(inc_h)s"
#if     0
#include "%(does_not_exist_h)s"
#endif

int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    printf("%%s\\n", STRING);
    return 0;
}
""" % locals())

test.write(['include', 'inc.h'], """\
#define STRING  "include/inc.h 1\\n"
""")

test.run(chdir = 'work', arguments = '.')

test.up_to_date(chdir = 'work', arguments = '.')

test.write(['include', 'inc.h'], """\
#define STRING  "include/inc.h 2\\n"
""")

test.not_up_to_date(chdir = 'work', arguments = '.')

test.pass_test()
