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
that Java files are created in the specified output directory.
"""

import TestSCons

test = TestSCons.TestSCons()

swig = test.where_is('swig')

if not swig:
    test.skip_test('Can not find installed "swig", skipping test.\n')

where_java_include=test.java_where_includes()

if not where_java_include:
    test.skip_test('Can not find installed Java include files, skipping test.\n')

test.write(['SConstruct'], """\
env = Environment(tools = ['default', 'swig'],
                CPPPATH=%(where_java_include)s,                 
                )

Java_foo_interface = env.SharedLibrary(
    'Java_foo_interface', 
    'Java_foo_interface.i', 
    SWIGOUTDIR = 'java/build dir',
    SWIGFLAGS = '-c++ -java -Wall',
    SWIGCXXFILESUFFIX = "_wrap.cpp")
""" % locals())

test.write('Java_foo_interface.i', """\
%module foopack
""")

# SCons should realize that it needs to create the "java/build dir"
# subdirectory to hold the generated .java files.
test.run(arguments = '.')

test.must_exist('java/build dir/foopackJNI.java')
test.must_exist('java/build dir/foopack.java') 

# SCons should remove the built .java files.
test.run(arguments = '-c')

test.must_not_exist('java/build dir/foopackJNI.java')
test.must_not_exist('java/build dir/foopack.java') 

# SCons should realize it needs to rebuild the removed .java files.
test.not_up_to_date(arguments = '.')

test.must_exist('java/build dir/foopackJNI.java')
test.must_exist('java/build dir/foopack.java') 


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
