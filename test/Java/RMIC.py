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

test.write('myrmic.py', r"""
import os
import sys
args = sys.argv[1:]
while args:
    a = args[0]
    if a == '-d':
        outdir = args[1]
        args = args[1:]
    elif a == '-classpath':
        args = args[1:]
    elif a == '-sourcepath':
        args = args[1:]
    else:
        break
    args = args[1:]
for file in args:
    infile = open(file, 'r')
    outfile = open(os.path.join(outdir, file[:-5] + '.class'), 'w')
    for l in infile.readlines():
        if l[:8] != '/*rmic*/':
            outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(tools = ['rmic'],
                  RMIC = r'%(_python_)s myrmic.py')
env.RMIC(target = 'outdir', source = 'test1.java')
""" % locals())

test.write('test1.java', """\
test1.java
/*rmic*/
line 3
""")

test.run(arguments = '.', stderr = None)

test.must_match(['outdir', 'test1.class'], "test1.java\nline 3\n", mode='r')

if os.path.normcase('.java') == os.path.normcase('.JAVA'):

    test.write('SConstruct', """\
env = Environment(tools = ['rmic'],
                  RMIC = r'%(_python_)s myrmic.py')
env.RMIC(target = 'outdir', source = 'test2.JAVA')
""" % locals())

    test.write('test2.JAVA', """\
test2.JAVA
/*rmic*/
line 3
""")

    test.run(arguments = '.', stderr = None)

    test.must_match(['outdir', 'test2.class'], "test2.JAVA\nline 3\n", mode='r')

where_javac, java_version = test.java_where_javac()
where_rmic = test.java_where_rmic()

# Try to get the major/minor Java version 
curver = (1, 0)
if java_version.count('.') == 1:
    # Check Java version
    major, minor = java_version.split('.')
    try:
        curver = (int(major), int(minor))
    except:
        pass

# Check the version of the found Java compiler.
# If it's 1.8 or higher, we skip the further RMIC test
# because we'll get warnings about the deprecated API...
# it's just not state-of-the-art anymore.
# Recent java versions (9 and greater) are back to being
# marketed as a simple version, but java_where_javac() will
# still return a dotted version, like 10.0. If this changes,
# will need to rework this rule.
# Note, how we allow simple version strings like "5" and
# "6" to successfully pass this test.
if curver < (1, 8):
    test.file_fixture('wrapper_with_args.py')

    test.write('SConstruct', """
foo = Environment(tools = ['javac', 'rmic'],
                  JAVAC = r'%(where_javac)s',
                  RMIC = r'%(where_rmic)s')
foo.Java(target = 'class1', source = 'com/sub/foo')
foo.RMIC(target = 'outdir1',
          source = ['class1/com/sub/foo/Example1.class',
                    'class1/com/sub/foo/Example2'],
          JAVACLASSDIR = 'class1')

rmic = foo.Dictionary('RMIC')
bar = foo.Clone(RMIC = r'%(_python_)s wrapper_with_args.py ' + rmic)
bar_classes = bar.Java(target = 'class2', source = 'com/sub/bar')
# XXX This is kind of a Python brute-force way to do what Ant
# does with its "excludes" attribute.  We should probably find
# a similar friendlier way to do this.
bar_classes = [c for c in bar_classes if str(c).find('Hello') == -1]
bar.RMIC(target = Dir('outdir2'), source = bar_classes)
""" % locals() )

    test.subdir('com',
                ['com', 'other'],
                ['com', 'sub'],
                ['com', 'sub', 'foo'],
                ['com', 'sub', 'bar'],
                'src3a',
                'src3b')
    
    test.write(['com', 'sub', 'foo', 'Hello.java'], """\
package com.sub.foo;

import java.rmi.Remote;
import java.rmi.RemoteException;

public interface Hello extends Remote {
    String sayHello() throws RemoteException;
}
""")

    test.write(['com', 'sub', 'foo', 'Example1.java'], """\
package com.sub.foo;

import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.RMISecurityManager;
import java.rmi.server.UnicastRemoteObject;

public class Example1 extends UnicastRemoteObject implements Hello {

    static final long serialVersionUID = 0;

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

    test.write(['com', 'sub', 'foo', 'Example2.java'], """\
package com.sub.foo;

import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.RMISecurityManager;
import java.rmi.server.UnicastRemoteObject;

public class Example2 extends UnicastRemoteObject implements Hello {

    static final long serialVersionUID = 0;

    public Example2() throws RemoteException {
        super();
    }

    public String sayHello() {
        return "Hello World!";
    }

    public static void main(String args[]) {
        if (System.getSecurityManager() == null) {
            System.setSecurityManager(new RMISecurityManager());
        }

        try {
            Example2 obj = new Example2();

            Naming.rebind("//myhost/HelloServer", obj);

            System.out.println("HelloServer bound in registry");
        } catch (Exception e) {
            System.out.println("Example2 err: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
""")

    test.write(['com', 'sub', 'bar', 'Hello.java'], """\
package com.sub.bar;

import java.rmi.Remote;
import java.rmi.RemoteException;

public interface Hello extends Remote {
    String sayHello() throws RemoteException;
}
""")

    test.write(['com', 'sub', 'bar', 'Example3.java'], """\
package com.sub.bar;

import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.RMISecurityManager;
import java.rmi.server.UnicastRemoteObject;

public class Example3 extends UnicastRemoteObject implements Hello {

    static final long serialVersionUID = 0;

    public Example3() throws RemoteException {
        super();
    }

    public String sayHello() {
        return "Hello World!";
    }

    public static void main(String args[]) {
        if (System.getSecurityManager() == null) {
            System.setSecurityManager(new RMISecurityManager());
        }

        try {
            Example3 obj = new Example3();

            Naming.rebind("//myhost/HelloServer", obj);

            System.out.println("HelloServer bound in registry");
        } catch (Exception e) {
            System.out.println("Example3 err: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
""")

    test.write(['com', 'sub', 'bar', 'Example4.java'], """\
package com.sub.bar;

import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.RMISecurityManager;
import java.rmi.server.UnicastRemoteObject;

public class Example4 extends UnicastRemoteObject implements Hello {

    static final long serialVersionUID = 0;

    public Example4() throws RemoteException {
        super();
    }

    public String sayHello() {
        return "Hello World!";
    }

    public static void main(String args[]) {
        if (System.getSecurityManager() == null) {
            System.setSecurityManager(new RMISecurityManager());
        }

        try {
            Example4 obj = new Example4();

            Naming.rebind("//myhost/HelloServer", obj);

            System.out.println("HelloServer bound in registry");
        } catch (Exception e) {
            System.out.println("Example4 err: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
""")

    test.run(arguments = '.')
    
    test.must_match('wrapper.out',
                    "wrapper_with_args.py %s -d outdir2 -classpath class2 com.sub.bar.Example3 com.sub.bar.Example4\n" % where_rmic,
                    mode='r')
    
    test.must_exist(test.workpath('outdir1', 'com', 'sub', 'foo', 'Example1_Stub.class'))
    test.must_exist(test.workpath('outdir1', 'com', 'sub', 'foo', 'Example2_Stub.class'))
    test.must_exist(test.workpath('outdir2', 'com', 'sub', 'bar', 'Example3_Stub.class'))
    test.must_exist(test.workpath('outdir2', 'com', 'sub', 'bar', 'Example4_Stub.class'))
    
    # We used to check for _Skel.class files as well, but they're not
    # generated by default starting with Java 1.5, and they apparently
    # haven't been needed for a while.  Don't bother looking, even if we're
    # running Java 1.4.  If we think they're needed but they don't exist
    # the test.up_to_date() call below will detect it.
    #test.must_exist(test.workpath('outdir1', 'com', 'sub', 'foo', 'Example1_Skel.class'))
    #test.must_exist(test.workpath('outdir1', 'com', 'sub', 'foo', 'Example2_Skel.class'))
    #test.must_exist(test.workpath('outdir2', 'com', 'sub', 'bar', 'Example3_Skel.class'))
    #test.must_exist(test.workpath('outdir2', 'com', 'sub', 'bar', 'Example4_Skel.class'))
    
    test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
