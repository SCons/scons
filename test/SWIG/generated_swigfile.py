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
Verify that SCons realizes the -noproxy option means no .py file will
be created.
"""

import sys

import TestSCons

# swig-python expects specific filenames.
# the platform specific suffix won't necessarily work.
if sys.platform == 'win32':
    _dll = '.dll'
else:
    _dll   = '.so'

# swig-python expects specific filenames.
# the platform specific suffix won't necessarily work.
if sys.platform == 'win32':
    _dll = '.dll'
else:
    _dll   = '.so'

test = TestSCons.TestSCons()

swig = test.where_is('swig')
if not swig:
    test.skip_test('Can not find installed "swig", skipping test.\n')

python, python_include, python_libpath, python_lib = \
             test.get_platform_python_info(python_h_required=True)

# handle testing on other platforms:
ldmodule_prefix = '_'


test.write('SConstruct', """
foo = Environment(CPPPATH=[r'%(python_include)s'],
                  SWIG=[r'%(swig)s'],
                  LIBPATH=[r'%(python_libpath)s'],
                  )
python_interface = foo.Command( 'test_py_swig.i', Value(1), 'echo %%module test_py_swig  > test_py_swig.i' )
python_c_file    = foo.CFile( target='python_swig_test',source=python_interface, SWIGFLAGS = '-python -c++' )
java_interface  = foo.Command( 'test_java_swig.i', Value(1),'echo %%module test_java_swig > test_java_swig.i' )
java_c_file     = foo.CFile( target='java_swig_test'  ,source=java_interface, SWIGFLAGS = '-java -c++' )

""" % locals())

expected_stdout = """\
echo %%module test_java_swig > test_java_swig.i
%(swig)s -o java_swig_test_wrap.cc -java -c++ test_java_swig.i
echo %%module test_py_swig > test_py_swig.i
%(swig)s -o python_swig_test_wrap.cc -python -c++ test_py_swig.i
""" % locals()
test.run(arguments = '.',stdout=test.wrap_stdout(expected_stdout))


# If we mistakenly depend on the .py file that SWIG didn't create
# (suppressed by the -noproxy option) then the build won't be up-to-date.
test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
