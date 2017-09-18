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
Test that the $SHCXXCOMSTR construction variable allows you to customize
the shared object C++ compilation output.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.file_fixture('mycompile.py')

alt_cpp_suffix=test.get_alt_cpp_suffix()

test.write('SConstruct', """
env = Environment(SHCXXCOM = r'%(_python_)s mycompile.py c++ $TARGET $SOURCE',
                  SHCXXCOMSTR = 'Building shared object $TARGET from $SOURCE',
                  SHOBJPREFIX='', SHOBJSUFFIX='.obj')
env.SharedObject(target = 'test1', source = 'test1.cpp')
env.SharedObject(target = 'test2', source = 'test2.cc')
env.SharedObject(target = 'test3', source = 'test3.cxx')
env.SharedObject(target = 'test4', source = 'test4.c++')
env.SharedObject(target = 'test5', source = 'test5.C++')
env.SharedObject(target = 'test6', source = 'test6%(alt_cpp_suffix)s')
""" % locals())

test.write('test1.cpp', "test1.cpp\n/*c++*/\n")
test.write('test2.cc',  "test2.cc\n/*c++*/\n")
test.write('test3.cxx', "test3.cxx\n/*c++*/\n")
test.write('test4.c++', "test4.c++\n/*c++*/\n")
test.write('test5.C++', "test5.C++\n/*c++*/\n")
test.write('test6'+alt_cpp_suffix, "test6.C\n/*c++*/\n")

test.run(stdout = test.wrap_stdout("""\
Building shared object test1.obj from test1.cpp
Building shared object test2.obj from test2.cc
Building shared object test3.obj from test3.cxx
Building shared object test4.obj from test4.c++
Building shared object test5.obj from test5.C++
Building shared object test6.obj from test6%(alt_cpp_suffix)s
""" % locals()))

test.must_match('test1.obj', "test1.cpp\n")
test.must_match('test2.obj', "test2.cc\n")
test.must_match('test3.obj', "test3.cxx\n")
test.must_match('test4.obj', "test4.c++\n")
test.must_match('test5.obj', "test5.C++\n")
test.must_match('test6.obj', "test6.C\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
