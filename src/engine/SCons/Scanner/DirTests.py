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
    def __init__(self, name):
        self.name = name
        self.abspath = test.workpath(name)
        self.fs = SCons.Node.FS.default_fs
    def __str__(self):
        return self.name
    def Entry(self, name):
        return self.fs.Entry(name)

class DirScannerTestCase1(unittest.TestCase):
    def runTest(self):
        s = SCons.Scanner.Dir.DirScanner()

        deps = s(DummyNode('dir'), {}, ())
        sss = map(str, deps)
        assert sss == ['f1', 'f2', 'sub'], sss

        deps = s(DummyNode('dir/sub'), {}, ())
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
