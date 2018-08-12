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

import SCons.compat

import io
import os
import sys
import unittest
from collections import UserDict, UserList, UserString

import TestCmd

import SCons.Errors

from SCons.Util import *

try: eval('unicode')
except NameError: HasUnicode = False
else:             HasUnicode = True

class OutBuffer(object):
    def __init__(self):
        self.buffer = ""

    def write(self, str):
        self.buffer = self.buffer + str

class dictifyTestCase(unittest.TestCase):
    def test_dictify(self):
        """Test the dictify() function"""
        r = SCons.Util.dictify(['a', 'b', 'c'], [1, 2, 3])
        assert r == {'a':1, 'b':2, 'c':3}, r

        r = {}
        SCons.Util.dictify(['a'], [1], r)
        SCons.Util.dictify(['b'], [2], r)
        SCons.Util.dictify(['c'], [3], r)
        assert r == {'a':1, 'b':2, 'c':3}, r

class UtilTestCase(unittest.TestCase):
    def test_splitext(self):
        assert splitext('foo') == ('foo','')
        assert splitext('foo.bar') == ('foo','.bar')
        assert splitext(os.path.join('foo.bar', 'blat')) == (os.path.join('foo.bar', 'blat'),'')

    class Node(object):
        def __init__(self, name, children=[]):
            self.children = children
            self.name = name
            self.nocache = None
        def __str__(self):
            return self.name
        def exists(self):
            return 1
        def rexists(self):
            return 1
        def has_builder(self):
            return 1
        def has_explicit_builder(self):
            return 1
        def side_effect(self):
            return 1
        def precious(self):
            return 1
        def always_build(self):
            return 1
        def is_up_to_date(self):
            return 1
        def noclean(self):
            return 1

    def tree_case_1(self):
        """Fixture for the render_tree() and print_tree() tests."""
        windows_h = self.Node("windows.h")
        stdlib_h = self.Node("stdlib.h")
        stdio_h = self.Node("stdio.h")
        bar_c = self.Node("bar.c", [stdlib_h, windows_h])
        bar_o = self.Node("bar.o", [bar_c])
        foo_c = self.Node("foo.c", [stdio_h])
        foo_o = self.Node("foo.o", [foo_c])
        foo = self.Node("foo", [foo_o, bar_o])

        expect = """\
+-foo
  +-foo.o
  | +-foo.c
  |   +-stdio.h
  +-bar.o
    +-bar.c
      +-stdlib.h
      +-windows.h
"""

        lines = expect.split('\n')[:-1]
        lines = ['[E BSPACN ]'+l for l in lines]
        withtags = '\n'.join(lines) + '\n'

        return foo, expect, withtags

    def tree_case_2(self, prune=1):
        """Fixture for the render_tree() and print_tree() tests."""

        types_h = self.Node('types.h')
        malloc_h = self.Node('malloc.h')
        stdlib_h = self.Node('stdlib.h', [types_h, malloc_h])
        bar_h = self.Node('bar.h', [stdlib_h])
        blat_h = self.Node('blat.h', [stdlib_h])
        blat_c = self.Node('blat.c', [blat_h, bar_h])
        blat_o = self.Node('blat.o', [blat_c])

        expect = """\
+-blat.o
  +-blat.c
    +-blat.h
    | +-stdlib.h
    |   +-types.h
    |   +-malloc.h
    +-bar.h
"""
        if prune:
            expect += """      +-[stdlib.h]
"""
        else:
            expect += """      +-stdlib.h
        +-types.h
        +-malloc.h
"""

        lines = expect.split('\n')[:-1]
        lines = ['[E BSPACN ]'+l for l in lines]
        withtags = '\n'.join(lines) + '\n'

        return blat_o, expect, withtags

    def test_render_tree(self):
        """Test the render_tree() function"""
        def get_children(node):
            return node.children

        node, expect, withtags = self.tree_case_1()
        actual = render_tree(node, get_children)
        assert expect == actual, (expect, actual)

        node, expect, withtags = self.tree_case_2()
        actual = render_tree(node, get_children, 1)
        assert expect == actual, (expect, actual)

        # Ensure that we can call render_tree on the same Node
        # again. This wasn't possible in version 2.4.1 and earlier
        # due to a bug in render_tree (visited was set to {} as default
        # parameter)
        actual = render_tree(node, get_children, 1)
        assert expect == actual, (expect, actual)

    def test_print_tree(self):
        """Test the print_tree() function"""
        def get_children(node):
            return node.children

        save_stdout = sys.stdout

        try:
            node, expect, withtags = self.tree_case_1()

            if sys.version_info.major < 3:
                IOStream = io.BytesIO
            else:
                IOStream = io.StringIO

            sys.stdout = IOStream()
            print_tree(node, get_children)
            actual = sys.stdout.getvalue()
            assert expect == actual, (expect, actual)

            sys.stdout = IOStream()
            print_tree(node, get_children, showtags=1)
            actual = sys.stdout.getvalue()
            assert withtags == actual, (withtags, actual)

            # Test that explicitly setting prune to zero works
            # the same as the default (see above)
            node, expect, withtags = self.tree_case_2(prune=0)

            sys.stdout = IOStream()
            print_tree(node, get_children, 0)
            actual = sys.stdout.getvalue()
            assert expect == actual, (expect, actual)

            sys.stdout = IOStream()
            print_tree(node, get_children, 0, showtags=1)
            actual = sys.stdout.getvalue()
            assert withtags == actual, (withtags, actual)

            # Test output with prune=1
            node, expect, withtags = self.tree_case_2(prune=1)

            sys.stdout = IOStream()
            print_tree(node, get_children, 1)
            actual = sys.stdout.getvalue()
            assert expect == actual, (expect, actual)

            # Ensure that we can call print_tree on the same Node
            # again. This wasn't possible in version 2.4.1 and earlier
            # due to a bug in print_tree (visited was set to {} as default
            # parameter)
            sys.stdout = IOStream()
            print_tree(node, get_children, 1)
            actual = sys.stdout.getvalue()
            assert expect == actual, (expect, actual)

            sys.stdout = IOStream()
            print_tree(node, get_children, 1, showtags=1)
            actual = sys.stdout.getvalue()
            assert withtags == actual, (withtags, actual)
        finally:
            sys.stdout = save_stdout

    def test_is_Dict(self):
        assert is_Dict({})
        assert is_Dict(UserDict())

        # os.environ is not a dictionary in python 3
        if sys.version_info < (3,0):
            assert is_Dict(os.environ)

        try:
            class mydict(dict):
                pass
        except TypeError:
            pass
        else:
            assert is_Dict(mydict({}))
        assert not is_Dict([])
        assert not is_Dict(())
        assert not is_Dict("")
        if HasUnicode:
            exec("assert not is_Dict(u'')")

    def test_is_List(self):
        assert is_List([])
        assert is_List(UserList())
        try:
            class mylist(list):
                pass
        except TypeError:
            pass
        else:
            assert is_List(mylist([]))
        assert not is_List(())
        assert not is_List({})
        assert not is_List("")
        if HasUnicode:
            exec("assert not is_List(u'')")

    def test_is_String(self):
        assert is_String("")
        if HasUnicode:
            exec("assert is_String(u'')")
        assert is_String(UserString(''))
        try:
            class mystr(str):
                pass
        except TypeError:
            pass
        else:
            assert is_String(mystr(''))
        assert not is_String({})
        assert not is_String([])
        assert not is_String(())

    def test_is_Tuple(self):
        assert is_Tuple(())
        try:
            class mytuple(tuple):
                pass
        except TypeError:
            pass
        else:
            assert is_Tuple(mytuple(()))
        assert not is_Tuple([])
        assert not is_Tuple({})
        assert not is_Tuple("")
        if HasUnicode:
            exec("assert not is_Tuple(u'')")

    def test_to_Bytes(self):
        """ Test the to_Bytes method"""
        if not PY3:
            self.assertEqual(to_bytes(UnicodeType('Hello')),
                             bytearray(u'Hello', 'utf-8'),
                             "Check that to_bytes creates byte array when presented with unicode string. PY2 only")


    def test_to_String(self):
        """Test the to_String() method."""
        assert to_String(1) == "1", to_String(1)
        assert to_String([ 1, 2, 3]) == str([1, 2, 3]), to_String([1,2,3])
        assert to_String("foo") == "foo", to_String("foo")
        assert to_String(None) == 'None'
        # test low level string converters too
        assert to_str(None) == 'None'
        assert to_bytes(None) == b'None'

        s1=UserString('blah')
        assert to_String(s1) == s1, s1
        assert to_String(s1) == 'blah', s1

        class Derived(UserString):
            pass
        s2 = Derived('foo')
        assert to_String(s2) == s2, s2
        assert to_String(s2) == 'foo', s2

        if HasUnicode:
            s3=UserString(unicode('bar'))
            assert to_String(s3) == s3, s3
            assert to_String(s3) == unicode('bar'), s3
            assert isinstance(to_String(s3), unicode), \
                   type(to_String(s3))

        if HasUnicode:
            s4 = unicode('baz')
            assert to_String(s4) == unicode('baz'), to_String(s4)
            assert isinstance(to_String(s4), unicode), \
                   type(to_String(s4))

    def test_WhereIs(self):
        test = TestCmd.TestCmd(workdir = '')

        sub1_xxx_exe = test.workpath('sub1', 'xxx.exe')
        sub2_xxx_exe = test.workpath('sub2', 'xxx.exe')
        sub3_xxx_exe = test.workpath('sub3', 'xxx.exe')
        sub4_xxx_exe = test.workpath('sub4', 'xxx.exe')

        test.subdir('subdir', 'sub1', 'sub2', 'sub3', 'sub4')

        if sys.platform != 'win32':
            test.write(sub1_xxx_exe, "\n")

        os.mkdir(sub2_xxx_exe)

        test.write(sub3_xxx_exe, "\n")
        os.chmod(sub3_xxx_exe, 0o777)

        test.write(sub4_xxx_exe, "\n")
        os.chmod(sub4_xxx_exe, 0o777)

        env_path = os.environ['PATH']

        try:
            pathdirs_1234 = [ test.workpath('sub1'),
                              test.workpath('sub2'),
                              test.workpath('sub3'),
                              test.workpath('sub4'),
                            ] + env_path.split(os.pathsep)

            pathdirs_1243 = [ test.workpath('sub1'),
                              test.workpath('sub2'),
                              test.workpath('sub4'),
                              test.workpath('sub3'),
                            ] + env_path.split(os.pathsep)

            os.environ['PATH'] = os.pathsep.join(pathdirs_1234)
            wi = WhereIs('xxx.exe')
            assert wi == test.workpath(sub3_xxx_exe), wi
            wi = WhereIs('xxx.exe', pathdirs_1243)
            assert wi == test.workpath(sub4_xxx_exe), wi
            wi = WhereIs('xxx.exe', os.pathsep.join(pathdirs_1243))
            assert wi == test.workpath(sub4_xxx_exe), wi

            wi = WhereIs('xxx.exe',reject = sub3_xxx_exe)
            assert wi == test.workpath(sub4_xxx_exe), wi
            wi = WhereIs('xxx.exe', pathdirs_1243, reject = sub3_xxx_exe)
            assert wi == test.workpath(sub4_xxx_exe), wi

            os.environ['PATH'] = os.pathsep.join(pathdirs_1243)
            wi = WhereIs('xxx.exe')
            assert wi == test.workpath(sub4_xxx_exe), wi
            wi = WhereIs('xxx.exe', pathdirs_1234)
            assert wi == test.workpath(sub3_xxx_exe), wi
            wi = WhereIs('xxx.exe', os.pathsep.join(pathdirs_1234))
            assert wi == test.workpath(sub3_xxx_exe), wi

            if sys.platform == 'win32':
                wi = WhereIs('xxx', pathext = '')
                assert wi is None, wi

                wi = WhereIs('xxx', pathext = '.exe')
                assert wi == test.workpath(sub4_xxx_exe), wi

                wi = WhereIs('xxx', path = pathdirs_1234, pathext = '.BAT;.EXE')
                assert wi.lower() == test.workpath(sub3_xxx_exe).lower(), wi

                # Test that we return a normalized path even when
                # the path contains forward slashes.
                forward_slash = test.workpath('') + '/sub3'
                wi = WhereIs('xxx', path = forward_slash, pathext = '.EXE')
                assert wi.lower() == test.workpath(sub3_xxx_exe).lower(), wi

            del os.environ['PATH']
            wi = WhereIs('xxx.exe')
            assert wi is None, wi

        finally:
            os.environ['PATH'] = env_path

    def test_get_env_var(self):
        """Testing get_environment_var()."""
        assert get_environment_var("$FOO") == "FOO", get_environment_var("$FOO")
        assert get_environment_var("${BAR}") == "BAR", get_environment_var("${BAR}")
        assert get_environment_var("$FOO_BAR1234") == "FOO_BAR1234", get_environment_var("$FOO_BAR1234")
        assert get_environment_var("${BAR_FOO1234}") == "BAR_FOO1234", get_environment_var("${BAR_FOO1234}")
        assert get_environment_var("${BAR}FOO") == None, get_environment_var("${BAR}FOO")
        assert get_environment_var("$BAR ") == None, get_environment_var("$BAR ")
        assert get_environment_var("FOO$BAR") == None, get_environment_var("FOO$BAR")
        assert get_environment_var("$FOO[0]") == None, get_environment_var("$FOO[0]")
        assert get_environment_var("${some('complex expression')}") == None, get_environment_var("${some('complex expression')}")

    def test_Proxy(self):
        """Test generic Proxy class."""
        class Subject(object):
            def foo(self):
                return 1
            def bar(self):
                return 2

        s=Subject()
        s.baz = 3

        class ProxyTest(Proxy):
            def bar(self):
                return 4

        p=ProxyTest(s)

        assert p.foo() == 1, p.foo()
        assert p.bar() == 4, p.bar()
        assert p.baz == 3, p.baz

        p.baz = 5
        s.baz = 6

        assert p.baz == 5, p.baz
        assert p.get() == s, p.get()

    def test_display(self):
        old_stdout = sys.stdout
        sys.stdout = OutBuffer()
        display("line1")
        display.set_mode(0)
        display("line2")
        display.set_mode(1)
        display("line3")
        display("line4\n", append_newline=0)
        display.set_mode(0)
        display("dont print1")
        display("dont print2\n", append_newline=0)
        display.set_mode(1)
        assert sys.stdout.buffer == "line1\nline3\nline4\n"
        sys.stdout = old_stdout

    def test_get_native_path(self):
        """Test the get_native_path() function."""
        import tempfile
        filename = tempfile.mktemp()
        str = '1234567890 ' + filename
        try:
            with open(filename, 'w') as f:
                f.write(str)
            with open(get_native_path(filename)) as f:
                assert f.read() == str
        finally:
            try:
                os.unlink(filename)
            except OSError:
                pass

    def test_PrependPath(self):
        """Test prepending to a path"""
        p1 = r'C:\dir\num\one;C:\dir\num\two'
        p2 = r'C:\mydir\num\one;C:\mydir\num\two'
        # have to include the pathsep here so that the test will work on UNIX too.
        p1 = PrependPath(p1,r'C:\dir\num\two',sep = ';')
        p1 = PrependPath(p1,r'C:\dir\num\three',sep = ';')
        p2 = PrependPath(p2,r'C:\mydir\num\three',sep = ';')
        p2 = PrependPath(p2,r'C:\mydir\num\one',sep = ';')
        assert(p1 == r'C:\dir\num\three;C:\dir\num\two;C:\dir\num\one')
        assert(p2 == r'C:\mydir\num\one;C:\mydir\num\three;C:\mydir\num\two')

    def test_AppendPath(self):
        """Test appending to a path."""
        p1 = r'C:\dir\num\one;C:\dir\num\two'
        p2 = r'C:\mydir\num\one;C:\mydir\num\two'
        # have to include the pathsep here so that the test will work on UNIX too.
        p1 = AppendPath(p1,r'C:\dir\num\two',sep = ';')
        p1 = AppendPath(p1,r'C:\dir\num\three',sep = ';')
        p2 = AppendPath(p2,r'C:\mydir\num\three',sep = ';')
        p2 = AppendPath(p2,r'C:\mydir\num\one',sep = ';')
        assert(p1 == r'C:\dir\num\one;C:\dir\num\two;C:\dir\num\three')
        assert(p2 == r'C:\mydir\num\two;C:\mydir\num\three;C:\mydir\num\one')

    def test_PrependPathPreserveOld(self):
        """Test prepending to a path while preserving old paths"""
        p1 = r'C:\dir\num\one;C:\dir\num\two'
        # have to include the pathsep here so that the test will work on UNIX too.
        p1 = PrependPath(p1,r'C:\dir\num\two',sep = ';', delete_existing=0)
        p1 = PrependPath(p1,r'C:\dir\num\three',sep = ';')
        assert(p1 == r'C:\dir\num\three;C:\dir\num\one;C:\dir\num\two')

    def test_AppendPathPreserveOld(self):
        """Test appending to a path while preserving old paths"""
        p1 = r'C:\dir\num\one;C:\dir\num\two'
        # have to include the pathsep here so that the test will work on UNIX too.
        p1 = AppendPath(p1,r'C:\dir\num\one',sep = ';', delete_existing=0)
        p1 = AppendPath(p1,r'C:\dir\num\three',sep = ';')
        assert(p1 == r'C:\dir\num\one;C:\dir\num\two;C:\dir\num\three')

    def test_addPathIfNotExists(self):
        """Test the AddPathIfNotExists() function"""
        env_dict = { 'FOO' : os.path.normpath('/foo/bar') + os.pathsep + \
                     os.path.normpath('/baz/blat'),
                     'BAR' : os.path.normpath('/foo/bar') + os.pathsep + \
                     os.path.normpath('/baz/blat'),
                     'BLAT' : [ os.path.normpath('/foo/bar'),
                                os.path.normpath('/baz/blat') ] }
        AddPathIfNotExists(env_dict, 'FOO', os.path.normpath('/foo/bar'))
        AddPathIfNotExists(env_dict, 'BAR', os.path.normpath('/bar/foo'))
        AddPathIfNotExists(env_dict, 'BAZ', os.path.normpath('/foo/baz'))
        AddPathIfNotExists(env_dict, 'BLAT', os.path.normpath('/baz/blat'))
        AddPathIfNotExists(env_dict, 'BLAT', os.path.normpath('/baz/foo'))

        assert env_dict['FOO'] == os.path.normpath('/foo/bar') + os.pathsep + \
               os.path.normpath('/baz/blat'), env_dict['FOO']
        assert env_dict['BAR'] == os.path.normpath('/bar/foo') + os.pathsep + \
               os.path.normpath('/foo/bar') + os.pathsep + \
               os.path.normpath('/baz/blat'), env_dict['BAR']
        assert env_dict['BAZ'] == os.path.normpath('/foo/baz'), env_dict['BAZ']
        assert env_dict['BLAT'] == [ os.path.normpath('/baz/foo'),
                                     os.path.normpath('/foo/bar'),
                                     os.path.normpath('/baz/blat') ], env_dict['BLAT' ]

    def test_CLVar(self):
        """Test the command-line construction variable class"""
        f = SCons.Util.CLVar('a b')

        r = f + 'c d'
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + ' c d'
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + ['c d']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c d'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + [' c d']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', ' c d'], r.data
        assert str(r) == 'a b  c d', str(r)

        r = f + ['c', 'd']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + [' c', 'd']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', ' c', 'd'], r.data
        assert str(r) == 'a b  c d', str(r)

        f = SCons.Util.CLVar(['a b'])

        r = f + 'c d'
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + ' c d'
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + ['c d']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a b', 'c d'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + [' c d']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a b', ' c d'], r.data
        assert str(r) == 'a b  c d', str(r)

        r = f + ['c', 'd']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + [' c', 'd']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a b', ' c', 'd'], r.data
        assert str(r) == 'a b  c d', str(r)

        f = SCons.Util.CLVar(['a', 'b'])

        r = f + 'c d'
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + ' c d'
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + ['c d']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c d'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + [' c d']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', ' c d'], r.data
        assert str(r) == 'a b  c d', str(r)

        r = f + ['c', 'd']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + [' c', 'd']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', ' c', 'd'], r.data
        assert str(r) == 'a b  c d', str(r)

    def test_Selector(self):
        """Test the Selector class"""

        class MyNode(object):
            def __init__(self, name):
                self.name = name

            def __str__(self):
                return self.name
            def get_suffix(self):
                return os.path.splitext(self.name)[1]

        s = Selector({'a' : 'AAA', 'b' : 'BBB'})
        assert s['a'] == 'AAA', s['a']
        assert s['b'] == 'BBB', s['b']
        exc_caught = None
        try:
            x = s['c']
        except KeyError:
            exc_caught = 1
        assert exc_caught, "should have caught a KeyError"
        s['c'] = 'CCC'
        assert s['c'] == 'CCC', s['c']

        class DummyEnv(UserDict):
            def subst(self, key):
                if key[0] == '$':
                    return self[key[1:]]
                return key

        env = DummyEnv()

        s = Selector({'.d' : 'DDD', '.e' : 'EEE'})
        ret = s(env, [])
        assert ret is None, ret
        ret = s(env, [MyNode('foo.d')])
        assert ret == 'DDD', ret
        ret = s(env, [MyNode('bar.e')])
        assert ret == 'EEE', ret
        ret = s(env, [MyNode('bar.x')])
        assert ret is None, ret
        s[None] = 'XXX'
        ret = s(env, [MyNode('bar.x')])
        assert ret == 'XXX', ret

        env = DummyEnv({'FSUFF' : '.f', 'GSUFF' : '.g'})

        s = Selector({'$FSUFF' : 'FFF', '$GSUFF' : 'GGG'})
        ret = s(env, [MyNode('foo.f')])
        assert ret == 'FFF', ret
        ret = s(env, [MyNode('bar.g')])
        assert ret == 'GGG', ret

    def test_adjustixes(self):
        """Test the adjustixes() function"""
        r = adjustixes('file', 'pre-', '-suf')
        assert r == 'pre-file-suf', r
        r = adjustixes('pre-file', 'pre-', '-suf')
        assert r == 'pre-file-suf', r
        r = adjustixes('file-suf', 'pre-', '-suf')
        assert r == 'pre-file-suf', r
        r = adjustixes('pre-file-suf', 'pre-', '-suf')
        assert r == 'pre-file-suf', r
        r = adjustixes('pre-file.xxx', 'pre-', '-suf')
        assert r == 'pre-file.xxx', r
        r = adjustixes('dir/file', 'pre-', '-suf')
        assert r == os.path.join('dir', 'pre-file-suf'), r

    def test_containsAny(self):
        """Test the containsAny() function"""
        assert containsAny('*.py', '*?[]')
        assert not containsAny('file.txt', '*?[]')

    def test_containsAll(self):
        """Test the containsAll() function"""
        assert containsAll('43221', '123')
        assert not containsAll('134', '123')

    def test_containsOnly(self):
        """Test the containsOnly() function"""
        assert containsOnly('.83', '0123456789.')
        assert not containsOnly('43221', '123')

    def test_LogicalLines(self):
        """Test the LogicalLines class"""
        content = u"""
foo \
bar \
baz
foo
bling \
bling \ bling
bling
"""
        fobj = io.StringIO(content)
        lines = LogicalLines(fobj).readlines()
        assert lines == [
            '\n',
            'foo bar baz\n',
            'foo\n',
            'bling bling \\ bling\n',
            'bling\n',
        ], lines

    def test_intern(self):
        s1 = silent_intern("spam")
        # TODO: Python 3.x does not have a unicode() global function
        if sys.version[0] == '2':
            s2 = silent_intern(unicode("unicode spam"))
        s3 = silent_intern(42)
        s4 = silent_intern("spam")
        assert id(s1) == id(s4)


class MD5TestCase(unittest.TestCase):

    def test_collect(self):
        """Test collecting a list of signatures into a new signature value
        """
        s = list(map(MD5signature, ('111', '222', '333')))

        assert '698d51a19d8a121ce581499d7b701668' == MD5collect(s[0:1])
        assert '8980c988edc2c78cc43ccb718c06efd5' == MD5collect(s[0:2])
        assert '53fd88c84ff8a285eb6e0a687e55b8c7' == MD5collect(s)

    def test_MD5signature(self):
        """Test generating a signature"""
        s = MD5signature('111')
        assert '698d51a19d8a121ce581499d7b701668' == s, s

        s = MD5signature('222')
        assert 'bcbe3365e6ac95ea2c0343a2395834dd' == s, s

class NodeListTestCase(unittest.TestCase):
    def test_simple_attributes(self):
        """Test simple attributes of a NodeList class"""
        class TestClass(object):
            def __init__(self, name, child=None):
                self.child = child
                self.bar = name

        t1 = TestClass('t1', TestClass('t1child'))
        t2 = TestClass('t2', TestClass('t2child'))
        t3 = TestClass('t3')

        nl = NodeList([t1, t2, t3])
        assert nl.bar == [ 't1', 't2', 't3' ], nl.bar
        assert nl[0:2].child.bar == [ 't1child', 't2child' ], \
               nl[0:2].child.bar

    def test_callable_attributes(self):
        """Test callable attributes of a NodeList class"""
        class TestClass(object):
            def __init__(self, name, child=None):
                self.child = child
                self.bar = name
            def foo(self):
                return self.bar + "foo"
            def getself(self):
                return self

        t1 = TestClass('t1', TestClass('t1child'))
        t2 = TestClass('t2', TestClass('t2child'))
        t3 = TestClass('t3')

        nl = NodeList([t1, t2, t3])
        assert nl.foo() == [ 't1foo', 't2foo', 't3foo' ], nl.foo()
        assert nl.bar == [ 't1', 't2', 't3' ], nl.bar
        assert nl.getself().bar == [ 't1', 't2', 't3' ], nl.getself().bar
        assert nl[0:2].child.foo() == [ 't1childfoo', 't2childfoo' ], \
               nl[0:2].child.foo()
        assert nl[0:2].child.bar == [ 't1child', 't2child' ], \
               nl[0:2].child.bar

    def test_null(self):
        """Test a null NodeList"""
        nl = NodeList([])
        r = str(nl)
        assert r == '', r
        for node in nl:
            raise Exception("should not enter this loop")


class flattenTestCase(unittest.TestCase):

    def test_scalar(self):
        """Test flattening a scalar"""
        result = flatten('xyz')
        assert result == ['xyz'], result


if __name__ == "__main__":
    unittest.main()


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
