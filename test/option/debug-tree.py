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
Test that the --debug=tree option prints a tree representation of the
complete dependencies of a target.
"""

import TestSCons
import sys
import string
import re
import time

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment(OBJSUFFIX = '.ooo', PROGSUFFIX = '.xxx')
env.Program('Foo', Split('Foo.c Bar.c'))
""")

# N.B.:  We use upper-case file names (Foo* and Bar*) so that the sorting
# order with our upper-case SConstruct file is the same on case-sensitive
# (UNIX/Linux) and case-insensitive (Windows) systems.

test.write('Foo.c', r"""
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
  +-Bar.ooo
    +-Bar.c
    +-Bar.h
    +-Foo.h
"""

test.run(arguments = "--debug=tree Foo.xxx")
test.fail_test(string.find(test.stdout(), tree1) == -1)

tree2 = """
+-.
  +-Bar.c
  +-Bar.ooo
  | +-Bar.c
  | +-Bar.h
  | +-Foo.h
  +-Foo.c
  +-Foo.ooo
  | +-Foo.c
  | +-Foo.h
  | +-Bar.h
  +-Foo.xxx
  | +-Foo.ooo
  | | +-Foo.c
  | | +-Foo.h
  | | +-Bar.h
  | +-Bar.ooo
  |   +-Bar.c
  |   +-Bar.h
  |   +-Foo.h
  +-SConstruct
"""
test.run(arguments = "--debug=tree .")
test.fail_test(string.find(test.stdout(), tree2) == -1)

# Make sure we print the debug stuff even if there's a build failure.
test.write('Bar.h', """
#ifndef BAR_H
#define BAR_H
#include "Foo.h"
#endif
THIS SHOULD CAUSE A BUILD FAILURE
""")

test.run(arguments = "--debug=tree Foo.xxx",
         status = 2,
         stderr = None)
test.fail_test(string.find(test.stdout(), tree1) == -1)

test.pass_test()
