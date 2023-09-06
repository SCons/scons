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

import os.path
import unittest
import fnmatch

import SCons.Scanner.IDL
import SCons.Tool.JavaCommon

import TestSCons

# Adding trace=trace to any of the parse_jave() calls below will cause
# the parser to spit out trace messages of the tokens it sees and the
# attendant transitions.

def trace(token, newstate) -> None:
    from SCons.Debug import Trace
    statename = newstate.__class__.__name__
    Trace('token = %s, state = %s\n' % (repr(token), statename))

class parse_javaTestCase(unittest.TestCase):

    def test_bare_bones(self) -> None:
        """Test a bare-bones class"""

        input = """\
package com.sub.bar;

public class Foo
{

     public static void main(String[] args)
     {

        /* This tests a former bug where strings would eat later code. */
        String hello1 = new String("Hello, world!");

     }

}
"""
        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input)
        assert pkg_dir == os.path.join('com', 'sub', 'bar'), pkg_dir
        assert classes == ['Foo'], classes


    def test_file_parser(self) -> None:
        """Test the file parser"""
        input = """\
package com.sub.bar;

public class Foo
{
     public static void main(String[] args)
     {
        /* This tests that unicde is handled . */
        String hello1 = new String("ఎత్తువెడల్పు");
     }
}
"""
        file_name = 'test_file_parser.java'
        with open(file_name, 'w', encoding='UTF-8') as jf:
            print(input, file=jf)

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java_file(file_name)
        if os.path.exists(file_name):
            os.remove(file_name)
        assert pkg_dir == os.path.join('com', 'sub', 'bar'), pkg_dir
        assert classes == ['Foo'], classes


    def test_dollar_sign(self) -> None:
        """Test class names with $ in them"""

        input = """\
public class BadDep {
  public void new$rand () {}
}
"""
        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input)
        assert pkg_dir is None, pkg_dir
        assert classes == ['BadDep'], classes



    def test_inner_classes(self) -> None:
        """Test parsing various forms of inner classes"""

        input = """\
class Empty {
}

interface Listener {
  public void execute();
}

public
class
Test implements Listener {
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

  class Inner2 {
     Inner2() { Listener l = new Listener(); }
  }

  /* Make sure this class doesn't get interpreted as an inner class of the previous one, when "new" is used in the previous class. */
  class Inner3 {

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
"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '1.4')
        assert pkg_dir is None, pkg_dir
        expect = [
                   'Empty',
                   'Listener',
                   'Test$1',
                   'Test$Inner',
                   'Test$Inner2',
                   'Test$Inner3',
                   'Test$2',
                   'Test$3',
                   'Test',
                   'Private$1',
                   'Private',
                 ]
        assert classes == expect, classes

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '1.5')
        assert pkg_dir is None, pkg_dir
        expect = [
                   'Empty',
                   'Listener',
                   'Test$Inner$1',
                   'Test$Inner',
                   'Test$Inner2',
                   'Test$Inner3',
                   'Test$1',
                   'Test$1$1',
                   'Test',
                   'Private$1',
                   'Private',
                 ]
        assert classes == expect, (expect, classes)

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '5')
        assert pkg_dir is None, pkg_dir
        expect = [
                   'Empty',
                   'Listener',
                   'Test$Inner$1',
                   'Test$Inner',
                   'Test$Inner2',
                   'Test$Inner3',
                   'Test$1',
                   'Test$1$1',
                   'Test',
                   'Private$1',
                   'Private',
                 ]
        assert classes == expect, (expect, classes)



    def test_comments(self) -> None:
        """Test a class with comments"""

        input = """\
package com.sub.foo;

import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.RMISecurityManager;
import java.rmi.server.UnicastRemoteObject;

public class Example1 extends UnicastRemoteObject implements Hello {

    public Example1() throws RemoteException {
        super();
    }

    public String sayHello() {
        return "Hello World!";
    }

    public static void main(String args[]) {
        if (System.getSecurityManager() == null) {
            System.setSecurityManager(new RMISecurityManager());
        }
        // a comment
        try {
            Example1 obj = new Example1();

            Naming.rebind("//myhost/HelloServer", obj);

            System.out.println("HelloServer bound in registry");
        } catch (Exception e) {
            System.out.println("Example1 err: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input)
        assert pkg_dir == os.path.join('com', 'sub', 'foo'), pkg_dir
        assert classes == ['Example1'], classes


    def test_arrays(self) -> None:
        """Test arrays of class instances"""

        input = """\
public class Test {
    MyClass abc = new MyClass();
    MyClass xyz = new MyClass();
    MyClass _array[] = new MyClass[] {
        abc,
        xyz
    }
}
"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input)
        assert pkg_dir is None, pkg_dir
        assert classes == ['Test'], classes



    def test_backslash(self) -> None:
        """Test backslash handling"""

        input = """\
public class MyTabs
{
        private class MyInternal
        {
        }
        private final static String PATH = "images\\\\";
}
"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input)
        assert pkg_dir is None, pkg_dir
        assert classes == ['MyTabs$MyInternal', 'MyTabs'], classes


    def test_enum(self) -> None:
        """Test the Java 1.5 enum keyword"""

        input = """\
package p;
public enum a {}
"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input)
        assert pkg_dir == 'p', pkg_dir
        assert classes == ['a'], classes


    def test_anon_classes(self) -> None:
        """Test anonymous classes"""

        input = """\
public abstract class TestClass
{
    public void completed()
    {
        new Thread()
        {
        }.start();

        new Thread()
        {
        }.start();
    }
}
"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input)
        assert pkg_dir is None, pkg_dir
        assert classes == ['TestClass$1', 'TestClass$2', 'TestClass'], classes


    def test_closing_bracket(self) -> None:
        """Test finding a closing bracket instead of an anonymous class"""

        input = """\
class TestSCons {
    public static void main(String[] args) {
        Foo[] fooArray = new Foo[] { new Foo() };
    }
}

class Foo { }
"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input)
        assert pkg_dir is None, pkg_dir
        assert classes == ['TestSCons', 'Foo'], classes


    def test_dot_class_attributes(self) -> None:
        """Test handling ".class" attributes"""

        input = """\
public class Test extends Object
{
    static {
        Class c = Object[].class;
        Object[] s = new Object[] {};
    }
}
"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input)
        assert classes == ['Test'], classes

        input = """\
public class A {
    public class B {
        public void F(Object[] o) {
            F(new Object[] {Object[].class});
        }
        public void G(Object[] o) {
            F(new Object[] {});
        }
    }
}
"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input)
        assert pkg_dir is None, pkg_dir
        assert classes == ['A$B', 'A'], classes

    def test_anonymous_classes_with_parentheses(self) -> None:
        """Test finding anonymous classes marked by parentheses"""

        input = """\
import java.io.File;

public class Foo {
    public static void main(String[] args) {
        File f = new File(
            new File("a") {
                public String toString() {
                    return "b";
                }
            } to String()
        ) {
            public String toString() {
                return "c";
            }
        };
    }
}
"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '1.4')
        assert classes == ['Foo$1', 'Foo$2', 'Foo'], classes

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '1.5')
        assert classes == ['Foo$1', 'Foo$1$1', 'Foo'], classes

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '6')
        assert classes == ['Foo$1', 'Foo$1$1', 'Foo'], classes



    def test_nested_anonymous_inner_classes(self) -> None:
        """Test finding nested anonymous inner classes"""

        input = """\
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
"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '1.4')
        expect = [ 'NestedExample$1', 'NestedExample$2', 'NestedExample' ]
        assert expect == classes, (expect, classes)

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '1.5')
        expect = [ 'NestedExample$1', 'NestedExample$1$1', 'NestedExample' ]
        assert expect == classes, (expect, classes)

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '6')
        expect = [ 'NestedExample$1', 'NestedExample$1$1', 'NestedExample' ]
        assert expect == classes, (expect, classes)

    def test_lambda_after_new(self) -> None:
        """Test lamdas after new"""

        input = """\
// import java.util.*;

public class LamdaExample
{

    public void testFunc (int arg1, String arg2, Runnable lambda){
    }
    public LamdaExample()
    {
        testFunc(
            5,
            new String("test"),
            // Lambda symbol is after new, and used curly braces so
            // we should not parse this as a new class.
            () -> {}
        );
    }


    public static void main(String argv[])
    {
            LamdaExample e = new LamdaExample();
    }
}
"""
        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '1.4')
        expect = [ 'LamdaExample' ]
        assert expect == classes, (expect, classes)

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '1.8')
        expect = [ 'LamdaExample' ]
        assert expect == classes, (expect, classes)

    def test_private_inner_class_instantiation(self) -> None:
        """Test anonymous inner class generated by private instantiation"""

        input = """\
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
"""

        # This is what we *should* generate, apparently due to the
        # private instantiation of the inner class, but don't today.
        #expect = [ 'test$1', 'test$inner', 'test' ]

        # What our parser currently generates, which doesn't match
        # what the Java compiler actually generates.
        expect = [ 'test$inner', 'test' ]

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '1.4')
        assert expect == classes, (expect, classes)

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '1.5')
        assert expect == classes, (expect, classes)

    def test_floating_point_numbers(self) -> None:
        """Test floating-point numbers in the input stream"""
        input = """
// Broken.java
class Broken
{
  /**
   * Detected.
   */
  Object anonymousInnerOK = new Runnable() { public void run () {} };

  /**
   * Detected.
   */
  class InnerOK { InnerOK () { } }

  {
    System.out.println("a number: " + 1000.0 + "");
  }

  /**
   * Not detected.
   */
  Object anonymousInnerBAD = new Runnable() { public void run () {} };

  /**
   * Not detected.
   */
  class InnerBAD { InnerBAD () { } }
}
"""

        expect = ['Broken$1', 'Broken$InnerOK', 'Broken$2', 'Broken$InnerBAD', 'Broken']

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '1.4')
        assert expect == classes, (expect, classes)

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '1.5')
        assert expect == classes, (expect, classes)


    def test_genercis(self) -> None:
        """Test that generics don't interfere with detecting anonymous classes"""

        input = """\
import java.util.Date;
import java.util.Comparator;

public class Foo
{
  public void foo()
  {
    Comparator<Date> comp = new Comparator<Date>()
      {
        static final long serialVersionUID = 1L;
        public int compare(Date lhs, Date rhs)
        {
          return 0;
        }
      };
  }
}
"""

        expect = [ 'Foo$1', 'Foo' ]

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '1.6')
        assert expect == classes, (expect, classes)

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '6')
        assert expect == classes, (expect, classes)


    def test_in_function_class_declaration(self) -> None:
        """
        Test that implementing a class in a function call doesn't confuse SCons.
        """

        input = """
package com.Matthew;

public class AnonDemo {

    public static void main(String[] args) {
        new AnonDemo().execute();
    }

    public void execute() {
        Foo bar = new Foo(new Foo() {
            @Override
            public int getX() { return this.x; }
        }) {
            @Override
            public int getX() { return this.x; }
        };
    }

    public abstract class Foo {
        public int x;
        public abstract int getX();

        public Foo(Foo f) {
            this.x = f.x;
        }

        public Foo() {}
    }
}
"""
        expect = ['AnonDemo$1',
                  'AnonDemo$2',
                  'AnonDemo$Foo',
                  'AnonDemo']
        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java(input, '1.8')
        assert expect == classes, (expect, classes)

    def test_jdk_globs(self) -> None:
        """
        Verify that the java path globs work with specific examples.
        :return:
        """
        from SCons.Tool.JavaCommon import (
            java_linux_include_dirs_glob,
            java_linux_version_include_dirs_glob,
            java_win32_dir_glob,
            java_win32_version_dir_glob,
            java_macos_include_dir_glob,
            java_macos_version_include_dir_glob,
        )

        # Test windows globs
        win_java_dirs = [
            (r'C:/Program Files/Java/jdk1.8.0_201/bin', '1.8.0'),
            (r'C:/Program Files/Java/jdk-11.0.2/bin', '11.0.2'),
            (r'C:/Program Files/AdoptOpenJDK/jdk-16.0.1.9-hotspot/bin', '16.0.1'),
            (r'C:/Program Files/Microsoft/jdk-17.0.0.35-hotspot/bin', '17.0.0'),
            (r'C:/Program Files/OpenJDK/openjdk-11.0.13_8/bin', '11.0.13'),
            (r'C:/Program Files/RedHat/java-1.8.0-openjdk-1.8.0.312-1/bin', '1.8.0'),
            (r'C:/Program Files/RedHat/java-11-openjdk-11.0.13-1/bin', '11.0.13'),
        ]

        for (wjd, version) in win_java_dirs:
            if not fnmatch.fnmatch(wjd, java_win32_dir_glob):
                self.fail(
                    "Didn't properly match %s with pattern %s"
                    % (wjd, java_win32_dir_glob)
                )
            if not fnmatch.fnmatch(wjd, java_win32_version_dir_glob % version):
                self.fail(
                    "Didn't properly match %s with version (%s) specific pattern %s"
                    % (wjd, version, java_win32_version_dir_glob % version)
                )

        non_win_java_include_dirs = [
            (
                '/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.191.b12-0.el7_5.x86_64/include',
                '1.8.0',
            ),
            ('/usr/lib/jvm/java-1.8.0-openjdk-amd64/include', '1.8.0'),
            ('/usr/lib/jvm/java-8-openjdk-amd64/include', '8'),
        ]

        # Test non-windows/non-macos globs
        for (wjd, version) in non_win_java_include_dirs:
            match = False
            globs_tried = []
            for jlig in java_linux_include_dirs_glob:
                globs_tried.append(jlig)

                if fnmatch.fnmatch(wjd, jlig):
                    match = True
                    break

            if not match:
                self.fail(
                    "Didn't properly match %s with pattern %s" % (wjd, globs_tried)
                )

            match = False
            globs_tried = []
            for jlvig in java_linux_version_include_dirs_glob:
                globs_tried.append(jlvig % version)
                if fnmatch.fnmatch(wjd, jlvig % version):
                    match = True
                    break

            if not match:
                self.fail(
                    "Didn't properly match %s with version (%s) specific pattern %s"
                    % (wjd, version, globs_tried)
                )

        # Test macos globs
        # Test windows globs
        macos_java_dirs = [
            # ('/System/Library/Frameworks/JavaVM.framework/Headers/', None),
            (
                '/System/Library/Frameworks/JavaVM.framework/Versions/11.0.2/Headers/',
                '11.0.2',
            ),
        ]

        if not fnmatch.fnmatch(
            '/System/Library/Frameworks/JavaVM.framework/Headers/',
            java_macos_include_dir_glob,
        ):
            self.fail(
                "Didn't properly match %s with pattern %s"
                % (
                    '/System/Library/Frameworks/JavaVM.framework/Headers/',
                    java_macos_include_dir_glob,
                )
            )

        for (wjd, version) in macos_java_dirs:
            if not fnmatch.fnmatch(wjd, java_macos_version_include_dir_glob % version):
                self.fail(
                    "Didn't properly match %s with version (%s) specific pattern %s"
                    % (wjd, version, java_macos_version_include_dir_glob % version)
                )


if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
