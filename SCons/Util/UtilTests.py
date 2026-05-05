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

from __future__ import annotations

import io
import os
import subprocess
import sys
import unittest
from collections import UserDict
from typing import Callable

import TestCmd

from SCons.Util import (
    CLVar,
    LogicalLines,
    NodeList,
    Proxy,
    Selector,
    WhereIs,
    _wait_for_process_to_die_non_psutil,
    adjustixes,
    containsAll,
    containsAny,
    containsOnly,
    dictify,
    display,
    flatten,
    get_native_path,
    print_tree,
    render_tree,
    silent_intern,
    splitext,
    wait_for_process_to_die,
)

try:
    import psutil  # noqa: F401
    has_psutil = True
except ImportError:
    has_psutil = False


# These Util classes have no unit tests. Some don't make sense to test?
# DisplayEngine, Delegate, UniqueList, Unbuffered


class OutBuffer:
    def __init__(self) -> None:
        self.buffer = ""

    def write(self, text: str) -> None:
        self.buffer = self.buffer + text


class dictifyTestCase(unittest.TestCase):
    def test_dictify(self) -> None:
        """Test the dictify() function"""
        r = dictify(['a', 'b', 'c'], [1, 2, 3])
        assert r == {'a': 1, 'b': 2, 'c': 3}, r

        r = {}
        dictify(['a'], [1], r)
        dictify(['b'], [2], r)
        dictify(['c'], [3], r)
        assert r == {'a': 1, 'b': 2, 'c': 3}, r


class UtilTestCase(unittest.TestCase):
    def test_splitext(self) -> None:
        assert splitext('foo') == ('foo', '')
        assert splitext('foo.bar') == ('foo', '.bar')
        assert splitext(os.path.join('foo.bar', 'blat')) == (os.path.join('foo.bar', 'blat'), '')

    class Node:
        def __init__(self, name, children=[]) -> None:
            self.children = children
            self.name = name
            self.nocache = None

        def __str__(self) -> str:
            return self.name

        def exists(self) -> bool:
            return True

        def rexists(self) -> bool:
            return True

        def has_builder(self) -> bool:
            return True

        def has_explicit_builder(self) -> bool:
            return True

        def side_effect(self) -> bool:
            return True

        def precious(self) -> bool:
            return True

        def always_build(self) -> bool:
            return True

        def is_up_to_date(self) -> bool:
            return True

        def noclean(self) -> bool:
            return True

    def tree_case_1(self):
        """Fixture for the render_tree() and print_tree() tests."""
        windows_h = self.Node("windows.h")
        stdlib_h = self.Node("stdlib.h")
        stdio_h = self.Node("stdio.h")
        bar_c = self.Node("bar.c", [stdlib_h, windows_h])
        bar_o = self.Node("bar.o", [bar_c])
        foo_c = self.Node("foo.c", [stdio_h])
        foo_o = self.Node("foo.o", [foo_c])
        prog = self.Node("prog", [foo_o, bar_o])

        expect = """\
+-prog
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

        return prog, expect, withtags

    def tree_case_2(self, prune: int=1):
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

    def test_render_tree(self) -> None:
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

    def test_print_tree(self) -> None:
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


    def test_WhereIs(self) -> None:
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


    def test_Proxy(self) -> None:
        """Test generic Proxy class."""

        class Subject:
            def meth(self) -> int:
                return 1

            def other(self) -> int:
                return 2

        s = Subject()
        s.attr = 3

        class ProxyTest(Proxy):
            def other(self) -> int:
                return 4

        p = ProxyTest(s)

        assert p.meth() == 1, p.meth()
        assert p.other() == 4, p.other()
        assert p.attr == 3, p.attr

        p.attr = 5
        s.attr = 6

        assert p.attr == 5, p.attr
        assert p.get() == s, p.get()

    def test_display(self) -> None:
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

    def test_get_native_path(self) -> None:
        """Test the get_native_path() function."""
        import tempfile
        f, filename = tempfile.mkstemp(text=True)
        os.close(f)
        data = '1234567890 ' + filename
        try:
            with open(filename, 'w') as file:
                file.write(data)
            with open(get_native_path(filename), 'r') as native:
                assert native.read() == data
        finally:
            try:
                os.unlink(filename)
            except OSError:
                pass

    def test_CLVar(self) -> None:
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


    def test_Selector(self) -> None:
        """Test the Selector class"""

        class MyNode:
            def __init__(self, name) -> None:
                self.name = name

            def __str__(self) -> str:
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

    def test_adjustixes(self) -> None:
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

    def test_containsAny(self) -> None:
        """Test the containsAny() function"""
        assert containsAny('*.py', '*?[]')
        assert not containsAny('file.txt', '*?[]')

    def test_containsAll(self) -> None:
        """Test the containsAll() function"""
        assert containsAll('43221', '123')
        assert not containsAll('134', '123')

    def test_containsOnly(self) -> None:
        """Test the containsOnly() function"""
        assert containsOnly('.83', '0123456789.')
        assert not containsOnly('43221', '123')

    def test_LogicalLines(self) -> None:
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

    def test_intern(self) -> None:
        s1 = silent_intern("spam")
        s3 = silent_intern(42)
        s4 = silent_intern("spam")
        assert id(s1) == id(s4)

    @unittest.skipUnless(has_psutil, "requires psutil")
    def test_wait_for_process_to_die_success_psutil(self) -> None:
        self._test_wait_for_process(wait_for_process_to_die)

    def test_wait_for_process_to_die_success_non_psutil(self) -> None:
        self._test_wait_for_process(_wait_for_process_to_die_non_psutil)

    def _test_wait_for_process(
        self, wait_fn: Callable[[int], None]
    ) -> None:
        cmd = [sys.executable, "-c", ""]
        p = subprocess.Popen(cmd)
        p.wait()
        wait_fn(p.pid)



class NodeListTestCase(unittest.TestCase):
    def test_simple_attributes(self) -> None:
        """Test simple attributes of a NodeList class"""

        class TestClass:
            def __init__(self, name, child=None) -> None:
                self.child = child
                self.name = name

        t1 = TestClass('t1', TestClass('t1child'))
        t2 = TestClass('t2', TestClass('t2child'))
        t3 = TestClass('t3')

        nl = NodeList([t1, t2, t3])
        assert nl.name == ['t1', 't2', 't3'], nl.name
        assert nl[0:2].child.name == ['t1child', 't2child'], \
            nl[0:2].child.name

    def test_callable_attributes(self) -> None:
        """Test callable attributes of a NodeList class"""

        class TestClass:
            def __init__(self, name, child=None) -> None:
                self.child = child
                self.name = name

            def meth(self):
                return self.name + "foo"

            def getself(self):
                return self

        t1 = TestClass('t1', TestClass('t1child'))
        t2 = TestClass('t2', TestClass('t2child'))
        t3 = TestClass('t3')

        nl = NodeList([t1, t2, t3])
        assert nl.meth() == ['t1foo', 't2foo', 't3foo'], nl.meth()
        assert nl.name == ['t1', 't2', 't3'], nl.name
        assert nl.getself().name == ['t1', 't2', 't3'], nl.getself().name
        assert nl[0:2].child.meth() == ['t1childfoo', 't2childfoo'], \
            nl[0:2].child.meth()
        assert nl[0:2].child.name == ['t1child', 't2child'], \
            nl[0:2].child.name

    def test_null(self):
        """Test a null NodeList"""
        nl = NodeList([])
        r = str(nl)
        assert r == '', r
        for node in nl:
            raise Exception("should not enter this loop")


class flattenTestCase(unittest.TestCase):

    def test_scalar(self) -> None:
        """Test flattening a scalar"""
        result = flatten('xyz')
        self.assertEqual(result, ['xyz'], result)

    def test_dictionary_values(self) -> None:
        """Test flattening the dictionary values"""
        items = {"a": 1, "b": 2, "c": 3}
        result = flatten(items.values())
        self.assertEqual(sorted(result), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
