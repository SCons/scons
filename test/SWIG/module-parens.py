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

import sys
import TestSCons

test = TestSCons.TestSCons()

swig = test.where_is('swig')
if not swig:
    test.skip_test('Can not find installed "swig", skipping test.\n')

python, python_include, python_libpath, python_lib = \
             test.get_platform_python_info(python_h_required=True)

# swig-python expects specific filenames.
# the platform specific suffix won't necessarily work.
if sys.platform == 'win32':
    _dll = '.pyd'
else:
    _dll   = '.so'

# On Windows, build a 32-bit exe if on 32-bit python.
if sys.platform == 'win32' and sys.maxsize <= 2**32:
    swig_arch_var="TARGET_ARCH='x86',"
else:
    swig_arch_var=""

test.write(['SConstruct'], """\
env = Environment(SWIGFLAGS = '-python -c++',
                  %(swig_arch_var)s
                  CPPPATH=[r'%(python_include)s'],
                  SWIG=[r'%(swig)s'],
                  LIBPATH=[r'%(python_libpath)s'],
                  LIBS='%(python_lib)s',
                  LDMODULESUFFIX='%(_dll)s',
                  )

env.LoadableModule('test1', ['test1.i', 'test1.cc'])
env.LoadableModule('test2', ['test2.i', 'test2.cc'])
""" % locals())

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

# Note that both tests use directors, so a file *_wrap.h should be generated
# in each case. If the emitter does not correctly allow for this, the test will
# not be up to date.
test.must_exist('test1_wrap.h')
test.must_exist('test2_wrap.h')
test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
