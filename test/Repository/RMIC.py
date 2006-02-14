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
Test building Java applications when using Repositories.
"""

import os
import string
import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

ENV = test.java_ENV()

if test.detect_tool('javac', ENV=ENV):
    where_javac = test.detect('JAVAC', 'javac', ENV=ENV)
else:
    where_javac = test.where_is('javac')
if not where_javac:
    test.skip_test("Could not find Java javac, skipping test(s).\n")

if test.detect_tool('rmic', ENV=ENV):
    where_rmic = test.detect('JAVAC', 'rmic', ENV=ENV)
else:
    where_rmic = test.where_is('rmic')
if not where_rmic:
    test.skip_test("Could not find Java rmic, skipping non-simulated test(s).\n")

where_java = test.where_is('java')
if not where_java:
    test.skip_test("Could not find Java java, skipping test(s).\n")

java = where_java
javac = where_javac
rmic = where_rmic

###############################################################################

#
test.subdir('rep1', ['rep1', 'src'],
            'work1',
            'work2',
            'work3')

#
rep1_classes = test.workpath('rep1', 'classes')
work1_classes = test.workpath('work1', 'classes')
work3_classes = test.workpath('work3', 'classes')

#
opts = '-Y ' + test.workpath('rep1')

#
test.write(['rep1', 'SConstruct'], """
import string
env = Environment(tools = ['javac', 'rmic'],
                  JAVAC = r'%s',
                  RMIC = r'%s')
classes = env.Java(target = 'classes', source = 'src')
# Brute-force removal of the "Hello" class.
classes = filter(lambda c: string.find(str(c), 'Hello') == -1, classes)
env.RMIC(target = 'outdir', source = classes)
""" % (javac, rmic))

test.write(['rep1', 'src', 'Hello.java'], """\
package com.sub.foo;

import java.rmi.Remote;
import java.rmi.RemoteException;

public interface Hello extends Remote {
    String sayHello() throws RemoteException;
}
""")

test.write(['rep1', 'src', 'Foo1.java'], """\
package com.sub.foo;

import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.RMISecurityManager;
import java.rmi.server.UnicastRemoteObject;

public class Foo1 extends UnicastRemoteObject implements Hello {

    public Foo1() throws RemoteException {
        super();
    }

    public String sayHello() {
        return "rep1/src/Foo1.java";
    }

    public static void main(String args[]) {
        if (System.getSecurityManager() == null) {
            System.setSecurityManager(new RMISecurityManager());
        }

        try {
            Foo1 obj = new Foo1();

            Naming.rebind("//myhost/HelloServer", obj);

            System.out.println("HelloServer bound in registry");
        } catch (Exception e) {
            System.out.println("Foo1 err: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
""")

test.write(['rep1', 'src', 'Foo2.java'], """\
package com.sub.foo;

import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.RMISecurityManager;
import java.rmi.server.UnicastRemoteObject;

public class Foo2 extends UnicastRemoteObject implements Hello {

    public Foo2() throws RemoteException {
        super();
    }

    public String sayHello() {
        return "rep1/src/Foo2.java";
    }

    public static void main(String args[]) {
        if (System.getSecurityManager() == null) {
            System.setSecurityManager(new RMISecurityManager());
        }

        try {
            Foo2 obj = new Foo2();

            Naming.rebind("//myhost/HelloServer", obj);

            System.out.println("HelloServer bound in registry");
        } catch (Exception e) {
            System.out.println("Foo2 err: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
""")

# Make the repository non-writable,
# so we'll detect if we try to write into it accidentally.
test.writable('repository', 0)

#
test.run(chdir = 'work1', options = opts, arguments = ".")

# XXX I'd rather run the resulting class files through the JVM here to
# see that they were built from the proper rep1 sources, but I don't
# know how to do that with RMI, so punt for now.

test.fail_test(os.path.exists(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Skel.class')))
test.fail_test(os.path.exists(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Stub.class')))
test.fail_test(os.path.exists(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Skel.class')))
test.fail_test(os.path.exists(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Stub.class')))

test.fail_test(not os.path.exists(test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Skel.class')))
test.fail_test(not os.path.exists(test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Stub.class')))
test.fail_test(not os.path.exists(test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Skel.class')))
test.fail_test(not os.path.exists(test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Stub.class')))

test.up_to_date(chdir = 'work1', options = opts, arguments = ".")

#
test.subdir(['work1', 'src'])

test.write(['work1', 'src', 'Hello.java'], """\
package com.sub.foo;

import java.rmi.Remote;
import java.rmi.RemoteException;

public interface Hello extends Remote {
    String sayHello() throws RemoteException;
}
""")

test.write(['work1', 'src', 'Foo1.java'], """\
package com.sub.foo;

import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.RMISecurityManager;
import java.rmi.server.UnicastRemoteObject;

public class Foo1 extends UnicastRemoteObject implements Hello {

    public Foo1() throws RemoteException {
        super();
    }

    public String sayHello() {
        return "work1/src/Foo1.java";
    }

    public static void main(String args[]) {
        if (System.getSecurityManager() == null) {
            System.setSecurityManager(new RMISecurityManager());
        }

        try {
            Foo1 obj = new Foo1();

            Naming.rebind("//myhost/HelloServer", obj);

            System.out.println("HelloServer bound in registry");
        } catch (Exception e) {
            System.out.println("Foo1 err: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
""")

test.write(['work1', 'src', 'Foo2.java'], """\
package com.sub.foo;

import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.RMISecurityManager;
import java.rmi.server.UnicastRemoteObject;

public class Foo2 extends UnicastRemoteObject implements Hello {

    public Foo2() throws RemoteException {
        super();
    }

    public String sayHello() {
        return "work1/src/Foo2.java";
    }

    public static void main(String args[]) {
        if (System.getSecurityManager() == null) {
            System.setSecurityManager(new RMISecurityManager());
        }

        try {
            Foo2 obj = new Foo2();

            Naming.rebind("//myhost/HelloServer", obj);

            System.out.println("HelloServer bound in registry");
        } catch (Exception e) {
            System.out.println("Foo2 err: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
""")

test.run(chdir = 'work1', options = opts, arguments = ".")

test.fail_test(string.find(test.stdout(), ' src/Foo1.java src/Foo2.java') == -1)
test.fail_test(string.find(test.stdout(), ' com.sub.foo.Foo1 com.sub.foo.Foo2') == -1)

# XXX I'd rather run the resulting class files through the JVM here to
# see that they were built from the proper work1 sources, but I don't
# know how to do that with RMI, so punt for now.

test.fail_test(os.path.exists(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Skel.class')))
test.fail_test(os.path.exists(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Stub.class')))
test.fail_test(os.path.exists(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Skel.class')))
test.fail_test(os.path.exists(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Stub.class')))

test.fail_test(not os.path.exists(test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Skel.class')))
test.fail_test(not os.path.exists(test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Stub.class')))
test.fail_test(not os.path.exists(test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Skel.class')))
test.fail_test(not os.path.exists(test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Stub.class')))

test.up_to_date(chdir = 'work1', options = opts, arguments = ".")

#
test.writable('rep1', 1)

test.run(chdir = 'rep1', options = opts, arguments = ".")

# XXX I'd rather run the resulting class files through the JVM here to
# see that they were built from the proper work1 sources, but I don't
# know how to do that with RMI, so punt for now.

test.fail_test(not os.path.exists(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Skel.class')))
test.fail_test(not os.path.exists(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Stub.class')))
test.fail_test(not os.path.exists(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Skel.class')))
test.fail_test(not os.path.exists(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Stub.class')))

test.up_to_date(chdir = 'rep1', options = opts, arguments = ".")

#
test.writable('repository', 0)

#
test.up_to_date(chdir = 'work2', options = opts, arguments = ".")

#
test.write(['work3', 'SConstruct'], """
import string
env = Environment(tools = ['javac', 'rmic'],
                  JAVAC = r'%s',
                  RMIC = r'%s')
classes = env.Java(target = 'classes', source = 'src')
# Brute-force removal of the "Hello" class.
classes = filter(lambda c: string.find(str(c), 'Hello') == -1, classes)
rmi_classes = env.RMIC(target = 'outdir', source = classes)
Local(rmi_classes)
""" % (javac, rmic))

test.run(chdir = 'work3', options = opts, arguments = ".")

test.fail_test(os.path.exists(test.workpath('work3', 'classes', 'com', 'sub', 'foo', 'Hello.class')))
test.fail_test(os.path.exists(test.workpath('work3', 'classes', 'com', 'sub', 'foo', 'Foo1.class')))
test.fail_test(os.path.exists(test.workpath('work3', 'classes', 'com', 'sub', 'foo', 'Foo2.class')))

test.fail_test(not os.path.exists(test.workpath('work3', 'outdir', 'com', 'sub', 'foo', 'Foo1_Skel.class')))
test.fail_test(not os.path.exists(test.workpath('work3', 'outdir', 'com', 'sub', 'foo', 'Foo1_Stub.class')))
test.fail_test(not os.path.exists(test.workpath('work3', 'outdir', 'com', 'sub', 'foo', 'Foo2_Skel.class')))
test.fail_test(not os.path.exists(test.workpath('work3', 'outdir', 'com', 'sub', 'foo', 'Foo2_Stub.class')))

test.pass_test()
