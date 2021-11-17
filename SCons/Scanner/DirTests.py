# MIT License
#
# Copyright The SCons Foundation
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

import os.path
import unittest

import TestCmd

import SCons.Node.FS
import SCons.Scanner.Dir
from SCons.SConsign import current_sconsign_filename

#class DummyNode:
#    def __init__(self, name, fs):
#        self.name = name
#        self.abspath = test.workpath(name)
#        self.fs = fs
#    def __str__(self):
#        return self.name
#    def Entry(self, name):
#        return self.fs.Entry(name)

class DummyEnvironment:
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

        sconsign = current_sconsign_filename()

        self.test.write(['dir', 'f1'], "dir/f1\n")
        self.test.write(['dir', 'f2'], "dir/f2\n")
        self.test.write(['dir', '{}'.format(sconsign)], "dir/{}\n".format(sconsign))
        self.test.write(['dir', '{}.bak'.format(sconsign)], "dir/{}.bak\n".format(sconsign))
        self.test.write(['dir', '{}.dat'.format(sconsign)], "dir/{}.dat\n".format(sconsign))
        self.test.write(['dir', '{}.db'.format(sconsign)], "dir/{}.db\n".format(sconsign))
        self.test.write(['dir', '{}.dblite'.format(sconsign)], "dir/{}.dblite\n".format(sconsign))
        self.test.write(['dir', '{}.dir'.format(sconsign)], "dir/{}.dir\n".format(sconsign))
        self.test.write(['dir', '{}.pag'.format(sconsign)], "dir/{}.pag\n".format(sconsign))
        self.test.write(['dir', 'sub', 'f3'], "dir/sub/f3\n")
        self.test.write(['dir', 'sub', 'f4'], "dir/sub/f4\n")
        self.test.write(['dir', 'sub', '{}'.format(sconsign)], "dir/{}\n".format(sconsign))
        self.test.write(['dir', 'sub', '{}.bak'.format(sconsign)], "dir/{}.bak\n".format(sconsign))
        self.test.write(['dir', 'sub', '{}.dat'.format(sconsign)], "dir/{}.dat\n".format(sconsign))
        self.test.write(['dir', 'sub', '{}.dblite'.format(sconsign)], "dir/{}.dblite\n".format(sconsign))
        self.test.write(['dir', 'sub', '{}.dir'.format(sconsign)], "dir/{}.dir\n".format(sconsign))
        self.test.write(['dir', 'sub', '{}.pag'.format(sconsign)], "dir/{}.pag\n".format(sconsign))

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
        assert sss == expect, "Found {}, expected {}".format(sss, expect)

        expect = [
            os.path.join('dir', 'sub', 'f3'),
            os.path.join('dir', 'sub', 'f4'),
        ]
        deps = s(env.Dir('dir/sub'), env, ())
        sss = list(map(str, deps))
        assert sss == expect, "Found {}, expected {}".format(sss, expect)

class DirEntryScannerTestCase(DirScannerTestBase):
    def runTest(self):
        env = DummyEnvironment(self.test.workpath())

        s = SCons.Scanner.Dir.DirEntryScanner()

        deps = s(env.Dir('dir'), env, ())
        sss = list(map(str, deps))
        assert sss == [], "Found {}, expected {}".format(sss, [])

        deps = s(env.Dir('dir/sub'), env, ())
        sss = list(map(str, deps))
        assert sss == [], "Found {}, expected {}".format(sss, [])

        # Make sure we don't blow up if handed a non-Dir node.
        deps = s(env.File('dir/f1'), env, ())
        sss = list(map(str, deps))
        assert sss == [], "Found {}, expected {}".format(sss, [])

if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
