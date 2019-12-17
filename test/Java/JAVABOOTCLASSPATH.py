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
Verify that use of $JAVABOOTCLASSPATH sets the -bootclasspath option
on javac compilations.
"""

import os

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

where_javac, java_version = test.java_where_javac()
where_javah = test.java_where_javah()

test.write('SConstruct', """
env = Environment(tools = ['javac', 'javah'],
                  JAVABOOTCLASSPATH = ['dir1', 'dir2'])
j1 = env.Java(target = 'class', source = 'com/Example1.java')
j2 = env.Java(target = 'class', source = 'com/Example2.java')
""" % locals())

test.subdir('com')

test.write(['com', 'Example1.java'], """\
package com;

public class Example1
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com', 'Example2.java'], """\
package com;

public class Example2
{

     public static void main(String[] args)
     {

     }

}
""")

# Setting -bootclasspath messes with the Java runtime environment, so
# we'll just take the easy way out and examine the -n output to see if
# the expected option shows up on the command line.

bootclasspath = os.pathsep.join(['dir1', 'dir2'])

expect = """\
javac -bootclasspath %(bootclasspath)s -d class -sourcepath com com.Example1\\.java
javac -bootclasspath %(bootclasspath)s -d class -sourcepath com com.Example2\\.java
""" % locals()

test.run(arguments = '-Q -n .', stdout = expect, match=TestSCons.match_re)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
