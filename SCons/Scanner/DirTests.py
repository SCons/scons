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
import sys
import unittest

import TestCmd

import SCons.Node.FS
import SCons.Scanner.Dir

#class DummyNode:
#    def __init__(self, name, fs):
#        self.name = name
#        self.abspath = test.workpath(name)
#        self.fs = fs
#    def __str__(self):
#        return self.name
#    def Entry(self, name):
#        return self.fs.Entry(name)

class DummyEnvironment(object):
    def __init__(self, root):
        self.fs = SCons.Node.FS.FS(root)
    def Dir(self, name):
        return self.fs.Dir(name)
    def Entry(self, name):
        return self.fs.Entry(name)
    def File(self, name):
        return self.fs.File(name)
    def get_factory(self, factory):
        return factory or self.fs.Entry

class DirScannerTestBase(unittest.TestCase):
    def setUp(self):
        self.test = TestCmd.TestCmd(workdir = '')

        self.test.subdir('dir', ['dir', 'sub'])

        self.test.write(['dir', 'f1'], "dir/f1\n")
        self.test.write(['dir', 'f2'], "dir/f2\n")
        self.test.write(['dir', '.sconsign'], "dir/.sconsign\n")
        self.test.write(['dir', '.sconsign.bak'], "dir/.sconsign.bak\n")
        self.test.write(['dir', '.sconsign.dat'], "dir/.sconsign.dat\n")
        self.test.write(['dir', '.sconsign.db'], "dir/.sconsign.db\n")
        self.test.write(['dir', '.sconsign.dblite'], "dir/.sconsign.dblite\n")
        self.test.write(['dir', '.sconsign.dir'], "dir/.sconsign.dir\n")
        self.test.write(['dir', '.sconsign.pag'], "dir/.sconsign.pag\n")
        self.test.write(['dir', 'sub', 'f3'], "dir/sub/f3\n")
        self.test.write(['dir', 'sub', 'f4'], "dir/sub/f4\n")
        self.test.write(['dir', 'sub', '.sconsign'], "dir/.sconsign\n")
        self.test.write(['dir', 'sub', '.sconsign.bak'], "dir/.sconsign.bak\n")
        self.test.write(['dir', 'sub', '.sconsign.dat'], "dir/.sconsign.dat\n")
        self.test.write(['dir', 'sub', '.sconsign.dblite'], "dir/.sconsign.dblite\n")
        self.test.write(['dir', 'sub', '.sconsign.dir'], "dir/.sconsign.dir\n")
        self.test.write(['dir', 'sub', '.sconsign.pag'], "dir/.sconsign.pag\n")

class DirScannerTestCase(DirScannerTestBase):
    def runTest(self):
        env = DummyEnvironment(self.test.workpath())

        s = SCons.Scanner.Dir.DirScanner()

        expect = [
            os.path.join('dir', 'f1'),
            os.path.join('dir', 'f2'),
            os.path.join('dir', 'sub'),
        ]
        deps = s(env.Dir('dir'), env, ())
        sss = list(map(str, deps))
        assert sss == expect, sss

        expect = [
            os.path.join('dir', 'sub', 'f3'),
            os.path.join('dir', 'sub', 'f4'),
        ]
        deps = s(env.Dir('dir/sub'), env, ())
        sss = list(map(str, deps))
        assert sss == expect, sss

class DirEntryScannerTestCase(DirScannerTestBase):
    def runTest(self):
        env = DummyEnvironment(self.test.workpath())

        s = SCons.Scanner.Dir.DirEntryScanner()

        deps = s(env.Dir('dir'), env, ())
        sss = list(map(str, deps))
        assert sss == [], sss

        deps = s(env.Dir('dir/sub'), env, ())
        sss = list(map(str, deps))
        assert sss == [], sss

        # Make sure we don't blow up if handed a non-Dir node.
        deps = s(env.File('dir/f1'), env, ())
        sss = list(map(str, deps))
        assert sss == [], sss

if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
