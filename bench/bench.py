#!/usr/bin/env python
#
# __COPYRIGHT__
#
# A script for timing snippets of Python code.
#
# By default, this script will execute a single Python file specified on
# the command line and time any functions in a list named "FunctionList"
# set by the Python file under test, or (by default) time any functions
# in the file whose names begin with "Func".
#
# All functions are assumed to get passed the same arguments, and the
# inputs are specified in a list named "Data," each element of which
# is a list consisting of a tag name, a list of positional arguments,
# and a dictionary of keyword arguments.
#
# Each function is expected to test a single, comparable snippet of
# of Python code.  IMPORTANT:  We want to test the timing of the code
# itself, not Python function call overhead, so every function should
# put its code under test within the following block:
#
#       for i in IterationList:
#
# This will allow (as much as possible) us to time just the code itself,
# not Python function call overhead.

import getopt
import sys
import time
import types

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

# The function used to get the current time.  The default of time.time is
# good on most UNIX systems, but time.clock (selectable via the --clock
# option) is better on Windows and some other UNIX systems.

Now = time.time


opts, args = getopt.getopt(sys.argv[1:], 'hi:r:',
                           ['clock', 'func=', 'help',
                            'iterations=', 'time', 'runs='])

for o, a in opts:
    if o in ['--clock']:
        Now = time.clock
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


execfile(args[0])


try:
    FunctionList
except NameError:
    function_names = filter(lambda x: x[:4] == FunctionPrefix, locals().keys())
    function_names.sort()
    l = map(lambda f, l=locals(): l[f], function_names)
    FunctionList = filter(lambda f: type(f) == types.FunctionType, l)

IterationList = [None] * Iterations

def timer(func, *args, **kw):
    results = []
    for i in range(Runs):
        start = Now()
        apply(func, args, kw)
        finish = Now()
        results.append((finish - start) / Iterations)
    return results

def display(label, results):
    total = reduce(lambda x, y: x+y, results, 0.0)
    print "    %8.3f" % ((total * 1e6) / len(results)), ':', label

for func in FunctionList:
    if func.__doc__: d = ' (' + func.__doc__ + ')'
    else: d = ''
    print func.__name__ + d + ':'

    for label, args, kw in Data:
        r = apply(timer, (func,)+args, kw)
        display(label, r)
