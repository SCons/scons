#!/usr/bin/env python
#
# A script for timing snippets of Python code.

import time

Now = time.time
#Now = time.clock       # better on Windows, some UNIX/Linux systems

# How many times each snippet of code will be run by the functions
# to gather the time (the "inner loop").

Iterations = 10000

# How many times we'll run each function to collect its aggregate time
# and try to average out timing differences induced by system performance
# (the "outer loop").

Runs = 10

# The functions containing the code snippets to test and compare.
# This script will test any function whose name begins with the string
# "Func" and assumes that they all get passed the same arguments.
# Each function should put its snippet within a block:
#
#       for i in IterationList:
#
# So that (as much as possible) we're testing just the code itself,
# not Python function call overhead.

def Func1(var, gvars, lvars):
    for i in IterationList:
        try:
            x = lvars[var]
        except KeyError:
            try:
                x = gvars[var]
            except KeyError:
                x = ''

def Func2(var, gvars, lvars):
    for i in IterationList:
        if lvars.has_key(var):
            x = lvars[var]
        else:
            try:
                x = gvars[var]
            except KeyError:
                x = ''

def Func3(var, gvars, lvars):
    for i in IterationList:
        if lvars.has_key(var):
            x = lvars[var]
        elif gvars.has_key(var):
            x = gvars[var]
        else:
            x = ''

def Func4(var, gvars, lvars):
    for i in IterationList:
        try:
            x = eval(var, gvars, lvars)
        except NameError:
            x = ''

# Data to pass to the functions on each run.  Each entry is a
# three-element tuple:
#
#   (
#       "Label to print describing this data run",
#       ('positional', 'arguments'),
#       {'keyword' : 'arguments'},
#   ),

Data = [
    (
        "Neither in gvars or lvars",
        ('x', {}, {}),
        {},
    ),
    (
        "Missing from lvars, found in gvars",
        ('x', {'x':1}, {}),
        {},
    ),
    (
        "Found in lvars",
        ('x', {'x':1}, {'x':2}),
        {},
    ),
]



IterationList = [None]

def timer(func, *args, **kw):
    global IterationList
    IterationList = [None] * Iterations
    results = []
    for i in range(Runs):
        start = Now()
        func(*args, **kw)
        finish = Now()
        results.append((finish - start) / Iterations)
    return results

def display(label, results):
    print '    ' + label + ':'
    print '    ',
    for r in results:
        print "%.3f" % (r * 1e6),
    print

def display(label, results):
    total = reduce(lambda x, y: x+y, results, 0.0)
    print "    %8.3f" % ((total * 1e6) / len(results)), ':', label

func_names = filter(lambda x: x.startswith('Func'), locals().keys())
func_names.sort()

for f in func_names:
    func = locals()[f]
    print f + ':'

    for label, args, kw in Data:
        r = apply(timer, (func,)+args, kw)
        display(label, r)
