#!/usr/bin/env python
# MIT License
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

"""
A script for timing snippets of Python code.

By default, this script will execute a single Python file specified on
the command line and time any functions in a list named "FunctionList"
set by the Python file under test, or (by default) time any functions
in the file whose names begin with "Func".

All functions are assumed to get passed the same arguments, and the
inputs are specified in a list named "Data," each element of which
is a list consisting of a tag name, a list of positional arguments,
and a dictionary of keyword arguments.

Each function is expected to test a single, comparable snippet of
of Python code.  IMPORTANT:  We want to test the timing of the code
itself, not Python function call overhead, so every function should
put its code under test within the following block:

      for i in IterationList:

This will allow (as much as possible) us to time just the code itself,
not Python function call overhead.
"""
from __future__ import division, print_function

import getopt
import os.path
import sys
import time
import types
from pprint import pprint


Usage = """\
Usage:  bench.py OPTIONS file.py
  --clock                       Use the time.clock function
  --func PREFIX                 Test functions whose names begin with PREFIX
  -h, --help                    Display this help and exit
  -i ITER, --iterations ITER    Run each code snippet ITER times
  --time                        Use the time.time function
  -r RUNS, --runs RUNS          Average times for RUNS invocations of
"""

# How many times each snippet of code will be (or should be) run by the
# functions under test to gather the time (the "inner loop").

Iterations = 1000

# How many times we'll run each function to collect its aggregate time
# and try to average out timing differences induced by system performance
# (the "outer loop").

Runs = 10

# The prefix of the functions under test.  This will be used if
# there's no explicit list defined in FunctionList.

FunctionPrefix = 'Func'

# Comment from Python2 timeit module:
# The difference in default timer function is because on Windows,
# clock() has microsecond granularity but time()'s granularity is 1/60th
# of a second; on Unix, clock() has 1/100th of a second granularity and
# time() is much more precise.  On either platform, the default timer
# functions measure wall clock time, not the CPU time.  This means that
# other processes running on the same computer may interfere with the
# timing.  The best thing to do when accurate timing is necessary is to
# repeat the timing a few times and use the best time.  The -i option is
# good for this.
# On Python3, a new time.perf_counter function picks the best available
# timer, so we use that if we can, else fall back as per above.

try:
    Now = time.perf_counter
except AttributeError:
    if sys.platform == 'win32':
        Now = time.clock
    else:
        Now = time.time

opts, args = getopt.getopt(sys.argv[1:], 'hi:r:',
                           ['clock', 'func=', 'help',
                            'iterations=', 'time', 'runs='])

for o, a in opts:
    if o in ['--clock']:
        try:
            Now = time.clock
        except AttributeError:
            sys.stderr.write("time.clock unavailable on this Python\n")
            sys.exit(1)
    elif o in ['--func']:
        FunctionPrefix = a
    elif o in ['-h', '--help']:
        sys.stdout.write(Usage)
        sys.exit(0)
    elif o in ['-i', '--iterations']:
        Iterations = int(a)
    elif o in ['--time']:
        Now = time.time
    elif o in ['-r', '--runs']:
        Runs = int(a)

if len(args) != 1:
    sys.stderr.write("bench.py:  only one file argument must be specified\n")
    sys.stderr.write(Usage)
    sys.exit(1)


(bench_name,_) = os.path.splitext(args[0])
print(f"Bench: {bench_name} : {args[0]}")
results_filename = f"{bench_name}_results.csv"

with open(args[0], 'r') as f:
    exec(f.read())

try:
    FunctionList
except NameError:
    function_names = sorted([x for x in list(locals().keys()) if x[:4] == FunctionPrefix])
    lvars = locals()
    l = [lvars[f] for f in function_names]
    FunctionList = [f for f in l if isinstance(f, types.FunctionType)]

IterationList = [None] * Iterations


def timer(func, *args, **kw):
    results = []
    for i in range(Runs):
        start = Now()
        func(*args, **kw)
        finish = Now()
        results.append((finish - start) / Iterations)
    return results


results_dict = {}


def display(func, result_label, results):
    total = 0.0
    for r in results:
        total += r

    test_result = (total * 1e6) / len(results)
    print("    %8.3f" % (test_result), ':', result_label)
    if results_dict.get(func.__doc__, False):
        results_dict[func.__doc__][result_label] = test_result
    else:
        results_dict[func.__doc__] = { result_label: test_result}


for func in FunctionList:
    if func.__doc__:
        d = ' (' + func.__doc__ + ')'
    else:
        d = ''
    print(func.__name__ + d + ':')

    for label, args, kw in Data:
        r = timer(func, *args, **kw)
        # print(f"{label} {r}")
        display(func, label, r)

py_ver_string = "%d.%d"%(sys.version_info.major, sys.version_info.minor)


# pprint(results_dict)

tests = [label for label, args, kw in Data]
columns = ['Python Version', 'Implementation'] + tests
with open(results_filename, 'a') as r:
    print(",".join(columns), file=r)

    for implementation in results_dict:
        print(f'{py_ver_string},"{implementation}"', file=r, end='')
        for test in tests:
            print(',%8.3f' % results_dict[implementation][test], file=r, end='')
        print(file=r)
