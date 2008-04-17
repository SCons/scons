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
Test that the --debug=stree option prints a dependency tree with output
that indicates the state of various Node status flags.
"""

import TestSCons
import sys
import string
import re
import time

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

CC = test.detect('CC')
LINK = test.detect('LINK')
if LINK is None: LINK = CC

test.write('SConstruct', """
env = Environment(OBJSUFFIX = '.ooo', PROGSUFFIX = '.xxx')
env.Program('foo', Split('foo.c bar.c'))
""")

test.write('foo.c', r"""
#include <stdio.h>
#include <stdlib.h>
#include "foo.h"
int main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("f1.c\n");
        exit (0);
}
""")

test.write('bar.c', """
#include "bar.h"
int local = 1;
""")

test.write('foo.h', """
#ifndef FOO_H
#define FOO_H
#include "bar.h"
#endif
""")

test.write('bar.h', """
#ifndef BAR_H
#define BAR_H
#include "foo.h"
#endif
""")

expect = """
scons: warning: The --debug=stree option is deprecated; please use --tree=all,status instead.
"""

stderr = TestSCons.re_escape(expect) + TestSCons.file_expr

stree = """
[E B   C  ]+-foo.xxx
[E B   C  ]  +-foo.ooo
[E     C  ]  | +-foo.c
[E     C  ]  | +-foo.h
[E     C  ]  | +-bar.h
[E     C  ]  | +-%(CC)s
[E B   C  ]  +-bar.ooo
[E     C  ]  | +-bar.c
[E     C  ]  | +-bar.h
[E     C  ]  | +-foo.h
[E     C  ]  | +-%(CC)s
[E     C  ]  +-%(LINK)s
""" % locals()

test.run(arguments = "--debug=stree foo.xxx",
         stderr = stderr)
test.fail_test(string.count(test.stdout(), stree) != 1)

stree2 = """
 E         = exists
  R        = exists in repository only
   b       = implicit builder
   B       = explicit builder
    S      = side effect
     P     = precious
      A    = always build
       C   = current
        N  = no clean
         H = no cache

[  B      ]+-foo.xxx
[  B      ]  +-foo.ooo
[E     C  ]  | +-foo.c
[E     C  ]  | +-foo.h
[E     C  ]  | +-bar.h
[E     C  ]  | +-%(CC)s
[  B      ]  +-bar.ooo
[E     C  ]  | +-bar.c
[E     C  ]  | +-bar.h
[E     C  ]  | +-foo.h
[E     C  ]  | +-%(CC)s
[E     C  ]  +-%(LINK)s
""" % locals()

test.run(arguments = '-c foo.xxx')

test.run(arguments = "--no-exec --debug=stree foo.xxx",
         stderr = stderr)
test.fail_test(string.count(test.stdout(), stree2) != 1)

test.pass_test()
