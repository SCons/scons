#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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

import TestSCons
import sys
import string

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment(OBJSUFFIX = '.ooo', PROGSUFFIX = '.xxx')
env.Program('foo', 'foo.c bar.c')
""")

test.write('foo.c', r"""
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

test.run(arguments = "--debug=tree foo.xxx")

import SCons.Defaults
obj = SCons.Defaults.ConstructionEnvironment['OBJSUFFIX']
tree = """
+-foo.xxx
  +-foo.ooo
  | +-foo.c
  | +-foo.h
  | +-bar.h
  +-bar.ooo
    +-bar.c
    +-bar.h
    +-foo.h
"""

test.fail_test(string.find(test.stdout(), tree) == -1)

test.run(arguments = "--debug=tree foo.xxx")
test.fail_test(string.find(test.stdout(), tree) == -1)


tree = """
+-foo.xxx
  +-foo.ooo
  +-bar.ooo
"""

test.run(arguments = "--debug=dtree foo.xxx")
test.fail_test(string.find(test.stdout(), tree) == -1)

tree = """scons: \".\" is up to date.

+-.
  +-SConstruct
  +-bar.c
  +-bar.h
  +-bar.ooo
  | +-bar.c
  | +-bar.h
  | +-foo.h
  +-foo.c
  +-foo.h
  +-foo.ooo
  | +-foo.c
  | +-foo.h
  | +-bar.h
  +-foo.xxx
    +-foo.ooo
    | +-foo.c
    | +-foo.h
    | +-bar.h
    +-bar.ooo
      +-bar.c
      +-bar.h
      +-foo.h
"""
test.run(arguments = "--debug=tree .")
test.fail_test(string.find(test.stdout(), tree) != 0)

test.run(arguments = "--debug=pdb", stdin = "n\ns\nq\n")
test.fail_test(string.find(test.stdout(), "(Pdb)") == -1)
test.fail_test(string.find(test.stdout(), "scons") == -1)

test.pass_test()

