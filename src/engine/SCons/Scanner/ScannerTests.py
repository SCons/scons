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

import unittest
import SCons.Scanner
import sys

class ScannerTestBase:
    
    def func(self, filename, env, *args):
        self.filename = filename
        self.env = env

        if len(args) > 0:
            self.arg = args[0]
        
        return self.deps


    def test(self, scanner, env, filename, deps, *args):
        self.deps = deps
        deps = scanner.scan(filename, env)

        self.failUnless(self.filename == filename, "the filename was passed incorrectly")
        self.failUnless(self.env == env, "the environment was passed incorrectly")
        self.failUnless(self.deps == deps, "the dependencies were returned incorrectly")

        if len(args) > 0:
            self.failUnless(self.arg == args[0], "the argument was passed incorrectly")
        else:
            self.failIf(hasattr(self, "arg"), "an argument was given when it shouldn't have been")

class DummyEnvironment:
    pass


class ScannerPositionalTestCase(ScannerTestBase, unittest.TestCase):
    "Test the Scanner class using the position argument"
    def runTest(self):
        s = SCons.Scanner.Scanner(self.func)
        env = DummyEnvironment()
        env.VARIABLE = "var1"
        self.test(s, env, 'f1.cpp', ['f1.h', 'f1.hpp'])

class ScannerKeywordTestCase(ScannerTestBase, unittest.TestCase):
    "Test the Scanner class using the keyword argument"
    def runTest(self):
        s = SCons.Scanner.Scanner(function = self.func)
        env = DummyEnvironment()
        env.VARIABLE = "var2"
        self.test(s, env, 'f2.cpp', ['f2.h', 'f2.hpp'])

class ScannerPositionalArgumentTestCase(ScannerTestBase, unittest.TestCase):
    "Test the Scanner class using the position argument and optional argument"
    def runTest(self):
        arg = "this is the argument"
        s = SCons.Scanner.Scanner(self.func, arg)
        env = DummyEnvironment()
        env.VARIABLE = "var3"
        self.test(s, env, 'f3.cpp', ['f3.h', 'f3.hpp'], arg)

class ScannerKeywordArgumentTestCase(ScannerTestBase, unittest.TestCase):
    "Test the Scanner class using the keyword argument and optional argument"
    def runTest(self):
        arg = "this is another argument"
        s = SCons.Scanner.Scanner(function = self.func, argument = arg)
        env = DummyEnvironment()
        env.VARIABLE = "var4"
        self.test(s, env, 'f4.cpp', ['f4.h', 'f4.hpp'], arg)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(ScannerPositionalTestCase())
    suite.addTest(ScannerKeywordTestCase())
    suite.addTest(ScannerPositionalArgumentTestCase())
    suite.addTest(ScannerKeywordArgumentTestCase())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)


