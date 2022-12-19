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

import functools
import io
import os
import sys
import unittest
import unittest.mock
import hashlib
import warnings
from collections import UserDict, UserList, UserString, namedtuple

import TestCmd

import SCons.Errors
import SCons.compat
from SCons.Util import (
    ALLOWED_HASH_FORMATS,
    AddPathIfNotExists,
    AppendPath,
    CLVar,
    LogicalLines,
    NodeList,
    PrependPath,
    Proxy,
    Selector,
    WhereIs,
    adjustixes,
    containsAll,
    containsAny,
    containsOnly,
    dictify,
    display,
    flatten,
    get_env_bool,
    get_environment_var,
    get_native_path,
    get_os_env_bool,
    hash_collect,
    hash_signature,
    is_Dict,
    is_List,
    is_String,
    is_Tuple,
    print_tree,
    render_tree,
    set_hash_format,
    silent_intern,
    splitext,
    to_String,
    to_bytes,
    to_str,
)
from SCons.Util.hashes import (
    _attempt_init_of_python_3_9_hash_object,
    _attempt_get_hash_function,
    _get_hash_object,
    _set_allowed_viable_default_hashes,
)

# These Util classes have no unit tests. Some don't make sense to test?
# DisplayEngine, Delegate, MethodWrapper, UniqueList, Unbuffered, Null, NullSeq


class OutBuffer:
    def __init__(self):
        self.buffer = ""

    def write(self, str):
        self.buffer = self.buffer + str


class dictifyTestCase(unittest.TestCase):
    def test_dictify(self):
        """Test the dictify() function"""
        r = dictify(['a', 'b', 'c'], [1, 2, 3])
        assert r == {'a': 1, 'b': 2, 'c': 3}, r

        r = {}
        dictify(['a'], [1], r)
        dictify(['b'], [2], r)
        dictify(['c'], [3], r)
        assert r == {'a': 1, 'b': 2, 'c': 3}, r


class UtilTestCase(unittest.TestCase):
    def test_splitext(self):
        assert splitext('foo') == ('foo', '')
        assert splitext('foo.bar') == ('foo', '.bar')
        assert splitext(os.path.join('foo.bar', 'blat')) == (os.path.join('foo.bar', 'blat'), '')

    class Node:
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
        lines = ['[E BSPACN ]' + l for l in lines]
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
        lines = ['[E BSPACN ]' + l for l in lines]
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

    def test_is_String(self):
        assert is_String("")
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

    def test_to_Bytes(self):
        """ Test the to_Bytes method"""
        self.assertEqual(to_bytes('Hello'),
                         bytearray('Hello', 'utf-8'),
                         "Check that to_bytes creates byte array when presented with non byte string.")

    def test_to_String(self):
        """Test the to_String() method."""
        assert to_String(1) == "1", to_String(1)
        assert to_String([1, 2, 3]) == str([1, 2, 3]), to_String([1, 2, 3])
        assert to_String("foo") == "foo", to_String("foo")
        assert to_String(None) == 'None'
        # test low level string converters too
        assert to_str(None) == 'None'
        assert to_bytes(None) == b'None'

        s1 = UserString('blah')
        assert to_String(s1) == s1, s1
        assert to_String(s1) == 'blah', s1

        class Derived(UserString):
            pass

        s2 = Derived('foo')
        assert to_String(s2) == s2, s2
        assert to_String(s2) == 'foo', s2


    def test_WhereIs(self):
        test = TestCmd.TestCmd(workdir='')

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
            pathdirs_1234 = [test.workpath('sub1'),
                             test.workpath('sub2'),
                             test.workpath('sub3'),
                             test.workpath('sub4'),
                             ] + env_path.split(os.pathsep)

            pathdirs_1243 = [test.workpath('sub1'),
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

            wi = WhereIs('xxx.exe', reject=sub3_xxx_exe)
            assert wi == test.workpath(sub4_xxx_exe), wi
            wi = WhereIs('xxx.exe', pathdirs_1243, reject=sub3_xxx_exe)
            assert wi == test.workpath(sub4_xxx_exe), wi

            os.environ['PATH'] = os.pathsep.join(pathdirs_1243)
            wi = WhereIs('xxx.exe')
            assert wi == test.workpath(sub4_xxx_exe), wi
            wi = WhereIs('xxx.exe', pathdirs_1234)
            assert wi == test.workpath(sub3_xxx_exe), wi
            wi = WhereIs('xxx.exe', os.pathsep.join(pathdirs_1234))
            assert wi == test.workpath(sub3_xxx_exe), wi

            if sys.platform == 'win32':
                wi = WhereIs('xxx', pathext='')
                assert wi is None, wi

                wi = WhereIs('xxx', pathext='.exe')
                assert wi == test.workpath(sub4_xxx_exe), wi

                wi = WhereIs('xxx', path=pathdirs_1234, pathext='.BAT;.EXE')
                assert wi.lower() == test.workpath(sub3_xxx_exe).lower(), wi

                # Test that we return a normalized path even when
                # the path contains forward slashes.
                forward_slash = test.workpath('') + '/sub3'
                wi = WhereIs('xxx', path=forward_slash, pathext='.EXE')
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
        assert get_environment_var("${BAR}FOO") is None, get_environment_var("${BAR}FOO")
        assert get_environment_var("$BAR ") is None, get_environment_var("$BAR ")
        assert get_environment_var("FOO$BAR") is None, get_environment_var("FOO$BAR")
        assert get_environment_var("$FOO[0]") is None, get_environment_var("$FOO[0]")
        assert get_environment_var("${some('complex expression')}") is None, get_environment_var(
            "${some('complex expression')}")

    def test_Proxy(self):
        """Test generic Proxy class."""

        class Subject:
            def foo(self):
                return 1

            def bar(self):
                return 2

        s = Subject()
        s.baz = 3

        class ProxyTest(Proxy):
            def bar(self):
                return 4

        p = ProxyTest(s)

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
        f, filename = tempfile.mkstemp(text=True)
        os.close(f)
        data = '1234567890 ' + filename
        try:
            with open(filename, 'w') as f:
                f.write(data)
            with open(get_native_path(filename), 'r') as f:
                assert f.read() == data
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
        p1 = PrependPath(p1, r'C:\dir\num\two', sep=';')
        p1 = PrependPath(p1, r'C:\dir\num\three', sep=';')
        assert p1 == r'C:\dir\num\three;C:\dir\num\two;C:\dir\num\one', p1

        p2 = PrependPath(p2, r'C:\mydir\num\three', sep=';')
        p2 = PrependPath(p2, r'C:\mydir\num\one', sep=';')
        assert p2 == r'C:\mydir\num\one;C:\mydir\num\three;C:\mydir\num\two', p2

        # check (only) first one is kept if there are dupes in new
        p3 = r'C:\dir\num\one'
        p3 = PrependPath(p3, r'C:\dir\num\two;C:\dir\num\three;C:\dir\num\two', sep=';')
        assert p3 == r'C:\dir\num\two;C:\dir\num\three;C:\dir\num\one', p3

    def test_AppendPath(self):
        """Test appending to a path."""
        p1 = r'C:\dir\num\one;C:\dir\num\two'
        p2 = r'C:\mydir\num\one;C:\mydir\num\two'
        # have to include the pathsep here so that the test will work on UNIX too.
        p1 = AppendPath(p1, r'C:\dir\num\two', sep=';')
        p1 = AppendPath(p1, r'C:\dir\num\three', sep=';')
        assert p1 == r'C:\dir\num\one;C:\dir\num\two;C:\dir\num\three', p1

        p2 = AppendPath(p2, r'C:\mydir\num\three', sep=';')
        p2 = AppendPath(p2, r'C:\mydir\num\one', sep=';')
        assert p2 == r'C:\mydir\num\two;C:\mydir\num\three;C:\mydir\num\one', p2

        # check (only) last one is kept if there are dupes in new
        p3 = r'C:\dir\num\one'
        p3 = AppendPath(p3, r'C:\dir\num\two;C:\dir\num\three;C:\dir\num\two', sep=';')
        assert p3 == r'C:\dir\num\one;C:\dir\num\three;C:\dir\num\two', p3

    def test_PrependPathPreserveOld(self):
        """Test prepending to a path while preserving old paths"""
        p1 = r'C:\dir\num\one;C:\dir\num\two'
        # have to include the pathsep here so that the test will work on UNIX too.
        p1 = PrependPath(p1, r'C:\dir\num\two', sep=';', delete_existing=0)
        p1 = PrependPath(p1, r'C:\dir\num\three', sep=';')
        assert p1 == r'C:\dir\num\three;C:\dir\num\one;C:\dir\num\two', p1

    def test_AppendPathPreserveOld(self):
        """Test appending to a path while preserving old paths"""
        p1 = r'C:\dir\num\one;C:\dir\num\two'
        # have to include the pathsep here so that the test will work on UNIX too.
        p1 = AppendPath(p1, r'C:\dir\num\one', sep=';', delete_existing=0)
        p1 = AppendPath(p1, r'C:\dir\num\three', sep=';')
        assert p1 == r'C:\dir\num\one;C:\dir\num\two;C:\dir\num\three', p1

    def test_addPathIfNotExists(self):
        """Test the AddPathIfNotExists() function"""
        env_dict = {'FOO': os.path.normpath('/foo/bar') + os.pathsep + \
                           os.path.normpath('/baz/blat'),
                    'BAR': os.path.normpath('/foo/bar') + os.pathsep + \
                           os.path.normpath('/baz/blat'),
                    'BLAT': [os.path.normpath('/foo/bar'),
                             os.path.normpath('/baz/blat')]}
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
        assert env_dict['BLAT'] == [os.path.normpath('/baz/foo'),
                                    os.path.normpath('/foo/bar'),
                                    os.path.normpath('/baz/blat')], env_dict['BLAT']

    def test_CLVar(self):
        """Test the command-line construction variable class"""

        # the default value should be an empty list
        d = CLVar()
        assert isinstance(d, CLVar), type(d)
        assert d.data == [], d.data
        assert str(d) == '', str(d)

        # input to CLVar is a string - should be split
        f = CLVar('aa bb')

        r = f + 'cc dd'
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa', 'bb', 'cc', 'dd'], r.data
        assert str(r) == 'aa bb cc dd', str(r)

        r = f + ' cc dd'
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa', 'bb', 'cc', 'dd'], r.data
        assert str(r) == 'aa bb cc dd', str(r)

        r = f + ['cc dd']
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa', 'bb', 'cc dd'], r.data
        assert str(r) == 'aa bb cc dd', str(r)

        r = f + [' cc dd']
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa', 'bb', ' cc dd'], r.data
        assert str(r) == 'aa bb  cc dd', str(r)

        r = f + ['cc', 'dd']
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa', 'bb', 'cc', 'dd'], r.data
        assert str(r) == 'aa bb cc dd', str(r)

        r = f + [' cc', 'dd']
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa', 'bb', ' cc', 'dd'], r.data
        assert str(r) == 'aa bb  cc dd', str(r)

        # input to CLVar is a list of one string, should not be split
        f = CLVar(['aa bb'])

        r = f + 'cc dd'
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa bb', 'cc', 'dd'], r.data
        assert str(r) == 'aa bb cc dd', str(r)

        r = f + ' cc dd'
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa bb', 'cc', 'dd'], r.data
        assert str(r) == 'aa bb cc dd', str(r)

        r = f + ['cc dd']
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa bb', 'cc dd'], r.data
        assert str(r) == 'aa bb cc dd', str(r)

        r = f + [' cc dd']
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa bb', ' cc dd'], r.data
        assert str(r) == 'aa bb  cc dd', str(r)

        r = f + ['cc', 'dd']
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa bb', 'cc', 'dd'], r.data
        assert str(r) == 'aa bb cc dd', str(r)

        r = f + [' cc', 'dd']
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa bb', ' cc', 'dd'], r.data
        assert str(r) == 'aa bb  cc dd', str(r)

        # input to CLVar is a list of strings
        f = CLVar(['aa', 'bb'])

        r = f + 'cc dd'
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa', 'bb', 'cc', 'dd'], r.data
        assert str(r) == 'aa bb cc dd', str(r)

        r = f + ' cc dd'
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa', 'bb', 'cc', 'dd'], r.data
        assert str(r) == 'aa bb cc dd', str(r)

        r = f + ['cc dd']
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa', 'bb', 'cc dd'], r.data
        assert str(r) == 'aa bb cc dd', str(r)

        r = f + [' cc dd']
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa', 'bb', ' cc dd'], r.data
        assert str(r) == 'aa bb  cc dd', str(r)

        r = f + ['cc', 'dd']
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa', 'bb', 'cc', 'dd'], r.data
        assert str(r) == 'aa bb cc dd', str(r)

        r = f + [' cc', 'dd']
        assert isinstance(r, CLVar), type(r)
        assert r.data == ['aa', 'bb', ' cc', 'dd'], r.data
        assert str(r) == 'aa bb  cc dd', str(r)

        # make sure inplace adding a string works as well (issue 2399)
        # UserList would convert the string to a list of chars
        f = CLVar(['aa', 'bb'])
        f += 'cc dd'
        assert isinstance(f, CLVar), type(f)
        assert f.data == ['aa', 'bb', 'cc', 'dd'], f.data
        assert str(f) == 'aa bb cc dd', str(f)

        f = CLVar(['aa', 'bb'])
        f += ' cc dd'
        assert isinstance(f, CLVar), type(f)
        assert f.data == ['aa', 'bb', 'cc', 'dd'], f.data
        assert str(f) == 'aa bb cc dd', str(f)


    def test_Selector(self):
        """Test the Selector class"""

        class MyNode:
            def __init__(self, name):
                self.name = name

            def __str__(self):
                return self.name

            def get_suffix(self):
                return os.path.splitext(self.name)[1]

        s = Selector({'a': 'AAA', 'b': 'BBB'})
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

        s = Selector({'.d': 'DDD', '.e': 'EEE'})
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

        env = DummyEnv({'FSUFF': '.f', 'GSUFF': '.g'})

        s = Selector({'$FSUFF': 'FFF', '$GSUFF': 'GGG'})
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

        # Verify that the odd case when library name is specified as 'lib'
        # doesn't yield lib.so, but yields the expected liblib.so
        r = adjustixes('PREFIX', 'PREFIX', 'SUFFIX')
        assert r == 'PREFIXPREFIXSUFFIX', "Failed handling when filename = PREFIX [r='%s']" % r

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
        content = """
foo \\
bar \\
baz
foo
bling \\
bling \\ bling
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
        s3 = silent_intern(42)
        s4 = silent_intern("spam")
        assert id(s1) == id(s4)


class HashTestCase(unittest.TestCase):

    def test_collect(self):
        """Test collecting a list of signatures into a new signature value
        """
        for algorithm, expected in {
            'md5': ('698d51a19d8a121ce581499d7b701668',
                    '8980c988edc2c78cc43ccb718c06efd5',
                    '53fd88c84ff8a285eb6e0a687e55b8c7'),
            'sha1': ('6216f8a75fd5bb3d5f22b6f9958cdede3fc086c2',
                     '42eda1b5dcb3586bccfb1c69f22f923145271d97',
                     '2eb2f7be4e883ebe52034281d818c91e1cf16256'),
            'sha256': ('f6e0a1e2ac41945a9aa7ff8a8aaa0cebc12a3bcc981a929ad5cf810a090e11ae',
                       '25235f0fcab8767b7b5ac6568786fbc4f7d5d83468f0626bf07c3dbeed391a7a',
                       'f8d3d0729bf2427e2e81007588356332e7e8c4133fae4bceb173b93f33411d17'),
        }.items():
            # if the current platform does not support the algorithm we're looking at,
            # skip the test steps for that algorithm, but display a warning to the user
            if algorithm not in ALLOWED_HASH_FORMATS:
                warnings.warn("Missing hash algorithm {} on this platform, cannot test with it".format(algorithm), ResourceWarning)
            else:
                hs = functools.partial(hash_signature, hash_format=algorithm)
                s = list(map(hs, ('111', '222', '333')))

                assert expected[0] == hash_collect(s[0:1], hash_format=algorithm)
                assert expected[1] == hash_collect(s[0:2], hash_format=algorithm)
                assert expected[2] == hash_collect(s, hash_format=algorithm)

    def test_MD5signature(self):
        """Test generating a signature"""
        for algorithm, expected in {
            'md5': ('698d51a19d8a121ce581499d7b701668',
                    'bcbe3365e6ac95ea2c0343a2395834dd'),
            'sha1': ('6216f8a75fd5bb3d5f22b6f9958cdede3fc086c2',
                     '1c6637a8f2e1f75e06ff9984894d6bd16a3a36a9'),
            'sha256': ('f6e0a1e2ac41945a9aa7ff8a8aaa0cebc12a3bcc981a929ad5cf810a090e11ae',
                       '9b871512327c09ce91dd649b3f96a63b7408ef267c8cc5710114e629730cb61f'),
        }.items():
            # if the current platform does not support the algorithm we're looking at,
            # skip the test steps for that algorithm, but display a warning to the user
            if algorithm not in ALLOWED_HASH_FORMATS:
                warnings.warn("Missing hash algorithm {} on this platform, cannot test with it".format(algorithm), ResourceWarning)
            else:
                s = hash_signature('111', hash_format=algorithm)
                assert expected[0] == s, s

                s = hash_signature('222', hash_format=algorithm)
                assert expected[1] == s, s

# this uses mocking out, which is platform specific, however, the FIPS
# behavior this is testing is also platform-specific, and only would be
# visible in hosts running Linux with the fips_mode kernel flag along
# with using OpenSSL.

class FIPSHashTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ###############################
        # algorithm mocks, can check if we called with usedforsecurity=False for python >= 3.9
        self.fake_md5=lambda usedforsecurity=True: (usedforsecurity, 'md5')
        self.fake_sha1=lambda usedforsecurity=True: (usedforsecurity, 'sha1')
        self.fake_sha256=lambda usedforsecurity=True: (usedforsecurity, 'sha256')
        ###############################

        ###############################
        # hashlib mocks
        md5Available = unittest.mock.Mock(md5=self.fake_md5)
        del md5Available.sha1
        del md5Available.sha256
        self.md5Available=md5Available

        md5Default = unittest.mock.Mock(md5=self.fake_md5, sha1=self.fake_sha1)
        del md5Default.sha256
        self.md5Default=md5Default

        sha1Default = unittest.mock.Mock(sha1=self.fake_sha1, sha256=self.fake_sha256)
        del sha1Default.md5
        self.sha1Default=sha1Default

        sha256Default = unittest.mock.Mock(sha256=self.fake_sha256, **{'md5.side_effect': ValueError, 'sha1.side_effect': ValueError})
        self.sha256Default=sha256Default

        all_throw = unittest.mock.Mock(**{'md5.side_effect': ValueError, 'sha1.side_effect': ValueError, 'sha256.side_effect': ValueError})
        self.all_throw=all_throw
        
        no_algorithms = unittest.mock.Mock()
        del no_algorithms.md5
        del no_algorithms.sha1
        del no_algorithms.sha256
        del no_algorithms.nonexist
        self.no_algorithms=no_algorithms
        
        unsupported_algorithm = unittest.mock.Mock(unsupported=self.fake_sha256)
        del unsupported_algorithm.md5
        del unsupported_algorithm.sha1
        del unsupported_algorithm.sha256
        del unsupported_algorithm.unsupported
        self.unsupported_algorithm=unsupported_algorithm
        ###############################

        ###############################
        # system version mocks
        VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')
        v3_8 = VersionInfo(3, 8, 199, 'super-beta', 1337)
        v3_9 = VersionInfo(3, 9, 0, 'alpha', 0)
        v4_8 = VersionInfo(4, 8, 0, 'final', 0)

        self.sys_v3_8 = unittest.mock.Mock(version_info=v3_8)
        self.sys_v3_9 = unittest.mock.Mock(version_info=v3_9)
        self.sys_v4_8 = unittest.mock.Mock(version_info=v4_8)
        ###############################

    def test_basic_failover_bad_hashlib_hash_init(self):
        """Tests that if the hashing function is entirely missing from hashlib (hashlib returns None),
        the hash init function returns None"""
        assert _attempt_init_of_python_3_9_hash_object(None) is None

    def test_basic_failover_bad_hashlib_hash_get(self):
        """Tests that if the hashing function is entirely missing from hashlib (hashlib returns None),
        the hash get function returns None"""
        assert _attempt_get_hash_function("nonexist", self.no_algorithms) is None

    def test_usedforsecurity_flag_behavior(self):
        """Test usedforsecurity flag -> should be set to 'True' on older versions of python, and 'False' on Python >= 3.9"""
        for version, expected in {
            self.sys_v3_8: (True, 'md5'),
            self.sys_v3_9: (False, 'md5'),
            self.sys_v4_8: (False, 'md5'),
        }.items():
            assert _attempt_init_of_python_3_9_hash_object(self.fake_md5, version) == expected
    
    def test_automatic_default_to_md5(self):
        """Test automatic default to md5 even if sha1 available"""
        for version, expected in {
            self.sys_v3_8: (True, 'md5'),
            self.sys_v3_9: (False, 'md5'),
            self.sys_v4_8: (False, 'md5'),
        }.items():
            _set_allowed_viable_default_hashes(self.md5Default, version)
            set_hash_format(None, self.md5Default, version)
            assert _get_hash_object(None, self.md5Default, version) == expected

    def test_automatic_default_to_sha256(self):
        """Test automatic default to sha256 if other algorithms available but throw"""
        for version, expected in {
            self.sys_v3_8: (True, 'sha256'),
            self.sys_v3_9: (False, 'sha256'),
            self.sys_v4_8: (False, 'sha256'),
        }.items():
            _set_allowed_viable_default_hashes(self.sha256Default, version)
            set_hash_format(None, self.sha256Default, version)
            assert _get_hash_object(None, self.sha256Default, version) == expected

    def test_automatic_default_to_sha1(self):
        """Test automatic default to sha1 if md5 is missing from hashlib entirely"""
        for version, expected in {
            self.sys_v3_8: (True, 'sha1'),
            self.sys_v3_9: (False, 'sha1'),
            self.sys_v4_8: (False, 'sha1'),
        }.items():
            _set_allowed_viable_default_hashes(self.sha1Default, version)
            set_hash_format(None, self.sha1Default, version)
            assert _get_hash_object(None, self.sha1Default, version) == expected
    
    def test_no_available_algorithms(self):
        """expect exceptions on no available algorithms or when all algorithms throw"""
        self.assertRaises(SCons.Errors.SConsEnvironmentError, _set_allowed_viable_default_hashes, self.no_algorithms)
        self.assertRaises(SCons.Errors.SConsEnvironmentError, _set_allowed_viable_default_hashes, self.all_throw)
        self.assertRaises(SCons.Errors.SConsEnvironmentError, _set_allowed_viable_default_hashes, self.unsupported_algorithm)

    def test_bad_algorithm_set_attempt(self):
        """expect exceptions on user setting an unsupported algorithm selections, either by host or by SCons"""

        # nonexistant hash algorithm, not supported by SCons
        _set_allowed_viable_default_hashes(self.md5Available)
        self.assertRaises(SCons.Errors.UserError, set_hash_format, 'blah blah blah', hashlib_used=self.no_algorithms)
        
        # md5 is default-allowed, but in this case throws when we attempt to use it
        _set_allowed_viable_default_hashes(self.md5Available)
        self.assertRaises(SCons.Errors.UserError, set_hash_format, 'md5', hashlib_used=self.all_throw)

        # user attempts to use an algorithm that isn't supported by their current system but is supported by SCons
        _set_allowed_viable_default_hashes(self.sha1Default)
        self.assertRaises(SCons.Errors.UserError, set_hash_format, 'md5', hashlib_used=self.all_throw)
        
        # user attempts to use an algorithm that is supported by their current system but isn't supported by SCons
        _set_allowed_viable_default_hashes(self.sha1Default)
        self.assertRaises(SCons.Errors.UserError, set_hash_format, 'unsupported', hashlib_used=self.unsupported_algorithm)

    def tearDown(self):
        """Return SCons back to the normal global state for the hashing functions."""
        _set_allowed_viable_default_hashes(hashlib, sys)
        set_hash_format(None)


class NodeListTestCase(unittest.TestCase):
    def test_simple_attributes(self):
        """Test simple attributes of a NodeList class"""

        class TestClass:
            def __init__(self, name, child=None):
                self.child = child
                self.bar = name

        t1 = TestClass('t1', TestClass('t1child'))
        t2 = TestClass('t2', TestClass('t2child'))
        t3 = TestClass('t3')

        nl = NodeList([t1, t2, t3])
        assert nl.bar == ['t1', 't2', 't3'], nl.bar
        assert nl[0:2].child.bar == ['t1child', 't2child'], \
            nl[0:2].child.bar

    def test_callable_attributes(self):
        """Test callable attributes of a NodeList class"""

        class TestClass:
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
        assert nl.foo() == ['t1foo', 't2foo', 't3foo'], nl.foo()
        assert nl.bar == ['t1', 't2', 't3'], nl.bar
        assert nl.getself().bar == ['t1', 't2', 't3'], nl.getself().bar
        assert nl[0:2].child.foo() == ['t1childfoo', 't2childfoo'], \
            nl[0:2].child.foo()
        assert nl[0:2].child.bar == ['t1child', 't2child'], \
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
        self.assertEqual(result, ['xyz'], result)

    def test_dictionary_values(self):
        """Test flattening the dictionary values"""
        items = {"a": 1, "b": 2, "c": 3}
        result = flatten(items.values())
        self.assertEqual(sorted(result), [1, 2, 3])


class OsEnviron:
    """Used to temporarily mock os.environ"""

    def __init__(self, environ):
        self._environ = environ

    def start(self):
        self._stored = os.environ
        os.environ = self._environ

    def stop(self):
        os.environ = self._stored
        del self._stored

    def __enter__(self):
        self.start()
        return os.environ

    def __exit__(self, *args):
        self.stop()


class get_env_boolTestCase(unittest.TestCase):
    def test_missing(self):
        env = dict()
        var = get_env_bool(env, 'FOO')
        assert var is False, "var should be False, not %s" % repr(var)
        env = {'FOO': '1'}
        var = get_env_bool(env, 'BAR')
        assert var is False, "var should be False, not %s" % repr(var)

    def test_true(self):
        for foo in ['TRUE', 'True', 'true',
                    'YES', 'Yes', 'yes',
                    'Y', 'y',
                    'ON', 'On', 'on',
                    '1', '20', '-1']:
            env = {'FOO': foo}
            var = get_env_bool(env, 'FOO')
            assert var is True, 'var should be True, not %s' % repr(var)

    def test_false(self):
        for foo in ['FALSE', 'False', 'false',
                    'NO', 'No', 'no',
                    'N', 'n',
                    'OFF', 'Off', 'off',
                    '0']:
            env = {'FOO': foo}
            var = get_env_bool(env, 'FOO', True)
            assert var is False, 'var should be True, not %s' % repr(var)

    def test_default(self):
        env = {'FOO': 'other'}
        var = get_env_bool(env, 'FOO', True)
        assert var is True, 'var should be True, not %s' % repr(var)
        var = get_env_bool(env, 'FOO', False)
        assert var is False, 'var should be False, not %s' % repr(var)


class get_os_env_boolTestCase(unittest.TestCase):
    def test_missing(self):
        with OsEnviron(dict()):
            var = get_os_env_bool('FOO')
            assert var is False, "var should be False, not %s" % repr(var)
        with OsEnviron({'FOO': '1'}):
            var = get_os_env_bool('BAR')
            assert var is False, "var should be False, not %s" % repr(var)

    def test_true(self):
        for foo in ['TRUE', 'True', 'true',
                    'YES', 'Yes', 'yes',
                    'Y', 'y',
                    'ON', 'On', 'on',
                    '1', '20', '-1']:
            with OsEnviron({'FOO': foo}):
                var = get_os_env_bool('FOO')
                assert var is True, 'var should be True, not %s' % repr(var)

    def test_false(self):
        for foo in ['FALSE', 'False', 'false',
                    'NO', 'No', 'no',
                    'N', 'n',
                    'OFF', 'Off', 'off',
                    '0']:
            with OsEnviron({'FOO': foo}):
                var = get_os_env_bool('FOO', True)
                assert var is False, 'var should be True, not %s' % repr(var)

    def test_default(self):
        with OsEnviron({'FOO': 'other'}):
            var = get_os_env_bool('FOO', True)
            assert var is True, 'var should be True, not %s' % repr(var)
            var = get_os_env_bool('FOO', False)
            assert var is False, 'var should be False, not %s' % repr(var)


if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
