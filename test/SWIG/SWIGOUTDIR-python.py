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
Verify that use of the $SWIGOUTDIR variable causes SCons to recognize
that Python files are created in the specified output directory.
"""

import TestSCons
import os

test = TestSCons.TestSCons()

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
                  SWIGOUTDIR='python/build dir',
                  FRAMEWORKS='%(python_frameworks_flags)s',
                 )

import sys
if sys.version[0] == '1':
    # SWIG requires the -classic flag on pre-2.0 Python versions.
    env.Append(SWIGFLAGS = ' -classic')

env.LoadableModule('python_foo_interface', 'python_foo_interface.i')
""" % locals())

test.write('python_foo_interface.i', """\
%module foopack
""")

# SCons should realize that it needs to create the "python/build dir"
# subdirectory to hold the generated .py files.
test.run(arguments = '.')

test.must_exist('python/build dir/foopack.py') 

# SCons should remove the built .py files.
test.run(arguments = '-c')

test.must_not_exist('python/build dir/foopack.py') 

# SCons should realize it needs to rebuild the removed .py files.
test.not_up_to_date(arguments = '.')

test.must_exist('python/build dir/foopack.py') 


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
