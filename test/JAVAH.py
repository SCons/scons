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
import string
import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.write('myjavah.py', r"""
import sys
args = sys.argv[1:]
while args:
    a = args[0]
    if a == '-d':
        args = args[1:]
    elif a == '-sourcepath':
        args = args[1:]
    else:
        break
    args = args[1:]
for file in args:
    infile = open(file, 'rb')
    outfile = open(file[:-5] + '.class', 'wb')
    for l in infile.readlines():
        if l[:9] != '/*javah*/':
            outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(tools = ['javah'],
                  JAVAH = r'%s myjavah.py')
env.JavaH(target = 'test1.class', source = 'test1.java')
""" % (python))

test.write('test1.java', """\
test1.java
/*javah*/
line 3
""")

#test.run(arguments = '.', stderr = None)

#test.fail_test(test.read('test1.class') != "test1.java\nline 3\n")

if os.path.normcase('.java') == os.path.normcase('.JAVA'):

    test.write('SConstruct', """\
env = Environment(tools = ['javah'],
                  JAVAH = r'%s myjavah.py')
env.Java(target = 'test2.class', source = 'test2.JAVA')
""" % python)

    test.write('test2.JAVA', """\
test2.JAVA
/*javah*/
line 3
""")

    test.run(arguments = '.', stderr = None)

    test.fail_test(test.read('test2.class') != "test2.JAVA\nline 3\n")


if not os.path.exists('/usr/local/j2sdk1.3.1/bin/javah'):
    print "Could not find Java, skipping test(s)."
    test.pass_test(1)



test.write("wrapper.py", """\
import os
import string
import sys
open('%s', 'ab').write("wrapper.py %%s\\n" %% string.join(sys.argv[1:]))
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

test.write('SConstruct', """
foo = Environment(tools = ['javac', 'javah'],
                  JAVAC = '/usr/local/j2sdk1.3.1/bin/javac',
                  JAVAH = '/usr/local/j2sdk1.3.1/bin/javah')
javah = foo.Dictionary('JAVAH')
bar = foo.Copy(JAVAH = r'%s wrapper.py ' + javah)
fff = foo.Java(target = 'class1', source = 'com/sub/foo')
bar_classes = bar.Java(target = 'class2', source = 'com/sub/bar')
foo_classes = foo.Java(target = 'class3', source = 'src')
foo.JavaH(target = 'outdir1',
          source = ['class1/com/sub/foo/Example1.class',
                    'class1/com/other/Example2',
                    'class1/com/sub/foo/Example3'],
          JAVACLASSDIR = 'class1')
bar.JavaH(target = 'outdir2', source = bar_classes)
foo.JavaH(target = File('output.h'), source = foo_classes)
""" % python)

test.subdir('com',
            ['com', 'sub'],
            ['com', 'sub', 'foo'],
            ['com', 'sub', 'bar'],
            'src')

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
package com.other;

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
package com.other;

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

test.write(['src', 'Test.java'], """\
class Empty {
}

interface Listener {
  public void execute();
}

public
class
Test {
  class Inner {
    void go() {
      use(new Listener() {
        public void execute() {
          System.out.println("In Inner");
        }
      });
    }
    String s1 = "class A";
    String s2 = "new Listener() { }";
    /* class B */
    /* new Listener() { } */
  }

  public static void main(String[] args) {
    new Test().run();
  }

  void run() {
    use(new Listener() {
      public void execute() {
        use(new Listener( ) {
          public void execute() {
            System.out.println("Inside execute()");
          }
        });
      }
    });

    new Inner().go();
  }

  void use(Listener l) {
    l.execute();
  }
}

class Private {
  void run() {
    new Listener() {
      public void execute() {
      }
    };
  }
}
""")

test.run(arguments = '.')

test.fail_test(test.read('wrapper.out') != "wrapper.py /usr/local/j2sdk1.3.1/bin/javah -d outdir2 -classpath class2 com.sub.bar.Example4 com.other.Example5 com.sub.bar.Example6\n")

test.fail_test(not os.path.exists(test.workpath('outdir1', 'com_sub_foo_Example1.h')))
test.fail_test(not os.path.exists(test.workpath('outdir1', 'com_other_Example2.h')))
test.fail_test(not os.path.exists(test.workpath('outdir1', 'com_sub_foo_Example3.h')))

test.fail_test(not os.path.exists(test.workpath('outdir2', 'com_sub_bar_Example4.h')))
test.fail_test(not os.path.exists(test.workpath('outdir2', 'com_other_Example5.h')))
test.fail_test(not os.path.exists(test.workpath('outdir2', 'com_sub_bar_Example6.h')))

test.up_to_date(arguments = '.')

test.pass_test()
