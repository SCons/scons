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
Test that the $JAVACCOMSTR construction variable allows you to configure
the javac output.
"""

import os.path

import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.subdir('src')



test.write('myjavac.py', r"""
import sys
outfile = open(sys.argv[1], 'wb')
for f in sys.argv[2:]:
    infile = open(f, 'rb')
    for l in filter(lambda l: l != '/*javac*/\n', infile.readlines()):
        outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(TOOLS = ['default', 'javac'],
                  JAVACCOM = r'%(python)s myjavac.py $TARGET $SOURCES',
                  JAVACCOMSTR = "Compiling class(es) $TARGET from $SOURCES")
env.Java(target = 'classes', source = 'src')
""" % locals())

test.write(['src', 'file1.java'], "file1.java\n/*javac*/\n")
test.write(['src', 'file2.java'], "file2.java\n/*javac*/\n")
test.write(['src', 'file3.java'], "file3.java\n/*javac*/\n")

classes_src_file1_class = os.path.join('classes', 'src', 'file1.class')
src_file1_java= os.path.join('src', 'file1.java')
src_file2_java= os.path.join('src', 'file2.java')
src_file3_java= os.path.join('src', 'file3.java')

test.run(stdout = test.wrap_stdout("""\
Compiling class(es) %(classes_src_file1_class)s from %(src_file1_java)s %(src_file2_java)s %(src_file3_java)s
""" % locals()))

test.must_match(['classes', 'src', 'file1.class'],
                "file1.java\nfile2.java\nfile3.java\n")



test.pass_test()
