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

import os.path
import string
import sys
import types
import unittest

import TestCmd
import SCons.Node.FS
import SCons.Scanner.Dir

test = TestCmd.TestCmd(workdir = '')

test.subdir('dir', ['dir', 'sub'])

test.write(['dir', 'f1'], "dir/f1\n")
test.write(['dir', 'f2'], "dir/f2\n")
test.write(['dir', '.sconsign'], "dir/.sconsign\n")
test.write(['dir', '.sconsign.dblite'], "dir/.sconsign.dblite\n")
test.write(['dir', 'sub', 'f3'], "dir/sub/f3\n")
test.write(['dir', 'sub', 'f4'], "dir/sub/f4\n")
test.write(['dir', 'sub', '.sconsign'], "dir/.sconsign\n")
test.write(['dir', 'sub', '.sconsign.dblite'], "dir/.sconsign.dblite\n")

class DummyNode:
    def __init__(self, name, fs):
        self.name = name
        self.abspath = test.workpath(name)
        self.fs = fs
    def __str__(self):
        return self.name
    def Entry(self, name):
        return self.fs.Entry(name)

class DummyEnvironment:
    def __init__(self):
        self.fs = SCons.Node.FS.FS()
    def Entry(self, name):
        node = DummyNode(name, self.fs)
        return node
    def get_factory(self, factory):
        return factory or self.fs.Entry

class DirScannerTestCase1(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment()

        s = SCons.Scanner.Dir.DirScanner()

        deps = s(env.Entry('dir'), env, ())
        sss = map(str, deps)
        assert sss == ['f1', 'f2', 'sub'], sss

        deps = s(env.Entry('dir/sub'), env, ())
        sss = map(str, deps)
        assert sss == ['f3', 'f4'], sss

def suite():
    suite = unittest.TestSuite()
    suite.addTest(DirScannerTestCase1())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)
