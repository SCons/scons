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
import SCons.Scanner.Prog
import SCons.Subst

test = TestCmd.TestCmd(workdir = '')

test.subdir('d1', ['d1', 'd2'], 'dir', ['dir', 'sub'])

libs = [ 'l1.lib', 'd1/l2.lib', 'd1/d2/l3.lib',
         'dir/libfoo.a', 'dir/sub/libbar.a', 'dir/libxyz.other']

for h in libs:
    test.write(h, "\n")

# define some helpers:

class DummyEnvironment(object):
    def __init__(self, **kw):
        self._dict = {'LIBSUFFIXES' : '.lib'}
        self._dict.update(kw)
        self.fs = SCons.Node.FS.FS(test.workpath(''))

    def Dictionary(self, *args):
        if not args:
            return self._dict
        elif len(args) == 1:
            return self._dict[args[0]]
        else:
            return [self._dict[x] for x in args]

    def has_key(self, key):
        return key in self.Dictionary()

    def __getitem__(self,key):
        return self.Dictionary()[key]

    def __setitem__(self,key,value):
        self.Dictionary()[key] = value

    def __delitem__(self,key):
        del self.Dictionary()[key]

    def subst(self, s, target=None, source=None, conv=None):
        return SCons.Subst.scons_subst(s, self, gvars=self._dict, lvars=self._dict)

    def subst_path(self, path, target=None, source=None, conv=None):
        if not isinstance(path, list):
            path = [path]
        return list(map(self.subst, path))

    def get_factory(self, factory):
        return factory or self.fs.File

    def Dir(self, filename):
        return self.fs.Dir(test.workpath(filename))

    def File(self, filename):
        return self.fs.File(test.workpath(filename))

class DummyNode(object):
    def __init__(self, name):
        self.name = name
    def rexists(self):
        return 1
    def __str__(self):
        return self.name
    
def deps_match(deps, libs):
    deps=sorted(map(str, deps))
    libs.sort()
    return list(map(os.path.normpath, deps)) == list(map(os.path.normpath, libs))

# define some tests:

class ProgramScannerTestCase1(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=[ test.workpath("") ],
                               LIBS=[ 'l1', 'l2', 'l3' ])
        s = SCons.Scanner.Prog.ProgramScanner()
        path = s.path(env)
        deps = s(DummyNode('dummy'), env, path)
        assert deps_match(deps, ['l1.lib']), list(map(str, deps))

        env = DummyEnvironment(LIBPATH=[ test.workpath("") ],
                               LIBS='l1')
        s = SCons.Scanner.Prog.ProgramScanner()
        path = s.path(env)
        deps = s(DummyNode('dummy'), env, path)
        assert deps_match(deps, ['l1.lib']), list(map(str, deps))

        f1 = env.fs.File(test.workpath('f1'))
        env = DummyEnvironment(LIBPATH=[ test.workpath("") ],
                               LIBS=[f1])
        s = SCons.Scanner.Prog.ProgramScanner()
        path = s.path(env)
        deps = s(DummyNode('dummy'), env, path)
        assert deps[0] is f1, deps

        f2 = env.fs.File(test.workpath('f1'))
        env = DummyEnvironment(LIBPATH=[ test.workpath("") ],
                               LIBS=f2)
        s = SCons.Scanner.Prog.ProgramScanner()
        path = s.path(env)
        deps = s(DummyNode('dummy'), env, path)
        assert deps[0] is f2, deps


class ProgramScannerTestCase2(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=list(map(test.workpath,
                                           ["", "d1", "d1/d2" ])),
                               LIBS=[ 'l1', 'l2', 'l3' ])
        s = SCons.Scanner.Prog.ProgramScanner()
        path = s.path(env)
        deps = s(DummyNode('dummy'), env, path)
        assert deps_match(deps, ['l1.lib', 'd1/l2.lib', 'd1/d2/l3.lib' ]), list(map(str, deps))

class ProgramScannerTestCase3(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=[test.workpath("d1/d2"),
                                        test.workpath("d1")],
                               LIBS='l2 l3'.split())
        s = SCons.Scanner.Prog.ProgramScanner()
        path = s.path(env)
        deps = s(DummyNode('dummy'), env, path)
        assert deps_match(deps, ['d1/l2.lib', 'd1/d2/l3.lib']), list(map(str, deps))

class ProgramScannerTestCase5(unittest.TestCase):
    def runTest(self):
        class SubstEnvironment(DummyEnvironment):
            def subst(self, arg, target=None, source=None, conv=None, path=test.workpath("d1")):
                if arg == "$blah":
                    return test.workpath("d1")
                else:
                    return arg
        env = SubstEnvironment(LIBPATH=[ "$blah" ],
                               LIBS='l2 l3'.split())
        s = SCons.Scanner.Prog.ProgramScanner()
        path = s.path(env)
        deps = s(DummyNode('dummy'), env, path)
        assert deps_match(deps, [ 'd1/l2.lib' ]), list(map(str, deps))

class ProgramScannerTestCase6(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=[ test.workpath("dir") ],
                               LIBS=['foo', 'sub/libbar', 'xyz.other'],
                               LIBPREFIXES=['lib'],
                               LIBSUFFIXES=['.a'])
        s = SCons.Scanner.Prog.ProgramScanner()
        path = s.path(env)
        deps = s(DummyNode('dummy'), env, path)
        assert deps_match(deps, ['dir/libfoo.a', 'dir/sub/libbar.a', 'dir/libxyz.other']), list(map(str, deps))

class ProgramScannerTestCase7(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=[ test.workpath("dir") ],
                               LIBS=['foo', '$LIBBAR', '$XYZ'],
                               LIBPREFIXES=['lib'],
                               LIBSUFFIXES=['.a'],
                               LIBBAR='sub/libbar',
                               XYZ='xyz.other')
        s = SCons.Scanner.Prog.ProgramScanner()
        path = s.path(env)
        deps = s(DummyNode('dummy'), env, path)
        assert deps_match(deps, ['dir/libfoo.a', 'dir/sub/libbar.a', 'dir/libxyz.other']), list(map(str, deps))

class ProgramScannerTestCase8(unittest.TestCase):
    def runTest(self):
        
        n1 = DummyNode('n1')
        env = DummyEnvironment(LIBPATH=[ test.workpath("dir") ],
                               LIBS=[n1],
                               LIBPREFIXES=['p1-', 'p2-'],
                               LIBSUFFIXES=['.1', '2'])
        s = SCons.Scanner.Prog.ProgramScanner(node_class = DummyNode)
        path = s.path(env)
        deps = s(DummyNode('dummy'), env, path)
        assert deps == [n1], deps

        n2 = DummyNode('n2')
        env = DummyEnvironment(LIBPATH=[ test.workpath("dir") ],
                               LIBS=[n1, [n2]],
                               LIBPREFIXES=['p1-', 'p2-'],
                               LIBSUFFIXES=['.1', '2'])
        s = SCons.Scanner.Prog.ProgramScanner(node_class = DummyNode)
        path = s.path(env)
        deps = s(DummyNode('dummy'), env, path)
        assert deps == [n1, n2], deps

class ProgramScannerTestCase9(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=[ test.workpath("dir") ],
                               LIBS=['foo', '$LIBBAR'],
                               LIBPREFIXES=['lib'],
                               LIBSUFFIXES=['.a'],
                               LIBBAR=['sub/libbar', 'xyz.other'])
        s = SCons.Scanner.Prog.ProgramScanner()
        path = s.path(env)
        deps = s(DummyNode('dummy'), env, path)
        assert deps_match(deps, ['dir/libfoo.a', 'dir/sub/libbar.a', 'dir/libxyz.other']), list(map(str, deps))

class ProgramScannerTestCase10(unittest.TestCase):
    def runTest(self):
        env = DummyEnvironment(LIBPATH=[ test.workpath("dir") ],
                               LIBS=['foo', '$LIBBAR'],
                               LIBPREFIXES=['lib'],
                               LIBSUFFIXES=['.a'],
                               LIBBAR='sub/libbar $LIBBAR2',
                               LIBBAR2=['xyz.other'])
        s = SCons.Scanner.Prog.ProgramScanner()
        path = s.path(env)
        deps = s(DummyNode('dummy'), env, path)
        assert deps_match(deps, ['dir/libfoo.a', 'dir/sub/libbar.a', 'dir/libxyz.other']), list(map(str, deps))

def suite():
    suite = unittest.TestSuite()
    suite.addTest(ProgramScannerTestCase1())
    suite.addTest(ProgramScannerTestCase2())
    suite.addTest(ProgramScannerTestCase3())
    suite.addTest(ProgramScannerTestCase5())
    suite.addTest(ProgramScannerTestCase6())
    suite.addTest(ProgramScannerTestCase7())
    suite.addTest(ProgramScannerTestCase8())
    suite.addTest(ProgramScannerTestCase9())
    suite.addTest(ProgramScannerTestCase10())
    try: unicode
    except NameError: pass
    else:
        code = """if 1:
            class ProgramScannerTestCase4(unittest.TestCase):
                def runTest(self):
                    env = DummyEnvironment(LIBPATH=[test.workpath("d1/d2"),
                                                    test.workpath("d1")],
                                           LIBS=u'l2 l3'.split())
                    s = SCons.Scanner.Prog.ProgramScanner()
                    path = s.path(env)
                    deps = s(DummyNode('dummy'), env, path)
                    assert deps_match(deps, ['d1/l2.lib', 'd1/d2/l3.lib']), map(str, deps)
            suite.addTest(ProgramScannerTestCase4())
            \n"""
        exec(code)
    return suite

if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
