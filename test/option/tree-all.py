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
Test that the --tree=all option prints a tree representation of the
complete dependencies of a target.
"""

import TestSCons
import sys

test = TestSCons.TestSCons()

CC = test.detect('CC')
LINK = test.detect('LINK')
if LINK is None: LINK = CC

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(OBJSUFFIX = '.ooo', PROGSUFFIX = '.xxx')
env.Program('Foo', Split('Foo.c Bar.c'))
""")

# N.B.:  We use upper-case file names (Foo* and Bar*) so that the sorting
# order with our upper-case SConstruct file is the same on case-sensitive
# (UNIX/Linux) and case-insensitive (Windows) systems.

test.write('Foo.c', r"""
#include <stdio.h>
#include <stdlib.h>
#include "Foo.h"
int main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("f1.c\n");
        exit (0);
}
""")

test.write('Bar.c', """
#include "Bar.h"
int local = 1;
""")

test.write('Foo.h', """
#ifndef FOO_H
#define FOO_H
#include "Bar.h"
#endif
""")

test.write('Bar.h', """
#ifndef BAR_H
#define BAR_H
#include "Foo.h"
#endif
""")

tree1 = """
+-Foo.xxx
  +-Foo.ooo
  | +-Foo.c
  | +-Foo.h
  | +-Bar.h
  | +-%(CC)s
  +-Bar.ooo
  | +-Bar.c
  | +-Bar.h
  | +-Foo.h
  | +-%(CC)s
  +-%(LINK)s
""" % locals()

test.run(arguments = "--tree=all Foo.xxx")
if test.stdout().count(tree1) != 1:
    sys.stdout.write('Did not find expected tree (or found duplicate) in the following output:\n')
    sys.stdout.write(test.stdout())
    test.fail_test()

tree2 = """
+-.
  +-Bar.c
  +-Bar.h
  +-Bar.ooo
  | +-Bar.c
  | +-Bar.h
  | +-Foo.h
  | +-%(CC)s
  +-Foo.c
  +-Foo.h
  +-Foo.ooo
  | +-Foo.c
  | +-Foo.h
  | +-Bar.h
  | +-%(CC)s
  +-Foo.xxx
  | +-Foo.ooo
  | | +-Foo.c
  | | +-Foo.h
  | | +-Bar.h
  | | +-%(CC)s
  | +-Bar.ooo
  | | +-Bar.c
  | | +-Bar.h
  | | +-Foo.h
  | | +-%(CC)s
  | +-%(LINK)s
  +-SConstruct
""" % locals()

test.run(arguments = "--tree=all .")
test.must_contain_all_lines(test.stdout(), [tree2])

tree3 = """
+-.
  +-Bar.c
  +-Bar.h
  +-Bar.ooo
  | +-Bar.c
  | +-Bar.h
  | +-Foo.h
  | +-%(CC)s
  +-Foo.c
  +-Foo.h
  +-Foo.ooo
  | +-Foo.c
  | +-Foo.h
  | +-Bar.h
  | +-%(CC)s
  +-Foo.xxx
  | +-[Foo.ooo]
  | +-[Bar.ooo]
  | +-%(LINK)s
  +-SConstruct
""" % locals()

test.run(arguments = "--tree=all,prune .")
if test.stdout().count(tree3) != 1:
    sys.stdout.write('Did not find expected tree (or found duplicate) in the following output:\n')
    sys.stdout.write(test.stdout())
    test.fail_test()

test.run(arguments = "--tree=prune .")
if test.stdout().count(tree3) != 1:
    sys.stdout.write('Did not find expected tree (or found duplicate) in the following output:\n')
    sys.stdout.write(test.stdout())
    test.fail_test()

tree4 = """
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

[  B      ]+-Foo.xxx
[  B      ]  +-Foo.ooo
[E     C  ]  | +-Foo.c
[E     C  ]  | +-Foo.h
[E     C  ]  | +-Bar.h
[E     C  ]  | +-%(CC)s
[  B      ]  +-Bar.ooo
[E     C  ]  | +-Bar.c
[E     C  ]  | +-Bar.h
[E     C  ]  | +-Foo.h
[E     C  ]  | +-%(CC)s
[E     C  ]  +-%(LINK)s
""" % locals()

test.run(arguments = '-c Foo.xxx')

test.run(arguments = "--no-exec --tree=all,status Foo.xxx")
if test.stdout().count(tree4) != 1:
    sys.stdout.write('Did not find expected tree (or found duplicate) in the following output:\n')
    sys.stdout.write(test.stdout())
    test.fail_test()

test.run(arguments = "--no-exec --tree=status Foo.xxx")
if test.stdout().count(tree4) != 1:
    sys.stdout.write('Did not find expected tree (or found duplicate) in the following output:\n')
    sys.stdout.write(test.stdout())
    test.fail_test()

# Make sure we print the debug stuff even if there's a build failure.
test.write('Bar.h', """
#ifndef BAR_H
#define BAR_H
#include "Foo.h"
#endif
THIS SHOULD CAUSE A BUILD FAILURE
""")

test.run(arguments = "--tree=all Foo.xxx",
         status = 2,
         stderr = None)
if test.stdout().count(tree1) != 1:
    sys.stdout.write('Did not find expected tree (or found duplicate) in the following output:\n')
    sys.stdout.write(test.stdout())
    test.fail_test()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
