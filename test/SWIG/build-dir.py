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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Make sure SWIG works when a VariantDir (or variant_dir) is used.

Test case courtesy Joe Maruszewski.
"""

import sys

import TestSCons

test = TestSCons.TestSCons()

swig = test.where_is('swig')
if not swig:
    test.skip_test('Can not find installed "swig", skipping test.\n')

# swig-python expects specific filenames.
# the platform specific suffix won't necessarily work.
if sys.platform == 'win32':
    _dll = '.dll'
else:
    _dll   = '.so'

test.subdir(['source'])

python, python_include, python_libpath, python_lib = \
             test.get_platform_python_info(python_h_required=True)

if sys.platform == 'win32' and sys.maxsize <= 2**32:
    swig_arch_var="TARGET_ARCH='x86',"
else:
    swig_arch_var=""

test.write(['SConstruct'], """\
#
# Create the build environment.
#
env = Environment(CPPPATH = [".", r'%(python_include)s'],
                  %(swig_arch_var)s
                  CPPDEFINES = "NDEBUG",
                  SWIG = [r'%(swig)s'],
                  SWIGFLAGS = ["-python", "-c++"],
                  SWIGCXXFILESUFFIX = "_wrap.cpp",
                  LDMODULEPREFIX='_',
                  LDMODULESUFFIX='%(_dll)s',
                  LIBPATH=[r'%(python_libpath)s'],
                  LIBS='%(python_lib)s',
                  )

Export("env")

#
# Build the libraries.
#
SConscript("source/SConscript", variant_dir = "build")
""" % locals())

test.write(['source', 'SConscript'], """\
Import("env")
lib = env.SharedLibrary("_linalg",
                        "linalg.i",
                        SHLIBPREFIX = "",
                        SHLIBSUFFIX = ".pyd")
""")

test.write(['source', 'Vector.hpp'], """\
class Vector
{
 public:
  Vector(int size = 0) : _size(size)
  {
    _v = new double[_size];
    for (int i = 0; i < _size; ++i)
      _v[i] = 0.0;
  }

  ~Vector() { delete [] _v; }

  int size() const { return _size; }

  double&        operator[](int key)       { return _v[key]; }
  double  const& operator[](int key) const { return _v[key]; }

 private:
  int _size;
  double* _v;
};
""")

test.write(['source', 'linalg.i'], """\
%module linalg
%{
#include <sstream>
#include "Vector.hpp"
%}


class Vector
{
public:
  Vector(int n = 0);
  ~Vector();

  %extend
  {
    const char* __str__() { return "linalg.Vector()"; }

    %pythoncode %{
    def __iter__(self):
        for i in range(len(self)):
            yield self[i]
    %}
  }
};
""")

test.write(['source', 'test.py'], """\
#!/usr/bin/env python
from __future__ import print_function

import linalg


x = linalg.Vector(5)
print(x)

x[1] = 99.5
x[3] = 8.3
x[4] = 11.1


for i, v in enumerate(x):
    print("\tx[%d] = %g" % (i, v))

""")

test.run(arguments = '.')

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
