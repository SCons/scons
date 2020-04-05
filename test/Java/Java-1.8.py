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
Test Java compilation with a live Java 1.8 "javac" compiler.
"""

import os
import sys

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()
test.dir_fixture('java_version_image')

version = '1.8'
where_javac, java_version = test.java_where_javac(version)
javac_path=os.path.dirname(where_javac)

if ' ' in javac_path:
    javac_path ='"%s"'%javac_path
java_arguments=["--javac_path=%s"%javac_path,"--java_version=%s"%version]

test.run(arguments = ['.']+java_arguments)

expect_1 = [
    test.workpath('class1', 'com', 'other', 'Example2.class'),
    test.workpath('class1', 'com', 'sub', 'foo', 'Example1.class'),
    test.workpath('class1', 'com', 'sub', 'foo', 'Example3.class'),
]

expect_2 = [
    test.workpath('class2', 'com', 'other', 'Example5.class'),
    test.workpath('class2', 'com', 'sub', 'bar', 'Example4.class'),
    test.workpath('class2', 'com', 'sub', 'bar', 'Example6.class'),
]

expect_3 = [
    test.workpath('class3', 'Empty.class'),
    test.workpath('class3', 'Example7.class'),
    test.workpath('class3', 'Listener.class'),
    test.workpath('class3', 'Private$1.class'),
    test.workpath('class3', 'Private.class'),
    test.workpath('class3', 'Test$1$1.class'),
    test.workpath('class3', 'Test$1.class'),
    test.workpath('class3', 'Test$Inner$1.class'),
    test.workpath('class3', 'Test$Inner.class'),
    test.workpath('class3', 'Test.class'),
]

expect_4 = [
    test.workpath('class4', 'NestedExample$1$1.class'),
    test.workpath('class4', 'NestedExample$1.class'),
    test.workpath('class4', 'NestedExample.class'),
]

expect_5 = [
    test.workpath('class5', 'Foo.class'),
    test.workpath('class5', 'TestSCons.class'),
]

expect_6 = [
    test.workpath('class6', 'test$1.class'),
    test.workpath('class6', 'test$inner.class'),
    test.workpath('class6', 'test.class'),
]

failed = None

def classes_must_match(dir, expect):
    global failed
    got = test.java_get_class_files(test.workpath(dir))
    if expect != got:
        sys.stderr.write("Expected the following class files in '%s':\n" % dir)
        for c in expect:
            sys.stderr.write('    %s\n' % c)
        sys.stderr.write("Got the following class files in '%s':\n" % dir)
        for c in got:
            sys.stderr.write('    %s\n' % c)
        failed = 1

def classes_must_not_exist(dir, expect):
    global failed
    present = [path for path in expect if os.path.exists(path)]
    if present:
        sys.stderr.write("Found the following unexpected class files in '%s' after cleaning:\n" % dir)
        for c in present:
            sys.stderr.write('    %s\n' % c)
        failed = 1

classes_must_match('class1', expect_1)
classes_must_match('class2', expect_2)
classes_must_match('class3', expect_3)
classes_must_match('class4', expect_4)
classes_must_match('class5', expect_5)
classes_must_match('class6', expect_6)

test.fail_test(failed)

test.up_to_date(options=["--debug=explain"]+java_arguments,
                arguments = '.')

test.run(arguments = ['-c','.']+java_arguments)

classes_must_not_exist('class1', expect_1)
classes_must_not_exist('class2', expect_2)
classes_must_not_exist('class3', expect_3)
classes_must_not_exist('class4', expect_4)
classes_must_not_exist('class5', expect_5)
# This test case should pass, but doesn't.
# The expect_6 list contains the class files that the Java compiler
# actually creates, apparently because of the "private" instantiation
# of the "inner" class.  Our parser doesn't currently detect this, so
# it doesn't know to remove that generated class file.
#classes_must_not_exist('class6', expect_6)

test.fail_test(failed)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
