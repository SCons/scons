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
Verify that use of $JAVASOURCEPATH allows finding Java .class
files in alternate locations by adding the -classpath option
to the javac command line.
"""

import pathlib

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

where_javac, java_version = test.java_where_javac()
where_javah = test.java_where_javah()

# TODO rework for 'javac -h', for now skip
# The logical test would be:  if java_version > 9:
# but java_where_javah() roots around and will find from an older version
if not test.Environment().WhereIs('javah'):
    test.skip_test("No Java javah for version > 9, skipping test.\n")

# On some systems, the alternatives system does not remove javah even if the
# preferred Java doesn't have it, so try another check
javacdir = pathlib.Path(where_javac).parent
javahdir = pathlib.Path(where_javah).parent
if javacdir != javahdir:
    test.skip_test("Cannot find Java javah matching javac, skipping test.\n")

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(tools=['javac', 'javah'])
j1 = env.Java(target='class1', source='com.1/Example1.java')
j2 = env.Java(target='class2', source='com.2/Example2.java')
env.JavaH(target='outdir', source=[j1, j2], JAVACLASSPATH='class2')
""" % locals())

test.subdir('com.1', 'com.2')

test.write(['com.1', 'Example1.java'], """\
package com;

public class Example1
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com.2', 'Example2.java'], """\
package com;

public class Example2
{

     public static void main(String[] args)
     {

     }

}
""")

test.run(arguments = '.')

test.must_exist(['class1', 'com', 'Example1.class'])
test.must_exist(['class2', 'com', 'Example2.class'])

test.must_exist(['outdir', 'com_Example1.h'])
test.must_exist(['outdir', 'com_Example2.h'])

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
