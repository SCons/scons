#
# Copyright (c) 2001 Steven Knight
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
import os.path

test = TestCmd.TestCmd(workdir = '')

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

headers = ['f1.h','f2.h', 'f3.h', 'never.h',
           'd1/f1.h', 'd1/f2.h', 'd1/f3.h',
           'd1/d2/f1.h', 'd1/d2/f2.h', 'd1/d2/f3.h', 'd1/d2/f4.h']

for h in headers:
    test.write(h, " ")

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

def deps_match(deps, headers):
    deps = map(str, deps)
    headers = map(test.workpath, headers)
    deps.sort()
    headers.sort()
    return map(os.path.normpath, deps) == \
           map(os.path.normpath, headers)

# define some tests:

class CScannerTestCase1(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([])
        s = SCons.Scanner.C.CScan()
        deps = s.scan(test.workpath('f1.cpp'), env)
        self.failUnless(deps_match(deps, ['f1.h', 'f2.h']), map(str, deps))

class CScannerTestCase2(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.C.CScan()
        deps = s.scan(test.workpath('f1.cpp'), env)
        headers = ['f1.h', 'd1/f2.h']
        self.failUnless(deps_match(deps, headers), map(str, deps))

class CScannerTestCase3(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.C.CScan()
        deps = s.scan(test.workpath('f2.cpp'), env)
        headers = ['f1.h', 'd1/f1.h', 'd1/d2/f1.h']
        self.failUnless(deps_match(deps, headers), map(str, deps))

class CScannerTestCase4(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([test.workpath("d1"), test.workpath("d1/d2")])
        s = SCons.Scanner.C.CScan()
        deps = s.scan(test.workpath('f2.cpp'), env)
        headers =  ['f1.h', 'd1/f1.h', 'd1/d2/f1.h', 'd1/d2/f4.h']
        self.failUnless(deps_match(deps, headers), map(str, deps))
        
class CScannerTestCase5(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment([])
        s = SCons.Scanner.C.CScan()
        deps = s.scan(test.workpath('f3.cpp'), env)
        headers =  ['f1.h', 'f2.h', 'f3.h', 'd1/f1.h', 'd1/f2.h', 'd1/f3.h']
        self.failUnless(deps_match(deps, headers), map(str, deps))

def suite():
    suite = unittest.TestSuite()
    suite.addTest(CScannerTestCase1())
    suite.addTest(CScannerTestCase2())
    suite.addTest(CScannerTestCase3())
    suite.addTest(CScannerTestCase4())
    suite.addTest(CScannerTestCase5())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)
