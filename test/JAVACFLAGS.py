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

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.subdir('src')

test.write('SConstruct', """
env = Environment(tools = ['javac'],
                  JAVAC = '/usr/local/j2sdk1.3.1/bin/javac',
                  JAVACFLAGS = '-O')
env.Java(target = 'classes', source = 'src')
""")

test.write(['src', 'Example1.java'], """\
package src;

public class Example1
{

     public static void main(String[] args)
     {

     }

}
""")

test.run(arguments = '.',
         stdout = test.wrap_stdout("/usr/local/j2sdk1.3.1/bin/javac -O -d classes -sourcepath src src/Example1.java\n"))

test.fail_test(not os.path.exists(test.workpath('classes', 'src', 'Example1.class')))

test.pass_test()
