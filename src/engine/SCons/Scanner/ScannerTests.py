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
        scanned = scanner.scan(filename, env)
        scanned_strs = map(lambda x: str(x), scanned)

        self.failUnless(self.filename == filename, "the filename was passed incorrectly")
        self.failUnless(self.env == env, "the environment was passed incorrectly")
        self.failUnless(scanned_strs == deps, "the dependencies were returned incorrectly")
        for d in scanned:
            self.failUnless(type(d) != type(""), "got a string in the dependencies")

        if len(args) > 0:
            self.failUnless(self.arg == args[0], "the argument was passed incorrectly")
        else:
            self.failIf(hasattr(self, "arg"), "an argument was given when it shouldn't have been")

class DummyEnvironment:
    pass


class ScannerPositionalTestCase(ScannerTestBase, unittest.TestCase):
    "Test the Scanner.Base class using the position argument"
    def runTest(self):
        s = SCons.Scanner.Base(self.func, "Pos")
        env = DummyEnvironment()
        env.VARIABLE = "var1"
        self.test(s, env, 'f1.cpp', ['f1.h', 'f1.hpp'])

	env = DummyEnvironment()
	env.VARIABLE = "i1"
	i = s.instance(env)
	self.test(i, env, 'i1.cpp', ['i1.h', 'i1.hpp'])

class ScannerKeywordTestCase(ScannerTestBase, unittest.TestCase):
    "Test the Scanner.Base class using the keyword argument"
    def runTest(self):
        s = SCons.Scanner.Base(function = self.func, name = "Key")
        env = DummyEnvironment()
        env.VARIABLE = "var2"
        self.test(s, env, 'f2.cpp', ['f2.h', 'f2.hpp'])

	env = DummyEnvironment()
	env.VARIABLE = "i2"
	i = s.instance(env)
	self.test(i, env, 'i2.cpp', ['i2.h', 'i2.hpp'])

class ScannerPositionalArgumentTestCase(ScannerTestBase, unittest.TestCase):
    "Test the Scanner.Base class using both position and optional arguments"
    def runTest(self):
        arg = "this is the argument"
        s = SCons.Scanner.Base(self.func, "PosArg", arg)
        env = DummyEnvironment()
        env.VARIABLE = "var3"
        self.test(s, env, 'f3.cpp', ['f3.h', 'f3.hpp'], arg)

	env = DummyEnvironment()
	env.VARIABLE = "i3"
	i = s.instance(env)
	self.test(i, env, 'i3.cpp', ['i3.h', 'i3.hpp'], arg)

class ScannerKeywordArgumentTestCase(ScannerTestBase, unittest.TestCase):
    "Test the Scanner.Base class using both keyword and optional arguments"
    def runTest(self):
        arg = "this is another argument"
        s = SCons.Scanner.Base(function = self.func, name = "KeyArg",
                               argument = arg)
        env = DummyEnvironment()
        env.VARIABLE = "var4"
        self.test(s, env, 'f4.cpp', ['f4.h', 'f4.hpp'], arg)

	env = DummyEnvironment()
	env.VARIABLE = "i4"
	i = s.instance(env)
	self.test(i, env, 'i4.cpp', ['i4.h', 'i4.hpp'], arg)

class ScannerHashTestCase(ScannerTestBase, unittest.TestCase):
    "Test the Scanner.Base class __hash__() method"
    def runTest(self):
        s = SCons.Scanner.Base(self.func, "Hash")
        dict = {}
        dict[s] = 777
        self.failUnless(hash(dict.keys()[0]) == hash(None),
                        "did not hash Scanner base class as expected")

def suite():
    suite = unittest.TestSuite()
    suite.addTest(ScannerPositionalTestCase())
    suite.addTest(ScannerKeywordTestCase())
    suite.addTest(ScannerPositionalArgumentTestCase())
    suite.addTest(ScannerKeywordArgumentTestCase())
    suite.addTest(ScannerHashTestCase())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)


