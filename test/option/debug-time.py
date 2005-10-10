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

def num(match, line):
    return float(re.search(match, line).group(1))

# Try to make things a little more equal by measuring Python overhead
# executing a minimal file, and reading the scons.py script itself from
# disk so that it's already been cached.
test.write('pass.py', "pass\n")
test.read(test.program)

start_time = time.time()
test.run(program=TestSCons.python, arguments=test.workpath('pass.py'))
overhead = time.time() - start_time 

start_time = time.time()
test.run(arguments = "--debug=time .")
complete_time = time.time() - start_time

expected_total_time = complete_time - overhead
lines = string.split(test.stdout(), '\n')

expected_command_time = 0.0
for cmdline in filter(lambda x: x[:23] == "Command execution time:", lines):
    n = num(r'Command execution time: (\d+\.\d+) seconds', cmdline)
    expected_command_time = expected_command_time + n

stdout = test.stdout()

total_time = num(r'Total build time: (\d+\.\d+) seconds', stdout)
sconscript_time = num(r'Total SConscript file execution time: (\d+\.\d+) seconds', stdout)
scons_time = num(r'Total SCons execution time: (\d+\.\d+) seconds', stdout)
command_time = num(r'Total command execution time: (\d+\.\d+) seconds', stdout)

def within_tolerance(expected, actual, tolerance):
    return abs((expected-actual)/actual) <= tolerance

failures = []

if not within_tolerance(expected_command_time, command_time, 0.01):
    failures.append("""\
SCons reported a total command execution time of %s,
but command execution times really totalled %s,
outside of the 1%% tolerance.
""" % (command_time, expected_command_time))

added_times = sconscript_time+scons_time+command_time
if not within_tolerance(total_time, added_times, 0.01):
    failures.append("""\
SCons reported a total build time of %s,
but the various execution times actually totalled %s,
outside of the 1%% tolerance.
""" % (total_time, added_times))

if not within_tolerance(total_time, expected_total_time, 0.15):
    failures.append("""\
SCons reported total build time of %s,
but the actual measured build time was %s
(end-to-end time of %s less Python overhead of %s),
outside of the 15%% tolerance.
""" % (total_time, expected_total_time, complete_time, overhead))

if failures:
    print string.join([test.stdout()] + failures, '\n')
    test.fail_test(1)

test.pass_test()
