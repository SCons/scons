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



test.write('myjavac.py', r"""
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
        if l[:9] != '/*javac*/':
            outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(tools = ['javac'],
                  JAVAC = r'%s myjavac.py')
env.Java(target = '.', source = '.')
""" % (python))

test.write('test1.java', """\
test1.java
/*javac*/
line 3
""")

test.run(arguments = '.', stderr = None)

test.fail_test(test.read('test1.class') != "test1.java\nline 3\n")

if os.path.normcase('.java') == os.path.normcase('.JAVA'):

    test.write('SConstruct', """\
env = Environment(tools = ['javac'],
                  JAVAC = r'%s myjavac.py')
env.Java(target = '.', source = '.')
""" % python)

    test.write('test2.JAVA', """\
test2.JAVA
/*javac*/
line 3
""")

    test.run(arguments = '.', stderr = None)

    test.fail_test(test.read('test2.class') != "test2.JAVA\nline 3\n")


if not os.path.exists('/usr/local/j2sdk1.3.1/bin/javac'):
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
foo = Environment(tools = ['javac'],
                  JAVAC = '/usr/local/j2sdk1.3.1/bin/javac')
javac = foo.Dictionary('JAVAC')
bar = foo.Copy(JAVAC = r'%s wrapper.py ' + javac)
foo.Java(target = 'classes', source = 'com/sub/foo')
bar.Java(target = 'classes', source = 'com/sub/bar')
foo.Java(target = 'classes', source = 'src')
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

# Acid-test file for parsing inner Java classes, courtesy Chad Austin.
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

test.fail_test(test.read('wrapper.out') != "wrapper.py /usr/local/j2sdk1.3.1/bin/javac -d classes -sourcepath com/sub/bar com/sub/bar/Example4.java com/sub/bar/Example5.java com/sub/bar/Example6.java\n")

test.fail_test(not os.path.exists(test.workpath('classes', 'com', 'sub', 'foo', 'Example1.class')))
test.fail_test(not os.path.exists(test.workpath('classes', 'com', 'other', 'Example2.class')))
test.fail_test(not os.path.exists(test.workpath('classes', 'com', 'sub', 'foo', 'Example3.class')))

test.fail_test(not os.path.exists(test.workpath('classes', 'com', 'sub', 'bar', 'Example4.class')))
test.fail_test(not os.path.exists(test.workpath('classes', 'com', 'other', 'Example5.class')))
test.fail_test(not os.path.exists(test.workpath('classes', 'com', 'sub', 'bar', 'Example6.class')))

test.fail_test(not os.path.exists(test.workpath('classes', 'Empty.class')))
test.fail_test(not os.path.exists(test.workpath('classes', 'Listener.class')))
test.fail_test(not os.path.exists(test.workpath('classes', 'Private.class')))
test.fail_test(not os.path.exists(test.workpath('classes', 'Private$1.class')))
test.fail_test(not os.path.exists(test.workpath('classes', 'Test.class')))
test.fail_test(not os.path.exists(test.workpath('classes', 'Test$1.class')))
test.fail_test(not os.path.exists(test.workpath('classes', 'Test$2.class')))
test.fail_test(not os.path.exists(test.workpath('classes', 'Test$3.class')))
test.fail_test(not os.path.exists(test.workpath('classes', 'Test$Inner.class')))

test.up_to_date(arguments = '.')

test.pass_test()
