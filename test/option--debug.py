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
import re
import time

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment(OBJSUFFIX = '.ooo', PROGSUFFIX = '.xxx')
env.Program('foo', Split('foo.c bar.c'))
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

############################
# test --debug=time

def num(match, line):
    return float(re.match(match, line).group(1))

start_time = time.time()
test.run(program=sys.executable, arguments='-c pass')
overhead = time.time() - start_time 

start_time = time.time()
test.run(arguments = "--debug=time .")
expected_total_time = time.time() - start_time - overhead
line = string.split(test.stdout(), '\n')

cmdline = filter(lambda x: x[:23] == "Command execution time:", line)

expected_command_time = num(r'Command execution time: (\d+\.\d+) seconds', cmdline[0])
expected_command_time = expected_command_time + num(r'Command execution time: (\d+\.\d+) seconds', cmdline[1])
expected_command_time = expected_command_time + num(r'Command execution time: (\d+\.\d+) seconds', cmdline[2])
expected_command_time = expected_command_time + num(r'Command execution time: (\d+\.\d+) seconds', cmdline[3])

totalline = filter(lambda x: x[:6] == "Total ", line)

total_time = num(r'Total build time: (\d+\.\d+) seconds', totalline[0])
sconscript_time = num(r'Total SConscript file execution time: (\d+\.\d+) seconds', totalline[1])
scons_time = num(r'Total SCons execution time: (\d+\.\d+) seconds', totalline[2])
command_time = num(r'Total command execution time: (\d+\.\d+) seconds', totalline[3])

def check(expected, actual, tolerance):
    return abs((expected-actual)/actual) <= tolerance

assert check(expected_command_time, command_time, 0.01)
assert check(total_time, sconscript_time+scons_time+command_time, 0.01) 
assert check(total_time, expected_total_time, 0.1)

test.pass_test()

