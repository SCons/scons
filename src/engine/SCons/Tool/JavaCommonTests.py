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

        assert pkg_dir is None, pkg_dir
        expect = [
                   'Empty',
                   'Listener',
                   'Test$1',
                   'Test$Inner',
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

if __name__ == "__main__":
    suite = unittest.TestSuite()
    tclasses = [ parse_javaTestCase ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(map(tclass, names))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
