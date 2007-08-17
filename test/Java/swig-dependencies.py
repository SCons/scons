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
Verify that dependencies on SWIG-generated .java files work correctly.

Test case courtesy Jonathan (toolshed@tigris.org).
"""

import TestSCons

test = TestSCons.TestSCons()

ENV = test.java_ENV()
if test.detect_tool('javac', ENV=ENV):
    where_javac = test.detect('JAVAC', 'javac', ENV=ENV)
else:
    where_javac = test.where_is('javac')
if not where_javac:
    test.skip_test("Could not find Java javac, skipping test(s).\n")

if test.detect_tool('jar', ENV=ENV):
    where_jar = test.detect('JAR', 'jar', ENV=ENV)
else:
    where_jar = test.where_is('jar')
if not where_jar:
    test.skip_test("Could not find Java jar, skipping test(s).\n")


test.subdir(['foo'],
            ['java'],
            ['java', 'build'])

test.write(['SConstruct'], """\
import os

env = Environment(ENV = os.environ)

env.Append(CPPFLAGS = ' -g -Wall')
        
Export('env')

SConscript('#foo/SConscript')
SConscript('#java/SConscript')
""")

test.write(['foo', 'SConscript'], """\
Import('env')

env.SharedLibrary('foo', 'foo.cpp')
""")

test.write(['foo', 'foo.cpp'], """\
#include "foo.h"

int fooAdd(int a, int b) {
	return a + b;
}
""")

test.write(['foo', 'foo.h'], """\
int fooAdd(int, int);
""")

test.write(['java', 'Java_foo_interface.i'], """\
#include "foo.h"

%module foopack
""")

test.write(['java', 'SConscript'], """\
import os

Import('env')

# unnecessary?
env = env.Copy()

env.Prepend(CPPPATH = ['#foo',])

libadd = ['foo',]

libpath = ['#foo',]

#swigflags = '-c++ -java -Wall -package foopack -Ifoo'
swigflags = '-c++ -java -Wall -Ifoo'

Java_foo_interface = env.SharedLibrary(
    'Java_foo_interface', 
    'Java_foo_interface.i', 
    LIBS = libadd, 
    LIBPATH = libpath, 
    SWIGFLAGS = swigflags, 
    SWIGOUTDIR = Dir('build'),
    SWIGCXXFILESUFFIX = "_wrap.cpp")

foopack_jar_javac = env.Java('classes', 'build')

env['JARCHDIR'] = 'java/classes'
foopack_jar = env.Jar(target = 'foopack.jar', source = 'classes')
""")

test.run(arguments = '.')

#test.must_exist(['java', 'classes', 'foopack', 'foopack.class'])
#test.must_exist(['java', 'classes', 'foopack', 'foopackJNI.class'])
test.must_exist(['java', 'classes', 'foopack.class'])
test.must_exist(['java', 'classes', 'foopackJNI.class'])

test.up_to_date(arguments = '.')

test.pass_test()
