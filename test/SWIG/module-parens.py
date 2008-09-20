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

"""
Verify that we handle %module(directors="1") statements, both with and
without white space before the opening parenthesis.
"""

import os.path
import TestSCons

test = TestSCons.TestSCons()

swig = test.where_is('swig')

if not swig:
    test.skip_test('Can not find installed "swig", skipping test.\n')

python_include_dir = test.get_python_inc()

python_frameworks_flags = test.get_python_frameworks_flags()

Python_h = os.path.join(python_include_dir, 'Python.h')
if not os.path.exists(Python_h):
    test.skip_test('Can not find %s, skipping test.\n' % Python_h)

test.write(['SConstruct'], """\
env = Environment(SWIGFLAGS = '-python -c++',
                  CPPPATH=r"%(python_include_dir)s",
                  SWIG=r'%(swig)s',
		  FRAMEWORKS='%(python_frameworks_flags)s',
		  )

import sys
if sys.version[0] == '1':
    # SWIG requires the -classic flag on pre-2.0 Python versions.
    env.Append(SWIGFLAGS = ' -classic')

env.LoadableModule('test1.so', ['test1.i', 'test1.cc'])
env.LoadableModule('test2.so', ['test2.i', 'test2.cc'])
env.Clean('.', ['test1_wrap.h', 'test2_wrap.h'])  ### SEE NOTE BELOW
""" % locals())
# NOTE: For some reason, this test on OS X is unstable.  The first time 'scons'
# is run, it works as expected.  However, when 'scons' is run again, the
# 'test?_wrap.os' files are rebuilt.  (When run a third time, it correctly
# determines that nothing is to be rebuilt.)  When 'scons -c' is run, the
# 'test?_wrap.h' files are not removed, meaning that they are not identified
# by the emitter.  Mentioning the two files in the SConscript file stabilizes
# the runs and makes the test reliable.  When whatever that is causing this
# instability is chased down and cured, this hack should be removed.

test.write(['test1.cc'], """\
int test1func()
{
  return 0;
}
""")

test.write(['test1.h'], """\
int test1func();
""")

test.write(['test1.i'], """\
%module(directors="1") test1

%{
#include "test1.h"
%}

%include "test1.h"
""")

test.write(['test2.cc'], """\
int test2func()
{
  return 0;
}
""")

test.write(['test2.h'], """\
int test2func();
""")

test.write(['test2.i'], """\
%module (directors="1") test2

%{
#include "test2.h"
%}

%include "test2.h"
""")

test.run(arguments = '.')

test.up_to_date(arguments = '.')

test.pass_test()
