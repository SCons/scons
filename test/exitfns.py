#!/usr/bin/env python

__revision__ = "test/exitfns.py __REVISION__ __DATE__ __DEVELOPER__"

from TestCmd import TestCmd

test = TestCmd(program = 'scons.py',
               workdir = '',
               interpreter = 'python')

sconstruct = """
from scons.exitfuncs import *

def x1():
    print "running x1"
def x2(n):
    print "running x2(%s)" % `n`
def x3(n, kwd=None):
    print "running x3(%s, kwd=%s)" % (`n`, `kwd`)

register(x3, "no kwd args")
register(x1)
register(x2, 12)
register(x3, 5, kwd="bar")
register(x3, "no kwd args")

"""

expected_output = """running x3('no kwd args', kwd=None)
running x3(5, kwd='bar')
running x2(12)
running x1
running x3('no kwd args', kwd=None)
"""

test.write('SConstruct', sconstruct)

test.run(chdir = '.', arguments='-f SConstruct')

test.fail_test(test.stdout() != expected_output)

test.write('SConstruct', """import sys
def f():
    pass

sys.exitfunc = f
""" + sconstruct)

test.run(chdir = '.', arguments='-f SConstruct')

test.fail_test(test.stdout() != expected_output)

test.pass_test()
