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

import TestSCons
import os

python = TestSCons.python

test = TestSCons.TestSCons()

where_javac, java_version = test.java_where_javac()

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
if curver >= (1, 8):
    test.skip_test('The found version of javac is higher than 1.7, skipping test.\n')


where_java = test.java_where_java()
where_rmic = test.java_where_rmic()

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
env = Environment(tools = ['javac', 'rmic'],
                  JAVAC = r'"%s"',
                  RMIC = r'"%s"')
classes = env.Java(target = 'classes', source = 'src')
# Brute-force removal of the "Hello" class.
classes = [c for c in classes if str(c).find('Hello') == -1]
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

    static final long serialVersionUID = 0;

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

    static final long serialVersionUID = 0;

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

test.must_not_exist(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Stub.class'))
test.must_not_exist(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Stub.class'))

test.must_exist    (test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Stub.class'))
test.must_exist    (test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Stub.class'))

# We used to check for _Skel.class files as well, but they're not
# generated by default starting with Java 1.5, and they apparently
# haven't been needed for a while.  Don't bother looking, even if we're
# running Java 1.4.  If we think they're needed but they don't exist
# the variou test.up_to_date() calls below will detect it.
#test.must_not_exist(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Skel.class'))
#test.must_exist    (test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Skel.class'))
#test.must_exist    (test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Skel.class'))

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

    static final long serialVersionUID = 0;

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

    static final long serialVersionUID = 0;

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

expect = [
    ' src' + os.sep + 'Foo1.java src' + os.sep + 'Foo2.java',
    ' com.sub.foo.Foo1 com.sub.foo.Foo2',
]

test.must_contain_all_lines(test.stdout(), expect)

# XXX I'd rather run the resulting class files through the JVM here to
# see that they were built from the proper work1 sources, but I don't
# know how to do that with RMI, so punt for now.

test.must_not_exist(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Stub.class'))
test.must_not_exist(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Stub.class'))
test.must_exist    (test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Stub.class'))
test.must_exist    (test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Stub.class'))

#test.must_not_exist(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Skel.class'))
#test.must_not_exist(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Skel.class'))
#test.must_exist    (test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Skel.class'))
#test.must_exist    (test.workpath('work1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Skel.class'))

test.up_to_date(chdir = 'work1', options = opts, arguments = ".")

#
test.writable('rep1', 1)

test.run(chdir = 'rep1', options = opts, arguments = ".")

# XXX I'd rather run the resulting class files through the JVM here to
# see that they were built from the proper work1 sources, but I don't
# know how to do that with RMI, so punt for now.

test.must_exist(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Stub.class'))
test.must_exist(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Stub.class'))

#test.must_exist(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo1_Skel.class'))
#test.must_exist(test.workpath('rep1', 'outdir', 'com', 'sub', 'foo', 'Foo2_Skel.class'))

test.up_to_date(chdir = 'rep1', options = opts, arguments = ".")

#
test.writable('repository', 0)

#
test.up_to_date(chdir = 'work2', options = opts, arguments = ".")

#
test.write(['work3', 'SConstruct'], """
env = Environment(tools = ['javac', 'rmic'],
                  JAVAC = r'"%s"',
                  RMIC = r'"%s"')
classes = env.Java(target = 'classes', source = 'src')
# Brute-force removal of the "Hello" class.
classes = [c for c in classes if str(c).find('Hello') == -1]
rmi_classes = env.RMIC(target = 'outdir', source = classes)
Local(rmi_classes)
""" % (javac, rmic))

test.run(chdir = 'work3', options = opts, arguments = ".")

test.must_not_exist(test.workpath('work3', 'classes', 'com', 'sub', 'foo', 'Hello.class'))
test.must_not_exist(test.workpath('work3', 'classes', 'com', 'sub', 'foo', 'Foo1.class'))
test.must_not_exist(test.workpath('work3', 'classes', 'com', 'sub', 'foo', 'Foo2.class'))

test.must_exist    (test.workpath('work3', 'outdir', 'com', 'sub', 'foo', 'Foo1_Stub.class'))
test.must_exist    (test.workpath('work3', 'outdir', 'com', 'sub', 'foo', 'Foo2_Stub.class'))

#test.must_exist    (test.workpath('work3', 'outdir', 'com', 'sub', 'foo', 'Foo1_Skel.class'))
#test.must_exist    (test.workpath('work3', 'outdir', 'com', 'sub', 'foo', 'Foo2_Skel.class'))

test.up_to_date(chdir = 'work3', options = opts, arguments = ".")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
