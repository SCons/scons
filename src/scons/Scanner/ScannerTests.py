__revision__ = "Scanner/ScannerTests.py __REVISION__ __DATE__ __DEVELOPER__"

import unittest
import scons.Scanner
import sys

class ScannerTestBase:
    
    def func(self, filename, env):
        self.filename = filename
        self.env = env
        return self.deps

    def error_func(self, filename, env):
        self.fail("the wrong function was called")

    def test(self, scanner, env, filename, deps):
        self.deps = deps
        deps = scanner.scan(filename, env)

        self.failUnless(self.filename == filename, "the filename was passed incorrectly")
        self.failUnless(self.env == env, "the environment was passed incorrectly")
        self.failUnless(self.deps == deps, "the dependencies were returned incorrectly")

class DummyEnvironment:
    pass


class ScannerPositionalTestCase(ScannerTestBase, unittest.TestCase):
    "Test the Scanner class using the position argument"
    def runTest(self):
        s = scons.Scanner.Scanner(self.func)
        env = DummyEnvironment()
        env.ARGUMENT = "arg1"
        self.test(s, env, 'f1.cpp', ['f1.h', 'f2.h'])

class ScannerKeywordTestCase(ScannerTestBase, unittest.TestCase):
    "Test the Scanner class using the keyword argument"
    def runTest(self):
        s = scons.Scanner.Scanner(function = self.func)
        env = DummyEnvironment()
        env.ARGUMENT = "arg1"
        self.test(s, env, 'f1.cpp', ['f1.h', 'f2.h'])

def suite():
    suite = unittest.TestSuite()
    suite.addTest(ScannerPositionalTestCase())
    suite.addTest(ScannerKeywordTestCase())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)


