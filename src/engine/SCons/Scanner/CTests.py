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
import os.path
import sys
import TestCmd
import unittest
import UserDict

import SCons.Node.FS
import SCons.Warnings

import SCons.Scanner.C

test = TestCmd.TestCmd(workdir = '')

os.chdir(test.workpath(''))

# create some source files and headers:

test.write('f1.cpp',"""
#include \"f1.h\"
#include <f2.h>

int main()
{
   return 0;
}
""")

test.write('f2.cpp',"""
#include \"d1/f1.h\"
#include <d2/f1.h>
#include \"f1.h\"
#import <f4.h>

int main()
{
   return 0;
}
""")

test.write('f3.cpp',"""
#include \t "f1.h"
   \t #include "f2.h"
#   \t include "f3-test.h"

#include \t <d1/f1.h>
   \t #include <d1/f2.h>
#   \t include <d1/f3-test.h>

// #include "never.h"

const char* x = "#include <never.h>"

int main()
{
   return 0;
}
""")


# for Emacs -> "

test.subdir('d1', ['d1', 'd2'])

headers = ['f1.h','f2.h', 'f3-test.h', 'fi.h', 'fj.h', 'never.h',
           'd1/f1.h', 'd1/f2.h', 'd1/f3-test.h', 'd1/fi.h', 'd1/fj.h',
           'd1/d2/f1.h', 'd1/d2/f2.h', 'd1/d2/f3-test.h',
           'd1/d2/f4.h', 'd1/d2/fi.h', 'd1/d2/fj.h']

for h in headers:
    test.write(h, " ")

test.write('f2.h',"""
#include "fi.h"
""")

test.write('f3-test.h',"""
#include <fj.h>
""")


test.subdir('include', 'subdir', ['subdir', 'include'])

test.write('fa.cpp',"""
#include \"fa.h\"
#include <fb.h>

int main()
{
   return 0;
}
""")

test.write(['include', 'fa.h'], "\n")
test.write(['include', 'fb.h'], "\n")
test.write(['subdir', 'include', 'fa.h'], "\n")
test.write(['subdir', 'include', 'fb.h'], "\n")


test.subdir('repository', ['repository', 'include'],
            ['repository', 'src' ])
test.subdir('work', ['work', 'src'])

test.write(['repository', 'include', 'iii.h'], "\n")

test.write(['work', 'src', 'fff.c'], """
#include <iii.h>
#include <jjj.h>

int main()
{
    return 0;
}
""")

test.write([ 'work', 'src', 'aaa.c'], """
#include "bbb.h"

int main()
{
   return 0;
}
""")

test.write([ 'work', 'src', 'bbb.h'], "\n")

test.write([ 'repository', 'src', 'ccc.c'], """
#include "ddd.h"

int main()
{
   return 0;
}
""")

test.write([ 'repository', 'src', 'ddd.h'], "\n")

test.write('f5.c', """\
#include\"f5a.h\"
#include<f5b.h>
""")

test.write("f5a.h", "\n")
test.write("f5b.h", "\n")

# define some helpers:

class DummyEnvironment(UserDict.UserDict):
    def __init__(self, **kw):
        UserDict.UserDict.__init__(self)
        self.data.update(kw)

    def Dictionary(self, *args):
        return self.data

    def subst(self, strSubst):
        if strSubst[0] == '$':
            return self.data[strSubst[1:]]
        return strSubst

    def subst_list(self, strSubst):
        if strSubst[0] == '$':
            return [self.data[strSubst[1:]]]
        return [[strSubst]]

    def subst_path(self, path):
        if type(path) != type([]):
            path = [path]
        return map(self.subst, path)

if os.path.normcase('foo') == os.path.normcase('FOO'):
    my_normpath = os.path.normcase
else:
    my_normpath = os.path.normpath

def deps_match(self, deps, headers):
    global my_normpath
    scanned = map(my_normpath, map(str, deps))
    expect = map(my_normpath, headers)
    self.failUnless(scanned == expect, "expect %s != scanned %s" % (expect, scanned))

def make_node(filename, fs=SCons.Node.FS.default_fs):
    return fs.File(test.workpath(filename))

# define some tests:

class CScannerTestCase1(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(CPPPATH=[])
        s = SCons.Scanner.C.CScan()
        path = s.path(env)
        deps = s(make_node('f1.cpp'), env, path)
        headers = ['f1.h', 'f2.h']
        deps_match(self, deps, map(test.workpath, headers))

class CScannerTestCase2(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(CPPPATH=[test.workpath("d1")])
        s = SCons.Scanner.C.CScan()
        path = s.path(env)
        deps = s(make_node('f1.cpp'), env, path)
        headers = ['d1/f2.h', 'f1.h']
        deps_match(self, deps, map(test.workpath, headers))

class CScannerTestCase3(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(CPPPATH=[test.workpath("d1")])
        s = SCons.Scanner.C.CScan()
        path = s.path(env)
        deps = s(make_node('f2.cpp'), env, path)
        headers = ['d1/d2/f1.h', 'd1/f1.h', 'f1.h']
        deps_match(self, deps, map(test.workpath, headers))

class CScannerTestCase4(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(CPPPATH=[test.workpath("d1"), test.workpath("d1/d2")])
        s = SCons.Scanner.C.CScan()
        path = s.path(env)
        deps = s(make_node('f2.cpp'), env, path)
        headers =  ['d1/d2/f1.h', 'd1/d2/f4.h', 'd1/f1.h', 'f1.h']
        deps_match(self, deps, map(test.workpath, headers))
        
class CScannerTestCase5(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(CPPPATH=[])
        s = SCons.Scanner.C.CScan()
        path = s.path(env)

        n = make_node('f3.cpp')
        def my_rexists(s=n):
            s.rexists_called = 1
            return s.old_rexists()
        setattr(n, 'old_rexists', n.rexists)
        setattr(n, 'rexists', my_rexists)

        deps = s(n, env, path)

        # Make sure rexists() got called on the file node being
        # scanned, essential for cooperation with BuildDir functionality.
        assert n.rexists_called
        
        headers =  ['d1/f1.h', 'd1/f2.h', 'd1/f3-test.h',
                    'f1.h', 'f2.h', 'f3-test.h']
        deps_match(self, deps, map(test.workpath, headers))

class CScannerTestCase6(unittest.TestCase):
    def runTest(self):
        env1 = DummyEnvironment(CPPPATH=[test.workpath("d1")])
        env2 = DummyEnvironment(CPPPATH=[test.workpath("d1/d2")])
        s = SCons.Scanner.C.CScan()
        path1 = s.path(env1)
        path2 = s.path(env2)
        deps1 = s(make_node('f1.cpp'), env1, path1)
        deps2 = s(make_node('f1.cpp'), env2, path2)
        headers1 =  ['d1/f2.h', 'f1.h']
        headers2 =  ['d1/d2/f2.h', 'f1.h']
        deps_match(self, deps1, map(test.workpath, headers1))
        deps_match(self, deps2, map(test.workpath, headers2))

class CScannerTestCase8(unittest.TestCase):
    def runTest(self):
        fs = SCons.Node.FS.FS(test.workpath(''))
        env = DummyEnvironment(CPPPATH=["include"])
        s = SCons.Scanner.C.CScan(fs = fs)
        path = s.path(env)
        deps1 = s(fs.File('fa.cpp'), env, path)
        fs.chdir(fs.Dir('subdir'))
        dir = fs.getcwd()
        fs.chdir(fs.Dir('..'))
        path = s.path(env, dir)
        deps2 = s(fs.File('#fa.cpp'), env, path)
        headers1 =  ['include/fa.h', 'include/fb.h']
        headers2 =  ['subdir/include/fa.h', 'subdir/include/fb.h']
        deps_match(self, deps1, headers1)
        deps_match(self, deps2, headers2)

class CScannerTestCase9(unittest.TestCase):
    def runTest(self):
        SCons.Warnings.enableWarningClass(SCons.Warnings.DependencyWarning)
        class TestOut:
            def __call__(self, x):
                self.out = x

        to = TestOut()
        to.out = None
        SCons.Warnings._warningOut = to
        test.write('fa.h','\n')
        fs = SCons.Node.FS.FS(test.workpath(''))
        env = DummyEnvironment(CPPPATH=[])
        s = SCons.Scanner.C.CScan(fs=fs)
        path = s.path(env)
        deps = s(fs.File('fa.cpp'), env, path)

        # Did we catch the warning associated with not finding fb.h?
        assert to.out
        
        deps_match(self, deps, [ 'fa.h' ])
        test.unlink('fa.h')

class CScannerTestCase10(unittest.TestCase):
    def runTest(self):
        fs = SCons.Node.FS.FS(test.workpath(''))
        fs.chdir(fs.Dir('include'))
        env = DummyEnvironment(CPPPATH=[])
        s = SCons.Scanner.C.CScan(fs=fs)
        path = s.path(env)
        test.write('include/fa.cpp', test.read('fa.cpp'))
        deps = s(fs.File('#include/fa.cpp'), env, path)
        fs.chdir(fs.Dir('..'))
        deps_match(self, deps, [ 'include/fa.h', 'include/fb.h' ])
        test.unlink('include/fa.cpp')

class CScannerTestCase11(unittest.TestCase):
    def runTest(self):
        os.chdir(test.workpath('work'))
        fs = SCons.Node.FS.FS(test.workpath('work'))
        fs.Repository(test.workpath('repository'))

        # Create a derived file in a directory that does not exist yet.
        # This was a bug at one time.
        f1=fs.File('include2/jjj.h')
        f1.builder=1
        env = DummyEnvironment(CPPPATH=['include', 'include2'])
        s = SCons.Scanner.C.CScan(fs=fs)
        path = s.path(env)
        deps = s(fs.File('src/fff.c'), env, path)
        deps_match(self, deps, [ test.workpath('repository/include/iii.h'), 'include2/jjj.h' ])
        os.chdir(test.workpath(''))

class CScannerTestCase12(unittest.TestCase):
    def runTest(self):
        os.chdir(test.workpath('work'))
        fs = SCons.Node.FS.FS(test.workpath('work'))
        fs.BuildDir('build1', 'src', 1)
        fs.BuildDir('build2', 'src', 0)
        fs.Repository(test.workpath('repository'))
        env = DummyEnvironment(CPPPATH=[])
        s = SCons.Scanner.C.CScan(fs = fs)
        path = s.path(env)
        deps1 = s(fs.File('build1/aaa.c'), env, path)
        deps_match(self, deps1, [ 'build1/bbb.h' ])
        deps2 = s(fs.File('build2/aaa.c'), env, path)
        deps_match(self, deps2, [ 'src/bbb.h' ])
        deps3 = s(fs.File('build1/ccc.c'), env, path)
        deps_match(self, deps3, [ 'build1/ddd.h' ])
        deps4 = s(fs.File('build2/ccc.c'), env, path)
        deps_match(self, deps4, [ test.workpath('repository/src/ddd.h') ])
        os.chdir(test.workpath(''))

class CScannerTestCase13(unittest.TestCase):
    def runTest(self):
        class SubstEnvironment(DummyEnvironment):
            def subst(self, arg, test=test):
                return test.workpath("d1")
        env = SubstEnvironment(CPPPATH=["blah"])
        s = SCons.Scanner.C.CScan()
        path = s.path(env)
        deps = s(make_node('f1.cpp'), env, path)
        headers = ['d1/f2.h', 'f1.h']
        deps_match(self, deps, map(test.workpath, headers))

class CScannerTestCase14(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(CPPPATH=[])
        s = SCons.Scanner.C.CScan()
        path = s.path(env)
        deps = s(make_node('f5.c'), env, path)
        headers = ['f5a.h', 'f5b.h']
        deps_match(self, deps, map(test.workpath, headers))

class CScannerTestCase15(unittest.TestCase):
    def runTest(self):
        suffixes = [".c", ".C", ".cxx", ".cpp", ".c++", ".cc",
                    ".h", ".H", ".hxx", ".hpp", ".hh",
                    ".F", ".fpp", ".FPP",
                    ".S", ".spp", ".SPP"]
        env = DummyEnvironment(CPPSUFFIXES = suffixes)
        s = SCons.Scanner.C.CScan()
        for suffix in suffixes:
            assert suffix in s.get_skeys(env), "%s not in skeys" % suffix



def suite():
    suite = unittest.TestSuite()
    suite.addTest(CScannerTestCase1())
    suite.addTest(CScannerTestCase2())
    suite.addTest(CScannerTestCase3())
    suite.addTest(CScannerTestCase4())
    suite.addTest(CScannerTestCase5())
    suite.addTest(CScannerTestCase6())
    suite.addTest(CScannerTestCase8())
    suite.addTest(CScannerTestCase9())
    suite.addTest(CScannerTestCase10())
    suite.addTest(CScannerTestCase11())
    suite.addTest(CScannerTestCase12())
    suite.addTest(CScannerTestCase13())
    suite.addTest(CScannerTestCase14())
    suite.addTest(CScannerTestCase15())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)
