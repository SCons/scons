#!/usr/bin/env python
#
# Copyright (c) 2001 Steven Knight
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

__revision__ = "test/option--test.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import sys
import string

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment()
env.Program('foo', 'foo.c bar.c')
""")

test.write('foo.c', """
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


if sys.platform == 'win32':
    foo = 'foo.exe'
else:
    foo = 'foo'

test.run(arguments = "--debug=tree " + foo)

tree = """
+-foo
  +-foo.o
  | +-foo.c
  |   +-foo.h
  |   +-bar.h
  +-bar.o
    +-bar.c
      +-bar.h
      +-foo.h
"""

assert string.find(test.stdout(), tree) != -1

test.run(arguments = "--debug=tree " + foo)
assert string.find(test.stdout(), tree) != -1

test.pass_test()

