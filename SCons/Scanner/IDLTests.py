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
import sys
import os
import os.path

import TestCmd
import TestUnit

import SCons.Scanner.IDL
import SCons.Node.FS
import SCons.Warnings

test = TestCmd.TestCmd(workdir = '')

os.chdir(test.workpath(''))

# create some source files and headers:

test.write('t1.idl','''
#include "f1.idl"
#include <f2.idl>
import "f3.idl";

[
        object,
        uuid(22995106-CE26-4561-AF1B-C71C6934B840),
        dual,
        helpstring("IBarObject Interface"),
        pointer_default(unique)
]
interface IBarObject : IDispatch
{
};
''')

test.write('t2.idl',"""
#include \"d1/f1.idl\"
#include <d2/f1.idl>
#include \"f1.idl\"
import <f3.idl>;

[
        object,
        uuid(22995106-CE26-4561-AF1B-C71C6934B840),
        dual,
        helpstring(\"IBarObject Interface\"),
        pointer_default(unique)
]
interface IBarObject : IDispatch
{
};
""")

test.write('t3.idl',"""
#include \t \"f1.idl\"
   \t #include \"f2.idl\"
#   \t include \"f3-test.idl\"

#include \t <d1/f1.idl>
   \t #include <d1/f2.idl>
#   \t include <d1/f3-test.idl>

import \t \"d1/f1.idl\"
   \t import \"d1/f2.idl\"

include \t \"never.idl\"
   \t include \"never.idl\"

// #include \"never.idl\"

const char* x = \"#include <never.idl>\"

[
        object,
        uuid(22995106-CE26-4561-AF1B-C71C6934B840),
        dual,
        helpstring(\"IBarObject Interface\"),
        pointer_default(unique)
]
interface IBarObject : IDispatch
{
};
""")

test.subdir('d1', ['d1', 'd2'])

headers = ['f1.idl','f2.idl', 'f3.idl', 'f3-test.idl', 'fi.idl', 'fj.idl', 'never.idl',
           'd1/f1.idl', 'd1/f2.idl', 'd1/f3-test.idl', 'd1/fi.idl', 'd1/fj.idl',
           'd1/d2/f1.idl', 'd1/d2/f2.idl', 'd1/d2/f3-test.idl',
           'd1/d2/f4.idl', 'd1/d2/fi.idl', 'd1/d2/fj.idl']

for h in headers:
    test.write(h, " ")

test.write('f2.idl',"""
#include "fi.idl"
""")

test.write('f3-test.idl',"""
#include <fj.idl>
""")


test.subdir('include', 'subdir', ['subdir', 'include'])

test.write('t4.idl',"""
#include \"fa.idl\"
#include <fb.idl>

[
        object,
        uuid(22995106-CE26-4561-AF1B-C71C6934B840),
        dual,
        helpstring(\"IBarObject Interface\"),
        pointer_default(unique)
]
interface IBarObject : IDispatch
{
};
""")

test.write(['include', 'fa.idl'], "\n")
test.write(['include', 'fb.idl'], "\n")
test.write(['subdir', 'include', 'fa.idl'], "\n")
test.write(['subdir', 'include', 'fb.idl'], "\n")

test.subdir('repository', ['repository', 'include'],
            ['repository', 'src' ])
test.subdir('work', ['work', 'src'])

test.write(['repository', 'include', 'iii.idl'], "\n")

test.write(['work', 'src', 'fff.c'], """
#include <iii.idl>
#include <jjj.idl>

int main(void)
{
    return 0;
}
""")

test.write([ 'work', 'src', 'aaa.c'], """
#include "bbb.idl"

int main(void)
{
   return 0;
}
""")

test.write([ 'work', 'src', 'bbb.idl'], "\n")

test.write([ 'repository', 'src', 'ccc.c'], """
#include "ddd.idl"

int main(void)
{
   return 0;
}
""")

test.write([ 'repository', 'src', 'ddd.idl'], "\n")

# define some helpers:

class DummyEnvironment:
    def __init__(self, listCppPath):
        self.path = listCppPath
        self.fs = SCons.Node.FS.FS(test.workpath(''))
        
    def Dictionary(self, *args):
        if not args:
            return { 'CPPPATH': self.path }
        elif len(args) == 1 and args[0] == 'CPPPATH':
            return self.path
        else:
            raise KeyError("Dummy environment only has CPPPATH attribute.")

    def subst(self, arg, target=None, source=None, conv=None):
        return arg

    def subst_path(self, path, target=None, source=None, conv=None):
        if not isinstance(path, list):
            path = [path]
        return list(map(self.subst, path))

    def has_key(self, key):
        return key in self.Dictionary()

    def __getitem__(self,key):
        return self.Dictionary()[key]

    def __setitem__(self,key,value):
        self.Dictionary()[key] = value

    def __delitem__(self,key):
        del self.Dictionary()[key]

    def get_calculator(self):
        return None

    def get_factory(self, factory):
        return factory or self.fs.File

    def Dir(self, filename):
        return self.fs.Dir(filename)

    def File(self, filename):
        return self.fs.File(filename)

global my_normpath
my_normpath = os.path.normpath

if os.path.normcase('foo') == os.path.normcase('FOO'):
    my_normpath = os.path.normcase

def deps_match(self, deps, headers):
    scanned = list(map(my_normpath, list(map(str, deps))))
    expect = list(map(my_normpath, headers))
    self.assertTrue(scanned == expect, "expect %s != scanned %s" % (expect, scanned))

# define some tests:

class IDLScannerTestCase1(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([])
        s = SCons.Scanner.IDL.IDLScan()
        path = s.path(env)
        deps = s(env.File('t1.idl'), env, path)
        headers = ['f1.idl', 'f3.idl', 'f2.idl']
        deps_match(self, deps, headers)

class IDLScannerTestCase2(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.IDL.IDLScan()
        path = s.path(env)
        deps = s(env.File('t1.idl'), env, path)
        headers = ['f1.idl', 'f3.idl', 'd1/f2.idl']
        deps_match(self, deps, headers)

class IDLScannerTestCase3(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.IDL.IDLScan()
        path = s.path(env)
        deps = s(env.File('t2.idl'), env, path)
        headers = ['d1/f1.idl', 'f1.idl', 'd1/d2/f1.idl', 'f3.idl']
        deps_match(self, deps, headers)

class IDLScannerTestCase4(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1"), test.workpath("d1/d2")])
        s = SCons.Scanner.IDL.IDLScan()
        path = s.path(env)
        deps = s(env.File('t2.idl'), env, path)
        headers =  ['d1/f1.idl', 'f1.idl', 'd1/d2/f1.idl', 'f3.idl']
        deps_match(self, deps, headers)
        
class IDLScannerTestCase5(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([])
        s = SCons.Scanner.IDL.IDLScan()
        path = s.path(env)

        n = env.File('t3.idl')
        def my_rexists(s):
            s.Tag('rexists_called', 1)
            return SCons.Node._rexists_map[s.GetTag('old_rexists')](s)
        n.Tag('old_rexists', n._func_rexists)
        SCons.Node._rexists_map[3] = my_rexists
        n._func_rexists = 3

        deps = s(n, env, path)

        # Make sure rexists() got called on the file node being
        # scanned, essential for cooperation with VariantDir functionality.
        assert n.GetTag('rexists_called')
        
        headers =  ['d1/f1.idl', 'd1/f2.idl',
                    'f1.idl', 'f2.idl', 'f3-test.idl',
                    'd1/f1.idl', 'd1/f2.idl', 'd1/f3-test.idl']
        deps_match(self, deps, headers)

class IDLScannerTestCase6(unittest.TestCase):
    def runTest(self):
        env1 = DummyEnvironment([test.workpath("d1")])
        env2 = DummyEnvironment([test.workpath("d1/d2")])
        s = SCons.Scanner.IDL.IDLScan()
        path1 = s.path(env1)
        path2 = s.path(env2)
        deps1 = s(env1.File('t1.idl'), env1, path1)
        deps2 = s(env2.File('t1.idl'), env2, path2)
        headers1 = ['f1.idl', 'f3.idl', 'd1/f2.idl']
        headers2 = ['f1.idl', 'f3.idl', 'd1/d2/f2.idl']
        deps_match(self, deps1, headers1)
        deps_match(self, deps2, headers2)

class IDLScannerTestCase7(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(["include"])
        s = SCons.Scanner.IDL.IDLScan()
        path = s.path(env)
        deps1 = s(env.File('t4.idl'), env, path)
        env.fs.chdir(env.Dir('subdir'))
        dir = env.fs.getcwd()
        env.fs.chdir(env.Dir(''))
        path = s.path(env, dir)
        deps2 = s(env.File('#t4.idl'), env, path)
        headers1 =  list(map(test.workpath, ['include/fa.idl', 'include/fb.idl']))
        headers2 =  ['include/fa.idl', 'include/fb.idl']
        deps_match(self, deps1, headers1)
        deps_match(self, deps2, headers2)

class IDLScannerTestCase8(unittest.TestCase):
    def runTest(self):
        SCons.Warnings.enableWarningClass(SCons.Warnings.DependencyWarning)
        class TestOut:
            def __call__(self, x):
                self.out = x

        to = TestOut()
        to.out = None
        SCons.Warnings._warningOut = to
        test.write('fa.idl','\n')
        env = DummyEnvironment([])
        s = SCons.Scanner.IDL.IDLScan()
        path = s.path(env)
        deps = s(env.File('t4.idl'), env, path)

        # Did we catch the warning associated with not finding fb.idl?
        assert to.out
        
        deps_match(self, deps, [ 'fa.idl' ])
        test.unlink('fa.idl')

class IDLScannerTestCase9(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([])
        env.fs.chdir(env.Dir('include'))
        s = SCons.Scanner.IDL.IDLScan()
        path = s.path(env)
        test.write('include/t4.idl', test.read('t4.idl'))
        deps = s(env.File('#include/t4.idl'), env, path)
        env.fs.chdir(env.Dir(''))
        deps_match(self, deps, [ 'fa.idl', 'fb.idl' ])
        test.unlink('include/t4.idl')

class IDLScannerTestCase10(unittest.TestCase):
    def runTest(self):
        os.chdir(test.workpath('work'))
        fs = SCons.Node.FS.FS(test.workpath('work'))
        fs.Repository(test.workpath('repository'))

        # Create a derived file in a directory that does not exist yet.
        # This was a bug at one time.
        env = DummyEnvironment(['include', 'include2'])
        env.fs = fs
        f1 = fs.File('include2/jjj.idl')
        f1.builder = 1
        s = SCons.Scanner.IDL.IDLScan()
        path = s.path(env)
        deps = s(fs.File('src/fff.c'), env, path)
        deps_match(self, deps, [ test.workpath('repository/include/iii.idl'),
                                 'include2/jjj.idl' ])
        os.chdir(test.workpath(''))

class IDLScannerTestCase11(unittest.TestCase):
    def runTest(self):
        os.chdir(test.workpath('work'))
        fs = SCons.Node.FS.FS(test.workpath('work'))
        fs.VariantDir('build1', 'src', 1)
        fs.VariantDir('build2', 'src', 0)
        fs.Repository(test.workpath('repository'))
        env = DummyEnvironment([])
        env.fs = fs
        s = SCons.Scanner.IDL.IDLScan()
        path = s.path(env)
        deps1 = s(fs.File('build1/aaa.c'), env, path)
        deps_match(self, deps1, [ 'build1/bbb.idl' ])
        deps2 = s(fs.File('build2/aaa.c'), env, path)
        deps_match(self, deps2, [ 'src/bbb.idl' ])
        deps3 = s(fs.File('build1/ccc.c'), env, path)
        deps_match(self, deps3, [ 'build1/ddd.idl' ])
        deps4 = s(fs.File('build2/ccc.c'), env, path)
        deps_match(self, deps4, [ test.workpath('repository/src/ddd.idl') ])
        os.chdir(test.workpath(''))

class IDLScannerTestCase12(unittest.TestCase):
    def runTest(self):
        class SubstEnvironment(DummyEnvironment):
            def subst(self, arg, target=None, source=None, conv=None, test=test):
                if arg == "$blah":
                    return test.workpath("d1")
                else:
                    return arg
        env = SubstEnvironment(["$blah"])
        s = SCons.Scanner.IDL.IDLScan()
        path = s.path(env)
        deps = s(env.File('t1.idl'), env, path)
        headers = ['f1.idl', 'f3.idl', 'd1/f2.idl']
        deps_match(self, deps, headers)
        

def suite():
    suite = unittest.TestSuite()
    suite.addTest(IDLScannerTestCase1())
    suite.addTest(IDLScannerTestCase2())
    suite.addTest(IDLScannerTestCase3())
    suite.addTest(IDLScannerTestCase4())
    suite.addTest(IDLScannerTestCase5())
    suite.addTest(IDLScannerTestCase6())
    suite.addTest(IDLScannerTestCase7())
    suite.addTest(IDLScannerTestCase8())
    suite.addTest(IDLScannerTestCase9())
    suite.addTest(IDLScannerTestCase10())
    suite.addTest(IDLScannerTestCase11())
    suite.addTest(IDLScannerTestCase12())
    return suite

if __name__ == "__main__":
    TestUnit.run(suite())

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
