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
import sys
import unittest

import SCons.Tool.JavaCommon


# Adding this trace to any of the calls below to the parse_java() method
# will cause the parser to spit out trace messages of the tokens it sees
# and state transitions.

def trace(token, newstate):
    from SCons.Debug import Trace
    statename = newstate.__class__.__name__
    Trace('token = %s, state = %s\n' % (repr(token), statename))

class parse_javaTestCase(unittest.TestCase):

    def test_bare_bones(self):
        """Test a bare-bones class"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java("""\
package com.sub.bar;

public class Foo
{

     public static void main(String[] args)
     {

        /* This tests a former bug where strings would eat later code. */
        String hello1 = new String("Hello, world!");

     }

}
""")
        assert pkg_dir == os.path.join('com', 'sub', 'bar'), pkg_dir
        assert classes == ['Foo'], classes


    def test_inner_classes(self):
        """Test parsing various forms of inner classes"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java("""\
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
""")
    
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


    def test_comments(self):
        """Test a class with comments"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java("""\
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
""")

        assert pkg_dir == os.path.join('com', 'sub', 'foo'), pkg_dir
        assert classes == ['Example1'], classes


    def test_arrays(self):
        """Test arrays of class instances"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java("""\
public class Test {
    MyClass abc = new MyClass();
    MyClass xyz = new MyClass();
    MyClass _array[] = new MyClass[] {
        abc,
        xyz
    }
}
""")
        assert pkg_dir == None, pkg_dir
        assert classes == ['Test'], classes


# This test comes from bug report #1197470:
#
#    http://sourceforge.net/tracker/index.php?func=detail&aid=1194740&group_id=30337&atid=398971
#
# I've captured it here so that someone with a better grasp of Java syntax
# and the parse_java() state machine can uncomment it and fix it some day.
#
#    def test_arrays_in_decls(self):
#        """Test how arrays in method declarations affect class detection"""
#
#        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java("""\
#public class A {
#    public class B{
#        public void F(Object[] o) {
#            F(new Object[] {Object[].class});
#        }
#        public void G(Object[] o) {
#            F(new Object[] {});
#        }
#    }
#}
#""")
#        assert pkg_dir == None, pkg_dir
#        assert classes == ['A$B', 'A'], classes


    def test_backslash(self):
        """Test backslash handling"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java("""\
public class MyTabs
{
        private class MyInternal
        {
        }
        private final static String PATH = "images\\\\";
}
""")
        assert pkg_dir == None, pkg_dir
        assert classes == ['MyTabs$MyInternal', 'MyTabs'], classes


    def test_enum(self):
        """Test the Java 1.5 enum keyword"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java("""\
package p;
public enum a {}
""")
        assert pkg_dir == 'p', pkg_dir
        assert classes == ['a'], classes


    def test_anon_classes(self):
        """Test anonymous classes"""
        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java("""\
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
""")
        assert pkg_dir == None, pkg_dir
        assert classes == ['TestClass$1', 'TestClass$2', 'TestClass'], classes



if __name__ == "__main__":
    suite = unittest.TestSuite()
    tclasses = [ parse_javaTestCase ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(map(tclass, names))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
