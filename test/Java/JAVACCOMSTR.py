#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

"""
Test that the $JAVACCOMSTR construction variable allows you to configure
the javac output.
"""

import os.path

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('src')

test.file_fixture('mycompile.py')

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(
    TOOLS=['default', 'javac'],
    JAVACCOM=r'%(_python_)s mycompile.py javac $TARGET $SOURCES',
    JAVACCOMSTR="Compiling class(es) $TARGET from $SOURCES",
)
env.Java(target='classes', source='src')
""" % locals())

test.write(['src', 'file1.java'], "file1.java\n/*javac*/\n")
test.write(['src', 'file2.java'], "file2.java\n/*javac*/\n")
test.write(['src', 'file3.java'], "file3.java\n/*javac*/\n")

classes_file1_class = os.path.join('classes', 'file1.class')
src_file1_java= os.path.join('src', 'file1.java')
src_file2_java= os.path.join('src', 'file2.java')
src_file3_java= os.path.join('src', 'file3.java')

test.run(stdout = test.wrap_stdout("""\
Compiling class(es) %(classes_file1_class)s from %(src_file1_java)s %(src_file2_java)s %(src_file3_java)s
""" % locals()))

test.must_match(['classes', 'file1.class'],
                "file1.java\nfile2.java\nfile3.java\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
