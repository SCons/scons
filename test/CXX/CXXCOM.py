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
Test the ability to configure the $CXXCOM construction variable.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.file_fixture('mycompile.py')

alt_cpp_suffix=test.get_alt_cpp_suffix()

test.write('SConstruct', """
env = Environment(CXXCOM = r'%(_python_)s mycompile.py c++ $TARGET $SOURCE',
                  OBJSUFFIX='.obj')
env.Object(target = 'test1', source = 'test1.cpp')
env.Object(target = 'test2', source = 'test2.cc')
env.Object(target = 'test3', source = 'test3.cxx')
env.Object(target = 'test4', source = 'test4.c++')
env.Object(target = 'test5', source = 'test5.C++')
env.Object(target = 'test6', source = 'test6%(alt_cpp_suffix)s')
""" % locals())

test.write('test1.cpp', "test1.cpp\n/*c++*/\n")
test.write('test2.cc',  "test2.cc\n/*c++*/\n")
test.write('test3.cxx', "test3.cxx\n/*c++*/\n")
test.write('test4.c++', "test4.c++\n/*c++*/\n")
test.write('test5.C++', "test5.C++\n/*c++*/\n")
test.write('test6'+alt_cpp_suffix, "test6.C\n/*c++*/\n")

test.run()

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
