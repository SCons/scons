#
# Copyright (c) 2001, 2002 Steven Knight
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

import TestCmd
import SCons.Scanner.C
import unittest
import sys
import os
import os.path
import SCons.Node.FS

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
#include <f4.h>

int main()
{
   return 0;
}
""")

test.write('f3.cpp',"""
#include \t "f1.h"
   \t #include "f2.h"
#   \t include "f3.h"

#include \t <d1/f1.h>
   \t #include <d1/f2.h>
#   \t include <d1/f3.h>

// #include "never.h"

const char* x = "#include <never.h>"

int main()
{
   return 0;
}
""")


# for Emacs -> "

test.subdir('d1', ['d1', 'd2'])

headers = ['f1.h','f2.h', 'f3.h', 'fi.h', 'fj.h', 'never.h',
           'd1/f1.h', 'd1/f2.h', 'd1/f3.h', 'd1/fi.h', 'd1/fj.h',
           'd1/d2/f1.h', 'd1/d2/f2.h', 'd1/d2/f3.h',
           'd1/d2/f4.h', 'd1/d2/fi.h', 'd1/d2/fj.h']

for h in headers:
    test.write(h, " ")

test.write('f2.h',"""
#include "fi.h"
""")

test.write('f3.h',"""
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

test.write('include/fa.h', "\n")
test.write('include/fb.h', "\n")
test.write('subdir/include/fa.h', "\n")
test.write('subdir/include/fb.h', "\n")

# define some helpers:

class DummyEnvironment:
    def __init__(self, listCppPath):
        self.path = listCppPath
        
    def Dictionary(self, *args):
        if not args:
            return { 'CPPPATH': self.path }
        elif len(args) == 1 and args[0] == 'CPPPATH':
            return self.path
        else:
            raise KeyError, "Dummy environment only has CPPPATH attribute."

def deps_match(self, deps, headers):
    scanned = map(os.path.normpath, map(str, deps))
    expect = map(os.path.normpath, headers)
    self.failUnless(scanned == expect, "expect %s != scanned %s" % (expect, scanned))

def make_node(filename, fs=SCons.Node.FS.default_fs):
    return fs.File(test.workpath(filename))

# define some tests:

class CScannerTestCase1(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([])
        s = SCons.Scanner.C.CScan()
        deps = s.instance(env).scan(make_node('f1.cpp'), env)
	headers = ['f1.h', 'f2.h', 'fi.h']
        deps_match(self, deps, map(test.workpath, headers))

class CScannerTestCase2(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.C.CScan()
        deps = s.instance(env).scan(make_node('f1.cpp'), env)
        headers = ['d1/f2.h', 'f1.h']
        deps_match(self, deps, map(test.workpath, headers))

class CScannerTestCase3(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.C.CScan()
        deps = s.instance(env).scan(make_node('f2.cpp'), env)
        headers = ['d1/d2/f1.h', 'd1/f1.h', 'f1.h']
        deps_match(self, deps, map(test.workpath, headers))

class CScannerTestCase4(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1"), test.workpath("d1/d2")])
        s = SCons.Scanner.C.CScan()
        deps = s.instance(env).scan(make_node('f2.cpp'), env)
        headers =  ['d1/d2/f1.h', 'd1/d2/f4.h', 'd1/f1.h', 'f1.h']
        deps_match(self, deps, map(test.workpath, headers))
        
class CScannerTestCase5(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([])
        s = SCons.Scanner.C.CScan()
        deps = s.instance(env).scan(make_node('f3.cpp'), env)
        
        # Make sure exists() gets called on the file node being
        # scanned, essential for cooperation with BuildDir functionality.
        assert SCons.Node.FS.default_fs.File(test.workpath('f3.cpp')).created
        
        headers =  ['d1/f1.h', 'd1/f2.h', 'd1/f3.h',
                    'f1.h', 'f2.h', 'f3.h', 'fi.h', 'fj.h']
        deps_match(self, deps, map(test.workpath, headers))

class CScannerTestCase6(unittest.TestCase):
    def runTest(self):
        env1 = DummyEnvironment([test.workpath("d1")])
        env2 = DummyEnvironment([test.workpath("d1/d2")])
        env3 = DummyEnvironment([test.workpath("d1/../d1")])
        s = SCons.Scanner.C.CScan()
        s1 = s.instance(env1)
        s2 = s.instance(env2)
        s3 = s.instance(env3)
        assert not s1 is s2
        assert s1 is s3
        deps1 = s1.scan(make_node('f1.cpp'), None)
        deps2 = s2.scan(make_node('f1.cpp'), None)
        headers1 =  ['d1/f2.h', 'f1.h']
        headers2 =  ['d1/d2/f2.h', 'f1.h']
        deps_match(self, deps1, map(test.workpath, headers1))
        deps_match(self, deps2, map(test.workpath, headers2))

class CScannerTestCase7(unittest.TestCase):
    def runTest(self):
        s = SCons.Scanner.C.CScan()
        s1 = s.instance(DummyEnvironment([test.workpath("d1")]))
        s2 = s.instance(DummyEnvironment([test.workpath("d1/../d1")]))
        dict = {}
        dict[s1] = 777
        assert dict[s2] == 777

class CScannerTestCase8(unittest.TestCase):
    def runTest(self):
        fs = SCons.Node.FS.FS(test.workpath(''))
        env = DummyEnvironment(["include"])
        s = SCons.Scanner.C.CScan(fs = fs)
        deps1 = s.instance(env).scan(fs.File('fa.cpp'), None)
        fs.chdir(fs.Dir('subdir'))
        deps2 = s.instance(env).scan(fs.File('#fa.cpp'), None)
        headers1 =  ['include/fa.h', 'include/fb.h']
        headers2 =  ['subdir/include/fa.h', 'subdir/include/fb.h']
        deps_match(self, deps1, headers1)
        deps_match(self, deps2, headers2)

class CScannerTestCase9(unittest.TestCase):
    def runTest(self):
        test.write('fa.h','\n')
        fs = SCons.Node.FS.FS(test.workpath(''))
        s = SCons.Scanner.C.CScan(fs=fs)
        env = DummyEnvironment([])
        deps = s.instance(env).scan(fs.File('fa.cpp'), None)
        deps_match(self, deps, [ 'fa.h' ])
        test.unlink('fa.h')

class CScannerTestCase10(unittest.TestCase):
    def runTest(self):
        fs = SCons.Node.FS.FS(test.workpath(''))
        fs.chdir(fs.Dir('include'))
        s = SCons.Scanner.C.CScan(fs=fs)
        env = DummyEnvironment([])
        test.write('include/fa.cpp', test.read('fa.cpp'))
        deps = s.instance(env).scan(fs.File('#include/fa.cpp'), None)
        deps_match(self, deps, [ 'include/fa.h', 'include/fb.h' ])
        test.unlink('include/fa.cpp')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(CScannerTestCase1())
    suite.addTest(CScannerTestCase2())
    suite.addTest(CScannerTestCase3())
    suite.addTest(CScannerTestCase4())
    suite.addTest(CScannerTestCase5())
    suite.addTest(CScannerTestCase6())
    suite.addTest(CScannerTestCase7())
    suite.addTest(CScannerTestCase8())
    suite.addTest(CScannerTestCase9())
    suite.addTest(CScannerTestCase10())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)
