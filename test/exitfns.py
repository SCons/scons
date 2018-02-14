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
import os
test = TestSCons.TestSCons()

# also exclude these tests since it overides the exit function which doesnt work with coverage 
# # more info here: https://coverage.readthedocs.io/en/coverage-4.4.2/subprocess.html#
# TODO: figure out how to cover tests which use exit functions
if test.coverage_run():
    test.skip_test("This test replaces the exit function which is needed by coverage to write test data; skipping test.")

sconstruct = """
from SCons.exitfuncs import *

def x1():
    print("running x1")
def x2(n):
    print("running x2(%s)" % repr(n))
def x3(n, kwd=None):
    print("running x3(%s, kwd=%s)" % (repr(n), repr(kwd)))

register(x3, "no kwd args")
register(x1)
register(x2, 12)
register(x3, 5, kwd="bar")
register(x3, "no kwd args")

"""

expected_output = test.wrap_stdout("scons: `.' is up to date.\n") + \
"""running x3('no kwd args', kwd=None)
running x3(5, kwd='bar')
running x2(12)
running x1
running x3('no kwd args', kwd=None)
"""

test.write('SConstruct', sconstruct)

test.run(arguments='-f SConstruct .', stdout = expected_output)

test.write('SConstruct', """import sys
def f():
    pass

sys.exitfunc = f
""" + sconstruct)

test.run(arguments='-f SConstruct .', stdout = expected_output)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
