#!/usr/bin/env python
#
# Copyright The SCons Foundation
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

import os
import random
import time

import TestSCons
from TestCmd import IS_WINDOWS

test = TestSCons.TestSCons()

try:
    import ninja
except ImportError:
    test.skip_test("Could not find module in python")

_python_ = TestSCons._python_
_exe = TestSCons._exe

ninja_bin = os.path.abspath(os.path.join(
    ninja.__file__,
    os.pardir,
    'data',
    'bin',
    'ninja' + _exe))

test.dir_fixture('ninja-fixture')

test.write('source_0.c', """
#include <stdio.h>
#include <stdlib.h>
#include "source_0.h"

int
print_function0()
{
    printf("main print");
    return 0;
}
""")

test.write('source_0.h', """
#include <stdio.h>
#include <stdlib.h>

int
print_function0();
""")


def get_num_cpus():
    """
    Function to get the number of CPUs the system has.
    """
    # Linux, Unix and MacOS:
    if hasattr(os, "sysconf"):
        if 'SC_NPROCESSORS_ONLN' in os.sysconf_names:
            # Linux & Unix:
            ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
        if isinstance(ncpus, int) and ncpus > 0:
            return ncpus
        # OSX:
        return int(os.popen("sysctl -n hw.ncpu")[1].read())
    # Windows:
    if 'NUMBER_OF_PROCESSORS' in os.environ:
        ncpus = int(os.environ["NUMBER_OF_PROCESSORS"])
    if ncpus > 0:
        return ncpus
    # Default
    return 1


def generate_source(parent_source, current_source):
    test.write('source_{}.c'.format(current_source), """
        #include <stdio.h>
        #include <stdlib.h>
        #include "source_%(parent_source)s.h"
        #include "source_%(current_source)s.h"

        int
        print_function%(current_source)s()
        {
            return print_function%(parent_source)s();
        }
        """ % locals())

    test.write('source_{}.h'.format(current_source), """
        #include <stdio.h>
        #include <stdlib.h>

        int
        print_function%(current_source)s();
        """ % locals())


def mod_source_return(test_num):
    parent_source = test_num - 1
    test.write('source_{}.c'.format(test_num), """
        #include <stdio.h>
        #include <stdlib.h>
        #include "source_%(parent_source)s.h"
        #include "source_%(test_num)s.h"

        int
        print_function%(test_num)s()
        {
            int test = 5 + 5;
            print_function%(parent_source)s();
            return test;
        }
        """ % locals())


def mod_source_orig(test_num):
    parent_source = test_num - 1
    test.write('source_{}.c'.format(test_num), """
        #include <stdio.h>
        #include <stdlib.h>
        #include "source_%(parent_source)s.h"
        #include "source_%(test_num)s.h"

        int
        print_function%(test_num)s()
        {
            return print_function%(parent_source)s();
        }
        """ % locals())


num_source = 200
for i in range(1, num_source + 1):
    generate_source(i - 1, i)

test.write('main.c', """
#include <stdio.h>
#include <stdlib.h>
#include "source_%(num_source)s.h"
int
main()
{
    print_function%(num_source)s();
    exit(0);
}
""" % locals())

test.write('SConstruct', """
SetOption('experimental','ninja')
DefaultEnvironment(tools=[])

env = Environment()
env.Tool('ninja')
sources = ['main.c'] + env.Glob('source*.c')
env.Program(target = 'print_bin', source = sources)
""")

test.write('SConstruct_no_ninja', """
env = Environment()
sources = ['main.c'] + env.Glob('source*.c')
env.Program(target = 'print_bin', source = sources)
""")

tests_mods = []
ninja_times = []
scons_times = []
for _ in range(10):
    tests_mods += [random.randrange(1, num_source, 1)]
jobs = '-j' + str(get_num_cpus())

ninja_program = [test.workpath('run_ninja_env.bat'), jobs] if IS_WINDOWS else [ninja_bin, jobs]

test.run(arguments='--disable-execute-ninja', stdout=None)
test.run(program=ninja_program, arguments='run-ninja-scons-daemon', stdout=None)
start = time.perf_counter()
test.run(program=ninja_program, stdout=None)
stop = time.perf_counter()
ninja_times += [stop - start]
test.run(program=test.workpath('print_bin'), stdout="main print")


for test_mod in tests_mods:
    mod_source_return(test_mod)
    start = time.perf_counter()
    test.run(program=ninja_program, stdout=None)
    stop = time.perf_counter()
    ninja_times += [stop - start]

for test_mod in tests_mods:
    mod_source_orig(test_mod)

# clean build and ninja files
test.run(arguments='-c', stdout=None)
test.must_contain_all_lines(test.stdout(), [
    'Removed build.ninja'])

start = time.perf_counter()
test.run(arguments=["-f", "SConstruct_no_ninja", jobs], stdout=None)
stop = time.perf_counter()
scons_times += [stop - start]
test.run(program=test.workpath('print_bin'), stdout="main print")

for test_mod in tests_mods:
    mod_source_return(test_mod)
    start = time.perf_counter()
    test.run(arguments=["-f", "SConstruct_no_ninja", jobs], stdout=None)
    stop = time.perf_counter()
    scons_times += [stop - start]

full_build_print = True
for ninja_time, scons_time in zip(ninja_times, scons_times):
    if ninja_time > scons_time:
        test.fail_test(message="Ninja was slower than SCons: SCons: {:.3f}s Ninja: {:.3f}s".format(scons_time, ninja_time))
    if full_build_print:
        full_build_print = False
        print("Clean build {} files - SCons: {:.3f}s Ninja: {:.3f}s".format(num_source, scons_time, ninja_time))
    else:
        print("Single File Rebuild   - SCons: {:.3f}s Ninja: {:.3f}s".format(scons_time, ninja_time))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
