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
Test Java compilation with a live Java 1.4 "javac" compiler.
"""

import os
import sys

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

where_javac, java_version = test.java_where_javac('1.4')



test.write('SConstruct', """
env = Environment(tools = ['javac'],
                  JAVAVERSION = '1.4',
                  JAVAC = r'%(where_javac)s')
env.Java(target = 'class1', source = 'com/sub/foo')
env.Java(target = 'class2', source = 'com/sub/bar')
env.Java(target = 'class3', source = ['src1', 'src2'])
env.Java(target = 'class4', source = ['src4'])
env.Java(target = 'class5', source = ['src5'])
env.Java(target = 'class6', source = ['src6'])
""" % locals())

test.subdir('com',
            ['com', 'sub'],
            ['com', 'sub', 'foo'],
            ['com', 'sub', 'bar'],
            'src1',
            'src2',
            'src4',
            'src5',
            'src6')

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
                new Thread() {
                        public void start()
                        {
                                new Thread() {
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
                new NestedExample();
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
        new Foo();
    }
}

class Foo { }
""")

# Test private inner class instantiation, courtesy Tilo Prutz:
#   https://github.com/SCons/scons/issues/1594
test.write(['src6', 'TestSCons.java'], """\
class test
{
    test()
    {
        super();
        new inner();
    }

    static class inner
    {
        private inner() {}
    }
}
""")



test.run(arguments = '.')

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
        missing = set(expect) - set(got)
        if missing:
            sys.stderr.write("Missing the following class files from '%s':\n" % dir)
            for c in missing:
                sys.stderr.write('    %s\n' % c)
        unexpected = set(got) - set(expect)
        if unexpected:
            sys.stderr.write("Found the following unexpected class files in '%s':\n" % dir)
            for c in unexpected:
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

test.up_to_date(options='--debug=explain', arguments = '.')

test.run(arguments = '-c .')

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
