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

import sys
import unittest
import UserDict

import SCons.Scanner

class DummyEnvironment(UserDict.UserDict):
    def __init__(self, dict=None, **kw):
        UserDict.UserDict.__init__(self, dict)
        self.data.update(kw)
    def subst(self, strSubst):
        if strSubst[0] == '$':
            return self.data[strSubst[1:]]
        return strSubst
    def subst_list(self, strSubst):
        if strSubst[0] == '$':
            return [self.data[strSubst[1:]]]
        return [[strSubst]]
    def subst_path(self, path):
        if type(path) != type([]):
            path = [path]
        return map(self.subst, path)

class FindPathDirsTestCase(unittest.TestCase):
    def test_FindPathDirs(self):
        """Test the FindPathDirs callable class"""

        class FS:
            def Rsearchall(self, nodes, must_exist=0, clazz=None, cwd=dir):
                return ['xxx'] + nodes

        env = DummyEnvironment(LIBPATH = [ 'foo' ])

        fpd = SCons.Scanner.FindPathDirs('LIBPATH', FS())
        result = fpd(env, dir)
        assert result == ('xxx', 'foo'), result

class ScannerTestCase(unittest.TestCase):
    
    def func(self, filename, env, target, *args):
        self.filename = filename
        self.env = env
        self.target = target

        if len(args) > 0:
            self.arg = args[0]
        
        return self.deps

    def test(self, scanner, env, filename, deps, *args):
        self.deps = deps
        path = scanner.path(env)
        scanned = scanner(filename, env, path)
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

    def test_positional(self):
        """Test the Scanner.Base class using positional arguments"""
        s = SCons.Scanner.Base(self.func, "Pos")
        env = DummyEnvironment()
        env.VARIABLE = "var1"
        self.test(s, env, 'f1.cpp', ['f1.h', 'f1.hpp'])

        env = DummyEnvironment()
        env.VARIABLE = "i1"
        self.test(s, env, 'i1.cpp', ['i1.h', 'i1.hpp'])

    def test_keywords(self):
        """Test the Scanner.Base class using keyword arguments"""
        s = SCons.Scanner.Base(function = self.func, name = "Key")
        env = DummyEnvironment()
        env.VARIABLE = "var2"
        self.test(s, env, 'f2.cpp', ['f2.h', 'f2.hpp'])

        env = DummyEnvironment()
        env.VARIABLE = "i2"
        self.test(s, env, 'i2.cpp', ['i2.h', 'i2.hpp'])

    def test_pos_opt(self):
        """Test the Scanner.Base class using both position and optional arguments"""
        arg = "this is the argument"
        s = SCons.Scanner.Base(self.func, "PosArg", arg)
        env = DummyEnvironment()
        env.VARIABLE = "var3"
        self.test(s, env, 'f3.cpp', ['f3.h', 'f3.hpp'], arg)

        env = DummyEnvironment()
        env.VARIABLE = "i3"
        self.test(s, env, 'i3.cpp', ['i3.h', 'i3.hpp'], arg)

    def test_key_opt(self):
        """Test the Scanner.Base class using both keyword and optional arguments"""
        arg = "this is another argument"
        s = SCons.Scanner.Base(function = self.func, name = "KeyArg",
                               argument = arg)
        env = DummyEnvironment()
        env.VARIABLE = "var4"
        self.test(s, env, 'f4.cpp', ['f4.h', 'f4.hpp'], arg)

        env = DummyEnvironment()
        env.VARIABLE = "i4"
        self.test(s, env, 'i4.cpp', ['i4.h', 'i4.hpp'], arg)

    def test_hash(self):
        """Test the Scanner.Base class __hash__() method"""
        s = SCons.Scanner.Base(self.func, "Hash")
        dict = {}
        dict[s] = 777
        self.failUnless(hash(dict.keys()[0]) == hash(repr(s)),
                        "did not hash Scanner base class as expected")

    def test_scan_check(self):
        """Test the Scanner.Base class scan_check() method"""
        def my_scan(filename, env, target, *args):
            return []
        def check(node, s=self):
            s.checked[node] = 1
            return 1
        env = DummyEnvironment()
        s = SCons.Scanner.Base(my_scan, "Check", scan_check = check)
        self.checked = {}
        path = s.path(env)
        scanned = s('x', env, path)
        self.failUnless(self.checked['x'] == 1,
                        "did not call check function")

    def test_recursive(self):
        """Test the Scanner.Base class recursive flag"""
        s = SCons.Scanner.Base(function = self.func)
        self.failUnless(s.recursive == None,
                        "incorrect default recursive value")
        s = SCons.Scanner.Base(function = self.func, recursive = None)
        self.failUnless(s.recursive == None,
                        "did not set recursive flag to None")
        s = SCons.Scanner.Base(function = self.func, recursive = 1)
        self.failUnless(s.recursive == 1,
                        "did not set recursive flag to 1")

    def test_get_skeys(self):
        """Test the Scanner.Base get_skeys() method"""
        s = SCons.Scanner.Base(function = self.func)
        sk = s.get_skeys()
        self.failUnless(sk == [],
                        "did not initialize to expected []")

        s = SCons.Scanner.Base(function = self.func, skeys = ['.1', '.2'])
        sk = s.get_skeys()
        self.failUnless(sk == ['.1', '.2'],
                        "sk was %s, not ['.1', '.2']")

        s = SCons.Scanner.Base(function = self.func, skeys = '$LIST')
        env = DummyEnvironment(LIST = ['.3', '.4'])
        sk = s.get_skeys(env)
        self.failUnless(sk == ['.3', '.4'],
                        "sk was %s, not ['.3', '.4']")

class CurrentTestCase(unittest.TestCase):
    def test_class(self):
        """Test the Scanner.Current class"""
        class MyNode:
            def __init__(self):
                self.called_has_builder = None
                self.called_current = None
                self.func_called = None
        class HasNoBuilder(MyNode):
            def has_builder(self):
                self.called_has_builder = 1
                return None
        class IsNotCurrent(MyNode):
            def has_builder(self):
                self.called_has_builder = 1
                return 1
            def current(self, sig):
                self.called_current = 1
                return None
        class IsCurrent(MyNode):
            def has_builder(self):
                self.called_has_builder = 1
                return 1
            def current(self, sig):
                self.called_current = 1
                return 1
        def func(node, env, path):
            node.func_called = 1
            return []
        env = DummyEnvironment()
        s = SCons.Scanner.Current(func)
        path = s.path(env)
        hnb = HasNoBuilder()
        s(hnb, env, path)
        self.failUnless(hnb.called_has_builder, "did not call has_builder()")
        self.failUnless(not hnb.called_current, "did call current()")
        self.failUnless(hnb.func_called, "did not call func()")
        inc = IsNotCurrent()
        s(inc, env, path)
        self.failUnless(inc.called_has_builder, "did not call has_builder()")
        self.failUnless(inc.called_current, "did not call current()")
        self.failUnless(not inc.func_called, "did call func()")
        ic = IsCurrent()
        s(ic, env, path)
        self.failUnless(ic.called_has_builder, "did not call has_builder()")
        self.failUnless(ic.called_current, "did not call current()")
        self.failUnless(ic.func_called, "did not call func()")

class ClassicTestCase(unittest.TestCase):
    def test_find_include(self):
        """Test the Scanner.Classic find_include() method"""
        env = DummyEnvironment()
        s = SCons.Scanner.Classic("t", ['.suf'], 'MYPATH', '^my_inc (\S+)')

        def _find_file(filename, paths, factory):
            return paths[0]+'/'+filename

        save = SCons.Node.FS.find_file
        SCons.Node.FS.find_file = _find_file

        try:
            n, i = s.find_include('aaa', 'foo', ('path',))
            assert n == 'foo/aaa', n
            assert i == 'aaa', i

        finally:
            SCons.Node.FS.find_file = save

    def test_name(self):
        """Test setting the Scanner.Classic name"""
        s = SCons.Scanner.Classic("my_name", ['.s'], 'MYPATH', '^my_inc (\S+)')
        assert s.name == "my_name", s.name

    def test_scan(self):
        """Test the Scanner.Classic scan() method"""
        class MyNode:
            def __init__(self, name):
                self.name = name
                self._rfile = self
                self.includes = None
            def rfile(self):
                return self._rfile
            def exists(self):
                return self._exists
            def get_contents(self):
                return self._contents
            def get_dir(self):
                return self._dir

        class MyScanner(SCons.Scanner.Classic):
            def find_include(self, include, source_dir, path):
                return include, include

        env = DummyEnvironment()
        s = MyScanner("t", ['.suf'], 'MYPATH', '^my_inc (\S+)')

        # If the node doesn't exist, scanning turns up nothing.
        n1 = MyNode("n1")
        n1._exists = None
        ret = s.scan(n1, env)
        assert ret == [], ret

        # Verify that it finds includes from the contents.
        n = MyNode("n")
        n._exists = 1
        n._dir = MyNode("n._dir")
        n._contents = 'my_inc abc\n'
        ret = s.scan(n, env)
        assert ret == ['abc'], ret

        # Verify that it uses the cached include info.
        n._contents = 'my_inc def\n'
        ret = s.scan(n, env)
        assert ret == ['abc'], ret

        # Verify that if we wipe the cache, it uses the new contents.
        n.includes = None
        ret = s.scan(n, env)
        assert ret == ['def'], ret

        # Verify that it sorts what it finds.
        n.includes = ['xyz', 'uvw']
        ret = s.scan(n, env)
        assert ret == ['uvw', 'xyz'], ret

        # Verify that we use the rfile() node.
        nr = MyNode("nr")
        nr._exists = 1
        nr._dir = MyNode("nr._dir")
        nr.includes = ['jkl', 'mno']
        n._rfile = nr
        ret = s.scan(n, env)
        assert ret == ['jkl', 'mno'], ret

class ClassicCPPTestCase(unittest.TestCase):
    def test_find_include(self):
        """Test the Scanner.ClassicCPP find_include() method"""
        env = DummyEnvironment()
        s = SCons.Scanner.ClassicCPP("Test", [], None, "")

        def _find_file(filename, paths, factory):
            return paths[0]+'/'+filename

        save = SCons.Node.FS.find_file
        SCons.Node.FS.find_file = _find_file

        try:
            n, i = s.find_include(('"', 'aaa'), 'foo', ('path',))
            assert n == 'foo/aaa', n
            assert i == 'aaa', i

            n, i = s.find_include(('<', 'bbb'), 'foo', ('path',))
            assert n == 'path/bbb', n
            assert i == 'bbb', i

        finally:
            SCons.Node.FS.find_file = _find_file

def suite():
    suite = unittest.TestSuite()
    tclasses = [
                 FindPathDirsTestCase,
                 ScannerTestCase,
                 CurrentTestCase,
                 ClassicTestCase,
                 ClassicCPPTestCase,
               ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(map(tclass, names))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)
