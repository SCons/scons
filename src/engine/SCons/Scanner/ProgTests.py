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
import SCons.Scanner.Prog

test = TestCmd.TestCmd(workdir = '')

test.subdir('d1', ['d1', 'd2'], 'dir', ['dir', 'sub'])

libs = [ 'l1.lib', 'd1/l2.lib', 'd1/d2/l3.lib',
         'dir/libfoo.a', 'dir/sub/libbar.a', 'dir/libxyz.other']

for h in libs:
    test.write(h, "\n")

# define some helpers:

class DummyEnvironment:
    def __init__(self, **kw):
        self._dict = {'LIBSUFFIXES' : '.lib'}
        self._dict.update(kw)

    def Dictionary(self, *args):
        if not args:
            return self._dict
        elif len(args) == 1:
            return self._dict[args[0]]
        else:
            return map(lambda x, s=self: s._dict[x], args)

    def has_key(self, key):
        return self.Dictionary().has_key(key)

    def __getitem__(self,key):
        return self.Dictionary()[key]

    def __setitem__(self,key,value):
        self.Dictionary()[key] = value

    def __delitem__(self,key):
        del self.Dictionary()[key]

    def subst(self, s):
        try:
            if s[0] == '$':
                return self._dict[s[1:]]
        except IndexError:
            return ''
        return s

    def subst_path(self, path):
        if type(path) != type([]):
            path = [path]
        return map(self.subst, path)

def deps_match(deps, libs):
    deps=map(str, deps)
    deps.sort()
    libs.sort()
    return map(os.path.normpath, deps) == \
           map(os.path.normpath,
               map(test.workpath, libs))

# define some tests:

class ProgScanTestCase1(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=[ test.workpath("") ],
                               LIBS=[ 'l1', 'l2', 'l3' ])
        s = SCons.Scanner.Prog.ProgScan()
        path = s.path(env)
        deps = s('dummy', env, path)
        assert deps_match(deps, ['l1.lib']), map(str, deps)

        env = DummyEnvironment(LIBPATH=[ test.workpath("") ],
                               LIBS='l1')
        s = SCons.Scanner.Prog.ProgScan()
        path = s.path(env)
        deps = s('dummy', env, path)
        assert deps_match(deps, ['l1.lib']), map(str, deps)

        f1 = SCons.Node.FS.default_fs.File(test.workpath('f1'))
        env = DummyEnvironment(LIBPATH=[ test.workpath("") ],
                               LIBS=[f1])
        s = SCons.Scanner.Prog.ProgScan()
        path = s.path(env)
        deps = s('dummy', env, path)
        assert deps[0] is f1, deps

        f2 = SCons.Node.FS.default_fs.File(test.workpath('f1'))
        env = DummyEnvironment(LIBPATH=[ test.workpath("") ],
                               LIBS=f2)
        s = SCons.Scanner.Prog.ProgScan()
        path = s.path(env)
        deps = s('dummy', env, path)
        assert deps[0] is f2, deps


class ProgScanTestCase2(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=map(test.workpath,
                                           ["", "d1", "d1/d2" ]),
                               LIBS=[ 'l1', 'l2', 'l3' ])
        s = SCons.Scanner.Prog.ProgScan()
        path = s.path(env)
        deps = s('dummy', env, path)
        assert deps_match(deps, ['l1.lib', 'd1/l2.lib', 'd1/d2/l3.lib' ]), map(str, deps)

class ProgScanTestCase3(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=[test.workpath("d1/d2"),
                                        test.workpath("d1")],
                               LIBS=string.split('l2 l3'))
        s = SCons.Scanner.Prog.ProgScan()
        path = s.path(env)
        deps = s('dummy', env, path)
        assert deps_match(deps, ['d1/l2.lib', 'd1/d2/l3.lib']), map(str, deps)

class ProgScanTestCase5(unittest.TestCase):
    def runTest(self):
        class SubstEnvironment(DummyEnvironment):
            def subst(self, arg, path=test.workpath("d1")):
                if arg == "blah":
                    return test.workpath("d1")
                else:
                    return arg
        env = SubstEnvironment(LIBPATH=[ "blah" ],
                               LIBS=string.split('l2 l3'))
        s = SCons.Scanner.Prog.ProgScan()
        path = s.path(env)
        deps = s('dummy', env, path)
        assert deps_match(deps, [ 'd1/l2.lib' ]), map(str, deps)

class ProgScanTestCase6(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=[ test.workpath("dir") ],
                               LIBS=['foo', 'sub/libbar', 'xyz.other'],
                               LIBPREFIXES=['lib'],
                               LIBSUFFIXES=['.a'])
        s = SCons.Scanner.Prog.ProgScan()
        path = s.path(env)
        deps = s('dummy', env, path)
        assert deps_match(deps, ['dir/libfoo.a', 'dir/sub/libbar.a', 'dir/libxyz.other']), map(str, deps)

class ProgScanTestCase7(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=[ test.workpath("dir") ],
                               LIBS=['foo', '$LIBBAR', '$XYZ'],
                               LIBPREFIXES=['lib'],
                               LIBSUFFIXES=['.a'],
                               LIBBAR='sub/libbar',
                               XYZ='xyz.other')
        s = SCons.Scanner.Prog.ProgScan()
        path = s.path(env)
        deps = s('dummy', env, path)
        assert deps_match(deps, ['dir/libfoo.a', 'dir/sub/libbar.a', 'dir/libxyz.other']), map(str, deps)

class ProgScanTestCase8(unittest.TestCase):
    def runTest(self):
        
        class DummyNode:
            pass

        n1 = DummyNode()
        env = DummyEnvironment(LIBPATH=[ test.workpath("dir") ],
                               LIBS=[n1],
                               LIBPREFIXES=['p1-', 'p2-'],
                               LIBSUFFIXES=['.1', '2'])
        s = SCons.Scanner.Prog.ProgScan(node_class = DummyNode)
        path = s.path(env)
        deps = s('dummy', env, path)
        assert deps == [n1], deps

        n2 = DummyNode()
        env = DummyEnvironment(LIBPATH=[ test.workpath("dir") ],
                               LIBS=[n1, [n2]],
                               LIBPREFIXES=['p1-', 'p2-'],
                               LIBSUFFIXES=['.1', '2'])
        s = SCons.Scanner.Prog.ProgScan(node_class = DummyNode)
        path = s.path(env)
        deps = s('dummy', env, path)
        assert deps == [n1, n2], deps

def suite():
    suite = unittest.TestSuite()
    suite.addTest(ProgScanTestCase1())
    suite.addTest(ProgScanTestCase2())
    suite.addTest(ProgScanTestCase3())
    suite.addTest(ProgScanTestCase5())
    suite.addTest(ProgScanTestCase6())
    suite.addTest(ProgScanTestCase7())
    suite.addTest(ProgScanTestCase8())
    if hasattr(types, 'UnicodeType'):
        code = """if 1:
            class ProgScanTestCase4(unittest.TestCase):
                def runTest(self):
                    env = DummyEnvironment(LIBPATH=[test.workpath("d1/d2"),
                                                    test.workpath("d1")],
                                           LIBS=string.split(u'l2 l3'))
                    s = SCons.Scanner.Prog.ProgScan()
                    path = s.path(env)
                    deps = s('dummy', env, path)
                    assert deps_match(deps, ['d1/l2.lib', 'd1/d2/l3.lib']), map(str, deps)
            suite.addTest(ProgScanTestCase4())
            \n"""
        exec code
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)
