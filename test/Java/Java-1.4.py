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
Test Java compilation with a live Java 1.4 "javac" compiler.
"""

import os
import os.path
import string
import sys
import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

ENV = test.java_ENV()

if test.detect_tool('javac', ENV=ENV):
    where_javac = test.detect('JAVAC', 'javac', ENV=ENV)
else:
    where_javac = test.where_is('javac')
if not where_javac:
    test.skip_test("Could not find Java javac, skipping test(s).\n")



test.write('SConstruct', """
env = Environment(tools = ['javac'],
                  JAVAVERSION = '1.4',
                  JAVAC = r'%(where_javac)s')
env.Java(target = 'class1', source = 'com/sub/foo')
env.Java(target = 'class2', source = 'com/sub/bar')
env.Java(target = 'class3', source = ['src1', 'src2'])
env.Java(target = 'class4', source = ['src4'])
env.Java(target = 'class5', source = ['src5'])
""" % locals())

test.subdir('com',
            ['com', 'sub'],
            ['com', 'sub', 'foo'],
            ['com', 'sub', 'bar'],
            'src1',
            'src2',
            'src4',
            'src5')

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

test.write(['src1', 'Example7.java'], """\
public class Example7
{

     public static void main(String[] args)
     {

     }

}
""")

# Acid-test file for parsing inner Java classes, courtesy Chad Austin.
test.write(['src2', 'Test.java'], """\
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

# Testing nested anonymous inner classes, courtesy Brandon Mansfield.
test.write(['src4', 'NestedExample.java'], """\
// import java.util.*;

public class NestedExample
{
        public NestedExample()
        {
                Thread t = new Thread() {
                        public void start()
                        {
                                Thread t = new Thread() {
                                        public void start()
                                        {
                                                try {Thread.sleep(200);}
                                                catch (Exception e) {}
                                        }
                                };
                                while (true)
                                {
                                        try {Thread.sleep(200);}
                                        catch (Exception e) {}
                                }
                        }
                };
        }


        public static void main(String argv[])
        {
                NestedExample e = new NestedExample();
        }
}
""")

# Test not finding an anonymous class when the second token after a
# "new" is a closing brace.  This duplicates a test from the unit tests,
# but lets us make sure that we correctly determine that everything is
# up-to-date after the build.
test.write(['src5', 'TestSCons.java'], """\
class TestSCons {
    public static void main(String[] args) {
        Foo[] fooArray = new Foo[] { new Foo() };
    }
}

class Foo { }
""")

test.run(arguments = '.')

def get_class_files(dir):
    def find_class_files(arg, dirname, fnames):
        for fname in fnames:
            if fname[-6:] == '.class':
                arg.append(os.path.join(dirname, fname))
    result = []
    os.path.walk(dir, find_class_files, result)
    result.sort()
    return result

classes_1 = get_class_files(test.workpath('class1'))
classes_2 = get_class_files(test.workpath('class2'))
classes_3 = get_class_files(test.workpath('class3'))
classes_4 = get_class_files(test.workpath('class4'))
classes_5 = get_class_files(test.workpath('class5'))

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
    test.workpath('class3', 'Test$1.class'),
    test.workpath('class3', 'Test$2.class'),
    test.workpath('class3', 'Test$3.class'),
    test.workpath('class3', 'Test$Inner.class'),
    test.workpath('class3', 'Test.class'),
]

expect_4 = [
    test.workpath('class4', 'NestedExample$1.class'),
    test.workpath('class4', 'NestedExample$2.class'),
    test.workpath('class4', 'NestedExample.class'),
]

expect_5 = [
    test.workpath('class5', 'Foo.class'),
    test.workpath('class5', 'TestSCons.class'),
]

failed = None

def classes_must_match(dir, expect, got):
    if expect != got:
        sys.stderr.write("Expected the following class files in '%s':\n" % dir)
        for c in expect:
            sys.stderr.write('    %s\n' % c)
        sys.stderr.write("Got the following class files in '%s':\n" % dir)
        for c in got:
            sys.stderr.write('    %s\n' % c)
        failed = 1

classes_must_match('class1', expect_1, classes_1)
classes_must_match('class2', expect_2, classes_2)
classes_must_match('class3', expect_3, classes_3)
classes_must_match('class4', expect_4, classes_4)

test.fail_test(failed)

test.up_to_date(options='--debug=explain', arguments = '.')

test.pass_test()
