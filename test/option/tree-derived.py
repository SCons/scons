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
Test that the --debug=dtree option correctly prints just the explicit
dependencies (sources or Depends()) of a target.
"""

import TestSCons
import sys
import string
import re
import time

test = TestSCons.TestSCons()

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

dtree1 = """
+-foo.xxx
  +-foo.ooo
  +-bar.ooo
"""

test.run(arguments = "--tree=derived foo.xxx")
test.fail_test(string.find(test.stdout(), dtree1) == -1)

dtree2 = """
+-.
  +-bar.ooo
  +-foo.ooo
  +-foo.xxx
    +-foo.ooo
    +-bar.ooo
"""

test.run(arguments = "--tree=derived .")
test.fail_test(string.find(test.stdout(), dtree2) == -1)

dtree3 = """
+-.
  +-bar.ooo
  +-foo.ooo
  +-foo.xxx
    +-[foo.ooo]
    +-[bar.ooo]
"""

test.run(arguments = "--tree=derived,prune .")
test.fail_test(string.find(test.stdout(), dtree3) == -1)

dtree4 = """
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
[  B      ]  +-bar.ooo
"""

test.run(arguments = '-c foo.xxx')

test.run(arguments = "--no-exec --tree=derived,status foo.xxx")
test.fail_test(string.find(test.stdout(), dtree4) == -1)

# Make sure we print the debug stuff even if there's a build failure.
test.write('bar.h', """
#ifndef BAR_H
#define BAR_H
#include "foo.h"
#endif
THIS SHOULD CAUSE A BUILD FAILURE
""")

test.run(arguments = "--tree=derived foo.xxx",
         status = 2,
         stderr = None)
test.fail_test(string.find(test.stdout(), dtree1) == -1)

test.pass_test()
