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

import unittest

import SCons.Tool.JavaCommon

class parse_javaTestCase(unittest.TestCase):

    def test_empty(self):
        """Test a bare-bones class"""

        pkg_dir, classes = SCons.Tool.JavaCommon.parse_java("""\
package com.sub.bar;

public class Foo
{

     public static void main(String[] args)
     {

     }

}
""")
        assert pkg_dir == 'com/sub/bar', pkg_dir
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

if __name__ == "__main__":
    suite = unittest.TestSuite()
    tclasses = [ parse_javaTestCase ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(map(tclass, names))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
