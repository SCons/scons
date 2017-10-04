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

import os

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('myjar.py', r"""
import sys
args = sys.argv[1:]
while args:
    a = args[0]
    if a == 'cf':
        out = args[1]
        args = args[1:]
    else:
        break
    args = args[1:]
outfile = open(out, 'w')
for file in args:
    infile = open(file, 'r')
    for l in infile.readlines():
        if l[:7] != '/*jar*/':
            outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(tools = ['jar'],
                  JAR = r'%(_python_)s myjar.py')
env.Jar(target = 'test1.jar', source = 'test1.class')
""" % locals())

test.write('test1.class', """\
test1.class
/*jar*/
line 3
""")

test.run(arguments='.', stderr=None)

test.must_match('test1.jar', "test1.class\nline 3\n", mode='r')

if os.path.normcase('.class') == os.path.normcase('.CLASS'):

    test.write('SConstruct', """
env = Environment(tools = ['jar'],
                  JAR = r'%(_python_)s myjar.py')
env.Jar(target = 'test2.jar', source = 'test2.CLASS')
""" % locals())

    test.write('test2.CLASS', """\
test2.CLASS
/*jar*/
line 3
""")

    test.run(arguments='.', stderr=None)

    test.must_match('test2.jar', "test2.CLASS\nline 3\n", mode='r')

test.write('myjar2.py', r"""
import sys
f=open(sys.argv[2], 'w')
f.write(" ".join(sys.argv[1:]))
f.write("\n")
f.close()
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(tools = ['jar'],
                  JAR = r'%(_python_)s myjar2.py',
                  JARFLAGS='cvf')
env.Jar(target = 'classes.jar', source = [ 'testdir/bar.class',
                                           'foo.mf' ],
        TESTDIR='testdir',
        JARCHDIR='$TESTDIR')
""" % locals())

test.subdir('testdir')
test.write(['testdir', 'bar.class'], 'foo')
test.write('foo.mf',
           """Manifest-Version : 1.0
           blah
           blah
           blah
           """)
test.run(arguments='classes.jar')
test.must_match('classes.jar',
                'cvfm classes.jar foo.mf -C testdir bar.class\n', mode='r')



where_javac, java_version = test.java_where_javac()
where_jar = test.java_where_jar()



test.file_fixture('wrapper_with_args.py')

test.write('SConstruct', """
foo = Environment(tools = ['javac', 'jar'],
                  JAVAC = r'%(where_javac)s',
                  JAR = r'%(where_jar)s')
jar = foo.Dictionary('JAR')
bar = foo.Clone(JAR = r'%(_python_)s wrapper_with_args.py ' + jar)
foo_classes = foo.Java(target = 'classes', source = 'com/sub/foo')
bar_classes = bar.Java(target = 'classes', source = 'com/sub/bar')
foo.Jar(target = 'foo', source = foo_classes)
bar.Jar(target = 'bar', source = bar_classes)
""" % locals())

test.subdir('com',
            ['com', 'sub'],
            ['com', 'sub', 'foo'],
            ['com', 'sub', 'bar'])

test.write(['com', 'sub', 'foo', 'Example1.java'], """\
package com.sub.foo;

public class Example1
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com', 'sub', 'foo', 'Example2.java'], """\
package com.sub.foo;

public class Example2
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com', 'sub', 'foo', 'Example3.java'], """\
package com.sub.foo;

public class Example3
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com', 'sub', 'bar', 'Example4.java'], """\
package com.sub.bar;

public class Example4
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com', 'sub', 'bar', 'Example5.java'], """\
package com.sub.bar;

public class Example5
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com', 'sub', 'bar', 'Example6.java'], """\
package com.sub.bar;

public class Example6
{

     public static void main(String[] args)
     {

     }

}
""")

test.run(arguments = '.')

expected_wrapper_out = "wrapper_with_args.py %(where_jar)s cf bar.jar -C classes com/sub/bar/Example4.class -C classes com/sub/bar/Example5.class -C classes com/sub/bar/Example6.class\n"
expected_wrapper_out = expected_wrapper_out.replace('/', os.sep)
test.must_match('wrapper.out',
                expected_wrapper_out % locals(), mode='r')

test.must_exist('foo.jar')
test.must_exist('bar.jar')

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
