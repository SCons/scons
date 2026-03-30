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

import SCons.compat

import copy
import io
import os
import sys
import unittest
from collections import UserDict as UD, UserList as UL, deque

import TestCmd

import SCons.Warnings
from SCons.Environment import (
    Environment,
    NoSubstitutionProxy,
    OverrideEnvironment,
    SubstitutionEnvironment,
)
from SCons.Util import CLVar
from SCons.SConsign import current_sconsign_filename


def diff_env(env1, env2):
    s1 = "env1 = {\n"
    s2 = "env2 = {\n"
    d = {}
    for k in list(env1._dict.keys()) + list(env2._dict.keys()):
        d[k] = None
    for k in sorted(d.keys()):
        if k in env1:
           if k in env2:
               if env1[k] != env2[k]:
                   s1 = s1 + "    " + repr(k) + " : " + repr(env1[k]) + "\n"
                   s2 = s2 + "    " + repr(k) + " : " + repr(env2[k]) + "\n"
           else:
               s1 = s1 + "    " + repr(k) + " : " + repr(env1[k]) + "\n"
        elif k in env2:
           s2 = s2 + "    " + repr(k) + " : " + repr(env2[k]) + "\n"
    s1 = s1 + "}\n"
    s2 = s2 + "}\n"
    return s1 + s2

def diff_dict(d1, d2):
    s1 = "d1 = {\n"
    s2 = "d2 = {\n"
    d = {}
    for k in list(d1.keys()) + list(d2.keys()):
        d[k] = None
    for k in sorted(d.keys()):
        if k in d1:
           if k in d2:
               if d1[k] != d2[k]:
                   s1 = s1 + "    " + repr(k) + " : " + repr(d1[k]) + "\n"
                   s2 = s2 + "    " + repr(k) + " : " + repr(d2[k]) + "\n"
           else:
               s1 = s1 + "    " + repr(k) + " : " + repr(d1[k]) + "\n"
        elif k in d2:
           s2 = s2 + "    " + repr(k) + " : " + repr(d2[k]) + "\n"
    s1 = s1 + "}\n"
    s2 = s2 + "}\n"
    return s1 + s2

called_it = {}
built_it = {}

class Builder(SCons.Builder.BuilderBase):
    """A dummy Builder class for testing purposes.  "Building"
    a target is simply setting a value in the dictionary.
    """
    def __init__(self, name = None) -> None:
        self.name = name

    def __call__(self, env, target=None, source=None, **kw) -> None:
        global called_it
        called_it['target'] = target
        called_it['source'] = source
        called_it.update(kw)

    def execute(self, target = None, **kw) -> None:
        global built_it
        built_it[target] = 1



scanned_it = {}

class Scanner:
    """A dummy Scanner class for testing purposes.  "Scanning"
    a target is simply setting a value in the dictionary.
    """
    def __init__(self, name, skeys=[]) -> None:
        self.name = name
        self.skeys = skeys

    def __call__(self, filename) -> None:
        global scanned_it
        scanned_it[filename] = 1

    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except AttributeError:
            return False

    def get_skeys(self, env):
        return self.skeys

    def __str__(self) -> str:
        return self.name


class DummyNode:
    def __init__(self, name) -> None:
        self.name = name
    def __str__(self) -> str:
        return self.name
    def rfile(self):
        return self
    def get_subst_proxy(self):
        return self

def test_tool( env ) -> None:
    env['_F77INCFLAGS'] = '${_concat(INCPREFIX, F77PATH, INCSUFFIX, __env__, RDirs, TARGET, SOURCE, affect_signature=False)}'

class TestEnvironmentFixture:
    def TestEnvironment(self, *args, **kw):
        if not kw or 'tools' not in kw:
            kw['tools'] = [test_tool]
        default_keys = { 'CC' : 'cc',
                         'CCFLAGS' : '-DNDEBUG',
                         'ENV' : { 'TMP' : '/tmp' } }
        for key, value in default_keys.items():
            if key not in kw:
                kw[key] = value
        if 'BUILDERS' not in kw:
            static_obj = SCons.Builder.Builder(action={},
                                               emitter={},
                                               suffix='.o',
                                               single_source=True)
            kw['BUILDERS'] = {'Object' : static_obj}
            static_obj.add_action('.cpp', 'fake action')

        env = Environment(*args, **kw)
        return env

class SubstitutionTestCase(unittest.TestCase):

    def test___init__(self) -> None:
        """Test initializing a SubstitutionEnvironment."""
        env = SubstitutionEnvironment()
        assert '__env__' not in env

    def test___cmp__(self) -> None:
        """Test comparing SubstitutionEnvironments."""
        env1 = SubstitutionEnvironment(XXX = 'x')
        env2 = SubstitutionEnvironment(XXX = 'x')
        env3 = SubstitutionEnvironment(XXX = 'xxx')
        env4 = SubstitutionEnvironment(XXX = 'x', YYY = 'x')

        with self.subTest():
            self.assertEqual(env1, env2)
        with self.subTest():
            self.assertNotEqual(env1, env3)
        with self.subTest():
            self.assertNotEqual(env1, env4)

    def test___delitem__(self) -> None:
        """Test deleting a variable from a SubstitutionEnvironment."""
        env1 = SubstitutionEnvironment(XXX = 'x', YYY = 'y')
        env2 = SubstitutionEnvironment(XXX = 'x')
        del env1['YYY']
        self.assertEqual(env1, env2)

    def test___getitem__(self) -> None:
        """Test fetching a variable from a SubstitutionEnvironment."""
        env = SubstitutionEnvironment(XXX = 'x')
        assert env['XXX'] == 'x', env['XXX']

    def test___setitem__(self) -> None:
        """Test setting a variable in a SubstitutionEnvironment."""
        env1 = SubstitutionEnvironment(XXX = 'x')
        env2 = SubstitutionEnvironment(XXX = 'x', YYY = 'y')
        env1['YYY'] = 'y'
        self.assertEqual(env1, env2)

    def test_get(self) -> None:
        """Test the SubstitutionEnvironment get() method."""
        env = SubstitutionEnvironment(XXX = 'x')
        assert env.get('XXX') == 'x', env.get('XXX')
        assert env.get('YYY') is None, env.get('YYY')

    def test_contains(self) -> None:
        """Test the SubstitutionEnvironment __contains__() method."""
        env = SubstitutionEnvironment(XXX = 'x')
        assert 'XXX' in env
        assert 'YYY' not in env

    def test_keys(self) -> None:
        """Test the SubstitutionEnvironment keys() method."""
        testdata = {'XXX': 'x', 'YYY': 'y'}
        env = SubstitutionEnvironment(**testdata)
        keys = list(env.keys())
        assert len(keys) == 2, keys
        for k in testdata.keys():
            assert k in keys, keys

    def test_values(self) -> None:
        """Test the SubstitutionEnvironment values() method."""
        testdata = {'XXX': 'x', 'YYY': 'y'}
        env = SubstitutionEnvironment(**testdata)
        values = list(env.values())
        assert len(values) == 2, values
        for v in testdata.values():
            assert v in values, values

    def test_items(self) -> None:
        """Test the SubstitutionEnvironment items() method."""
        testdata = {'XXX': 'x', 'YYY': 'y'}
        env = SubstitutionEnvironment(**testdata)
        items = list(env.items())
        assert len(items) == 2, items
        for k, v in testdata.items():
            assert (k, v) in items, items

    def test_setdefault(self) -> None:
        """Test the SubstitutionEnvironment setdefault() method."""
        env = SubstitutionEnvironment(XXX = 'x')
        assert env.setdefault('XXX', 'z') == 'x', env['XXX']
        assert env.setdefault('YYY', 'y') == 'y', env['YYY']
        assert 'YYY' in env

    def test_arg2nodes(self) -> None:
        """Test the arg2nodes method."""
        env = SubstitutionEnvironment()
        dict = {}
        class X(SCons.Node.Node):
            pass
        def Factory(name, directory = None, create: int = 1, dict=dict, X=X):
            if name not in dict:
                dict[name] = X()
                dict[name].name = name
            return dict[name]

        nodes = env.arg2nodes("Util.py UtilTests.py", Factory)
        assert len(nodes) == 1, nodes
        assert isinstance(nodes[0], X)
        assert nodes[0].name == "Util.py UtilTests.py", nodes[0].name

        nodes = env.arg2nodes(["Util.py", "UtilTests.py"], Factory)
        assert len(nodes) == 2, nodes
        assert isinstance(nodes[0], X)
        assert isinstance(nodes[1], X)
        assert nodes[0].name == "Util.py", nodes[0].name
        assert nodes[1].name == "UtilTests.py", nodes[1].name

        n1 = Factory("Util.py")
        nodes = env.arg2nodes([n1, "UtilTests.py"], Factory)
        assert len(nodes) == 2, nodes
        assert isinstance(nodes[0], X)
        assert isinstance(nodes[1], X)
        assert nodes[0].name == "Util.py", nodes[0].name
        assert nodes[1].name == "UtilTests.py", nodes[1].name

        class SConsNode(SCons.Node.Node):
            pass
        nodes = env.arg2nodes(SConsNode())
        assert len(nodes) == 1, nodes
        assert isinstance(nodes[0], SConsNode), nodes[0]

        class OtherNode:
            pass
        nodes = env.arg2nodes(OtherNode())
        assert len(nodes) == 1, nodes
        assert isinstance(nodes[0], OtherNode), nodes[0]

        def lookup_a(str, F=Factory):
            if str[0] == 'a':
                n = F(str)
                n.a = 1
                return n
            else:
                return None

        def lookup_b(str, F=Factory):
            if str[0] == 'b':
                n = F(str)
                n.b = 1
                return n
            else:
                return None

        env_ll = SubstitutionEnvironment()
        env_ll.lookup_list = [lookup_a, lookup_b]

        nodes = env_ll.arg2nodes(['aaa', 'bbb', 'ccc'], Factory)
        assert len(nodes) == 3, nodes

        assert nodes[0].name == 'aaa', nodes[0]
        assert nodes[0].a == 1, nodes[0]
        assert not hasattr(nodes[0], 'b'), nodes[0]

        assert nodes[1].name == 'bbb'
        assert not hasattr(nodes[1], 'a'), nodes[1]
        assert nodes[1].b == 1, nodes[1]

        assert nodes[2].name == 'ccc'
        assert not hasattr(nodes[2], 'a'), nodes[1]
        assert not hasattr(nodes[2], 'b'), nodes[1]

        def lookup_bbbb(str, F=Factory):
            if str == 'bbbb':
                n = F(str)
                n.bbbb = 1
                return n
            else:
                return None

        def lookup_c(str, F=Factory):
            if str[0] == 'c':
                n = F(str)
                n.c = 1
                return n
            else:
                return None

        nodes = env.arg2nodes(['bbbb', 'ccc'], Factory,
                                     [lookup_c, lookup_bbbb, lookup_b])
        assert len(nodes) == 2, nodes

        assert nodes[0].name == 'bbbb'
        assert not hasattr(nodes[0], 'a'), nodes[1]
        assert not hasattr(nodes[0], 'b'), nodes[1]
        assert nodes[0].bbbb == 1, nodes[1]
        assert not hasattr(nodes[0], 'c'), nodes[0]

        assert nodes[1].name == 'ccc'
        assert not hasattr(nodes[1], 'a'), nodes[1]
        assert not hasattr(nodes[1], 'b'), nodes[1]
        assert not hasattr(nodes[1], 'bbbb'), nodes[0]
        assert nodes[1].c == 1, nodes[1]

    def test_arg2nodes_target_source(self) -> None:
        """Test the arg2nodes method with target= and source= keywords
        """
        targets = [DummyNode('t1'), DummyNode('t2')]
        sources = [DummyNode('s1'), DummyNode('s2')]
        env = SubstitutionEnvironment()
        nodes = env.arg2nodes(['${TARGET}-a',
                               '${SOURCE}-b',
                               '${TARGETS[1]}-c',
                               '${SOURCES[1]}-d'],
                              DummyNode,
                              target=targets,
                              source=sources)
        names = [n.name for n in nodes]
        assert names == ['t1-a', 's1-b', 't2-c', 's2-d'], names

    def test_gvars(self) -> None:
        """Test the base class gvars() method"""
        env = SubstitutionEnvironment()
        gvars = env.gvars()
        assert gvars == {}, gvars

    def test_lvars(self) -> None:
        """Test the base class lvars() method"""
        env = SubstitutionEnvironment()
        lvars = env.lvars()
        assert lvars == {}, lvars

    def test_subst(self) -> None:
        """Test substituting construction variables within strings

        Check various combinations, including recursive expansion
        of variables into other variables.
        """
        env = SubstitutionEnvironment(AAA = 'a', BBB = 'b')
        mystr = env.subst("$AAA ${AAA}A $BBBB $BBB")
        assert mystr == "a aA b", mystr

        # Changed the tests below to reflect a bug fix in
        # subst()
        env = SubstitutionEnvironment(AAA = '$BBB', BBB = 'b', BBBA = 'foo')
        mystr = env.subst("$AAA ${AAA}A ${AAA}B $BBB")
        assert mystr == "b bA bB b", mystr

        env = SubstitutionEnvironment(AAA = '$BBB', BBB = '$CCC', CCC = 'c')
        mystr = env.subst("$AAA ${AAA}A ${AAA}B $BBB")
        assert mystr == "c cA cB c", mystr

        # Lists:
        env = SubstitutionEnvironment(AAA = ['a', 'aa', 'aaa'])
        mystr = env.subst("$AAA")
        assert mystr == "a aa aaa", mystr

        # Tuples:
        env = SubstitutionEnvironment(AAA = ('a', 'aa', 'aaa'))
        mystr = env.subst("$AAA")
        assert mystr == "a aa aaa", mystr

        t1 = DummyNode('t1')
        t2 = DummyNode('t2')
        s1 = DummyNode('s1')
        s2 = DummyNode('s2')

        env = SubstitutionEnvironment(AAA = 'aaa')
        s = env.subst('$AAA $TARGET $SOURCES', target=[t1, t2], source=[s1, s2])
        assert s == "aaa t1 s1 s2", s
        s = env.subst('$AAA $TARGETS $SOURCE', target=[t1, t2], source=[s1, s2])
        assert s == "aaa t1 t2 s1", s

        # Test callables in the SubstitutionEnvironment
        def foo(target, source, env, for_signature):
            assert str(target) == 't', target
            assert str(source) == 's', source
            return env["FOO"]

        env = SubstitutionEnvironment(BAR=foo, FOO='baz')
        t = DummyNode('t')
        s = DummyNode('s')

        subst = env.subst('test $BAR', target=t, source=s)
        assert subst == 'test baz', subst

        # Test not calling callables in the SubstitutionEnvironment
        if 0:
            # This will take some serious surgery to subst() and
            # subst_list(), so just leave these tests out until we can
            # do that.
            def bar(arg) -> None:
                pass

            env = SubstitutionEnvironment(BAR=bar, FOO='$BAR')

            subst = env.subst('$BAR', call=None)
            assert subst is bar, subst

            subst = env.subst('$FOO', call=None)
            assert subst is bar, subst

    def test_subst_kw(self) -> None:
        """Test substituting construction variables within dictionaries"""
        env = SubstitutionEnvironment(AAA = 'a', BBB = 'b')
        kw = env.subst_kw({'$AAA' : 'aaa', 'bbb' : '$BBB'})
        assert len(kw) == 2, kw
        assert kw['a'] == 'aaa', kw['a']
        assert kw['bbb'] == 'b', kw['bbb']

    def test_subst_list(self) -> None:
        """Test substituting construction variables in command lists
        """
        env = SubstitutionEnvironment(AAA = 'a', BBB = 'b')
        l = env.subst_list("$AAA ${AAA}A $BBBB $BBB")
        assert l == [["a", "aA", "b"]], l

        # Changed the tests below to reflect a bug fix in
        # subst()
        env = SubstitutionEnvironment(AAA = '$BBB', BBB = 'b', BBBA = 'foo')
        l = env.subst_list("$AAA ${AAA}A ${AAA}B $BBB")
        assert l == [["b", "bA", "bB", "b"]], l

        env = SubstitutionEnvironment(AAA = '$BBB', BBB = '$CCC', CCC = 'c')
        l = env.subst_list("$AAA ${AAA}A ${AAA}B $BBB")
        assert l == [["c", "cA", "cB", "c"]], l

        env = SubstitutionEnvironment(AAA = '$BBB', BBB = '$CCC', CCC = [ 'a', 'b\nc' ])
        lst = env.subst_list([ "$AAA", "B $CCC" ])
        assert lst == [[ "a", "b"], ["c", "B a", "b"], ["c"]], lst

        t1 = DummyNode('t1')
        t2 = DummyNode('t2')
        s1 = DummyNode('s1')
        s2 = DummyNode('s2')

        env = SubstitutionEnvironment(AAA = 'aaa')
        s = env.subst_list('$AAA $TARGET $SOURCES', target=[t1, t2], source=[s1, s2])
        assert s == [["aaa", "t1", "s1", "s2"]], s
        s = env.subst_list('$AAA $TARGETS $SOURCE', target=[t1, t2], source=[s1, s2])
        assert s == [["aaa", "t1", "t2", "s1"]], s

        # Test callables in the SubstitutionEnvironment
        def foo(target, source, env, for_signature):
            assert str(target) == 't', target
            assert str(source) == 's', source
            return env["FOO"]

        env = SubstitutionEnvironment(BAR=foo, FOO='baz')
        t = DummyNode('t')
        s = DummyNode('s')

        lst = env.subst_list('test $BAR', target=t, source=s)
        assert lst == [['test', 'baz']], lst

        # Test not calling callables in the SubstitutionEnvironment
        if 0:
            # This will take some serious surgery to subst() and
            # subst_list(), so just leave these tests out until we can
            # do that.
            def bar(arg) -> None:
                pass

            env = SubstitutionEnvironment(BAR=bar, FOO='$BAR')

            subst = env.subst_list('$BAR', call=None)
            assert subst is bar, subst

            subst = env.subst_list('$FOO', call=None)
            assert subst is bar, subst

    def test_subst_path(self) -> None:
        """Test substituting a path list
        """
        class MyProxy:
            def __init__(self, val) -> None:
                self.val = val
            def get(self):
                return self.val + '-proxy'

        class MyNode:
            def __init__(self, val) -> None:
                self.val = val
            def get_subst_proxy(self):
                return self
            def __str__(self) -> str:
                return self.val

        class MyObj:
            def get(self):
                return self

        env = SubstitutionEnvironment(FOO='foo',
                                      BAR='bar',
                                      LIST=['one', 'two'],
                                      PROXY=MyProxy('my1'))

        r = env.subst_path('$FOO')
        assert r == ['foo'], r

        r = env.subst_path(['$FOO', 'xxx', '$BAR'])
        assert r == ['foo', 'xxx', 'bar'], r

        r = env.subst_path(['$FOO', '$LIST', '$BAR'])
        assert list(map(str, r)) == ['foo', 'one two', 'bar'], r

        r = env.subst_path(['$FOO', '$TARGET', '$SOURCE', '$BAR'])
        assert r == ['foo', '', '', 'bar'], r

        r = env.subst_path(['$FOO', '$TARGET', '$BAR'], target=MyNode('ttt'))
        assert list(map(str, r)) == ['foo', 'ttt', 'bar'], r

        r = env.subst_path(['$FOO', '$SOURCE', '$BAR'], source=MyNode('sss'))
        assert list(map(str, r)) == ['foo', 'sss', 'bar'], r

        n = MyObj()

        r = env.subst_path(['$PROXY', MyProxy('my2'), n])
        assert r == ['my1-proxy', 'my2-proxy', n], r

        class StringableObj:
            def __init__(self, s) -> None:
                self.s = s
            def __str__(self) -> str:
                return self.s

        env = SubstitutionEnvironment(FOO=StringableObj("foo"),
                          BAR=StringableObj("bar"))

        r = env.subst_path([ "${FOO}/bar", "${BAR}/baz" ])
        assert r == [ "foo/bar", "bar/baz" ], r

        r = env.subst_path([ "bar/${FOO}", "baz/${BAR}" ])
        assert r == [ "bar/foo", "baz/bar" ], r

        r = env.subst_path([ "bar/${FOO}/bar", "baz/${BAR}/baz" ])
        assert r == [ "bar/foo/bar", "baz/bar/baz" ], r

    def test_subst_target_source(self) -> None:
        """Test the base environment subst_target_source() method"""
        env = SubstitutionEnvironment(AAA = 'a', BBB = 'b')
        mystr = env.subst_target_source("$AAA ${AAA}A $BBBB $BBB")
        assert mystr == "a aA b", mystr

    def test_backtick(self) -> None:
        """Test the backtick() method for capturing command output"""
        env = SubstitutionEnvironment()

        test = TestCmd.TestCmd(workdir = '')
        test.write('stdout.py', """\
import sys
sys.stdout.write('this came from stdout.py\\n')
sys.exit(0)
""")
        test.write('stderr.py', """\
import sys
sys.stderr.write('this came from stderr.py\\n')
sys.exit(0)
""")
        test.write('fail.py', """\
import sys
sys.exit(1)
""")
        test.write('echo.py', """\
import os, sys
sys.stdout.write(os.environ['ECHO'] + '\\n')
sys.exit(0)
""")

        save_stderr = sys.stderr

        python = '"' + sys.executable + '"'

        try:
            sys.stderr = io.StringIO()
            cmd = '%s %s' % (python, test.workpath('stdout.py'))
            output = env.backtick(cmd)
            errout = sys.stderr.getvalue()
            assert output == 'this came from stdout.py\n', output
            assert errout == '', errout

            sys.stderr = io.StringIO()
            cmd = '%s %s' % (python, test.workpath('stderr.py'))
            output = env.backtick(cmd)
            errout = sys.stderr.getvalue()
            assert output == '', output
            assert errout == 'this came from stderr.py\n', errout

            sys.stderr = io.StringIO()
            cmd = '%s %s' % (python, test.workpath('fail.py'))
            try:
                env.backtick(cmd)
            except OSError as e:
                assert str(e) == f'{cmd!r} exited 1', str(e)
            else:
                self.fail("did not catch expected OSError")

            sys.stderr = io.StringIO()
            cmd = '%s %s' % (python, test.workpath('echo.py'))
            env['ENV'] = os.environ.copy()
            env['ENV']['ECHO'] = 'this came from ECHO'
            output = env.backtick(cmd)
            errout = sys.stderr.getvalue()
            assert output == 'this came from ECHO\n', output
            assert errout == '', errout

        finally:
            sys.stderr = save_stderr

    def test_AddMethod(self) -> None:
        """Test the AddMethod() method"""
        env = SubstitutionEnvironment(FOO = 'foo')

        def func(self):
            return 'func-' + self['FOO']

        assert not hasattr(env, 'func')
        env.AddMethod(func)
        r = env.func()
        assert r == 'func-foo', r

        assert not hasattr(env, 'bar')
        env.AddMethod(func, 'bar')
        r = env.bar()
        assert r == 'func-foo', r

        def func2(self, arg: str=''):
            return 'func2-' + self['FOO'] + arg

        env.AddMethod(func2)
        r = env.func2()
        assert r == 'func2-foo', r
        r = env.func2('-xxx')
        assert r == 'func2-foo-xxx', r

        env.AddMethod(func2, 'func')
        r = env.func()
        assert r == 'func2-foo', r
        r = env.func('-yyy')
        assert r == 'func2-foo-yyy', r

        # Test that clones of clones correctly re-bind added methods.
        env1 = Environment(FOO = '1')
        env1.AddMethod(func2)
        env2 = env1.Clone(FOO = '2')
        env3 = env2.Clone(FOO = '3')
        env4 = env3.Clone(FOO = '4')
        r = env1.func2()
        assert r == 'func2-1', r
        r = env2.func2()
        assert r == 'func2-2', r
        r = env3.func2()
        assert r == 'func2-3', r
        r = env4.func2()
        assert r == 'func2-4', r

        # Test that clones don't re-bind an attribute that the user set.
        env1 = Environment(FOO = '1')
        env1.AddMethod(func2)
        def replace_func2() -> str:
            return 'replace_func2'
        env1.func2 = replace_func2
        env2 = env1.Clone(FOO = '2')
        r = env2.func2()
        assert r == 'replace_func2', r

        # Test clone rebinding if using global AddMethod.
        env1 = Environment(FOO='1')
        SCons.Util.AddMethod(env1, func2)
        r = env1.func2()
        assert r == 'func2-1', r
        r = env1.func2('-xxx')
        assert r == 'func2-1-xxx', r
        env2 = env1.Clone(FOO='2')
        r = env2.func2()
        assert r == 'func2-2', r


    def test_Override(self) -> None:
        """Test overriding construction variables"""
        env = SubstitutionEnvironment(ONE=1, TWO=2, THREE=3, FOUR=4)
        assert env['ONE'] == 1, env['ONE']
        assert env['TWO'] == 2, env['TWO']
        assert env['THREE'] == 3, env['THREE']
        assert env['FOUR'] == 4, env['FOUR']

        env2 = env.Override({'TWO'   : '10',
                             'THREE' :'x $THREE y',
                             'FOUR'  : ['x', '$FOUR', 'y']})
        assert env2['ONE'] == 1, env2['ONE']
        assert env2['TWO'] == '10', env2['TWO']
        assert env2['THREE'] == 'x 3 y', env2['THREE']
        assert env2['FOUR'] == ['x', 4, 'y'], env2['FOUR']

        assert env['ONE'] == 1, env['ONE']
        assert env['TWO'] == 2, env['TWO']
        assert env['THREE'] == 3, env['THREE']
        assert env['FOUR'] == 4, env['FOUR']

        env2.Replace(ONE = "won")
        assert env2['ONE'] == "won", env2['ONE']
        assert env['ONE'] == 1, env['ONE']

    def test_ParseFlags(self) -> None:
        """Test the ParseFlags() method
        """
        env = SubstitutionEnvironment()

        empty = {
            'ASFLAGS'       : [],
            'CFLAGS'        : [],
            'CCFLAGS'       : [],
            'CXXFLAGS'      : [],
            'CPPDEFINES'    : [],
            'CPPFLAGS'      : [],
            'CPPPATH'       : [],
            'FRAMEWORKPATH' : [],
            'FRAMEWORKS'    : [],
            'LIBPATH'       : [],
            'LIBS'          : [],
            'LINKFLAGS'     : [],
            'RPATH'         : [],
        }

        d = env.ParseFlags(None)
        assert d == empty, d

        d = env.ParseFlags('')
        assert d == empty, d

        d = env.ParseFlags([])
        assert d == empty, d

        s = (
            "-I/usr/include/fum -I bar -X "
            '-I"C:\\Program Files\\ASCEND\\include" '
            "-L/usr/fax -L foo -lxxx -l yyy "
            '-L"C:\\Program Files\\ASCEND" -lascend '
            "-Wa,-as -Wl,-link "
            "-Wl,-rpath=rpath1 "
            "-Wl,-R,rpath2 "
            "-Wl,-Rrpath3 "
            "-Wp,-cpp "
            "-std=c99 "
            "-std=c++0x "
            "-framework Carbon "
            "-frameworkdir=fwd1 "
            "-Ffwd2 "
            "-F fwd3 "
            "-dylib_file foo-dylib "
            "-pthread "
            "-fmerge-all-constants "
            "-fopenmp "
            "-mno-cygwin -mwindows "
            "-arch i386 "
            "-isysroot /tmp "
            "-iquote /usr/include/foo1 "
            "-isystem /usr/include/foo2 "
            "-idirafter /usr/include/foo3 "
            "-imacros /usr/include/foo4 "
            "-include /usr/include/foo5 "
            "--param l1-cache-size=32 --param l2-cache-size=6144 "
            "+DD64 "
            "-DFOO -DBAR=value -D BAZ "
            "-fsanitize=memory "
            "-fsanitize-address-use-after-return "
            "-stdlib=libc++"
        )

        d = env.ParseFlags(s)

        assert d['ASFLAGS'] == ['-as'], d['ASFLAGS']
        assert d['CFLAGS']  == ['-std=c99']
        assert d['CCFLAGS'] == ['-X', '-Wa,-as',
                                '-pthread', '-fmerge-all-constants',
                                '-fopenmp', '-mno-cygwin',
                                ('-arch', 'i386'), ('-isysroot', '/tmp'),
                                ('-iquote', '/usr/include/foo1'),
                                ('-isystem', '/usr/include/foo2'),
                                ('-idirafter', '/usr/include/foo3'),
                                ('-imacros', env.fs.File('/usr/include/foo4')),
                                ('-include', env.fs.File('/usr/include/foo5')),
                                ('--param', 'l1-cache-size=32'), ('--param', 'l2-cache-size=6144'),
                                '+DD64',
                                '-fsanitize=memory',
                                '-fsanitize-address-use-after-return'], repr(d['CCFLAGS'])
        assert d['CXXFLAGS'] == ['-std=c++0x', '-stdlib=libc++'], repr(d['CXXFLAGS'])
        assert d['CPPDEFINES'] == ['FOO', ['BAR', 'value'], 'BAZ'], d['CPPDEFINES']
        assert d['CPPFLAGS'] == ['-Wp,-cpp'], d['CPPFLAGS']
        assert d['CPPPATH'] == ['/usr/include/fum',
                                'bar',
                                'C:\\Program Files\\ASCEND\\include'], d['CPPPATH']
        assert d['FRAMEWORKPATH'] == ['fwd1', 'fwd2', 'fwd3'], d['FRAMEWORKPATH']
        assert d['FRAMEWORKS'] == ['Carbon'], d['FRAMEWORKS']
        assert d['LIBPATH'] == ['/usr/fax',
                                'foo',
                                'C:\\Program Files\\ASCEND'], d['LIBPATH']
        LIBS = list(map(str, d['LIBS']))
        assert LIBS == ['xxx', 'yyy', 'ascend'], (d['LIBS'], LIBS)
        assert d['LINKFLAGS'] == ['-Wl,-link',
                                  '-dylib_file', 'foo-dylib',
                                  '-pthread', '-fmerge-all-constants', '-fopenmp',
                                  '-mno-cygwin', '-mwindows',
                                  ('-arch', 'i386'),
                                  ('-isysroot', '/tmp'),
                                  '+DD64',
                                  '-fsanitize=memory',
                                  '-fsanitize-address-use-after-return'], repr(d['LINKFLAGS'])
        assert d['RPATH'] == ['rpath1', 'rpath2', 'rpath3'], d['RPATH']


    def test_MergeFlags(self) -> None:
        """Test the MergeFlags() method."""

        env = SubstitutionEnvironment()
        # does not set flag if value empty
        env.MergeFlags('')
        assert 'CCFLAGS' not in env, env['CCFLAGS']
        # merges value if flag did not exist
        env.MergeFlags('-X')
        assert env['CCFLAGS'] == ['-X'], env['CCFLAGS']

        # avoid SubstitutionEnvironment for these, has no .Append method,
        # which is needed for unique=False test
        env = Environment(CCFLAGS="")
        # merge with existing but empty flag
        env.MergeFlags('-X')
        assert env['CCFLAGS'] == ['-X'], env['CCFLAGS']
        # default Unique=True enforces no dupes
        env.MergeFlags('-X')
        assert env['CCFLAGS'] == ['-X'], env['CCFLAGS']
        # Unique=False allows dupes
        env.MergeFlags('-X', unique=False)
        assert env['CCFLAGS'] == ['-X', '-X'], env['CCFLAGS']

        # merge from a dict with list values
        env = SubstitutionEnvironment(B='b')
        env.MergeFlags({'A': ['aaa'], 'B': ['bb', 'bbb']})
        assert env['A'] == ['aaa'], env['A']
        assert env['B'] == ['b', 'bb', 'bbb'], env['B']

        # issue #2961: merge from a dict with string values
        env = SubstitutionEnvironment(B='b')
        env.MergeFlags({'A': 'aaa', 'B': 'bb bbb'})
        assert env['A'] == ['aaa'], env['A']
        assert env['B'] == ['b', 'bb', 'bbb'], env['B']

        # issue #4231: CPPDEFINES can be a deque, tripped up merge logic
        env = Environment(CPPDEFINES=deque(['aaa', 'bbb']))
        env.MergeFlags({'CPPDEFINES': 'ccc'})
        self.assertEqual(env['CPPDEFINES'], deque(['aaa', 'bbb', 'ccc']))

        # issue #3665: if merging dict which is a compound object
        # (i.e. value can be lists, etc.), the value object should not
        # be modified. per the issue, this happened if key not in env.
        env = SubstitutionEnvironment()
        try:
            del env['CFLAGS']  # just to be sure
        except KeyError:
            pass
        flags = {'CFLAGS': ['-pipe', '-pthread', '-g']}
        import copy

        saveflags = copy.deepcopy(flags)
        env.MergeFlags(flags)
        self.assertEqual(flags, saveflags)


class BaseTestCase(unittest.TestCase,TestEnvironmentFixture):

    reserved_variables = [
        'CHANGED_SOURCES',
        'CHANGED_TARGETS',
        'SOURCE',
        'SOURCES',
        'TARGET',
        'TARGETS',
        'UNCHANGED_SOURCES',
        'UNCHANGED_TARGETS',
    ]

    def test___init__(self) -> None:
        """Test construction Environment creation

        Create two with identical arguments and check that
        they compare the same.
        """
        env1 = self.TestEnvironment(XXX = 'x', YYY = 'y')
        env2 = self.TestEnvironment(XXX = 'x', YYY = 'y')
        assert env1 == env2, diff_env(env1, env2)

        assert '__env__' not in env1
        assert '__env__' not in env2

    def test_variables(self) -> None:
        """Test that variables only get applied once."""
        class FakeOptions:
            def __init__(self, key, val) -> None:
                self.calls = 0
                self.key = key
                self.val = val
            def keys(self):
                return [self.key]
            def Update(self, env) -> None:
                env[self.key] = self.val
                self.calls = self.calls + 1

        o = FakeOptions('AAA', 'fake_opt')
        env = Environment(variables=o, AAA='keyword_arg')
        assert o.calls == 1, o.calls
        assert env['AAA'] == 'fake_opt', env['AAA']

    def test_get(self) -> None:
        """Test the get() method."""
        env = self.TestEnvironment(aaa = 'AAA')

        x = env.get('aaa')
        assert x == 'AAA', x
        x = env.get('aaa', 'XXX')
        assert x == 'AAA', x
        x = env.get('bbb')
        assert x is None, x
        x = env.get('bbb', 'XXX')
        assert x == 'XXX', x

    def test_Builder_calls(self) -> None:
        """Test Builder calls through different environments
        """
        global called_it

        b1 = Builder()
        b2 = Builder()

        env = Environment()
        env.Replace(BUILDERS = { 'builder1' : b1,
                                 'builder2' : b2 })
        called_it = {}
        env.builder1('in1')
        assert called_it['target'] is None, called_it
        assert called_it['source'] == ['in1'], called_it

        called_it = {}
        env.builder2(source = 'in2', xyzzy = 1)
        assert called_it['target'] is None, called_it
        assert called_it['source'] == ['in2'], called_it
        assert called_it['xyzzy'] == 1, called_it

        called_it = {}
        env.builder1(foo = 'bar')
        assert called_it['foo'] == 'bar', called_it
        assert called_it['target'] is None, called_it
        assert called_it['source'] is None, called_it

    def test_BuilderWrapper_attributes(self) -> None:
        """Test getting and setting of BuilderWrapper attributes."""
        b1 = Builder()
        b2 = Builder()
        e1 = Environment()
        e2 = Environment()

        e1.Replace(BUILDERS={'b': b1})
        bw = e1.b

        assert bw.env is e1
        bw.env = e2
        assert bw.env is e2

        assert bw.builder is b1
        bw.builder = b2
        assert bw.builder is b2

        self.assertRaises(AttributeError, getattr, bw, 'foobar')
        bw.foobar = 42
        assert bw.foobar == 42

    # This unit test is currently disabled because we don't think the
    # underlying method it tests (Environment.BuilderWrapper.execute())
    # is necessary, but we're leaving the code here for now in case
    # that's mistaken.
    @unittest.skip("BuilderWrapper.execute method not needed")
    def test_Builder_execs(self) -> None:
        """Test Builder execution through different environments

        One environment is initialized with a single
        Builder object, one with a list of a single Builder
        object, and one with a list of two Builder objects.
        """
        global built_it

        b1 = Builder()
        b2 = Builder()

        built_it = {}
        env3 = Environment()
        env3.Replace(BUILDERS = { 'builder1' : b1,
                                  'builder2' : b2 })
        env3.builder1.execute(target = 'out1')
        env3.builder2.execute(target = 'out2')
        env3.builder1.execute(target = 'out3')
        assert built_it['out1']
        assert built_it['out2']
        assert built_it['out3']

        env4 = env3.Clone()
        assert env4.builder1.env is env4, "builder1.env (%s) == env3 (%s)?" % (
env4.builder1.env, env3)
        assert env4.builder2.env is env4, "builder2.env (%s) == env3 (%s)?" % (
env4.builder1.env, env3)

        # Now test BUILDERS as a dictionary.
        built_it = {}
        env5 = self.TestEnvironment(BUILDERS={ 'foo' : b1 })
        env5['BUILDERS']['bar'] = b2
        env5.foo.execute(target='out1')
        env5.bar.execute(target='out2')
        assert built_it['out1']
        assert built_it['out2']

        built_it = {}
        env6 = Environment()
        env6['BUILDERS'] = { 'foo' : b1,
                             'bar' : b2 }
        env6.foo.execute(target='out1')
        env6.bar.execute(target='out2')
        assert built_it['out1']
        assert built_it['out2']



    def test_Scanners(self) -> None:
        """Test setting SCANNERS in various ways

        One environment is initialized with a single
        Scanner object, one with a list of a single Scanner
        object, and one with a list of two Scanner objects.
        """
        global scanned_it

        s1 = Scanner(name = 'scanner1', skeys = [".c", ".cc"])
        s2 = Scanner(name = 'scanner2', skeys = [".m4"])
        s3 = Scanner(name = 'scanner3', skeys = [".m4", ".m5"])
        s4 = Scanner(name = 'scanner4', skeys = [None])

#        XXX Tests for scanner execution through different environments,
#        XXX if we ever want to do that some day
#        scanned_it = {}
#        env1 = self.TestEnvironment(SCANNERS = s1)
#        env1.scanner1(filename = 'out1')
#        assert scanned_it['out1']
#
#        scanned_it = {}
#        env2 = self.TestEnvironment(SCANNERS = [s1])
#        env1.scanner1(filename = 'out1')
#        assert scanned_it['out1']
#
#        scanned_it = {}
#        env3 = Environment()
#        env3.Replace(SCANNERS = [s1])
#        env3.scanner1(filename = 'out1')
#        env3.scanner2(filename = 'out2')
#        env3.scanner1(filename = 'out3')
#        assert scanned_it['out1']
#        assert scanned_it['out2']
#        assert scanned_it['out3']

        suffixes = [".c", ".cc", ".cxx", ".m4", ".m5"]

        env = Environment()
        try: del env['SCANNERS']
        except KeyError: pass
        s = list(map(env.get_scanner, suffixes))
        assert s == [None, None, None, None, None], s

        env = self.TestEnvironment(SCANNERS = [])
        s = list(map(env.get_scanner, suffixes))
        assert s == [None, None, None, None, None], s

        env.Replace(SCANNERS = [s1])
        s = list(map(env.get_scanner, suffixes))
        assert s == [s1, s1, None, None, None], s

        env.Append(SCANNERS = [s2])
        s = list(map(env.get_scanner, suffixes))
        assert s == [s1, s1, None, s2, None], s

        env.AppendUnique(SCANNERS = [s3])
        s = list(map(env.get_scanner, suffixes))
        assert s == [s1, s1, None, s2, s3], s

        env = env.Clone(SCANNERS = [s2])
        s = list(map(env.get_scanner, suffixes))
        assert s == [None, None, None, s2, None], s

        env['SCANNERS'] = [s1]
        s = list(map(env.get_scanner, suffixes))
        assert s == [s1, s1, None, None, None], s

        env.PrependUnique(SCANNERS = [s2, s1])
        s = list(map(env.get_scanner, suffixes))
        assert s == [s1, s1, None, s2, None], s

        env.Prepend(SCANNERS = [s3])
        s = list(map(env.get_scanner, suffixes))
        assert s == [s1, s1, None, s3, s3], s

        # Verify behavior of case-insensitive suffix matches on Windows.
        uc_suffixes = [_.upper() for _ in suffixes]

        env = Environment(SCANNERS = [s1, s2, s3],
                          PLATFORM = 'linux')

        s = list(map(env.get_scanner, suffixes))
        assert s == [s1, s1, None, s2, s3], s

        s = list(map(env.get_scanner, uc_suffixes))
        assert s == [None, None, None, None, None], s

        env['PLATFORM'] = 'win32'

        s = list(map(env.get_scanner, uc_suffixes))
        assert s == [s1, s1, None, s2, s3], s

        # Verify behavior for a scanner returning None (on Windows
        # where we might try to perform case manipulation on None).
        env.Replace(SCANNERS = [s4])
        s = list(map(env.get_scanner, suffixes))
        assert s == [None, None, None, None, None], s

    def test_ENV(self) -> None:
        """Test setting the external ENV in Environments
        """
        env = Environment()
        assert 'ENV' in env.Dictionary()

        env = self.TestEnvironment(ENV = { 'PATH' : '/foo:/bar' })
        assert env.Dictionary('ENV')['PATH'] == '/foo:/bar'

    def test_ReservedVariables(self) -> None:
        """Test warning generation when reserved variable names are set"""
        warning = SCons.Warnings.ReservedVariableWarning
        SCons.Warnings.enableWarningClass(warning)
        old = SCons.Warnings.warningAsException(1)

        try:
            env4 = Environment()
            for kw in self.reserved_variables:
                exc_caught = None
                try:
                    env4[kw] = 'xyzzy'
                except warning:
                    exc_caught = 1
                assert exc_caught, "Did not catch ReservedVariableWarning for `%s'" % kw
                assert kw not in env4, "`%s' variable was incorrectly set" % kw
        finally:
            SCons.Warnings.warningAsException(old)

    def test_FutureReservedVariables(self) -> None:
        """Test warning generation when future reserved variable names are set"""

        future_reserved_variables = []

        warning = SCons.Warnings.FutureReservedVariableWarning
        SCons.Warnings.enableWarningClass(warning)
        old = SCons.Warnings.warningAsException(1)

        try:
            env4 = Environment()
            for kw in future_reserved_variables:
                exc_caught = None
                try:
                    env4[kw] = 'xyzzy'
                except warning:
                    exc_caught = 1
                assert exc_caught, "Did not catch FutureReservedVariableWarning for `%s'" % kw
                assert kw in env4, "`%s' variable was not set" % kw
        finally:
            SCons.Warnings.warningAsException(old)

    def test_IllegalVariables(self) -> None:
        """Test that use of illegal variables raises an exception"""
        env = Environment()
        def test_it(var, env=env) -> None:
            exc_caught = None
            try:
                env[var] = 1
            except SCons.Errors.UserError:
                exc_caught = 1
            assert exc_caught, "did not catch UserError for '%s'" % var
        env['aaa'] = 1
        assert env['aaa'] == 1, env['aaa']
        test_it('foo/bar')
        test_it('foo.bar')
        test_it('foo-bar')

    def test_autogenerate(self) -> None:
        """Test autogenerating variables in a dictionary."""

        drive, p = os.path.splitdrive(os.getcwd())
        def normalize_path(path, drive=drive):
            if path[0] in '\\/':
                path = drive + path
            path = os.path.normpath(path)
            drive, path = os.path.splitdrive(path)
            return drive.lower() + path

        env = self.TestEnvironment(LIBS = [ 'foo', 'bar', 'baz' ],
                                   LIBLINKPREFIX = 'foo',
                                   LIBLINKSUFFIX = 'bar')

        def RDirs(pathlist, fs=env.fs):
            return fs.Dir('xx').Rfindalldirs(pathlist)

        env['RDirs'] = RDirs
        flags = env.subst_list('$_LIBFLAGS', 1)[0]
        assert flags == ['foobar', 'foobar', 'foobazbar'], flags

        blat = env.fs.Dir('blat')

        env.Replace(CPPPATH = [ 'foo', '$FOO/bar', blat ],
                    INCPREFIX = 'foo ',
                    INCSUFFIX = 'bar',
                    FOO = 'baz')
        flags = env.subst_list('$_CPPINCFLAGS', 1)[0]
        expect = [ '$(',
                   normalize_path('foo'),
                   normalize_path('xx/foobar'),
                   normalize_path('foo'),
                   normalize_path('xx/baz/bar'),
                   normalize_path('foo'),
                   normalize_path('blatbar'),
                   '$)',
        ]
        assert flags == expect, flags

        # do a Replace using the dict form
        newvalues = {
            "F77PATH": ['foo', '$FOO/bar', blat],
            "INCPREFIX": 'foo ',
            "INCSUFFIX": 'bar',
            "FOO": 'baz',
        }
        env.Replace(**newvalues)
        flags = env.subst_list('$_F77INCFLAGS', 1)[0]
        expect = [ '$(',
                   normalize_path('foo'),
                   normalize_path('xx/foobar'),
                   normalize_path('foo'),
                   normalize_path('xx/baz/bar'),
                   normalize_path('foo'),
                   normalize_path('blatbar'),
                   '$)',
        ]
        assert flags == expect, flags

        env.Replace(CPPPATH = '', F77PATH = '', LIBPATH = '')
        l = env.subst_list('$_CPPINCFLAGS')
        assert l == [[]], l
        l = env.subst_list('$_F77INCFLAGS')
        assert l == [[]], l
        l = env.subst_list('$_LIBDIRFLAGS')
        assert l == [[]], l

        env.fs.Repository('/rep1')
        env.fs.Repository('/rep2')
        env.Replace(CPPPATH = [ 'foo', '/__a__/b', '$FOO/bar', blat],
                    INCPREFIX = '-I ',
                    INCSUFFIX = 'XXX',
                    FOO = 'baz')
        flags = env.subst_list('$_CPPINCFLAGS', 1)[0]
        expect = [ '$(',
                   '-I', normalize_path('xx/fooXXX'),
                   '-I', normalize_path('/rep1/xx/fooXXX'),
                   '-I', normalize_path('/rep2/xx/fooXXX'),
                   '-I', normalize_path('/__a__/bXXX'),
                   '-I', normalize_path('xx/baz/barXXX'),
                   '-I', normalize_path('/rep1/xx/baz/barXXX'),
                   '-I', normalize_path('/rep2/xx/baz/barXXX'),
                   '-I', normalize_path('blatXXX'),
                   '$)'
        ]
        def normalize_if_path(arg, np=normalize_path):
            if arg not in ('$(','$)','-I'):
                return np(str(arg))
            return arg
        flags = list(map(normalize_if_path, flags))
        assert flags == expect, flags

    def test_platform(self) -> None:
        """Test specifying a platform callable when instantiating."""
        class platform:
            def __str__(self) -> str:        return "TestPlatform"
            def __call__(self, env) -> None:  env['XYZZY'] = 777

        def tool(env) -> None:
            env['SET_TOOL'] = 'initialized'
            assert env['PLATFORM'] == "TestPlatform"

        env = self.TestEnvironment(platform = platform(), tools = [tool])
        assert env['XYZZY'] == 777, env
        assert env['PLATFORM'] == "TestPlatform"
        assert env['SET_TOOL'] == "initialized"

    def test_Default_PLATFORM(self) -> None:
        """Test overriding the default PLATFORM variable"""
        class platform:
            def __str__(self) -> str:        return "DefaultTestPlatform"
            def __call__(self, env) -> None:  env['XYZZY'] = 888

        def tool(env) -> None:
            env['SET_TOOL'] = 'abcde'
            assert env['PLATFORM'] == "DefaultTestPlatform"

        import SCons.Defaults
        save = SCons.Defaults.ConstructionEnvironment.copy()
        try:
            import SCons.Defaults
            SCons.Defaults.ConstructionEnvironment.update({
                'PLATFORM' : platform(),
            })
            env = self.TestEnvironment(tools = [tool])
            assert env['XYZZY'] == 888, env
            assert env['PLATFORM'] == "DefaultTestPlatform"
            assert env['SET_TOOL'] == "abcde"
        finally:
            SCons.Defaults.ConstructionEnvironment = save

    def test_tools(self) -> None:
        """Test specifying a tool callable when instantiating."""
        def t1(env) -> None:
            env['TOOL1'] = 111
        def t2(env) -> None:
            env['TOOL2'] = 222
        def t3(env) -> None:
            env['AAA'] = env['XYZ']
        def t4(env) -> None:
            env['TOOL4'] = 444
        env = self.TestEnvironment(tools = [t1, t2, t3], XYZ = 'aaa')
        assert env['TOOL1'] == 111, env['TOOL1']
        assert env['TOOL2'] == 222, env
        assert env['AAA'] == 'aaa', env
        t4(env)
        assert env['TOOL4'] == 444, env

        test = TestCmd.TestCmd(workdir = '')
        test.write('faketool.py', """\
def generate(env, **kw):
    for k, v in kw.items():
        env[k] = v

def exists(env):
    return True
""")

        env = self.TestEnvironment(tools = [('faketool', {'a':1, 'b':2, 'c':3})],
                          toolpath = [test.workpath('')])
        assert env['a'] == 1, env['a']
        assert env['b'] == 2, env['b']
        assert env['c'] == 3, env['c']

    def test_Default_TOOLS(self) -> None:
        """Test overriding the default TOOLS variable"""
        def t5(env) -> None:
            env['TOOL5'] = 555
        def t6(env) -> None:
            env['TOOL6'] = 666
        def t7(env) -> None:
            env['BBB'] = env['XYZ']
        def t8(env) -> None:
            env['TOOL8'] = 888

        import SCons.Defaults
        save = SCons.Defaults.ConstructionEnvironment.copy()
        try:
            SCons.Defaults.ConstructionEnvironment.update({
                'TOOLS' : [t5, t6, t7],
            })
            env = Environment(XYZ = 'bbb')
            assert env['TOOL5'] == 555, env['TOOL5']
            assert env['TOOL6'] == 666, env
            assert env['BBB'] == 'bbb', env
            t8(env)
            assert env['TOOL8'] == 888, env
        finally:
            SCons.Defaults.ConstructionEnvironment = save

    def test_null_tools(self) -> None:
        """Test specifying a tool of None is OK."""
        def t1(env) -> None:
            env['TOOL1'] = 111
        def t2(env) -> None:
            env['TOOL2'] = 222
        env = self.TestEnvironment(tools = [t1, None, t2], XYZ = 'aaa')
        assert env['TOOL1'] == 111, env['TOOL1']
        assert env['TOOL2'] == 222, env
        assert env['XYZ'] == 'aaa', env
        env = self.TestEnvironment(tools = [None], XYZ = 'xyz')
        assert env['XYZ'] == 'xyz', env
        env = self.TestEnvironment(tools = [t1, '', t2], XYZ = 'ddd')
        assert env['TOOL1'] == 111, env['TOOL1']
        assert env['TOOL2'] == 222, env
        assert env['XYZ'] == 'ddd', env

    def test_default_copy_cache(self) -> None:
        copied = False

        def copy2(self, src, dst) -> None:
            nonlocal copied
            copied = True

        save_copy_from_cache = SCons.CacheDir.CacheDir.copy_from_cache
        SCons.CacheDir.CacheDir.copy_from_cache = copy2

        save_copy_to_cache = SCons.CacheDir.CacheDir.copy_to_cache
        SCons.CacheDir.CacheDir.copy_to_cache = copy2

        env = self.TestEnvironment()

        SCons.Environment.default_copy_from_cache(env, 'test.in', 'test.out')
        assert copied

        copied = False
        SCons.Environment.default_copy_to_cache(env, 'test.in', 'test.out')
        assert copied

        SCons.CacheDir.CacheDir.copy_from_cache = save_copy_from_cache
        SCons.CacheDir.CacheDir.copy_to_cache = save_copy_to_cache

    # function is in Defaults.py, tested here to use TestEnvironment
    def test__concat(self) -> None:
        """Test _concat()"""
        e1 = self.TestEnvironment(PRE='pre', SUF='suf', STR='a b', LIST=['a', 'b'])
        s = e1.subst
        x = s("${_concat('', '', '', __env__)}")
        assert x == '', x
        x = s("${_concat('', [], '', __env__)}")
        assert x == '', x
        x = s("${_concat(PRE, '', SUF, __env__)}")
        assert x == '', x
        x = s("${_concat(PRE, STR, SUF, __env__)}")
        assert x == 'prea bsuf', x
        x = s("${_concat(PRE, LIST, SUF, __env__)}")
        assert x == 'preasuf prebsuf', x
        x = s("${_concat(PRE, LIST, SUF, __env__,affect_signature=False)}", raw=True)
        assert x == '$( preasuf prebsuf $)', x


    # function is in Defaults.py, tested here to use TestEnvironment
    def test__concat_nested(self) -> None:
        """Test _concat() on a nested substitution strings."""
        e = self.TestEnvironment(PRE='pre', SUF='suf',
                                 L1=['a', 'b'],
                                 L2=['c', 'd'],
                                 L3=['$L2'])
        x = e.subst('$( ${_concat(PRE, L1, SUF, __env__)} $)')
        assert x == 'preasuf prebsuf', x
        e.AppendUnique(L1 = ['$L2'])
        x = e.subst('$( ${_concat(PRE, L1, SUF, __env__)} $)')
        assert x == 'preasuf prebsuf precsuf predsuf', x
        e.AppendUnique(L1 = ['$L3'])
        x = e.subst('$( ${_concat(PRE, L1, SUF, __env__)} $)')
        assert x == 'preasuf prebsuf precsuf predsuf precsuf predsuf', x


    # function is in Defaults.py, tested here to use TestEnvironment
    def test__stripixes(self) -> None:
        """Test _stripixes()"""
        # LIBPREFIXES and LIBSUFFIXES are stripped, except if an entry
        # begins with LIBLITERALPREFIX. Check this with and without that
        # argument being passed, and whether or not LIBLITERALPREFIX is
        # explicitly set.
        e = self.TestEnvironment(
            PRE='pre',
            SUF='suf',
            LIST=['xxx-a', 'b.yyy', 'zzxxx-c.yyy'],
            LIBPREFIXES=['xxx-'],
            LIBSUFFIXES=['.yyy'],
        )

        # e['LIBLITERALPREFIX'] = ''
        with self.subTest():
            x = e.subst('$( ${_stripixes(PRE, LIST, SUF, LIBPREFIXES, LIBSUFFIXES,__env__, LIBLITERALPREFIX)} $)')
            self.assertEqual('preasuf prebsuf prezzxxx-csuf', x)

        with self.subTest():
            x = e.subst('$( ${_stripixes(PRE, LIST, SUF, LIBPREFIXES, LIBSUFFIXES,__env__)} $)')
            self.assertEqual('preasuf prebsuf prezzxxx-csuf', x)

        # add it to the env:
        e['LIBLITERALPREFIX'] = 'zz'

        with self.subTest():
            x = e.subst('$( ${_stripixes(PRE, LIST, SUF, LIBPREFIXES, LIBSUFFIXES,__env__, LIBLITERALPREFIX)} $)')
            self.assertEqual('preasuf prebsuf prezzxxx-c.yyysuf', x)

        with self.subTest():
            x = e.subst('$( ${_stripixes(PRE, LIST, SUF, LIBPREFIXES, LIBSUFFIXES,__env__)} $)')
            self.assertEqual('preasuf prebsuf prezzxxx-csuf', x)

        # And special case: LIBLITERALPREFIX is the same as os.pathsep:
        e['LIBLITERALPREFIX'] = os.pathsep
        with self.subTest():
            x = e.subst('$( ${_stripixes(PRE, LIST, SUF, LIBPREFIXES, LIBSUFFIXES,__env__, LIBLITERALPREFIX)} $)')
        self.assertEqual('preasuf prebsuf prezzxxx-csuf', x)


    def test_gvars(self) -> None:
        """Test the Environment gvars() method."""
        env = self.TestEnvironment(XXX = 'x', YYY = 'y', ZZZ = 'z')
        gvars = env.gvars()
        assert gvars['XXX'] == 'x', gvars['XXX']
        assert gvars['YYY'] == 'y', gvars['YYY']
        assert gvars['ZZZ'] == 'z', gvars['ZZZ']

    def test__update(self) -> None:
        """Test the _update() method."""
        env = self.TestEnvironment(X = 'x', Y = 'y', Z = 'z')
        assert env['X'] == 'x', env['X']
        assert env['Y'] == 'y', env['Y']
        assert env['Z'] == 'z', env['Z']
        env._update({'X'       : 'xxx',
                     'TARGET'  : 't',
                     'TARGETS' : 'ttt',
                     'SOURCE'  : 's',
                     'SOURCES' : 'sss',
                     'Z'       : 'zzz'})
        assert env['X'] == 'xxx', env['X']
        assert env['Y'] == 'y', env['Y']
        assert env['Z'] == 'zzz', env['Z']
        assert env['TARGET'] == 't', env['TARGET']
        assert env['TARGETS'] == 'ttt', env['TARGETS']
        assert env['SOURCE'] == 's', env['SOURCE']
        assert env['SOURCES'] == 'sss', env['SOURCES']

    def test_Append(self) -> None:
        """Test appending to construction variables in an Environment."""
        b1 = Environment()['BUILDERS']
        b2 = Environment()['BUILDERS']
        assert b1 == b2, diff_dict(b1, b2)

        cases = [
            ('a1',       'A1',           'a1A1'),
            ('a2',       ['A2'],         ['a2', 'A2']),
            ('a3',       UL(['A3']),     UL(['a', '3', 'A3'])),
            ('a4',       '',             'a4'),
            ('a5',       [],             ['a5']),
            ('a6',       UL([]),         UL(['a', '6'])),
            ('a7',       [''],           ['a7', '']),
            ('a8',       UL(['']),       UL(['a', '8', ''])),

            (['e1'],     'E1',           ['e1', 'E1']),
            (['e2'],     ['E2'],         ['e2', 'E2']),
            (['e3'],     UL(['E3']),     UL(['e3', 'E3'])),
            (['e4'],     '',             ['e4']),
            (['e5'],     [],             ['e5']),
            (['e6'],     UL([]),         UL(['e6'])),
            (['e7'],     [''],           ['e7', '']),
            (['e8'],     UL(['']),       UL(['e8', ''])),

            (UL(['i1']), 'I1',           UL(['i1', 'I', '1'])),
            (UL(['i2']), ['I2'],         UL(['i2', 'I2'])),
            (UL(['i3']), UL(['I3']),     UL(['i3', 'I3'])),
            (UL(['i4']), '',             UL(['i4'])),
            (UL(['i5']), [],             UL(['i5'])),
            (UL(['i6']), UL([]),         UL(['i6'])),
            (UL(['i7']), [''],           UL(['i7', ''])),
            (UL(['i8']), UL(['']),       UL(['i8', ''])),

            ({'d1':1},   'D1',           {'d1':1, 'D1':None}),
            ({'d2':1},   ['D2'],         {'d2':1, 'D2':None}),
            ({'d3':1},   UL(['D3']),     {'d3':1, 'D3':None}),
            ({'d4':1},   {'D4':1},       {'d4':1, 'D4':1}),
            ({'d5':1},   UD({'D5':1}),   UD({'d5':1, 'D5':1})),

            (UD({'u1':1}), 'U1',         UD({'u1':1, 'U1':None})),
            (UD({'u2':1}), ['U2'],       UD({'u2':1, 'U2':None})),
            (UD({'u3':1}), UL(['U3']),   UD({'u3':1, 'U3':None})),
            (UD({'u4':1}), {'U4':1},     UD({'u4':1, 'U4':1})),
            ((UD({'u5':1}), UD({'U5':1}), UD({'u5':1, 'U5':1}))),

            ('',         'M1',           'M1'),
            ('',         ['M2'],         ['M2']),
            ('',         UL(['M3']),     UL(['M3'])),
            ('',         '',             ''),
            ('',         [],             []),
            ('',         UL([]),         UL([])),
            ('',         [''],           ['']),
            ('',         UL(['']),       UL([''])),

            ([],         'N1',           ['N1']),
            ([],         ['N2'],         ['N2']),
            ([],         UL(['N3']),     UL(['N3'])),
            ([],         '',             []),
            ([],         [],             []),
            ([],         UL([]),         UL([])),
            ([],         [''],           ['']),
            ([],         UL(['']),       UL([''])),

            (UL([]),     'O1',           ['O', '1']),
            (UL([]),     ['O2'],         ['O2']),
            (UL([]),     UL(['O3']),     UL(['O3'])),
            (UL([]),     '',             UL([])),
            (UL([]),     [],             UL([])),
            (UL([]),     UL([]),         UL([])),
            (UL([]),     [''],           UL([''])),
            (UL([]),     UL(['']),       UL([''])),

            ([''],       'P1',           ['', 'P1']),
            ([''],       ['P2'],         ['', 'P2']),
            ([''],       UL(['P3']),     UL(['', 'P3'])),
            ([''],       '',             ['']),
            ([''],       [],             ['']),
            ([''],       UL([]),         UL([''])),
            ([''],       [''],           ['', '']),
            ([''],       UL(['']),       UL(['', ''])),

            (UL(['']),   'Q1',           ['', 'Q', '1']),
            (UL(['']),   ['Q2'],         ['', 'Q2']),
            (UL(['']),   UL(['Q3']),     UL(['', 'Q3'])),
            (UL(['']),   '',             UL([''])),
            (UL(['']),   [],             UL([''])),
            (UL(['']),   UL([]),         UL([''])),
            (UL(['']),   [''],           UL(['', ''])),
            (UL(['']),   UL(['']),       UL(['', ''])),
        ]

        env = Environment()
        failed = 0
        for input, append, expect in cases:
            env['XXX'] = copy.copy(input)
            try:
                env.Append(XXX=append)
            except Exception as e:
                if failed == 0: print()
                print("    %s Append %s exception: %s" % \
                      (repr(input), repr(append), e))
                failed = failed + 1
            else:
                result = env['XXX']
                if result != expect:
                    if failed == 0: print()
                    print("    %s Append %s => %s did not match %s" % \
                          (repr(input), repr(append), repr(result), repr(expect)))
                    failed += 1
        assert failed == 0, "%d Append() cases failed" % failed

        env['UL'] = UL(['foo'])
        env.Append(UL = 'bar')
        result = env['UL']
        assert isinstance(result, UL), repr(result)
        assert result == ['foo', 'b', 'a', 'r'], result

        env['CLVar'] = CLVar(['foo'])
        env.Append(CLVar = 'bar')
        result = env['CLVar']
        assert isinstance(result, CLVar), repr(result)
        assert result == ['foo', 'bar'], result

        class C:
            def __init__(self, name) -> None:
                self.name = name
            def __str__(self) -> str:
                return self.name
            def __eq__(self, other):
                raise Exception("should not compare")

        ccc = C('ccc')

        env2 = self.TestEnvironment(CCC1 = ['c1'], CCC2 = ccc)
        env2.Append(CCC1 = ccc, CCC2 = ['c2'])
        assert env2['CCC1'][0] == 'c1', env2['CCC1']
        assert env2['CCC1'][1] is ccc, env2['CCC1']
        assert env2['CCC2'][0] is ccc, env2['CCC2']
        assert env2['CCC2'][1] == 'c2', env2['CCC2']

        env3 = self.TestEnvironment(X = {'x1' : 7})
        env3.Append(X = {'x1' : 8, 'x2' : 9}, Y = {'y1' : 10})
        assert env3['X'] == {'x1': 8, 'x2': 9}, env3['X']
        assert env3['Y'] == {'y1': 10}, env3['Y']

        z1 = Builder()
        z2 = Builder()
        env4 = self.TestEnvironment(BUILDERS = {'z1' : z1})
        env4.Append(BUILDERS = {'z2' : z2})
        assert env4['BUILDERS'] == {'z1' : z1, 'z2' : z2}, env4['BUILDERS']
        assert hasattr(env4, 'z1')
        assert hasattr(env4, 'z2')

    def test_AppendENVPath(self) -> None:
        """Test appending to an ENV path."""
        env1 = self.TestEnvironment(
            ENV={'PATH': r'C:\dir\num\one;C:\dir\num\two'},
            MYENV={'MYPATH': r'C:\mydir\num\one;C:\mydir\num\two'},
        )

        # have to include the pathsep here so that the test will work on UNIX too.
        env1.AppendENVPath('PATH', r'C:\dir\num\two', sep=';')
        env1.AppendENVPath('PATH', r'C:\dir\num\three', sep=';')
        assert (
            env1['ENV']['PATH'] == r'C:\dir\num\one;C:\dir\num\two;C:\dir\num\three'
        ), env1['ENV']['PATH']

        # add nonexisting - at end
        env1.AppendENVPath('MYPATH', r'C:\mydir\num\three', 'MYENV', sep=';')
        assert (
            env1['MYENV']['MYPATH'] == r'C:\mydir\num\one;C:\mydir\num\two;C:\mydir\num\three'
        ), env1['MYENV']['MYPATH']

        # add existing with delete_existing true - moves to the end
        env1.AppendENVPath(
            'MYPATH', r'C:\mydir\num\one', 'MYENV', sep=';', delete_existing=True
        )
        assert (
            env1['MYENV']['MYPATH'] == r'C:\mydir\num\two;C:\mydir\num\three;C:\mydir\num\one'
        ), env1['MYENV']['MYPATH']

        # this should do nothing since delete_existing is false
        env1.AppendENVPath('MYPATH', r'C:\mydir\num\three', 'MYENV', sep=';')
        assert (
            env1['MYENV']['MYPATH'] == r'C:\mydir\num\two;C:\mydir\num\three;C:\mydir\num\one'
        ), env1['MYENV']['MYPATH']

        test = TestCmd.TestCmd(workdir='')
        test.subdir('sub1', 'sub2')
        p = env1['ENV']['PATH']
        env1.AppendENVPath('PATH', '#sub1', sep=';')
        env1.AppendENVPath('PATH', env1.fs.Dir('sub2'), sep=';')
        assert env1['ENV']['PATH'] == p + ';sub1;sub2', env1['ENV']['PATH']


    def test_AppendUnique(self) -> None:
        """Test appending to unique values to construction variables

        This strips values that are already present when lists are involved.
        """
        env = self.TestEnvironment(AAA1 = 'a1',
                          AAA2 = 'a2',
                          AAA3 = 'a3',
                          AAA4 = 'a4',
                          AAA5 = 'a5',
                          BBB1 = ['b1'],
                          BBB2 = ['b2'],
                          BBB3 = ['b3'],
                          BBB4 = ['b4'],
                          BBB5 = ['b5'],
                          CCC1 = '',
                          CCC2 = '',
                          DDD1 = ['a', 'b', 'c'],
                          DDD2 = ['a', 'a', 'b'])
        env['LL1'] = [env.Literal('a literal'), env.Literal('b literal')]
        env['LL2'] = [env.Literal('c literal'), env.Literal('b literal')]
        env.AppendUnique(AAA1 = 'a1',
                         AAA2 = ['a2'],
                         AAA3 = ['a3', 'b', 'c', 'c', 'b', 'a3'], # ignore dups
                         AAA4 = 'a4.new',
                         AAA5 = ['a5.new'],
                         BBB1 = 'b1',
                         BBB2 = ['b2'],
                         BBB3 = ['b3', 'c', 'd', 'c', 'b3'],
                         BBB4 = 'b4.new',
                         BBB5 = ['b5.new'],
                         CCC1 = 'c1',
                         CCC2 = ['c2'],
                         DDD1 = 'b',
                         DDD2 = 'a',
                         LL1  = env.Literal('a literal'),
                         LL2  = env.Literal('a literal'))

        assert env['AAA1'] == 'a1a1', env['AAA1']
        assert env['AAA2'] == ['a2'], env['AAA2']
        assert env['AAA3'] == ['a3', 'b', 'c'], env['AAA3']
        assert env['AAA4'] == 'a4a4.new', env['AAA4']
        assert env['AAA5'] == ['a5', 'a5.new'], env['AAA5']
        assert env['BBB1'] == ['b1'], env['BBB1']
        assert env['BBB2'] == ['b2'], env['BBB2']
        assert env['BBB3'] == ['b3', 'c', 'd'], env['BBB3']
        assert env['BBB4'] == ['b4', 'b4.new'], env['BBB4']
        assert env['BBB5'] == ['b5', 'b5.new'], env['BBB5']
        assert env['CCC1'] == 'c1', env['CCC1']
        assert env['CCC2'] == ['c2'], env['CCC2']
        assert env['DDD1'] == ['a', 'b', 'c'], env['DDD1']
        assert env['DDD2'] == ['a', 'a', 'b'], env['DDD2']  # keep existing dup
        assert env['LL1'] == [
            env.Literal('a literal'),
            env.Literal('b literal'),
        ], env['LL1']
        assert env['LL2'] == [
            env.Literal('c literal'),
            env.Literal('b literal'),
            env.Literal('a literal'),
        ], [str(x) for x in env['LL2']]

        env.AppendUnique(DDD1='b', delete_existing=True)
        assert env['DDD1'] == ['a', 'c', 'b'], env['DDD1']  # b moves to end

        env.AppendUnique(DDD1=['a', 'b'], delete_existing=True)
        assert env['DDD1'] == ['c', 'a', 'b'], env['DDD1']  # a & b move to end

        env.AppendUnique(DDD1=['e', 'f', 'e'], delete_existing=True)
        assert env['DDD1'] == ['c', 'a', 'b', 'f', 'e'], env['DDD1']  # add last

        env.AppendUnique(DDD2=['a'], delete_existing=True)
        assert env['DDD2'] == ['b', 'a'], env['DDD2']  # all existing instances deleted

        # issue regression: substrings should not be deleted
        env.AppendUnique(BBB4='b4.newer', delete_existing=True)
        assert env['BBB4'] == ['b4', 'b4.new', 'b4.newer'], env['BBB4']

        env['CLVar'] = CLVar([])
        env.AppendUnique(CLVar='bar')
        result = env['CLVar']
        assert isinstance(result, CLVar), repr(result)
        assert result == ['bar'], result

        env['CLVar'] = CLVar(['abc'])
        env.AppendUnique(CLVar='bar')
        result = env['CLVar']
        assert isinstance(result, CLVar), repr(result)
        assert result == ['abc', 'bar'], result

        env['CLVar'] = CLVar(['bar'])
        env.AppendUnique(CLVar='bar')
        result = env['CLVar']
        assert isinstance(result, CLVar), repr(result)
        assert result == ['bar'], result


    def test_Clone(self) -> None:
        """Test construction environment cloning.

        The clone should compare equal if there are no overrides.
        Update the clone independently afterwards and check that
        the original remains intact (that is, no dangling
        references point to objects in the copied environment).
        Clone the original with some construction variable
        updates and check that the original remains intact
        and the copy has the updated values.
        """
        with self.subTest():
            env1 = self.TestEnvironment(XXX='x', YYY='y')
            env2 = env1.Clone()
            env1copy = env1.Clone()
            self.assertEqual(env1copy, env1)
            self.assertEqual(env2, env1)
            env2.Replace(YYY = 'yyy')
            self.assertNotEqual(env1, env2)
            self.assertEqual(env1, env1copy)

            env3 = env1.Clone(XXX='x3', ZZZ='z3')
            self.assertNotEqual(env3, env1)
            self.assertEqual(env3.Dictionary('XXX'), 'x3')
            self.assertEqual(env1.Dictionary('XXX'), 'x')
            self.assertEqual(env3.Dictionary('YYY'), 'y')
            self.assertEqual(env3.Dictionary('ZZZ'), 'z3')
            self.assertRaises(KeyError, env1.Dictionary, 'ZZZ')   # leak test
            self.assertEqual(env1, env1copy)

        # Ensure that lists and dictionaries are deep copied, but not instances
        with self.subTest():

            class TestA:
                pass

            env1 = self.TestEnvironment(
                XXX=TestA(),
                YYY=[1, 2, 3],
                ZZZ={1: 2, 3: 4}
            )
            env2 = env1.Clone()
            env2.Dictionary('YYY').append(4)
            env2.Dictionary('ZZZ')[5] = 6
            self.assertIs(env1.Dictionary('XXX'), env2.Dictionary('XXX'))
            self.assertIn(4, env2.Dictionary('YYY'))
            self.assertNotIn(4, env1.Dictionary('YYY'))
            self.assertIn(5, env2.Dictionary('ZZZ'))
            self.assertNotIn(5, env1.Dictionary('ZZZ'))

        # We also need to look at the special cases in semi_deepcopy()
        # used when cloning - these should not leak to the original either
        with self.subTest():
            env1 = self.TestEnvironment(
                XXX=deque([1, 2, 3]),
                YYY=UL([1, 2, 3]),
                ZZZ=UD({1: 2, 3: 4}),
            )
            env2 = env1.Clone()
            env2['XXX'].append(4)
            env2['YYY'].append(4)
            env2['ZZZ'][5] = 6
            self.assertIn(4, env2['XXX'])
            self.assertNotIn(4, env1['XXX'])
            self.assertIn(4, env2['YYY'])
            self.assertNotIn(4, env1['YYY'])
            self.assertIn(5, env2['ZZZ'])
            self.assertNotIn(5, env1['ZZZ'])

        # BUILDERS is special...
        with self.subTest():
            env1 = self.TestEnvironment(BUILDERS={'b1': Builder()})
            assert hasattr(env1, 'b1'), "env1.b1 was not set"
            assert env1.b1.object == env1, "b1.object doesn't point to env1"
            env2 = env1.Clone(BUILDERS = {'b2' : Builder()})
            assert env2 != env1
            assert hasattr(env1, 'b1'), "b1 was mistakenly cleared from env1"
            assert env1.b1.object == env1, "b1.object was changed"
            assert not hasattr(env2, 'b1'), "b1 was not cleared from env2"
            assert hasattr(env2, 'b2'), "env2.b2 was not set"
            assert env2.b2.object == env2, "b2.object doesn't point to env2"

        # Ensure that specifying new tools in a copied environment works.
        with self.subTest():

            def foo(env) -> None:
                env['FOO'] = 1

            def bar(env) -> None:
                env['BAR'] = 2

            def baz(env) -> None:
                env['BAZ'] = 3

            env1 = self.TestEnvironment(tools=[foo])
            env2 = env1.Clone()
            env3 = env1.Clone(tools=[bar, baz])

            assert env1.get('FOO') == 1
            assert env1.get('BAR') is None
            assert env1.get('BAZ') is None
            assert env2.get('FOO') == 1
            assert env2.get('BAR') is None
            assert env2.get('BAZ') is None
            assert env3.get('FOO') == 1
            assert env3.get('BAR') == 2
            assert env3.get('BAZ') == 3

        # Ensure that recursive variable substitution when copying
        # environments works properly.
        with self.subTest():
            env1 = self.TestEnvironment(CCFLAGS='-DFOO', XYZ='-DXYZ')
            env2 = env1.Clone(
                CCFLAGS='$CCFLAGS -DBAR', XYZ=['-DABC', 'x $XYZ y', '-DDEF']
            )
            x = env2.get('CCFLAGS')
            assert x == '-DFOO -DBAR', x
            x = env2.get('XYZ')
            assert x == ['-DABC', 'x -DXYZ y', '-DDEF'], x

        # Ensure that special properties of a class don't get
        # lost on copying.
        with self.subTest():
            env1 = self.TestEnvironment(FLAGS=CLVar('flag1 flag2'))
            x = env1.get('FLAGS')
            assert x == ['flag1', 'flag2'], x
            env2 = env1.Clone()
            env2.Append(FLAGS='flag3 flag4')
            x = env2.get('FLAGS')
            assert x == ['flag1', 'flag2', 'flag3', 'flag4'], x
            x = env1.get('FLAGS')
            assert x == ['flag1', 'flag2'], x

        # Ensure that appending directly to a copied CLVar
        # doesn't modify the original.
        with self.subTest():
            env1 = self.TestEnvironment(FLAGS=CLVar('flag1 flag2'))
            x = env1.get('FLAGS')
            assert x == ['flag1', 'flag2'], x
            env2 = env1.Clone()
            env2['FLAGS'] += ['flag3', 'flag4']
            x = env2.get('FLAGS')
            assert x == ['flag1', 'flag2', 'flag3', 'flag4'], x
            x = env1.get('FLAGS')
            assert x == ['flag1', 'flag2'], x

        # Test that the environment stores the toolpath and
        # re-uses it for copies.
        with self.subTest():
            test = TestCmd.TestCmd(workdir='')

            test.write('xxx.py', """\
def exists(env):
    return True
def generate(env):
    env['XXX'] = 'one'
""")

            test.write('yyy.py', """\
def exists(env):
    return True
def generate(env):
    env['YYY'] = 'two'
""")

            env = self.TestEnvironment(tools=['xxx'], toolpath=[test.workpath('')])
            assert env['XXX'] == 'one', env['XXX']
            env = env.Clone(tools=['yyy'])
            assert env['YYY'] == 'two', env['YYY']

        # Test that
        with self.subTest():
            real_value = [4]

            def my_tool(env, rv=real_value) -> None:
                assert env['KEY_THAT_I_WANT'] == rv[0]
                env['KEY_THAT_I_WANT'] = rv[0] + 1

            env = self.TestEnvironment()

            real_value[0] = 5
            env = env.Clone(KEY_THAT_I_WANT=5, tools=[my_tool])
            assert env['KEY_THAT_I_WANT'] == real_value[0], env['KEY_THAT_I_WANT']

            real_value[0] = 6
            env = env.Clone(KEY_THAT_I_WANT=6, tools=[my_tool])
            assert env['KEY_THAT_I_WANT'] == real_value[0], env['KEY_THAT_I_WANT']

        # test for pull request #150
        with self.subTest():
            env = self.TestEnvironment()
            env._dict.pop('BUILDERS')
            assert ('BUILDERS' in env) is False
            env2 = env.Clone()

    def test_Detect(self) -> None:
        """Test Detect()ing tools"""
        test = TestCmd.TestCmd(workdir = '')
        test.subdir('sub1', 'sub2')
        sub1 = test.workpath('sub1')
        sub2 = test.workpath('sub2')

        if sys.platform == 'win32':
            test.write(['sub1', 'xxx'], "sub1/xxx\n")
            test.write(['sub2', 'xxx'], "sub2/xxx\n")

            env = self.TestEnvironment(ENV = { 'PATH' : [sub1, sub2] })

            x = env.Detect('xxx.exe')
            assert x is None, x

            test.write(['sub2', 'xxx.exe'], "sub2/xxx.exe\n")

            env = self.TestEnvironment(ENV = { 'PATH' : [sub1, sub2] })

            x = env.Detect('xxx.exe')
            assert x == 'xxx.exe', x

            test.write(['sub1', 'xxx.exe'], "sub1/xxx.exe\n")

            x = env.Detect('xxx.exe')
            assert x == 'xxx.exe', x

        else:
            test.write(['sub1', 'xxx.exe'], "sub1/xxx.exe\n")
            test.write(['sub2', 'xxx.exe'], "sub2/xxx.exe\n")

            env = self.TestEnvironment(ENV = { 'PATH' : [sub1, sub2] })

            x = env.Detect('xxx.exe')
            assert x is None, x

            sub2_xxx_exe = test.workpath('sub2', 'xxx.exe')
            os.chmod(sub2_xxx_exe, 0o755)

            env = self.TestEnvironment(ENV = { 'PATH' : [sub1, sub2] })

            x = env.Detect('xxx.exe')
            assert x == 'xxx.exe', x

            sub1_xxx_exe = test.workpath('sub1', 'xxx.exe')
            os.chmod(sub1_xxx_exe, 0o755)

            x = env.Detect('xxx.exe')
            assert x == 'xxx.exe', x

        env = self.TestEnvironment(ENV = { 'PATH' : [] })
        x = env.Detect('xxx.exe')
        assert x is None, x

    def test_Dictionary(self) -> None:
        """Test retrieval of known construction variables

        Fetch them from the Dictionary and check for well-known
        defaults that get inserted.
        """
        env = self.TestEnvironment(XXX = 'x', YYY = 'y', ZZZ = 'z')
        assert env.Dictionary('XXX') == 'x'
        assert env.Dictionary('YYY') == 'y'
        assert env.Dictionary('XXX', 'ZZZ') == ['x', 'z']
        xxx, zzz = env.Dictionary('XXX', 'ZZZ')
        assert xxx == 'x'
        assert zzz == 'z'
        # added in 4.9.0: as_dict flag
        with self.subTest():
            expect = {'XXX': 'x'}
            self.assertEqual(env.Dictionary('XXX', as_dict=True), expect)
        with self.subTest():
            expect = {'XXX': 'x', 'YYY': 'y'}
            self.assertEqual(env.Dictionary('XXX', 'YYY', as_dict=True), expect)
        assert 'BUILDERS' in env.Dictionary()
        assert 'CC' in env.Dictionary()
        assert 'CCFLAGS' in env.Dictionary()
        assert 'ENV' in env.Dictionary()

        assert env['XXX'] == 'x'
        env['XXX'] = 'foo'
        assert env.Dictionary('XXX') == 'foo'
        del env['XXX']
        assert 'XXX' not in env.Dictionary()

    def test_FindIxes(self) -> None:
        """Test FindIxes()"""
        env = self.TestEnvironment(LIBPREFIX='lib',
                          LIBSUFFIX='.a',
                          SHLIBPREFIX='lib',
                          SHLIBSUFFIX='.so',
                          PREFIX='pre',
                          SUFFIX='post')

        paths = [os.path.join('dir', 'libfoo.a'),
                 os.path.join('dir', 'libfoo.so')]

        assert paths[0] == env.FindIxes(paths, 'LIBPREFIX', 'LIBSUFFIX')
        assert paths[1] == env.FindIxes(paths, 'SHLIBPREFIX', 'SHLIBSUFFIX')
        assert None is env.FindIxes(paths, 'PREFIX', 'POST')

        paths = ['libfoo.a', 'prefoopost']

        assert paths[0] == env.FindIxes(paths, 'LIBPREFIX', 'LIBSUFFIX')
        assert None is env.FindIxes(paths, 'SHLIBPREFIX', 'SHLIBSUFFIX')
        assert paths[1] == env.FindIxes(paths, 'PREFIX', 'SUFFIX')

    def test_ParseConfig(self) -> None:
        """Test the ParseConfig() method"""
        env = self.TestEnvironment(COMMAND='command',
                          ASFLAGS='assembler',
                          CCFLAGS=[''],
                          CPPDEFINES=[],
                          CPPFLAGS=[''],
                          CPPPATH='string',
                          FRAMEWORKPATH=[],
                          FRAMEWORKS=[],
                          LIBPATH=['list'],
                          LIBS='',
                          LINKFLAGS=[''],
                          RPATH=[])

        orig_backtick = env.backtick
        class my_backtick:
            """mocked backtick routine so command is not actually issued.

            Just returns the string it was given.
            """
            def __init__(self, save_command, output) -> None:
                self.save_command = save_command
                self.output = output
            def __call__(self, command):
                self.save_command.append(command)
                return self.output

        try:
            save_command = []
            env.backtick = my_backtick(save_command,
                                 "-I/usr/include/fum -I bar -X\n" + \
                                 "-L/usr/fax -L foo -lxxx -l yyy " + \
                                 "-Wa,-as -Wl,-link " + \
                                 "-Wl,-rpath=rpath1 " + \
                                 "-Wl,-R,rpath2 " + \
                                 "-Wl,-Rrpath3 " + \
                                 "-Wp,-cpp abc " + \
                                 "-framework Carbon " + \
                                 "-frameworkdir=fwd1 " + \
                                 "-Ffwd2 " + \
                                 "-F fwd3 " + \
                                 "-pthread " + \
                                 "-fmerge-all-constants " + \
                                 "-mno-cygwin -mwindows " + \
                                 "-arch i386 -isysroot /tmp " + \
                                 "-iquote /usr/include/foo1 " + \
                                 "-isystem /usr/include/foo2 " + \
                                 "-idirafter /usr/include/foo3 " + \
                                 "+DD64 " + \
                                 "-DFOO -DBAR=value")
            env.ParseConfig("fake $COMMAND")
            assert save_command == ['fake command'], save_command
            assert env['ASFLAGS'] == ['assembler', '-as'], env['ASFLAGS']
            assert env['CCFLAGS'] == ['', '-X', '-Wa,-as',
                                      '-pthread', '-fmerge-all-constants', '-mno-cygwin',
                                      ('-arch', 'i386'), ('-isysroot', '/tmp'),
                                      ('-iquote', '/usr/include/foo1'),
                                      ('-isystem', '/usr/include/foo2'),
                                      ('-idirafter', '/usr/include/foo3'),
                                      '+DD64'], env['CCFLAGS']
            self.assertEqual(list(env['CPPDEFINES']), ['FOO', ['BAR', 'value']])
            assert env['CPPFLAGS'] == ['', '-Wp,-cpp'], env['CPPFLAGS']
            assert env['CPPPATH'] == ['string', '/usr/include/fum', 'bar'], env['CPPPATH']
            assert env['FRAMEWORKPATH'] == ['fwd1', 'fwd2', 'fwd3'], env['FRAMEWORKPATH']
            assert env['FRAMEWORKS'] == ['Carbon'], env['FRAMEWORKS']
            assert env['LIBPATH'] == ['list', '/usr/fax', 'foo'], env['LIBPATH']
            assert env['LIBS'] == ['xxx', 'yyy', env.File('abc')], env['LIBS']
            assert env['LINKFLAGS'] == ['', '-Wl,-link', '-pthread',
                                        '-fmerge-all-constants',
                                        '-mno-cygwin', '-mwindows',
                                        ('-arch', 'i386'),
                                        ('-isysroot', '/tmp'),
                                        '+DD64'], env['LINKFLAGS']
            assert env['RPATH'] == ['rpath1', 'rpath2', 'rpath3'], env['RPATH']

            env.backtick = my_backtick([], "-Ibar")
            env.ParseConfig("fake2")
            assert env['CPPPATH'] == ['string', '/usr/include/fum', 'bar'], env['CPPPATH']
            env.ParseConfig("fake2", unique=0)
            assert env['CPPPATH'] == ['string', '/usr/include/fum', 'bar', 'bar'], env['CPPPATH']
        finally:
            env.backtick = orig_backtick

        # check that we can pass our own function,
        # and that it works for both values of unique

        def my_function(myenv, flags, unique: bool=True) -> None:
            import json

            args = json.loads(flags)
            if unique:
                myenv.AppendUnique(**args)
            else:
                myenv.Append(**args)

        json_str = '{"LIBS": ["yyy", "xxx", "yyy"]}'

        env = Environment(LIBS=['xxx'])
        env2 = env.Clone()
        env.backtick = my_backtick([], json_str)
        env2.backtick = my_backtick([], json_str)

        env.ParseConfig("foo", my_function)
        assert env['LIBS'] == ['xxx', 'yyy'], env['LIBS']

        env2.ParseConfig("foo2", my_function, unique=False)
        assert env2['LIBS'] == ['xxx', 'yyy', 'xxx', 'yyy'], env2['LIBS']


    def test_ParseDepends(self) -> None:
        """Test the ParseDepends() method"""
        test = TestCmd.TestCmd(workdir = '')

        test.write('single', """
#file: dependency

f0: \
   d1 \
   d2 \
   d3 \

""")

        test.write('multiple', """
f1: foo
f2 f3: bar
f4: abc def
#file: dependency
f5: \
   ghi \
   jkl \
   mno \
""")

        env = self.TestEnvironment(SINGLE = test.workpath('single'))

        tlist = []
        dlist = []
        def my_depends(target, dependency, tlist=tlist, dlist=dlist) -> None:
            tlist.extend(target)
            dlist.extend(dependency)

        env.Depends = my_depends

        env.ParseDepends(test.workpath('does_not_exist'))

        exc_caught = None
        try:
            env.ParseDepends(test.workpath('does_not_exist'), must_exist=True)
        except IOError:
            exc_caught = 1
        assert exc_caught, "did not catch expected IOError"

        del tlist[:]
        del dlist[:]

        env.ParseDepends('$SINGLE', only_one=True)
        t = list(map(str, tlist))
        d = list(map(str, dlist))
        assert t == ['f0'], t
        assert d == ['d1', 'd2', 'd3'], d

        del tlist[:]
        del dlist[:]

        env.ParseDepends(test.workpath('multiple'))
        t = list(map(str, tlist))
        d = list(map(str, dlist))
        assert t == ['f1', 'f2', 'f3', 'f4', 'f5'], t
        assert d == ['foo', 'bar', 'abc', 'def', 'ghi', 'jkl', 'mno'], d

        exc_caught = None
        try:
            env.ParseDepends(test.workpath('multiple'), only_one=True)
        except SCons.Errors.UserError:
            exc_caught = 1
        assert exc_caught, "did not catch expected UserError"

    def test_Platform(self) -> None:
        """Test the Platform() method"""
        env = self.TestEnvironment(WIN32='win32', NONE='no-such-platform')

        exc_caught = None
        try:
            env.Platform('does_not_exist')
        except SCons.Errors.UserError:
            exc_caught = 1
        assert exc_caught, "did not catch expected UserError"

        exc_caught = None
        try:
            env.Platform('$NONE')
        except SCons.Errors.UserError:
            exc_caught = 1
        assert exc_caught, "did not catch expected UserError"

        env.Platform('posix')
        assert env['OBJSUFFIX'] == '.o', env['OBJSUFFIX']

        env.Platform('$WIN32')
        assert env['OBJSUFFIX'] == '.obj', env['OBJSUFFIX']

    def test_Prepend(self) -> None:
        """Test prepending to construction variables in an Environment."""
        cases = [
            ('a1',       'A1',           'A1a1'),
            ('a2',       ['A2'],         ['A2', 'a2']),
            ('a3',       UL(['A3']),     UL(['A3', 'a', '3'])),
            ('a4',       '',             'a4'),
            ('a5',       [],             ['a5']),
            ('a6',       UL([]),         UL(['a', '6'])),
            ('a7',       [''],           ['', 'a7']),
            ('a8',       UL(['']),       UL(['', 'a', '8'])),

            (['e1'],     'E1',           ['E1', 'e1']),
            (['e2'],     ['E2'],         ['E2', 'e2']),
            (['e3'],     UL(['E3']),     UL(['E3', 'e3'])),
            (['e4'],     '',             ['e4']),
            (['e5'],     [],             ['e5']),
            (['e6'],     UL([]),         UL(['e6'])),
            (['e7'],     [''],           ['', 'e7']),
            (['e8'],     UL(['']),       UL(['', 'e8'])),

            (UL(['i1']), 'I1',           UL(['I', '1', 'i1'])),
            (UL(['i2']), ['I2'],         UL(['I2', 'i2'])),
            (UL(['i3']), UL(['I3']),     UL(['I3', 'i3'])),
            (UL(['i4']), '',             UL(['i4'])),
            (UL(['i5']), [],             UL(['i5'])),
            (UL(['i6']), UL([]),         UL(['i6'])),
            (UL(['i7']), [''],           UL(['', 'i7'])),
            (UL(['i8']), UL(['']),       UL(['', 'i8'])),

            ({'d1':1},   'D1',           {'d1':1, 'D1':None}),
            ({'d2':1},   ['D2'],         {'d2':1, 'D2':None}),
            ({'d3':1},   UL(['D3']),     {'d3':1, 'D3':None}),
            ({'d4':1},   {'D4':1},       {'d4':1, 'D4':1}),
            ({'d5':1},   UD({'D5':1}),   UD({'d5':1, 'D5':1})),

            (UD({'u1':1}), 'U1',         UD({'u1':1, 'U1':None})),
            (UD({'u2':1}), ['U2'],       UD({'u2':1, 'U2':None})),
            (UD({'u3':1}), UL(['U3']),   UD({'u3':1, 'U3':None})),
            (UD({'u4':1}), {'U4':1},     UD({'u4':1, 'U4':1})),
            (UD({'u5':1}), UD({'U5':1}), UD({'u5':1, 'U5':1})),

            ('',         'M1',           'M1'),
            ('',         ['M2'],         ['M2']),
            ('',         UL(['M3']),     UL(['M3'])),
            ('',         '',             ''),
            ('',         [],             []),
            ('',         UL([]),         UL([])),
            ('',         [''],           ['']),
            ('',         UL(['']),       UL([''])),

            ([],         'N1',           ['N1']),
            ([],         ['N2'],         ['N2']),
            ([],         UL(['N3']),     UL(['N3'])),
            ([],         '',             []),
            ([],         [],             []),
            ([],         UL([]),         UL([])),
            ([],         [''],           ['']),
            ([],         UL(['']),       UL([''])),

            (UL([]),     'O1',           UL(['O', '1'])),
            (UL([]),     ['O2'],         UL(['O2'])),
            (UL([]),     UL(['O3']),     UL(['O3'])),
            (UL([]),     '',             UL([])),
            (UL([]),     [],             UL([])),
            (UL([]),     UL([]),         UL([])),
            (UL([]),     [''],           UL([''])),
            (UL([]),     UL(['']),       UL([''])),

            ([''],       'P1',           ['P1', '']),
            ([''],       ['P2'],         ['P2', '']),
            ([''],       UL(['P3']),     UL(['P3', ''])),
            ([''],       '',             ['']),
            ([''],       [],             ['']),
            ([''],       UL([]),         UL([''])),
            ([''],       [''],           ['', '']),
            ([''],       UL(['']),       UL(['', ''])),

            (UL(['']),   'Q1',           UL(['Q', '1', ''])),
            (UL(['']),   ['Q2'],         UL(['Q2', ''])),
            (UL(['']),   UL(['Q3']),     UL(['Q3', ''])),
            (UL(['']),   '',             UL([''])),
            (UL(['']),   [],             UL([''])),
            (UL(['']),   UL([]),         UL([''])),
            (UL(['']),   [''],           UL(['', ''])),
            (UL(['']),   UL(['']),       UL(['', ''])),
        ]

        env = Environment()
        failed = 0
        for input, prepend, expect in cases:
            env['XXX'] = copy.copy(input)
            try:
                env.Prepend(XXX=prepend)
            except Exception as e:
                if failed == 0: print()
                print("    %s Prepend %s exception: %s" % \
                      (repr(input), repr(prepend), e))
                failed = failed + 1
            else:
                result = env['XXX']
                if result != expect:
                    if failed == 0: print()
                    print("    %s Prepend %s => %s did not match %s" % \
                          (repr(input), repr(prepend), repr(result), repr(expect)))
                    failed += 1
        assert failed == 0, "%d Prepend() cases failed" % failed

        env['UL'] = UL(['foo'])
        env.Prepend(UL = 'bar')
        result = env['UL']
        assert isinstance(result, UL), repr(result)
        assert result == ['b', 'a', 'r', 'foo'], result

        env['CLVar'] = CLVar(['foo'])
        env.Prepend(CLVar = 'bar')
        result = env['CLVar']
        assert isinstance(result, CLVar), repr(result)
        assert result == ['bar', 'foo'], result

        env3 = self.TestEnvironment(X = {'x1' : 7})
        env3.Prepend(X = {'x1' : 8, 'x2' : 9}, Y = {'y1' : 10})
        assert env3['X'] == {'x1': 8, 'x2' : 9}, env3['X']
        assert env3['Y'] == {'y1': 10}, env3['Y']

        z1 = Builder()
        z2 = Builder()
        env4 = self.TestEnvironment(BUILDERS = {'z1' : z1})
        env4.Prepend(BUILDERS = {'z2' : z2})
        assert env4['BUILDERS'] == {'z1' : z1, 'z2' : z2}, env4['BUILDERS']
        assert hasattr(env4, 'z1')
        assert hasattr(env4, 'z2')

    def test_PrependENVPath(self) -> None:
        """Test prepending to an ENV path."""
        env1 = self.TestEnvironment(
            ENV={'PATH': r'C:\dir\num\one;C:\dir\num\two'},
            MYENV={'MYPATH': r'C:\mydir\num\one;C:\mydir\num\two'},
        )

        # have to include the pathsep here so that the test will work on UNIX too.
        env1.PrependENVPath('PATH', r'C:\dir\num\two', sep=';')
        env1.PrependENVPath('PATH', r'C:\dir\num\three', sep=';')
        assert (
            env1['ENV']['PATH'] == r'C:\dir\num\three;C:\dir\num\two;C:\dir\num\one'
        ), env1['ENV']['PATH']


        # add nonexisting - at front
        env1.PrependENVPath('MYPATH', r'C:\mydir\num\three', 'MYENV', sep=';')
        assert (
            env1['MYENV']['MYPATH'] == r'C:\mydir\num\three;C:\mydir\num\one;C:\mydir\num\two'
        ), env1['MYENV']['MYPATH']

        # add existing - moves to the front
        env1.PrependENVPath('MYPATH', r'C:\mydir\num\one', 'MYENV', sep=';')
        # this should do nothing since delete_existing is false
        env1.PrependENVPath(
            'MYPATH', r'C:\mydir\num\three', 'MYENV', sep=';', delete_existing=False
        )
        assert (
            env1['MYENV']['MYPATH'] == r'C:\mydir\num\one;C:\mydir\num\three;C:\mydir\num\two'
        ), env1['MYENV']['MYPATH']

        test = TestCmd.TestCmd(workdir='')
        test.subdir('sub1', 'sub2')
        p = env1['ENV']['PATH']
        env1.PrependENVPath('PATH', '#sub1', sep=';')
        env1.PrependENVPath('PATH', env1.fs.Dir('sub2'), sep=';')
        assert env1['ENV']['PATH'] == 'sub2;sub1;' + p, env1['ENV']['PATH']


    def test_PrependUnique(self) -> None:
        """Test prepending unique values to construction variables

        This strips values that are already present when lists are
        involved."""
        env = self.TestEnvironment(AAA1 = 'a1',
                          AAA2 = 'a2',
                          AAA3 = 'a3',
                          AAA4 = 'a4',
                          AAA5 = 'a5',
                          BBB1 = ['b1'],
                          BBB2 = ['b2'],
                          BBB3 = ['b3'],
                          BBB4 = ['b4'],
                          BBB5 = ['b5'],
                          CCC1 = '',
                          CCC2 = '',
                          DDD1 = ['a', 'b', 'c'],
                          DDD2 = ['b', 'a', 'a'])
        env.PrependUnique(AAA1 = 'a1',
                          AAA2 = ['a2'],
                          AAA3 = ['a3', 'b', 'c', 'b', 'a3'], # ignore dups
                          AAA4 = 'a4.new',
                          AAA5 = ['a5.new'],
                          BBB1 = 'b1',
                          BBB2 = ['b2'],
                          BBB3 = ['b3', 'b', 'c', 'b3'],
                          BBB4 = 'b4.new',
                          BBB5 = ['b5.new'],
                          CCC1 = 'c1',
                          CCC2 = ['c2'],
                          DDD1 = 'b',
                          DDD2 = 'a')
        assert env['AAA1'] == 'a1a1', env['AAA1']
        assert env['AAA2'] == ['a2'], env['AAA2']
        assert env['AAA3'] == ['c', 'b', 'a3'], env['AAA3']
        assert env['AAA4'] == 'a4.newa4', env['AAA4']
        assert env['AAA5'] == ['a5.new', 'a5'], env['AAA5']
        assert env['BBB1'] == ['b1'], env['BBB1']
        assert env['BBB2'] == ['b2'], env['BBB2']
        assert env['BBB3'] == ['b', 'c', 'b3'], env['BBB3']
        assert env['BBB4'] == ['b4.new', 'b4'], env['BBB4']
        assert env['BBB5'] == ['b5.new', 'b5'], env['BBB5']
        assert env['CCC1'] == 'c1', env['CCC1']
        assert env['CCC2'] == ['c2'], env['CCC2']
        assert env['DDD1'] == ['a', 'b', 'c'], env['DDD1']
        assert env['DDD2'] == ['b', 'a', 'a'], env['DDD2']  # keep existing dup

        env.PrependUnique(DDD1='b', delete_existing=True)
        assert env['DDD1'] == ['b', 'a', 'c'], env['DDD1']  # b moves to front

        env.PrependUnique(DDD1=['a', 'c'], delete_existing=True)
        assert env['DDD1'] == ['a', 'c', 'b'], env['DDD1']  # a & c move to front

        env.PrependUnique(DDD1=['d', 'e', 'd'], delete_existing=True)
        assert env['DDD1'] == ['d', 'e', 'a', 'c', 'b'], env['DDD1']

        env.PrependUnique(DDD2=['a'], delete_existing=True)
        assert env['DDD2'] == ['a', 'b'], env['DDD2']  # all existing instances deleted

        # issue regression: substrings should not be deleted
        env.PrependUnique(BBB4='b4.newer', delete_existing=True)
        assert env['BBB4'] == ['b4.newer', 'b4.new', 'b4'], env['BBB4']

        env['CLVar'] = CLVar([])
        env.PrependUnique(CLVar='bar')
        result = env['CLVar']
        assert isinstance(result, CLVar), repr(result)
        assert result == ['bar'], result

        env['CLVar'] = CLVar(['abc'])
        env.PrependUnique(CLVar='bar')
        result = env['CLVar']
        assert isinstance(result, CLVar), repr(result)
        assert result == ['bar', 'abc'], result

        env['CLVar'] = CLVar(['bar'])
        env.PrependUnique(CLVar='bar')
        result = env['CLVar']
        assert isinstance(result, CLVar), repr(result)
        assert result == ['bar'], result


    def test_Replace(self) -> None:
        """Test replacing construction variables in an Environment

        After creation of the Environment, of course.
        """
        env1 = self.TestEnvironment(AAA = 'a', BBB = 'b')
        env1.Replace(BBB = 'bbb', CCC = 'ccc')

        env2 = self.TestEnvironment(AAA = 'a', BBB = 'bbb', CCC = 'ccc')
        assert env1 == env2, diff_env(env1, env2)

        b1 = Builder()
        b2 = Builder()
        env3 = self.TestEnvironment(BUILDERS = {'b1' : b1})
        assert hasattr(env3, 'b1'), "b1 was not set"
        env3.Replace(BUILDERS = {'b2' : b2})
        assert not hasattr(env3, 'b1'), "b1 was not cleared"
        assert hasattr(env3, 'b2'), "b2 was not set"

    def test_ReplaceIxes(self) -> None:
        """Test ReplaceIxes()"""
        env = self.TestEnvironment(LIBPREFIX='lib',
                          LIBSUFFIX='.a',
                          SHLIBPREFIX='lib',
                          SHLIBSUFFIX='.so',
                          PREFIX='pre',
                          SUFFIX='post')

        assert 'libfoo.a' == env.ReplaceIxes('libfoo.so',
                                             'SHLIBPREFIX', 'SHLIBSUFFIX',
                                             'LIBPREFIX', 'LIBSUFFIX')

        assert os.path.join('dir', 'libfoo.a') == env.ReplaceIxes(os.path.join('dir', 'libfoo.so'),
                                                                   'SHLIBPREFIX', 'SHLIBSUFFIX',
                                                                   'LIBPREFIX', 'LIBSUFFIX')

        assert 'libfoo.a' == env.ReplaceIxes('prefoopost',
                                             'PREFIX', 'SUFFIX',
                                             'LIBPREFIX', 'LIBSUFFIX')

    def test_SetDefault(self) -> None:
        """Test the SetDefault method"""
        env = self.TestEnvironment(tools = [])
        env.SetDefault(V1 = 1)
        env.SetDefault(V1 = 2)
        assert env['V1'] == 1
        env['V2'] = 2
        env.SetDefault(V2 = 1)
        assert env['V2'] == 2

    def test_Tool(self) -> None:
        """Test the Tool() method"""
        env = self.TestEnvironment(LINK='link', NONE='no-such-tool')

        exc_caught = None
        try:
            tool = env.Tool('does_not_exist')
        except SCons.Errors.UserError:
            exc_caught = 1
        else:
            assert isinstance(tool, SCons.Tool.Tool)
        assert exc_caught, "did not catch expected UserError"

        exc_caught = None
        try:
            env.Tool('$NONE')
        except SCons.Errors.UserError:
            exc_caught = 1
        assert exc_caught, "did not catch expected UserError"

        # Use a non-existent toolpath directory just to make sure we
        # can call Tool() with the keyword argument.
        env.Tool('cc', toolpath=['/no/such/directory'])
        assert env['CC'] == 'cc', env['CC']

        env.Tool('$LINK')
        assert env['LINK'] == '$SMARTLINK', env['LINK']

        # Test that the environment stores the toolpath and
        # re-uses it for later calls.
        test = TestCmd.TestCmd(workdir = '')

        test.write('xxx.py', """\
def exists(env):
    return True
def generate(env):
    env['XXX'] = 'one'
""")

        test.write('yyy.py', """\
def exists(env):
    return True
def generate(env):
    env['YYY'] = 'two'
""")

        env = self.TestEnvironment(tools=['xxx'], toolpath=[test.workpath('')])
        assert env['XXX'] == 'one', env['XXX']
        env.Tool('yyy')
        assert env['YYY'] == 'two', env['YYY']

    def test_WhereIs(self) -> None:
        """Test the WhereIs() method"""
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

        path = os.pathsep.join(pathdirs_1234)
        env = self.TestEnvironment(ENV = {'PATH' : path})
        wi = env.WhereIs('')
        assert wi is None
        wi = env.WhereIs('xxx.exe')
        assert wi == test.workpath(sub3_xxx_exe), wi
        wi = env.WhereIs('xxx.exe', pathdirs_1243)
        assert wi == test.workpath(sub4_xxx_exe), wi
        wi = env.WhereIs('xxx.exe', os.pathsep.join(pathdirs_1243))
        assert wi == test.workpath(sub4_xxx_exe), wi

        wi = env.WhereIs('xxx.exe', reject = sub3_xxx_exe)
        assert wi == test.workpath(sub4_xxx_exe), wi
        wi = env.WhereIs('xxx.exe', pathdirs_1243, reject = sub3_xxx_exe)
        assert wi == test.workpath(sub4_xxx_exe), wi

        path = os.pathsep.join(pathdirs_1243)
        env = self.TestEnvironment(ENV = {'PATH' : path})
        wi = env.WhereIs('xxx.exe')
        assert wi == test.workpath(sub4_xxx_exe), wi
        wi = env.WhereIs('xxx.exe', pathdirs_1234)
        assert wi == test.workpath(sub3_xxx_exe), wi
        wi = env.WhereIs('xxx.exe', os.pathsep.join(pathdirs_1234))
        assert wi == test.workpath(sub3_xxx_exe), wi

        if sys.platform == 'win32':
            wi = env.WhereIs('xxx', pathext = '')
            assert wi is None, wi

            wi = env.WhereIs('xxx', pathext = '.exe')
            assert wi == test.workpath(sub4_xxx_exe), wi

            wi = env.WhereIs('xxx', path = pathdirs_1234, pathext = '.BAT;.EXE')
            assert wi.lower() == test.workpath(sub3_xxx_exe).lower(), wi

            # Test that we return a normalized path even when
            # the path contains forward slashes.
            forward_slash = test.workpath('') + '/sub3'
            wi = env.WhereIs('xxx', path = forward_slash, pathext = '.EXE')
            assert wi.lower() == test.workpath(sub3_xxx_exe).lower(), wi



    def test_Action(self) -> None:
        """Test the Action() method"""
        import SCons.Action

        env = self.TestEnvironment(FOO = 'xyzzy')

        a = env.Action('foo')
        assert a, a
        assert a.__class__ is SCons.Action.CommandAction, a.__class__

        a = env.Action('$FOO')
        assert a, a
        assert a.__class__ is SCons.Action.CommandAction, a.__class__

        a = env.Action('$$FOO')
        assert a, a
        assert a.__class__ is SCons.Action.LazyAction, a.__class__

        a = env.Action(['$FOO', 'foo'])
        assert a, a
        assert a.__class__ is SCons.Action.ListAction, a.__class__

        def func(arg) -> None:
            pass
        a = env.Action(func)
        assert a, a
        assert a.__class__ is SCons.Action.FunctionAction, a.__class__

    def test_AddPostAction(self) -> None:
        """Test the AddPostAction() method"""
        env = self.TestEnvironment(FOO='fff', BAR='bbb')

        n = env.AddPostAction('$FOO', lambda x: x)
        assert str(n[0]) == 'fff', n[0]

        n = env.AddPostAction(['ggg', '$BAR'], lambda x: x)
        assert str(n[0]) == 'ggg', n[0]
        assert str(n[1]) == 'bbb', n[1]

    def test_AddPreAction(self) -> None:
        """Test the AddPreAction() method"""
        env = self.TestEnvironment(FOO='fff', BAR='bbb')

        n = env.AddPreAction('$FOO', lambda x: x)
        assert str(n[0]) == 'fff', n[0]

        n = env.AddPreAction(['ggg', '$BAR'], lambda x: x)
        assert str(n[0]) == 'ggg', n[0]
        assert str(n[1]) == 'bbb', n[1]

    def test_Alias(self) -> None:
        """Test the Alias() method"""
        env = self.TestEnvironment(FOO='kkk', BAR='lll', EA='export_alias')

        tgt = env.Alias('new_alias')[0]
        assert str(tgt) == 'new_alias', tgt
        assert tgt.sources == [], tgt.sources
        assert not hasattr(tgt, 'builder'), tgt.builder

        tgt = env.Alias('None_alias', None)[0]
        assert str(tgt) == 'None_alias', tgt
        assert tgt.sources == [], tgt.sources

        tgt = env.Alias('empty_list', [])[0]
        assert str(tgt) == 'empty_list', tgt
        assert tgt.sources == [], tgt.sources

        tgt = env.Alias('export_alias', [ 'asrc1', '$FOO' ])[0]
        assert str(tgt) == 'export_alias', tgt
        assert len(tgt.sources) == 2, list(map(str, tgt.sources))
        assert str(tgt.sources[0]) == 'asrc1', list(map(str, tgt.sources))
        assert str(tgt.sources[1]) == 'kkk', list(map(str, tgt.sources))

        n = env.Alias(tgt, source = ['$BAR', 'asrc4'])[0]
        assert n is tgt, n
        assert len(tgt.sources) == 4, list(map(str, tgt.sources))
        assert str(tgt.sources[2]) == 'lll', list(map(str, tgt.sources))
        assert str(tgt.sources[3]) == 'asrc4', list(map(str, tgt.sources))

        n = env.Alias('$EA', 'asrc5')[0]
        assert n is tgt, n
        assert len(tgt.sources) == 5, list(map(str, tgt.sources))
        assert str(tgt.sources[4]) == 'asrc5', list(map(str, tgt.sources))

        t1, t2 = env.Alias(['t1', 't2'], ['asrc6', 'asrc7'])
        assert str(t1) == 't1', t1
        assert str(t2) == 't2', t2
        assert len(t1.sources) == 2, list(map(str, t1.sources))
        assert str(t1.sources[0]) == 'asrc6', list(map(str, t1.sources))
        assert str(t1.sources[1]) == 'asrc7', list(map(str, t1.sources))
        assert len(t2.sources) == 2, list(map(str, t2.sources))
        assert str(t2.sources[0]) == 'asrc6', list(map(str, t2.sources))
        assert str(t2.sources[1]) == 'asrc7', list(map(str, t2.sources))

        tgt = env.Alias('add', 's1')
        tgt = env.Alias('add', 's2')[0]
        s = list(map(str, tgt.sources))
        assert s == ['s1', 's2'], s
        tgt = env.Alias(tgt, 's3')[0]
        s = list(map(str, tgt.sources))
        assert s == ['s1', 's2', 's3'], s

        tgt = env.Alias('act', None, "action1")[0]
        s = str(tgt.builder.action)
        assert s == "action1", s
        tgt = env.Alias('act', None, "action2")[0]
        s = str(tgt.builder.action)
        assert s == "action1\naction2", s
        tgt = env.Alias(tgt, None, "action3")[0]
        s = str(tgt.builder.action)
        assert s == "action1\naction2\naction3", s

    def test_AlwaysBuild(self) -> None:
        """Test the AlwaysBuild() method"""
        env = self.TestEnvironment(FOO='fff', BAR='bbb')
        t = env.AlwaysBuild('a', 'b$FOO', ['c', 'd'], '$BAR',
                            env.fs.Dir('dir'), env.fs.File('file'))
        assert t[0].__class__.__name__ == 'Entry'
        assert t[0].get_internal_path() == 'a'
        assert t[0].always_build
        assert t[1].__class__.__name__ == 'Entry'
        assert t[1].get_internal_path() == 'bfff'
        assert t[1].always_build
        assert t[2].__class__.__name__ == 'Entry'
        assert t[2].get_internal_path() == 'c'
        assert t[2].always_build
        assert t[3].__class__.__name__ == 'Entry'
        assert t[3].get_internal_path() == 'd'
        assert t[3].always_build
        assert t[4].__class__.__name__ == 'Entry'
        assert t[4].get_internal_path() == 'bbb'
        assert t[4].always_build
        assert t[5].__class__.__name__ == 'Dir'
        assert t[5].get_internal_path() == 'dir'
        assert t[5].always_build
        assert t[6].__class__.__name__ == 'File'
        assert t[6].get_internal_path() == 'file'
        assert t[6].always_build

    def test_VariantDir(self) -> None:
        """Test the VariantDir() method"""
        class MyFS:
             def Dir(self, name):
                 return name
             def VariantDir(self, variant_dir, src_dir, duplicate) -> None:
                 self.variant_dir = variant_dir
                 self.src_dir = src_dir
                 self.duplicate = duplicate

        env = self.TestEnvironment(FOO = 'fff', BAR = 'bbb')
        env.fs = MyFS()

        env.VariantDir('build', 'src')
        assert env.fs.variant_dir == 'build', env.fs.variant_dir
        assert env.fs.src_dir == 'src', env.fs.src_dir
        assert env.fs.duplicate == 1, env.fs.duplicate

        env.VariantDir('build${FOO}', '${BAR}src', 0)
        assert env.fs.variant_dir == 'buildfff', env.fs.variant_dir
        assert env.fs.src_dir == 'bbbsrc', env.fs.src_dir
        assert env.fs.duplicate == 0, env.fs.duplicate

    def test_Builder(self) -> None:
        """Test the Builder() method"""
        env = self.TestEnvironment(FOO = 'xyzzy')

        b = env.Builder(action = 'foo')
        assert b is not None, b

        b = env.Builder(action = '$FOO')
        assert b is not None, b

        b = env.Builder(action = ['$FOO', 'foo'])
        assert b is not None, b

        def func(arg) -> None:
            pass
        b = env.Builder(action = func)
        assert b is not None, b
        b = env.Builder(generator = func)
        assert b is not None, b

    def test_CacheDir(self) -> None:
        """Test the CacheDir() method"""

        test = TestCmd.TestCmd(workdir = '')

        test_cachedir = os.path.join(test.workpath(),'CacheDir')
        test_cachedir_config = os.path.join(test_cachedir, 'config')
        test_foo = os.path.join(test.workpath(), 'foo-cachedir')
        test_foo_config = os.path.join(test_foo,'config')
        test_foo1 = os.path.join(test.workpath(), 'foo1-cachedir')
        test_foo1_config = os.path.join(test_foo1, 'config')

        env = self.TestEnvironment(CD = test_cachedir)

        env.CacheDir(test_foo)
        assert env._CacheDir_path == test_foo, env._CacheDir_path
        assert os.path.isfile(test_foo_config), "No file %s"%test_foo_config

        env.CacheDir('$CD')
        assert env._CacheDir_path == test_cachedir, env._CacheDir_path
        assert os.path.isfile(test_cachedir_config), "No file %s"%test_cachedir_config

        # Now verify that -n/-no_exec wil prevent the CacheDir/config from being created
        import SCons.Action
        SCons.Action.execute_actions = False
        env.CacheDir(test_foo1)
        assert env._CacheDir_path == test_foo1, env._CacheDir_path
        assert not os.path.isfile(test_foo1_config), "No file %s"%test_foo1_config


    def test_Clean(self) -> None:
        """Test the Clean() method"""
        env = self.TestEnvironment(FOO = 'fff', BAR = 'bbb')

        CT = SCons.Environment.CleanTargets

        foo = env.arg2nodes('foo')[0]
        fff = env.arg2nodes('fff')[0]

        t = env.Clean('foo', 'aaa')
        l = list(map(str, CT[foo]))
        assert l == ['aaa'], l

        t = env.Clean(foo, ['$BAR', 'ccc'])
        l = list(map(str, CT[foo]))
        assert l == ['aaa', 'bbb', 'ccc'], l

        eee = env.arg2nodes('eee')[0]

        t = env.Clean('$FOO', 'ddd')
        l = list(map(str, CT[fff]))
        assert l == ['ddd'], l
        t = env.Clean(fff, [eee, 'fff'])
        l = list(map(str, CT[fff]))
        assert l == ['ddd', 'eee', 'fff'], l

    def test_Command(self) -> None:
        """Test the Command() method."""
        env = Environment()
        t = env.Command(target='foo.out', source=['foo1.in', 'foo2.in'],
                        action='buildfoo $target $source')[0]
        assert t.builder is not None
        assert t.builder.action.__class__.__name__ == 'CommandAction'
        assert t.builder.action.cmd_list == 'buildfoo $target $source'
        assert 'foo1.in' in [x.get_internal_path() for x in t.sources]
        assert 'foo2.in' in [x.get_internal_path() for x in t.sources]

        sub = env.fs.Dir('sub')
        t = env.Command(target='bar.out', source='sub',
                        action='buildbar $target $source')[0]
        assert 'sub' in [x.get_internal_path() for x in t.sources]

        def testFunc(env, target, source) -> int:
            assert str(target[0]) == 'foo.out'
            srcs = list(map(str, source))
            assert 'foo1.in' in srcs and 'foo2.in' in srcs, srcs
            return 0

        # avoid spurious output from action
        act = env.Action(testFunc, cmdstr=None)
        t = env.Command(target='foo.out', source=['foo1.in','foo2.in'],
                        action=act)[0]
        assert t.builder is not None
        assert t.builder.action.__class__.__name__ == 'FunctionAction'
        t.build()
        assert 'foo1.in' in [x.get_internal_path() for x in t.sources]
        assert 'foo2.in' in [x.get_internal_path() for x in t.sources]

        x = []
        def test2(baz, x=x) -> None:
            x.append(baz)
        env = self.TestEnvironment(TEST2 = test2)
        t = env.Command(target='baz.out', source='baz.in',
                        action='${TEST2(XYZ)}',
                        XYZ='magic word')[0]
        assert t.builder is not None
        t.build()
        assert x[0] == 'magic word', x

        t = env.Command(target='${X}.out', source='${X}.in',
                        action = 'foo',
                        X = 'xxx')[0]
        assert str(t) == 'xxx.out', str(t)
        assert 'xxx.in' in [x.get_internal_path() for x in t.sources]

        env = self.TestEnvironment(source_scanner = 'should_not_find_this')
        t = env.Command(target='file.out', source='file.in',
                        action = 'foo',
                        source_scanner = 'fake')[0]
        assert t.builder.source_scanner == 'fake', t.builder.source_scanner

    def test_Configure(self) -> None:
        """Test the Configure() method"""
        # Configure() will write to a local temporary file.
        test = TestCmd.TestCmd(workdir = '')
        save = os.getcwd()

        try:
            os.chdir(test.workpath())

            env = self.TestEnvironment(FOO = 'xyzzy')

            def func(arg) -> None:
                pass

            c = env.Configure()
            assert c is not None, c
            c.Finish()

            c = env.Configure(custom_tests = {'foo' : func, '$FOO' : func})
            assert c is not None, c
            assert hasattr(c, 'foo')
            assert hasattr(c, 'xyzzy')
            c.Finish()
        finally:
            os.chdir(save)

    def test_Depends(self) -> None:
        """Test the explicit Depends method."""
        env = self.TestEnvironment(FOO = 'xxx', BAR='yyy')
        env.Dir('dir1')
        env.Dir('dir2')
        env.File('xxx.py')
        env.File('yyy.py')
        t = env.Depends(target='EnvironmentTest.py',
                        dependency='Environment.py')[0]
        assert t.__class__.__name__ == 'Entry', t.__class__.__name__
        assert t.get_internal_path() == 'EnvironmentTest.py'
        assert len(t.depends) == 1
        d = t.depends[0]
        assert d.__class__.__name__ == 'Entry', d.__class__.__name__
        assert d.get_internal_path() == 'Environment.py'

        t = env.Depends(target='${FOO}.py', dependency='${BAR}.py')[0]
        assert t.__class__.__name__ == 'File', t.__class__.__name__
        assert t.get_internal_path() == 'xxx.py'
        assert len(t.depends) == 1
        d = t.depends[0]
        assert d.__class__.__name__ == 'File', d.__class__.__name__
        assert d.get_internal_path() == 'yyy.py'

        t = env.Depends(target='dir1', dependency='dir2')[0]
        assert t.__class__.__name__ == 'Dir', t.__class__.__name__
        assert t.get_internal_path() == 'dir1'
        assert len(t.depends) == 1
        d = t.depends[0]
        assert d.__class__.__name__ == 'Dir', d.__class__.__name__
        assert d.get_internal_path() == 'dir2'

    def test_Dir(self) -> None:
        """Test the Dir() method"""
        class MyFS:
            def Dir(self, name) -> str:
                return 'Dir(%s)' % name

        env = self.TestEnvironment(FOO = 'foodir', BAR = 'bardir')
        env.fs = MyFS()

        d = env.Dir('d')
        assert d == 'Dir(d)', d

        d = env.Dir('$FOO')
        assert d == 'Dir(foodir)', d

        d = env.Dir('${BAR}_$BAR')
        assert d == 'Dir(bardir_bardir)', d

        d = env.Dir(['dir1'])
        assert d == ['Dir(dir1)'], d

        d = env.Dir(['dir1', 'dir2'])
        assert d == ['Dir(dir1)', 'Dir(dir2)'], d

    def test_NoClean(self) -> None:
        """Test the NoClean() method"""
        env = self.TestEnvironment(FOO='ggg', BAR='hhh')
        env.Dir('p_hhhb')
        env.File('p_d')
        t = env.NoClean('p_a', 'p_${BAR}b', ['p_c', 'p_d'], 'p_$FOO')

        assert t[0].__class__.__name__ == 'Entry', t[0].__class__.__name__
        assert t[0].get_internal_path() == 'p_a'
        assert t[0].noclean
        assert t[1].__class__.__name__ == 'Dir', t[1].__class__.__name__
        assert t[1].get_internal_path() == 'p_hhhb'
        assert t[1].noclean
        assert t[2].__class__.__name__ == 'Entry', t[2].__class__.__name__
        assert t[2].get_internal_path() == 'p_c'
        assert t[2].noclean
        assert t[3].__class__.__name__ == 'File', t[3].__class__.__name__
        assert t[3].get_internal_path() == 'p_d'
        assert t[3].noclean
        assert t[4].__class__.__name__ == 'Entry', t[4].__class__.__name__
        assert t[4].get_internal_path() == 'p_ggg'
        assert t[4].noclean

    def test_Dump(self) -> None:
        """Test the Dump() method"""
        env = self.TestEnvironment(FOO='foo', FOOFLAGS=CLVar('--bar --baz'))

        # changed in 4.9.0: single arg now displays as a dict,
        #   not a bare value; more than one arg is allowed.
        with self.subTest():  # one-arg version
            self.assertEqual(env.Dump('FOO'), "{'FOO': 'foo'}")

        with self.subTest():  # multi-arg version
            expect = "{'FOO': 'foo', 'FOOFLAGS': ['--bar', '--baz']}"
            self.assertEqual(env.Dump('FOO', 'FOOFLAGS'), expect)

        with self.subTest():  # no-arg version
            self.assertGreater(len(env.Dump()), 200)

        with self.subTest():  # one-arg JSON version, simple value
            expect = '{\n    "FOO": "foo"\n}'
            self.assertEqual(env.Dump('FOO', format='json'), expect)

        with self.subTest():  # one-arg JSON version, list value
            expect = '{\n    "FOOFLAGS": [\n        "--bar",\n        "--baz"\n    ]\n}'
            self.assertEqual(env.Dump('FOOFLAGS', format='json'), expect)

        with self.subTest():  # multi--arg JSON version, list value
            expect = '{\n    "FOO": "foo",\n    "FOOFLAGS": [\n        "--bar",\n        "--baz"\n    ]\n}'
            self.assertEqual(env.Dump('FOO', 'FOOFLAGS', format='json'), expect)

        with self.subTest():  # full JSON version
            import json
            env_dict = json.loads(env.Dump(format='json'))
            self.assertEqual(env_dict['FOO'], 'foo')

        with self.subTest():  # unsupported format type
            with self.assertRaises(ValueError) as cm:
                env.Dump(format='markdown')
            self.assertEqual(str(cm.exception), "Unsupported serialization format: markdown.")


    def test_Environment(self) -> None:
        """Test the Environment() method"""
        env = self.TestEnvironment(FOO = 'xxx', BAR = 'yyy')

        e2 = env.Environment(X = '$FOO', Y = '$BAR')
        assert e2['X'] == 'xxx', e2['X']
        assert e2['Y'] == 'yyy', e2['Y']

    def test_Execute(self) -> None:
        """Test the Execute() method"""

        class MyAction:
            def __init__(self, *args, **kw) -> None:
                self.args = args
            def __call__(self, target, source, env) -> str:
                return "%s executed" % self.args

        env = Environment()
        env.Action = MyAction

        result = env.Execute("foo")
        assert result == "foo executed", result

    def test_Entry(self) -> None:
        """Test the Entry() method"""
        class MyFS:
            def Entry(self, name) -> str:
                return 'Entry(%s)' % name

        env = self.TestEnvironment(FOO = 'fooentry', BAR = 'barentry')
        env.fs = MyFS()

        e = env.Entry('e')
        assert e == 'Entry(e)', e

        e = env.Entry('$FOO')
        assert e == 'Entry(fooentry)', e

        e = env.Entry('${BAR}_$BAR')
        assert e == 'Entry(barentry_barentry)', e

        e = env.Entry(['entry1'])
        assert e == ['Entry(entry1)'], e

        e = env.Entry(['entry1', 'entry2'])
        assert e == ['Entry(entry1)', 'Entry(entry2)'], e

    def test_File(self) -> None:
        """Test the File() method"""
        class MyFS:
            def File(self, name) -> str:
                return 'File(%s)' % name

        env = self.TestEnvironment(FOO = 'foofile', BAR = 'barfile')
        env.fs = MyFS()

        f = env.File('f')
        assert f == 'File(f)', f

        f = env.File('$FOO')
        assert f == 'File(foofile)', f

        f = env.File('${BAR}_$BAR')
        assert f == 'File(barfile_barfile)', f

        f = env.File(['file1'])
        assert f == ['File(file1)'], f

        f = env.File(['file1', 'file2'])
        assert f == ['File(file1)', 'File(file2)'], f

    def test_FindFile(self) -> None:
        """Test the FindFile() method"""
        env = self.TestEnvironment(FOO = 'fff', BAR = 'bbb')

        r = env.FindFile('foo', ['no_such_directory'])
        assert r is None, r

        # XXX

    def test_Flatten(self) -> None:
        """Test the Flatten() method"""
        env = Environment()
        l = env.Flatten([1])
        assert l == [1]
        l = env.Flatten([1, [2, [3, [4]]]])
        assert l == [1, 2, 3, 4], l

    def test_GetBuildPath(self) -> None:
        """Test the GetBuildPath() method."""
        env = self.TestEnvironment(MAGIC = 'xyzzy')

        p = env.GetBuildPath('foo')
        assert p == 'foo', p

        p = env.GetBuildPath('$MAGIC')
        assert p == 'xyzzy', p

    def test_Ignore(self) -> None:
        """Test the explicit Ignore method."""
        env = self.TestEnvironment(FOO='yyy', BAR='zzz')
        env.Dir('dir1')
        env.Dir('dir2')
        env.File('yyyzzz')
        env.File('zzzyyy')

        t = env.Ignore(target='targ.py', dependency='dep.py')[0]
        assert t.__class__.__name__ == 'Entry', t.__class__.__name__
        assert t.get_internal_path() == 'targ.py'
        assert len(t.ignore) == 1
        i = t.ignore[0]
        assert i.__class__.__name__ == 'Entry', i.__class__.__name__
        assert i.get_internal_path() == 'dep.py'

        t = env.Ignore(target='$FOO$BAR', dependency='$BAR$FOO')[0]
        assert t.__class__.__name__ == 'File', t.__class__.__name__
        assert t.get_internal_path() == 'yyyzzz'
        assert len(t.ignore) == 1
        i = t.ignore[0]
        assert i.__class__.__name__ == 'File', i.__class__.__name__
        assert i.get_internal_path() == 'zzzyyy'

        t = env.Ignore(target='dir1', dependency='dir2')[0]
        assert t.__class__.__name__ == 'Dir', t.__class__.__name__
        assert t.get_internal_path() == 'dir1'
        assert len(t.ignore) == 1
        i = t.ignore[0]
        assert i.__class__.__name__ == 'Dir', i.__class__.__name__
        assert i.get_internal_path() == 'dir2'

    def test_Literal(self) -> None:
        """Test the Literal() method"""
        env = self.TestEnvironment(FOO='fff', BAR='bbb')
        list = env.subst_list([env.Literal('$FOO'), '$BAR'])[0]
        assert list == ['$FOO', 'bbb'], list
        list = env.subst_list(['$FOO', env.Literal('$BAR')])[0]
        assert list == ['fff', '$BAR'], list

    def test_Local(self) -> None:
        """Test the Local() method."""
        env = self.TestEnvironment(FOO='lll')

        l = env.Local(env.fs.File('fff'))
        assert str(l[0]) == 'fff', l[0]

        l = env.Local('ggg', '$FOO')
        assert str(l[0]) == 'ggg', l[0]
        assert str(l[1]) == 'lll', l[1]

    def test_Precious(self) -> None:
        """Test the Precious() method"""
        env = self.TestEnvironment(FOO='ggg', BAR='hhh')
        env.Dir('p_hhhb')
        env.File('p_d')
        t = env.Precious('p_a', 'p_${BAR}b', ['p_c', 'p_d'], 'p_$FOO')

        assert t[0].__class__.__name__ == 'Entry', t[0].__class__.__name__
        assert t[0].get_internal_path() == 'p_a'
        assert t[0].precious
        assert t[1].__class__.__name__ == 'Dir', t[1].__class__.__name__
        assert t[1].get_internal_path() == 'p_hhhb'
        assert t[1].precious
        assert t[2].__class__.__name__ == 'Entry', t[2].__class__.__name__
        assert t[2].get_internal_path() == 'p_c'
        assert t[2].precious
        assert t[3].__class__.__name__ == 'File', t[3].__class__.__name__
        assert t[3].get_internal_path() == 'p_d'
        assert t[3].precious
        assert t[4].__class__.__name__ == 'Entry', t[4].__class__.__name__
        assert t[4].get_internal_path() == 'p_ggg'
        assert t[4].precious

    def test_Pseudo(self) -> None:
        """Test the Pseudo() method"""
        env = self.TestEnvironment(FOO='ggg', BAR='hhh')
        env.Dir('p_hhhb')
        env.File('p_d')
        t = env.Pseudo('p_a', 'p_${BAR}b', ['p_c', 'p_d'], 'p_$FOO')

        assert t[0].__class__.__name__ == 'Entry', t[0].__class__.__name__
        assert t[0].get_internal_path() == 'p_a'
        assert t[0].pseudo
        assert t[1].__class__.__name__ == 'Dir', t[1].__class__.__name__
        assert t[1].get_internal_path() == 'p_hhhb'
        assert t[1].pseudo
        assert t[2].__class__.__name__ == 'Entry', t[2].__class__.__name__
        assert t[2].get_internal_path() == 'p_c'
        assert t[2].pseudo
        assert t[3].__class__.__name__ == 'File', t[3].__class__.__name__
        assert t[3].get_internal_path() == 'p_d'
        assert t[3].pseudo
        assert t[4].__class__.__name__ == 'Entry', t[4].__class__.__name__
        assert t[4].get_internal_path() == 'p_ggg'
        assert t[4].pseudo

    def test_Repository(self) -> None:
        """Test the Repository() method."""
        class MyFS:
            def __init__(self) -> None:
                self.list = []
            def Repository(self, *dirs) -> None:
                self.list.extend(list(dirs))
            def Dir(self, name):
                return name
        env = self.TestEnvironment(FOO='rrr', BAR='sss')
        env.fs = MyFS()
        env.Repository('/tmp/foo')
        env.Repository('/tmp/$FOO', '/tmp/$BAR/foo')
        expect = ['/tmp/foo', '/tmp/rrr', '/tmp/sss/foo']
        assert env.fs.list == expect, env.fs.list

    def test_Scanner(self) -> None:
        """Test the Scanner() method"""
        def scan(node, env, target, arg) -> None:
            pass

        env = self.TestEnvironment(FOO = scan)

        s = env.Scanner('foo')
        assert s is not None, s

        s = env.Scanner(function = 'foo')
        assert s is not None, s

        if 0:
            s = env.Scanner('$FOO')
            assert s is not None, s

            s = env.Scanner(function = '$FOO')
            assert s is not None, s

    def test_SConsignFile(self) -> None:
        """Test the SConsignFile() method"""
        import SCons.SConsign

        class MyFS:
            SConstruct_dir = os.sep + 'dir'

        env = self.TestEnvironment(FOO = 'SConsign',
                          BAR = os.path.join(os.sep, 'File'))
        env.fs = MyFS()
        env.Execute = lambda action: None

        try:
            fnames = []
            dbms = []
            def capture(name, dbm_module, fnames=fnames, dbms=dbms) -> None:
                fnames.append(name)
                dbms.append(dbm_module)

            save_SConsign_File = SCons.SConsign.File
            SCons.SConsign.File = capture

            env.SConsignFile('foo')
            assert fnames[-1] == os.path.join(os.sep, 'dir', 'foo'), fnames
            assert dbms[-1] is None, dbms

            env.SConsignFile('$FOO')
            assert fnames[-1] == os.path.join(os.sep, 'dir', 'SConsign'), fnames
            assert dbms[-1] is None, dbms

            env.SConsignFile('/$FOO')
            assert fnames[-1] == os.sep + 'SConsign', fnames
            assert dbms[-1] is None, dbms

            env.SConsignFile(os.sep + '$FOO')
            assert fnames[-1] == os.sep + 'SConsign', fnames
            assert dbms[-1] is None, dbms

            env.SConsignFile('$BAR', 'x')
            assert fnames[-1] == os.path.join(os.sep, 'File'), fnames
            assert dbms[-1] == 'x', dbms

            env.SConsignFile('__$BAR', 7)
            assert fnames[-1] == os.path.join(os.sep, 'dir', '__', 'File'), fnames
            assert dbms[-1] == 7, dbms

            env.SConsignFile()
            assert fnames[-1] == os.path.join(os.sep, 'dir', current_sconsign_filename()), fnames
            assert dbms[-1] is None, dbms

            env.SConsignFile(None)
            assert fnames[-1] is None, fnames
            assert dbms[-1] is None, dbms
        finally:
            SCons.SConsign.File = save_SConsign_File

    def test_SideEffect(self) -> None:
        """Test the SideEffect() method"""
        env = self.TestEnvironment(LIB='lll', FOO='fff', BAR='bbb')
        env.File('mylll.pdb')
        env.Dir('mymmm.pdb')

        foo = env.Object('foo.obj', 'foo.cpp')[0]
        bar = env.Object('bar.obj', 'bar.cpp')[0]
        s = env.SideEffect('mylib.pdb', ['foo.obj', 'bar.obj'])
        assert len(s) == 1, len(s)
        s = s[0]
        assert s.__class__.__name__ == 'Entry', s.__class__.__name__
        assert s.get_internal_path() == 'mylib.pdb'
        assert s.side_effect
        assert foo.side_effects == [s]
        assert bar.side_effects == [s]

        fff = env.Object('fff.obj', 'fff.cpp')[0]
        bbb = env.Object('bbb.obj', 'bbb.cpp')[0]
        s = env.SideEffect('my${LIB}.pdb', ['${FOO}.obj', '${BAR}.obj'])
        assert len(s) == 1, len(s)
        s = s[0]
        assert s.__class__.__name__ == 'File', s.__class__.__name__
        assert s.get_internal_path() == 'mylll.pdb'
        assert s.side_effect
        assert fff.side_effects == [s], fff.side_effects
        assert bbb.side_effects == [s], bbb.side_effects

        ggg = env.Object('ggg.obj', 'ggg.cpp')[0]
        ccc = env.Object('ccc.obj', 'ccc.cpp')[0]
        s = env.SideEffect('mymmm.pdb', ['ggg.obj', 'ccc.obj'])
        assert len(s) == 1, len(s)
        s = s[0]
        assert s.__class__.__name__ == 'Dir', s.__class__.__name__
        assert s.get_internal_path() == 'mymmm.pdb'
        assert s.side_effect
        assert ggg.side_effects == [s], ggg.side_effects
        assert ccc.side_effects == [s], ccc.side_effects

        # Verify that duplicate side effects are not allowed.
        before = len(ggg.side_effects)
        s = env.SideEffect('mymmm.pdb', ggg)
        assert len(s) == 0, len(s)
        assert len(ggg.side_effects) == before, len(ggg.side_effects)

    def test_Split(self) -> None:
        """Test the Split() method"""
        env = self.TestEnvironment(FOO = 'fff', BAR = 'bbb')
        s = env.Split("foo bar")
        assert s == ["foo", "bar"], s
        s = env.Split("$FOO bar")
        assert s == ["fff", "bar"], s
        s = env.Split(["foo", "bar"])
        assert s == ["foo", "bar"], s
        s = env.Split(["foo", "${BAR}-bbb"])
        assert s == ["foo", "bbb-bbb"], s
        s = env.Split("foo")
        assert s == ["foo"], s
        s = env.Split("$FOO$BAR")
        assert s == ["fffbbb"], s


    def test_Value(self) -> None:
        """Test creating a Value() object
        """
        env = Environment()
        v1 = env.Value('a')
        assert v1.value == 'a', v1.value

        value2 = 'a'
        v2 = env.Value(value2)
        assert v2.value == value2, v2.value
        assert v2.value is value2, v2.value

        assert v1 is v2

        v3 = env.Value('c', 'build-c')
        assert v3.value == 'c', v3.value

        v4 = env.Value(b'\x00\x0F', name='name')
        assert v4.value == b'\x00\x0F', v4.value
        assert v4.name == 'name', v4.name


    def test_Environment_global_variable(self) -> None:
        """Test setting Environment variable to an Environment.Base subclass"""
        class MyEnv(SCons.Environment.Base):
            def xxx(self, string):
                return self.subst(string)

        SCons.Environment.Environment = MyEnv

        env = SCons.Environment.Environment(FOO = 'foo')

        f = env.subst('$FOO')
        assert f == 'foo', f

        f = env.xxx('$FOO')
        assert f == 'foo', f

    def test_bad_keywords(self) -> None:
        """Test trying to use reserved keywords in an Environment"""
        added = []

        env = self.TestEnvironment(TARGETS = 'targets',
                                   SOURCES = 'sources',
                                   SOURCE = 'source',
                                   TARGET = 'target',
                                   CHANGED_SOURCES = 'changed_sources',
                                   CHANGED_TARGETS = 'changed_targets',
                                   UNCHANGED_SOURCES = 'unchanged_sources',
                                   UNCHANGED_TARGETS = 'unchanged_targets',
                                   INIT = 'init')
        bad_msg = '%s is not reserved, but got omitted; see Environment.construction_var_name_ok'
        added.append('INIT')
        for x in self.reserved_variables:
            assert x not in env, env[x]
        for x in added:
            assert x in env, bad_msg % x

        env.Append(TARGETS = 'targets',
                   SOURCES = 'sources',
                   SOURCE = 'source',
                   TARGET = 'target',
                   CHANGED_SOURCES = 'changed_sources',
                   CHANGED_TARGETS = 'changed_targets',
                   UNCHANGED_SOURCES = 'unchanged_sources',
                   UNCHANGED_TARGETS = 'unchanged_targets',
                   APPEND = 'append')
        added.append('APPEND')
        for x in self.reserved_variables:
            assert x not in env, env[x]
        for x in added:
            assert x in env, bad_msg % x

        env.AppendUnique(TARGETS = 'targets',
                         SOURCES = 'sources',
                         SOURCE = 'source',
                         TARGET = 'target',
                         CHANGED_SOURCES = 'changed_sources',
                         CHANGED_TARGETS = 'changed_targets',
                         UNCHANGED_SOURCES = 'unchanged_sources',
                         UNCHANGED_TARGETS = 'unchanged_targets',
                         APPENDUNIQUE = 'appendunique')
        added.append('APPENDUNIQUE')
        for x in self.reserved_variables:
            assert x not in env, env[x]
        for x in added:
            assert x in env, bad_msg % x

        env.Prepend(TARGETS = 'targets',
                    SOURCES = 'sources',
                    SOURCE = 'source',
                    TARGET = 'target',
                    CHANGED_SOURCES = 'changed_sources',
                    CHANGED_TARGETS = 'changed_targets',
                    UNCHANGED_SOURCES = 'unchanged_sources',
                    UNCHANGED_TARGETS = 'unchanged_targets',
                    PREPEND = 'prepend')
        added.append('PREPEND')
        for x in self.reserved_variables:
            assert x not in env, env[x]
        for x in added:
            assert x in env, bad_msg % x

        env.Prepend(TARGETS = 'targets',
                    SOURCES = 'sources',
                    SOURCE = 'source',
                    TARGET = 'target',
                    CHANGED_SOURCES = 'changed_sources',
                    CHANGED_TARGETS = 'changed_targets',
                    UNCHANGED_SOURCES = 'unchanged_sources',
                    UNCHANGED_TARGETS = 'unchanged_targets',
                    PREPENDUNIQUE = 'prependunique')
        added.append('PREPENDUNIQUE')
        for x in self.reserved_variables:
            assert x not in env, env[x]
        for x in added:
            assert x in env, bad_msg % x

        env.Replace(TARGETS = 'targets',
                    SOURCES = 'sources',
                    SOURCE = 'source',
                    TARGET = 'target',
                    CHANGED_SOURCES = 'changed_sources',
                    CHANGED_TARGETS = 'changed_targets',
                    UNCHANGED_SOURCES = 'unchanged_sources',
                    UNCHANGED_TARGETS = 'unchanged_targets',
                    REPLACE = 'replace')
        added.append('REPLACE')
        for x in self.reserved_variables:
            assert x not in env, env[x]
        for x in added:
            assert x in env, bad_msg % x

        copy = env.Clone(TARGETS = 'targets',
                         SOURCES = 'sources',
                         SOURCE = 'source',
                         TARGET = 'target',
                         CHANGED_SOURCES = 'changed_sources',
                         CHANGED_TARGETS = 'changed_targets',
                         UNCHANGED_SOURCES = 'unchanged_sources',
                         UNCHANGED_TARGETS = 'unchanged_targets',
                         COPY = 'copy')
        for x in self.reserved_variables:
            assert x not in copy, env[x]
        for x in added + ['COPY']:
            assert x in copy, bad_msg % x

        over = env.Override({'TARGETS' : 'targets',
                             'SOURCES' : 'sources',
                             'SOURCE' : 'source',
                             'TARGET' : 'target',
                             'CHANGED_SOURCES' : 'changed_sources',
                             'CHANGED_TARGETS' : 'changed_targets',
                             'UNCHANGED_SOURCES' : 'unchanged_sources',
                             'UNCHANGED_TARGETS' : 'unchanged_targets',
                             'OVERRIDE' : 'override'})
        for x in self.reserved_variables:
            assert x not in over, over[x]
        for x in added + ['OVERRIDE']:
            assert x in over, bad_msg % x

    def test_parse_flags(self) -> None:
        """Test the Base class parse_flags argument"""
        # all we have to show is that it gets to MergeFlags internally
        env = Environment(tools=[], parse_flags = '-X')
        assert env['CCFLAGS'] == ['-X'], env['CCFLAGS']

        env = Environment(tools=[], CCFLAGS=None, parse_flags = '-Y')
        assert env['CCFLAGS'] == ['-Y'], env['CCFLAGS']

        env = Environment(tools=[], CPPDEFINES='FOO', parse_flags='-std=c99 -X -DBAR')
        assert env['CFLAGS']  == ['-std=c99'], env['CFLAGS']
        assert env['CCFLAGS'] == ['-X'], env['CCFLAGS']
        self.assertEqual(list(env['CPPDEFINES']), ['FOO', 'BAR'])

    def test_clone_parse_flags(self) -> None:
        """Test the env.Clone() parse_flags argument"""
        # all we have to show is that it gets to MergeFlags internally
        env = Environment(tools = [])
        env2 = env.Clone(parse_flags = '-X')
        assert 'CCFLAGS' not in env
        assert env2['CCFLAGS'] == ['-X'], env2['CCFLAGS']

        env = Environment(tools = [], CCFLAGS=None)
        env2 = env.Clone(parse_flags = '-Y')
        assert env['CCFLAGS'] is None, env['CCFLAGS']
        assert env2['CCFLAGS'] == ['-Y'], env2['CCFLAGS']

        env = Environment(tools = [], CPPDEFINES = 'FOO')
        env2 = env.Clone(parse_flags = '-std=c99 -X -DBAR')
        assert 'CFLAGS' not in env
        assert env2['CFLAGS']  == ['-std=c99'], env2['CFLAGS']
        assert 'CCFLAGS' not in env
        assert env2['CCFLAGS'] == ['-X'], env2['CCFLAGS']
        assert env['CPPDEFINES'] == 'FOO', env['CPPDEFINES']
        self.assertEqual(list(env2['CPPDEFINES']), ['FOO','BAR'])


class OverrideEnvironmentTestCase(unittest.TestCase,TestEnvironmentFixture):

    def setUp(self) -> None:
        env = Environment()
        env._dict = {'XXX' : 'x', 'YYY' : 'y'}

        def verify_value(env, key, value, *args, **kwargs) -> None:
            """Verifies that key is value on the env this is called with."""
            self.assertEqual(env[key], value)

        env.AddMethod(verify_value)
        # env2 does not overrride 'YYY' to test passthrough
        env2 = OverrideEnvironment(env, {'XXX' : 'x2'})
        # env3 overrides both, plus sets a new var 'ZZZ'
        env3 = OverrideEnvironment(env2, {'XXX' : 'x3', 'YYY' : 'y3', 'ZZZ' : 'z3'})
        self.envs = [env, env2, env3]

    def checkpath(self, node, expect):
        return str(node) == os.path.normpath(expect)

    def test___init__(self) -> None:
        """Test OverrideEnvironment initialization"""
        env, env2, env3 = self.envs

        with self.subTest():
            self.assertEqual(env['XXX'], 'x')
        with self.subTest():
            self.assertEqual(env2['XXX'], 'x2')
        with self.subTest():
            self.assertEqual(env3['XXX'], 'x3')
        with self.subTest():
            self.assertEqual(env['YYY'], 'y')
        with self.subTest():
            self.assertEqual(env2['YYY'], 'y')
        with self.subTest():
            self.assertEqual(env3['YYY'], 'y3')
        with self.subTest():
            self.assertNotIn('ZZZ', env)
        with self.subTest():
            self.assertNotIn('ZZZ', env2)
        with self.subTest():
            self.assertEqual(env3['ZZZ'], 'z3')

    def test___setitem__(self) -> None:
        """Test setting a variable does not leak through."""
        env, env2, env3 = self.envs
        env3['QQQ'] = 'q'
        with self.subTest():
            self.assertEqual(env3['QQQ'], 'q')
        with self.subTest():
            self.assertNotIn('QQQ', env2)
        with self.subTest():
            self.assertNotIn('QQQ', env)

    def test___delitem__(self) -> None:
        """Test deleting variables from an OverrideEnvironment"""
        env, env2, env3 = self.envs

        # changed in 4.9.0: delete does not cascade to underlying envs
        # XXX is in all three, del from env3 should affect only it
        del env3['XXX']
        with self.subTest():
            self.assertIn('XXX', env)
        with self.subTest():
            self.assertIn('XXX', env2)
        with self.subTest():
            self.assertNotIn('XXX', env3)

        # YYY unique in env and env3, shadowed in env2: env2 should still work.
        del env3['YYY']
        with self.subTest():
            self.assertIn('YYY', env)
        with self.subTest():
            self.assertEqual(env2['YYY'], 'y')
        with self.subTest():
            self.assertIn('YYY', env2)
        with self.subTest():
            self.assertNotIn('YYY', env3)

        # ZZZ is only in env3, none should have it
        del env3['ZZZ']
        with self.subTest():
            self.assertNotIn('ZZZ', env)
        with self.subTest():
            self.assertNotIn('ZZZ', env2)
        with self.subTest():
            self.assertNotIn('ZZZ', env3)

        # make sure we can write back after deletion
        env3['XXX'] = 'x4'
        with self.subTest():
            self.assertEqual(env3['XXX'], 'x4')
        with self.subTest():
            self.assertEqual(env2['XXX'], 'x2')
        with self.subTest():
            self.assertEqual(env['XXX'], 'x')

    def test_get(self) -> None:
        """Test the OverrideEnvironment get() method"""
        env, env2, env3 = self.envs
        assert env.get('XXX') == 'x', env.get('XXX')
        assert env2.get('XXX') == 'x2', env2.get('XXX')
        assert env3.get('XXX') == 'x3', env3.get('XXX')
        assert env.get('YYY') == 'y', env.get('YYY')
        assert env2.get('YYY') == 'y', env2.get('YYY')
        assert env3.get('YYY') == 'y3', env3.get('YYY')
        assert env.get('ZZZ') is None, env.get('ZZZ')
        assert env2.get('ZZZ') is None, env2.get('ZZZ')
        assert env3.get('ZZZ') == 'z3', env3.get('ZZZ')

    def test_contains(self) -> None:
        """Test the OverrideEnvironment __contains__() method"""
        env, env2, env3 = self.envs
        assert 'XXX' in env, 'XXX' in env
        assert 'XXX' in env2, 'XXX' in env2
        assert 'XXX' in env3, 'XXX' in env3
        assert 'YYY' in env, 'YYY' in env
        assert 'YYY' in env2, 'YYY' in env2
        assert 'YYY' in env3, 'YYY' in env3
        assert 'ZZZ' not in env, 'ZZZ' in env
        assert 'ZZZ' not in env2, 'ZZZ' in env2
        assert 'ZZZ' in env3, 'ZZZ' in env3

    def test_Dictionary(self) -> None:
        """Test the OverrideEnvironment Dictionary() method"""
        env, env2, env3 = self.envs
        # nothing overrriden
        items = env.Dictionary()
        assert items == {'XXX' : 'x', 'YYY' : 'y'}, items

        # env2 overrides XXX, YYY unchanged
        items = env2.Dictionary()
        assert items == {'XXX' : 'x2', 'YYY' : 'y'}, items

        # env3 overrides XXX, YYY, adds ZZZ
        items = env3.Dictionary()
        assert items == {'XXX' : 'x3', 'YYY' : 'y3', 'ZZZ' : 'z3'}, items

        # test one-arg and multi-arg Dictionary
        assert env3.Dictionary('XXX') == 'x3', env3.Dictionary('XXX')
        xxx, yyy = env2.Dictionary('XXX', 'YYY')
        assert xxx == 'x2', xxx
        assert yyy == 'y', yyy
        # added in NEXT_VERSION: as_dict flag
        with self.subTest():
            expect = {'XXX': 'x3'}
            self.assertEqual(env3.Dictionary('XXX', as_dict=True), expect)
        with self.subTest():
            expect = {'XXX': 'x2', 'YYY': 'y'}
            self.assertEqual(env2.Dictionary('XXX', 'YYY', as_dict=True), expect)

        # test deletion in top override
        del env3['XXX']
        self.assertRaises(KeyError, env3.Dictionary, 'XXX')
        # changed in 4.9.0: *not* deleted from underlying envs
        assert 'XXX' in env2.Dictionary()
        assert 'XXX' in env.Dictionary()


    def test_items(self) -> None:
        """Test the OverrideEnvironment items() method"""
        env, env2, env3 = self.envs
        items = sorted(env.items())
        assert items == [('XXX', 'x'), ('YYY', 'y')], items
        items = sorted(env2.items())
        assert items == [('XXX', 'x2'), ('YYY', 'y')], items
        items = sorted(env3.items())
        assert items == [('XXX', 'x3'), ('YYY', 'y3'), ('ZZZ', 'z3')], items

    def test_keys(self) -> None:
        """Test the OverrideEnvironment keys() method"""
        env, env2, env3 = self.envs
        keys = sorted(env.keys())
        assert keys == ['XXX', 'YYY'], keys
        keys = sorted(env2.keys())
        assert keys == ['XXX', 'YYY'], keys
        keys = sorted(env3.keys())
        assert keys == ['XXX', 'YYY', 'ZZZ'], keys

    def test_values(self) -> None:
        """Test the OverrideEnvironment values() method"""
        env, env2, env3 = self.envs
        values = sorted(env.values())
        assert values == ['x', 'y'], values
        values = sorted(env2.values())
        assert values == ['x2', 'y'], values
        values = sorted(env3.values())
        assert values == ['x3', 'y3', 'z3'], values

    def test_setdefault(self) -> None:
        """Test the OverrideEnvironment setdefault() method."""
        env, env2, env3 = self.envs
        # does not set for existing key
        assert env2.setdefault('XXX', 'z') == 'x2', env2['XXX']
        # set/return using default for non-existing key
        assert env2.setdefault('ZZZ', 'z2') == 'z2', env2['ZZZ']
        # set did not leak through to base env
        assert 'ZZZ' not in env

    def test_gvars(self) -> None:
        """Test the OverrideEnvironment gvars() method"""
        env, env2, env3 = self.envs
        gvars = env.gvars()
        assert gvars == {'XXX' : 'x', 'YYY' : 'y'}, gvars
        gvars = env2.gvars()
        assert gvars == {'XXX' : 'x', 'YYY' : 'y'}, gvars
        gvars = env3.gvars()
        assert gvars == {'XXX' : 'x', 'YYY' : 'y'}, gvars

    def test_lvars(self) -> None:
        """Test the OverrideEnvironment lvars() method"""
        env, env2, env3 = self.envs
        lvars = env.lvars()
        assert lvars == {}, lvars
        lvars = env2.lvars()
        assert lvars == {'XXX' : 'x2'}, lvars
        lvars = env3.lvars()
        assert lvars == {'XXX' : 'x3', 'YYY' : 'y3', 'ZZZ' : 'z3'}, lvars

    def test_Replace(self) -> None:
        """Test the OverrideEnvironment Replace() method"""
        env, env2, env3 = self.envs
        # initial state already proven by test___init__

        env.Replace(YYY='y4')
        assert env['XXX'] == 'x', env['XXX']
        assert env2['XXX'] == 'x2', env2['XXX']
        assert env3['XXX'] == 'x3', env3['XXX']
        assert env['YYY'] == 'y4', env['YYY']
        assert env2['YYY'] == 'y4', env2['YYY']
        assert env3['YYY'] == 'y3', env3['YYY']


    def test_Override_Leakage(self) -> None:
        """Test OverrideEnvironment modifying a variable for leakage."""
        env, env2, env3 = self.envs
        # initial state already proven by test___init__

        # string appending should be additive - only in the override
        env.Append(WWW='w')
        self.assertEqual(env2['WWW'], 'w')
        with self.subTest():
            env2.Append(WWW='w2')
            self.assertEqual(env2['WWW'], 'ww2')
            # did it leak?
            self.assertEqual(env['WWW'], 'w', "leak error")

        # append to a string already in the override
        self.assertEqual(env['XXX'], 'x')
        self.assertEqual(env2['XXX'], 'x2')
        with self.subTest():
            env2.Append(XXX='x4')
            self.assertEqual(env2['XXX'], 'x2x4')
            # did it leak?
            self.assertEqual(env['XXX'], 'x', "leak error")

        # add a new mutable key to base env, but copy it before modifying
        # This isn't a terribly interesting test, just shows that if you
        # "behave carefully", things don't leak.
        env.Append(QQQ=deque(['q1', 'q2', 'q3']))
        self.assertEqual(env2['QQQ'], deque(['q1', 'q2', 'q3']))
        with self.subTest():
            env2['QQQ'] = env2['QQQ'].copy()
            env2.Append(QQQ='q4')
            self.assertEqual(env2['QQQ'], deque(['q1', 'q2', 'q3', 'q4']))
            # did it leak?
            self.assertNotIn('q4', env['QQQ'], "leak error")


    @unittest.expectedFailure
    def test_Override_Mutable_Leakage(self) -> None:
        """Test OverrideEnvironment modifying a mutable variable for leakage.

        This is factored out from test_Override_Leakage as currently
        there is no way to prevent the leakage when updating a mutable
        element such as a list - thus it's marked as an xfail. This
        gives us something to come back to if we ever invent some sort
        of isolation via object copying, etc.
        """
        env, env2, env3 = self.envs
        # initial state already proven by test___init__

        # add a new key to base env, with a mutable value
        env.Append(QQQ=deque(['q1', 'q2', 'q3']))
        self.assertEqual(env2['QQQ'], deque(['q1', 'q2', 'q3']))
        with self.subTest():
            env2.Append(QQQ='q4')
            self.assertEqual(env2['QQQ'], deque(['q1', 'q2', 'q3', 'q4']))
            # did it leak?
            self.assertNotIn('q4', env['QQQ'], "leak error")


    # Tests a number of Base methods through an OverrideEnvironment to
    # make sure they handle overridden construction variables properly.
    #
    # The following Base methods also call self.subst(), and so could
    # theoretically be subject to problems with evaluating overridden
    # variables, but they're never really called that way in the rest
    # of our code, so we won't worry about them (at least for now):
    #
    # ParseConfig()
    # ParseDepends()
    # Platform()
    # Tool()
    #
    # Action()
    # Alias()
    # Builder()
    # CacheDir()
    # Configure()
    # Environment()
    # FindFile()
    # Scanner()

    # It's unlikely Clone() will ever be called this way, so let the
    # other methods test that handling overridden values works.
    #def test_Clone(self):
    #    """Test the OverrideEnvironment Clone() method"""
    #    pass

    def test_FindIxes(self) -> None:
        """Test the OverrideEnvironment FindIxes() method"""
        env, env2, env3 = self.envs
        x = env.FindIxes(['xaaay'], 'XXX', 'YYY')
        assert x == 'xaaay', x
        x = env2.FindIxes(['x2aaay'], 'XXX', 'YYY')
        assert x == 'x2aaay', x
        x = env3.FindIxes(['x3aaay3'], 'XXX', 'YYY')
        assert x == 'x3aaay3', x

    def test_ReplaceIxes(self) -> None:
        """Test the OverrideEnvironment ReplaceIxes() method"""
        env, env2, env3 = self.envs
        x = env.ReplaceIxes('xaaay', 'XXX', 'YYY', 'YYY', 'XXX')
        assert x == 'yaaax', x
        x = env2.ReplaceIxes('x2aaay', 'XXX', 'YYY', 'YYY', 'XXX')
        assert x == 'yaaax2', x
        x = env3.ReplaceIxes('x3aaay3', 'XXX', 'YYY', 'YYY', 'XXX')
        assert x == 'y3aaax3', x

    # It's unlikely WhereIs() will ever be called this way, so let the
    # other methods test that handling overridden values works.
    #def test_WhereIs(self):
    #    """Test the OverrideEnvironment WhereIs() method"""
    #    pass

    def test_PseudoBuilderInherits(self) -> None:
        """Test that pseudo-builders inherit the overrided values."""
        env, env2, env3 = self.envs
        env.verify_value('XXX', 'x')
        env2.verify_value('XXX', 'x2')
        env3.verify_value('XXX', 'x3')

    def test_Dir(self) -> None:
        """Test the OverrideEnvironment Dir() method"""
        env, env2, env3 = self.envs
        x = env.Dir('ddir/$XXX')
        assert self.checkpath(x, 'ddir/x'), str(x)
        x = env2.Dir('ddir/$XXX')
        assert self.checkpath(x, 'ddir/x2'), str(x)
        x = env3.Dir('ddir/$XXX')
        assert self.checkpath(x, 'ddir/x3'), str(x)

    def test_Entry(self) -> None:
        """Test the OverrideEnvironment Entry() method"""
        env, env2, env3 = self.envs
        x = env.Entry('edir/$XXX')
        assert self.checkpath(x, 'edir/x'), str(x)
        x = env2.Entry('edir/$XXX')
        assert self.checkpath(x, 'edir/x2'), str(x)
        x = env3.Entry('edir/$XXX')
        assert self.checkpath(x, 'edir/x3'), str(x)

    def test_File(self) -> None:
        """Test the OverrideEnvironment File() method"""
        env, env2, env3 = self.envs
        x = env.File('fdir/$XXX')
        assert self.checkpath(x, 'fdir/x'), str(x)
        x = env2.File('fdir/$XXX')
        assert self.checkpath(x, 'fdir/x2'), str(x)
        x = env3.File('fdir/$XXX')
        assert self.checkpath(x, 'fdir/x3'), str(x)

    def test_Split(self) -> None:
        """Test the OverrideEnvironment Split() method"""
        env, env2, env3 = self.envs
        env['AAA'] = '$XXX $YYY $ZZZ'
        x = env.Split('$AAA')
        assert x == ['x', 'y'], x
        x = env2.Split('$AAA')
        assert x == ['x2', 'y'], x
        x = env3.Split('$AAA')
        assert x == ['x3', 'y3', 'z3'], x

    def test_parse_flags(self) -> None:
        """Test the OverrideEnvironment parse_flags argument"""
        # all we have to show is that it gets to MergeFlags internally
        env = SubstitutionEnvironment()
        env2 = env.Override({'parse_flags' : '-X'})
        assert 'CCFLAGS' not in env
        assert env2['CCFLAGS'] == ['-X'], env2['CCFLAGS']

        env = SubstitutionEnvironment(CCFLAGS=None)
        env2 = env.Override({'parse_flags' : '-Y'})
        assert env['CCFLAGS'] is None, env['CCFLAGS']
        assert env2['CCFLAGS'] == ['-Y'], env2['CCFLAGS']

        env = SubstitutionEnvironment(CPPDEFINES='FOO')
        env2 = env.Override({'parse_flags': '-std=c99 -X -DBAR'})
        assert 'CFLAGS' not in env
        assert env2['CFLAGS']  == ['-std=c99'], env2['CFLAGS']
        assert 'CCFLAGS' not in env
        assert env2['CCFLAGS'] == ['-X'], env2['CCFLAGS']
        # make sure they are independent
        self.assertIsNot(env['CPPDEFINES'], env2['CPPDEFINES'])
        assert env['CPPDEFINES'] == 'FOO', env['CPPDEFINES']
        self.assertEqual(list(env2['CPPDEFINES']), ['FOO','BAR'])


class NoSubstitutionProxyTestCase(unittest.TestCase,TestEnvironmentFixture):

    def test___init__(self) -> None:
        """Test NoSubstitutionProxy initialization"""
        env = self.TestEnvironment(XXX = 'x', YYY = 'y')
        assert env['XXX'] == 'x', env['XXX']
        assert env['YYY'] == 'y', env['YYY']

        proxy = NoSubstitutionProxy(env)
        assert proxy['XXX'] == 'x', proxy['XXX']
        assert proxy['YYY'] == 'y', proxy['YYY']

    def test_attributes(self) -> None:
        """Test getting and setting NoSubstitutionProxy attributes"""
        env = Environment()
        setattr(env, 'env_attr', 'value1')

        proxy = NoSubstitutionProxy(env)
        setattr(proxy, 'proxy_attr', 'value2')

        x = getattr(env, 'env_attr')
        assert x == 'value1', x
        x = getattr(proxy, 'env_attr')
        assert x == 'value1', x

        x = getattr(env, 'proxy_attr')
        assert x == 'value2', x
        x = getattr(proxy, 'proxy_attr')
        assert x == 'value2', x

    def test_subst(self) -> None:
        """Test the NoSubstitutionProxy.subst() method"""
        env = self.TestEnvironment(XXX = 'x', YYY = 'y')
        assert env['XXX'] == 'x', env['XXX']
        assert env['YYY'] == 'y', env['YYY']

        proxy = NoSubstitutionProxy(env)
        assert proxy['XXX'] == 'x', proxy['XXX']
        assert proxy['YYY'] == 'y', proxy['YYY']

        x = env.subst('$XXX')
        assert x == 'x', x
        x = proxy.subst('$XXX')
        assert x == '$XXX', x

        x = proxy.subst('$YYY', raw=7, target=None, source=None,
                        conv=None,
                        extra_meaningless_keyword_argument=None)
        assert x == '$YYY', x

    def test_subst_kw(self) -> None:
        """Test the NoSubstitutionProxy.subst_kw() method"""
        env = self.TestEnvironment(XXX = 'x', YYY = 'y')
        assert env['XXX'] == 'x', env['XXX']
        assert env['YYY'] == 'y', env['YYY']

        proxy = NoSubstitutionProxy(env)
        assert proxy['XXX'] == 'x', proxy['XXX']
        assert proxy['YYY'] == 'y', proxy['YYY']

        x = env.subst_kw({'$XXX':'$YYY'})
        assert x == {'x':'y'}, x
        x = proxy.subst_kw({'$XXX':'$YYY'})
        assert x == {'$XXX':'$YYY'}, x

    def test_subst_list(self) -> None:
        """Test the NoSubstitutionProxy.subst_list() method"""
        env = self.TestEnvironment(XXX = 'x', YYY = 'y')
        assert env['XXX'] == 'x', env['XXX']
        assert env['YYY'] == 'y', env['YYY']

        proxy = NoSubstitutionProxy(env)
        assert proxy['XXX'] == 'x', proxy['XXX']
        assert proxy['YYY'] == 'y', proxy['YYY']

        x = env.subst_list('$XXX')
        assert x == [['x']], x
        x = proxy.subst_list('$XXX')
        assert x == [[]], x

        x = proxy.subst_list('$YYY', raw=0, target=None, source=None, conv=None)
        assert x == [[]], x

    def test_subst_target_source(self) -> None:
        """Test the NoSubstitutionProxy.subst_target_source() method"""
        env = self.TestEnvironment(XXX = 'x', YYY = 'y')
        assert env['XXX'] == 'x', env['XXX']
        assert env['YYY'] == 'y', env['YYY']

        proxy = NoSubstitutionProxy(env)
        assert proxy['XXX'] == 'x', proxy['XXX']
        assert proxy['YYY'] == 'y', proxy['YYY']

        args = ('$XXX $TARGET $SOURCE $YYY',)
        kw = {'target' : DummyNode('ttt'), 'source' : DummyNode('sss')}
        x = env.subst_target_source(*args, **kw)
        assert x == 'x ttt sss y', x
        x = proxy.subst_target_source(*args, **kw)
        assert x == ' ttt sss ', x


if __name__ == "__main__":
    unittest.main()
