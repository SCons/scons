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

import os
import string
import sys
import TestCmd
import unittest
import UserList

from SCons.Environment import *
import SCons.Warnings

def diff_env(env1, env2):
    s1 = "env1 = {\n"
    s2 = "env2 = {\n"
    d = {}
    for k in env1._dict.keys() + env2._dict.keys():
	d[k] = None
    keys = d.keys()
    keys.sort()
    for k in keys:
        if env1.has_key(k):
           if env2.has_key(k):
               if env1[k] != env2[k]:
                   s1 = s1 + "    " + repr(k) + " : " + repr(env1[k]) + "\n"
                   s2 = s2 + "    " + repr(k) + " : " + repr(env2[k]) + "\n"
           else:
               s1 = s1 + "    " + repr(k) + " : " + repr(env1[k]) + "\n"
        elif env2.has_key(k):
           s2 = s2 + "    " + repr(k) + " : " + repr(env2[k]) + "\n"
    s1 = s1 + "}\n"
    s2 = s2 + "}\n"
    return s1 + s2

def diff_dict(d1, d2):
    s1 = "d1 = {\n"
    s2 = "d2 = {\n"
    d = {}
    for k in d1.keys() + d2.keys():
	d[k] = None
    keys = d.keys()
    keys.sort()
    for k in keys:
        if d1.has_key(k):
           if d2.has_key(k):
               if d1[k] != d2[k]:
                   s1 = s1 + "    " + repr(k) + " : " + repr(d1[k]) + "\n"
                   s2 = s2 + "    " + repr(k) + " : " + repr(d2[k]) + "\n"
           else:
               s1 = s1 + "    " + repr(k) + " : " + repr(d1[k]) + "\n"
        elif env2.has_key(k):
           s2 = s2 + "    " + repr(k) + " : " + repr(d2[k]) + "\n"
    s1 = s1 + "}\n"
    s2 = s2 + "}\n"
    return s1 + s2

called_it = {}
built_it = {}

class Builder:
    """A dummy Builder class for testing purposes.  "Building"
    a target is simply setting a value in the dictionary.
    """
    def __init__(self, name = None):
        self.name = name

    def __call__(self, env, target=None, source=None, **kw):
        global called_it
        called_it['target'] = target
        called_it['source'] = source
        called_it.update(kw)

    def execute(self, target = None, **kw):
        global built_it
        built_it[target] = 1



scanned_it = {}

class Scanner:
    """A dummy Scanner class for testing purposes.  "Scanning"
    a target is simply setting a value in the dictionary.
    """
    def __init__(self, name, skeys=[]):
        self.name = name
        self.skeys = skeys

    def __call__(self, filename):
        global scanned_it
        scanned_it[filename] = 1

    def __cmp__(self, other):
        try:
            return cmp(self.__dict__, other.__dict__)
        except AttributeError:
            return 1

    def get_skeys(self, env):
        return self.skeys

    def __str__(self):
        return self.name



class CLVar(UserList.UserList):
    def __init__(self, seq):
        if type(seq) == type(''):
            seq = string.split(seq)
        UserList.UserList.__init__(self, seq)
    def __coerce__(self, other):
        return (self, CLVar(other))



class DummyNode:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name
    def rfile(self):
        return self
    def get_subst_proxy(self):
        return self



class SubstitutionTestCase(unittest.TestCase):

    def test___init__(self):
        """Test initializing a SubstitutionEnvironment
        """
        env = SubstitutionEnvironment()
        assert not env.has_key('__env__')

    def test___cmp__(self):
        """Test comparing SubstitutionEnvironments
        """

        env1 = SubstitutionEnvironment(XXX = 'x')
        env2 = SubstitutionEnvironment(XXX = 'x')
        env3 = SubstitutionEnvironment(XXX = 'xxx')
        env4 = SubstitutionEnvironment(XXX = 'x', YYY = 'x')

        assert env1 == env2
        assert env1 != env3
        assert env1 != env4

    def test___delitem__(self):
        """Test deleting a variable from a SubstitutionEnvironment
        """
        env1 = SubstitutionEnvironment(XXX = 'x', YYY = 'y')
        env2 = SubstitutionEnvironment(XXX = 'x')
        del env1['YYY']
        assert env1 == env2

    def test___getitem__(self):
        """Test deleting a variable from a SubstitutionEnvironment
        """
        env = SubstitutionEnvironment(XXX = 'x')
        assert env['XXX'] == 'x', env['XXX']

    def test___setitem__(self):
        """Test deleting a variable from a SubstitutionEnvironment
        """
        env1 = SubstitutionEnvironment(XXX = 'x')
        env2 = SubstitutionEnvironment(XXX = 'x', YYY = 'y')
        env1['YYY'] = 'y'
        assert env1 == env2

    def test_get(self):
        """Test the SubstitutionEnvironment get() method
        """
        env = SubstitutionEnvironment(XXX = 'x')
        assert env.get('XXX') == 'x', env.get('XXX')
        assert env.get('YYY') is None, env.get('YYY')

    def test_has_key(self):
        """Test the SubstitutionEnvironment has_key() method
        """
        env = SubstitutionEnvironment(XXX = 'x')
        assert env.has_key('XXX')
        assert not env.has_key('YYY')

    def test_items(self):
        """Test the SubstitutionEnvironment items() method
        """
        env = SubstitutionEnvironment(XXX = 'x', YYY = 'y')
        items = env.items()
        assert items == [('XXX','x'), ('YYY','y')], items

    def test_arg2nodes(self):
        """Test the arg2nodes method
        """
        env = SubstitutionEnvironment()
        dict = {}
        class X(SCons.Node.Node):
            pass
        def Factory(name, directory = None, create = 1, dict=dict, X=X):
            if not dict.has_key(name):
                dict[name] = X()
                dict[name].name = name
            return dict[name]

        nodes = env.arg2nodes("Util.py UtilTests.py", Factory)
        assert len(nodes) == 1, nodes
        assert isinstance(nodes[0], X)
        assert nodes[0].name == "Util.py UtilTests.py"

        import types
        if hasattr(types, 'UnicodeType'):
            code = """if 1:
                nodes = env.arg2nodes(u"Util.py UtilTests.py", Factory)
                assert len(nodes) == 1, nodes
                assert isinstance(nodes[0], X)
                assert nodes[0].name == u"Util.py UtilTests.py"
                \n"""
            exec code in globals(), locals()

        nodes = env.arg2nodes(["Util.py", "UtilTests.py"], Factory)
        assert len(nodes) == 2, nodes
        assert isinstance(nodes[0], X)
        assert isinstance(nodes[1], X)
        assert nodes[0].name == "Util.py"
        assert nodes[1].name == "UtilTests.py"

        n1 = Factory("Util.py")
        nodes = env.arg2nodes([n1, "UtilTests.py"], Factory)
        assert len(nodes) == 2, nodes
        assert isinstance(nodes[0], X)
        assert isinstance(nodes[1], X)
        assert nodes[0].name == "Util.py"
        assert nodes[1].name == "UtilTests.py"

        class SConsNode(SCons.Node.Node):
            pass
        nodes = env.arg2nodes(SConsNode())
        assert len(nodes) == 1, nodes
        assert isinstance(nodes[0], SConsNode), node

        class OtherNode:
            pass
        nodes = env.arg2nodes(OtherNode())
        assert len(nodes) == 1, nodes
        assert isinstance(nodes[0], OtherNode), node

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

    def test_gvars(self):
        """Test the base class gvars() method"""
        env = SubstitutionEnvironment()
        gvars = env.gvars()
        assert gvars == {}, gvars

    def test_lvars(self):
        """Test the base class lvars() method"""
        env = SubstitutionEnvironment()
        lvars = env.lvars()
        assert lvars == {}, lvars

    def test_subst(self):
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
            def bar(arg):
                pass

            env = SubstitutionEnvironment(BAR=bar, FOO='$BAR')

            subst = env.subst('$BAR', call=None)
            assert subst is bar, subst

            subst = env.subst('$FOO', call=None)
            assert subst is bar, subst

    def test_subst_kw(self):
        """Test substituting construction variables within dictionaries"""
        env = SubstitutionEnvironment(AAA = 'a', BBB = 'b')
        kw = env.subst_kw({'$AAA' : 'aaa', 'bbb' : '$BBB'})
        assert len(kw) == 2, kw
        assert kw['a'] == 'aaa', kw['a']
        assert kw['bbb'] == 'b', kw['bbb']

    def test_subst_list(self):
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
        assert l == [["c", "cA", "cB", "c"]], mystr

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
            def bar(arg):
                pass

            env = SubstitutionEnvironment(BAR=bar, FOO='$BAR')

            subst = env.subst_list('$BAR', call=None)
            assert subst is bar, subst

            subst = env.subst_list('$FOO', call=None)
            assert subst is bar, subst

    def test_subst_path(self):
        """Test substituting a path list
        """
        class MyProxy:
            def __init__(self, val):
                self.val = val
            def get(self):
                return self.val + '-proxy'

        class MyObj:
            pass

        env = SubstitutionEnvironment(FOO='foo', BAR='bar', PROXY=MyProxy('my1'))

        r = env.subst_path('$FOO')
        assert r == ['foo'], r

        r = env.subst_path(['$FOO', 'xxx', '$BAR'])
        assert r == ['foo', 'xxx', 'bar'], r

        n = MyObj()

        r = env.subst_path(['$PROXY', MyProxy('my2'), n])
        assert r == ['my1-proxy', 'my2-proxy', n], r

        class StringableObj:
            def __init__(self, s):
                self.s = s
            def __str__(self):
                return self.s

        env = SubstitutionEnvironment(FOO=StringableObj("foo"),
                          BAR=StringableObj("bar"))

        r = env.subst_path([ "${FOO}/bar", "${BAR}/baz" ])
        assert r == [ "foo/bar", "bar/baz" ]

        r = env.subst_path([ "bar/${FOO}", "baz/${BAR}" ])
        assert r == [ "bar/foo", "baz/bar" ]

        r = env.subst_path([ "bar/${FOO}/bar", "baz/${BAR}/baz" ])
        assert r == [ "bar/foo/bar", "baz/bar/baz" ]

    def test_subst_target_source(self):
        """Test the base environment subst_target_source() method"""
        env = SubstitutionEnvironment(AAA = 'a', BBB = 'b')
        mystr = env.subst_target_source("$AAA ${AAA}A $BBBB $BBB")
        assert mystr == "a aA b", mystr

    def test_Override(self):
        "Test overriding construction variables"
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



class BaseTestCase(unittest.TestCase):

    def test___init__(self):
        """Test construction Environment creation

        Create two with identical arguments and check that
        they compare the same.
        """
        env1 = Environment(XXX = 'x', YYY = 'y')
        env2 = Environment(XXX = 'x', YYY = 'y')
        assert env1 == env2, diff_env(env1, env2)

        assert not env1.has_key('__env__')
        assert not env2.has_key('__env__')

    def test_get(self):
        """Test the get() method."""
        env = Environment(aaa = 'AAA')

        x = env.get('aaa')
        assert x == 'AAA', x
        x = env.get('aaa', 'XXX')
        assert x == 'AAA', x
        x = env.get('bbb')
        assert x is None, x
        x = env.get('bbb', 'XXX')
        assert x == 'XXX', x

    def test_Builder_calls(self):
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
        assert called_it['target'] == None, called_it
        assert called_it['source'] == ['in1'], called_it

        called_it = {}
        env.builder2(source = 'in2', xyzzy = 1)
        assert called_it['target'] == None, called_it
        assert called_it['source'] == ['in2'], called_it
        assert called_it['xyzzy'] == 1, called_it

        called_it = {}
        env.builder1(foo = 'bar')
        assert called_it['foo'] == 'bar', called_it
        assert called_it['target'] == None, called_it
        assert called_it['source'] == None, called_it



    def test_Builder_execs(self):
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

        env4 = env3.Copy()
        assert env4.builder1.env is env4, "builder1.env (%s) == env3 (%s)?" % (env4.builder1.env, env3)
        assert env4.builder2.env is env4, "builder2.env (%s) == env3 (%s)?" % (env4.builder1.env, env3)

        # Now test BUILDERS as a dictionary.
        built_it = {}
        env5 = Environment(BUILDERS={ 'foo' : b1 })
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

    def test_Scanners(self):
        """Test setting SCANNERS in various ways

        One environment is initialized with a single
        Scanner object, one with a list of a single Scanner
        object, and one with a list of two Scanner objects.
        """
        global scanned_it

        s1 = Scanner(name = 'scanner1', skeys = [".c", ".cc"])
        s2 = Scanner(name = 'scanner2', skeys = [".m4"])
        s3 = Scanner(name = 'scanner3', skeys = [".m4", ".m5"])

#        XXX Tests for scanner execution through different environments,
#        XXX if we ever want to do that some day
#        scanned_it = {}
#        env1 = Environment(SCANNERS = s1)
#        env1.scanner1(filename = 'out1')
#        assert scanned_it['out1']
#
#        scanned_it = {}
#        env2 = Environment(SCANNERS = [s1])
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

        env = Environment(SCANNERS = [])
        s = map(env.get_scanner, suffixes)
        assert s == [None, None, None, None, None], s

        env.Replace(SCANNERS = [s1])
        s = map(env.get_scanner, suffixes)
        assert s == [s1, s1, None, None, None], s

        env.Append(SCANNERS = [s2])
        s = map(env.get_scanner, suffixes)
        assert s == [s1, s1, None, s2, None], s

        env.AppendUnique(SCANNERS = [s3])
        s = map(env.get_scanner, suffixes)
        assert s == [s1, s1, None, s2, s3], s

        env = env.Copy(SCANNERS = [s2])
        s = map(env.get_scanner, suffixes)
        assert s == [None, None, None, s2, None], s

        env['SCANNERS'] = [s1]
        s = map(env.get_scanner, suffixes)
        assert s == [s1, s1, None, None, None], s

        env.PrependUnique(SCANNERS = [s2, s1])
        s = map(env.get_scanner, suffixes)
        assert s == [s1, s1, None, s2, None], s

        env.Prepend(SCANNERS = [s3])
        s = map(env.get_scanner, suffixes)
        assert s == [s1, s1, None, s3, s3], s

    def test_ENV(self):
	"""Test setting the external ENV in Environments
	"""
	env = Environment()
	assert env.Dictionary().has_key('ENV')

	env = Environment(ENV = { 'PATH' : '/foo:/bar' })
	assert env.Dictionary('ENV')['PATH'] == '/foo:/bar'

    def test_ReservedVariables(self):
        """Test generation of warnings when reserved variable names
        are set in an environment."""

        SCons.Warnings.enableWarningClass(SCons.Warnings.ReservedVariableWarning)
        old = SCons.Warnings.warningAsException(1)

        try:
            env4 = Environment()
            for kw in ['TARGET', 'TARGETS', 'SOURCE', 'SOURCES']:
                exc_caught = None
                try:
                    env4[kw] = 'xyzzy'
                except SCons.Warnings.ReservedVariableWarning:
                    exc_caught = 1
                assert exc_caught, "Did not catch ReservedVariableWarning for `%s'" % kw
                assert not env4.has_key(kw), "`%s' variable was incorrectly set" % kw
        finally:
            SCons.Warnings.warningAsException(old)

    def test_IllegalVariables(self):
        """Test that use of illegal variables raises an exception"""
        env = Environment()
        def test_it(var, env=env):
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

    def test_autogenerate(dict):
        """Test autogenerating variables in a dictionary."""

        def RDirs(pathlist):
            return SCons.Node.FS.default_fs.Rsearchall(pathlist,
                                                       clazz=SCons.Node.FS.Dir,
                                                       must_exist=0,
                                                       cwd=SCons.Node.FS.default_fs.Dir('xx'))

        env = Environment(LIBS = [ 'foo', 'bar', 'baz' ],
                          LIBLINKPREFIX = 'foo',
                          LIBLINKSUFFIX = 'bar',
                          RDirs=RDirs)
        flags = env.subst_list('$_LIBFLAGS', 1)[0]
        assert len(flags) == 3, flags
        assert flags[0] == 'foobar', \
               flags[0]
        assert flags[1] == 'foobar', \
               flags[1]
        assert flags[2] == 'foobazbar', \
               flags[2]

        blat = SCons.Node.FS.default_fs.Dir('blat')

        env = Environment(CPPPATH = [ 'foo', '$FOO/bar', blat ],
                          INCPREFIX = 'foo ',
                          INCSUFFIX = 'bar',
                          FOO = 'baz',
                          RDirs=RDirs)
        flags = env.subst_list('$_CPPINCFLAGS', 1)[0]
        assert len(flags) == 8, flags
        assert flags[0] == '$(', \
               flags[0]
        assert flags[1] == os.path.normpath('foo'), \
               flags[1]
        assert flags[2] == os.path.normpath('xx/foobar'), \
               flags[2]
        assert flags[3] == os.path.normpath('foo'), \
               flags[3]
        assert flags[4] == os.path.normpath('xx/baz/bar'), \
               flags[4]
        assert flags[5] == os.path.normpath('foo'), \
               flags[5]
        assert flags[6] == os.path.normpath('blatbar'), \
               flags[6]
        assert flags[7] == '$)', \
               flags[7]

        env = Environment(F77PATH = [ 'foo', '$FOO/bar', blat ],
                          INCPREFIX = 'foo ',
                          INCSUFFIX = 'bar',
                          FOO = 'baz',
                          RDirs=RDirs)
        flags = env.subst_list('$_F77INCFLAGS', 1)[0]
        assert len(flags) == 8, flags
        assert flags[0] == '$(', \
               flags[0]
        assert flags[1] == os.path.normpath('foo'), \
               flags[1]
        assert flags[2] == os.path.normpath('xx/foobar'), \
               flags[2]
        assert flags[3] == os.path.normpath('foo'), \
               flags[3]
        assert flags[4] == os.path.normpath('xx/baz/bar'), \
               flags[4]
        assert flags[5] == os.path.normpath('foo'), \
               flags[5]
        assert flags[6] == os.path.normpath('blatbar'), \
               flags[6]
        assert flags[7] == '$)', \
               flags[7]

        env = Environment(CPPPATH = '', F77PATH = '', LIBPATH = '',
                          RDirs=RDirs)
        l = env.subst_list('$_CPPINCFLAGS')
        assert len(l[0]) == 0, l[0]
        l = env.subst_list('$_F77INCFLAGS')
        assert len(l[0]) == 0, l[0]
        l = env.subst_list('$_LIBDIRFLAGS')
        assert len(l[0]) == 0, l[0]

        SCons.Node.FS.default_fs.Repository('/rep1')
        SCons.Node.FS.default_fs.Repository('/rep2')
        env = Environment(CPPPATH = [ 'foo', '/a/b', '$FOO/bar', blat],
                          INCPREFIX = '-I ',
                          INCSUFFIX = 'XXX',
                          FOO = 'baz',
                          RDirs=RDirs)
        flags = env.subst_list('$_CPPINCFLAGS', 1)[0]
        assert flags[0] == '$(', \
               flags[0]
        assert flags[1] == '-I', \
               flags[1]
        assert flags[2] == os.path.normpath('xx/fooXXX'), \
               flags[2]
        assert flags[3] == '-I', \
               flags[3]
        assert flags[4] == os.path.normpath('/rep1/xx/fooXXX'), \
               flags[4]
        assert flags[5] == '-I', \
               flags[5]
        assert flags[6] == os.path.normpath('/rep2/xx/fooXXX'), \
               flags[6]
        assert flags[7] == '-I', \
               flags[7]
        assert flags[8] == os.path.normpath('/a/bXXX'), \
               flags[8]
        assert flags[9] == '-I', \
               flags[9]
        assert flags[10] == os.path.normpath('xx/baz/barXXX'), \
               flags[10]
        assert flags[11] == '-I', \
               flags[11]
        assert flags[12] == os.path.normpath('/rep1/xx/baz/barXXX'), \
               flags[12]
        assert flags[13] == '-I', \
               flags[13]
        assert flags[14] == os.path.normpath('/rep2/xx/baz/barXXX'), \
               flags[14]
        assert flags[15] == '-I', \
               flags[15]
        assert flags[16] == os.path.normpath('blatXXX'), \
               flags[16]
        assert flags[17] == '$)', \
               flags[17]

    def test_platform(self):
        """Test specifying a platform callable when instantiating."""
        class platform:
            def __str__(self):        return "TestPlatform"
            def __call__(self, env):  env['XYZZY'] = 777

        def tool(env):
            env['SET_TOOL'] = 'initialized'
            assert env['PLATFORM'] == "TestPlatform"

        env = Environment(platform = platform(), tools = [tool])
        assert env['XYZZY'] == 777, env
        assert env['PLATFORM'] == "TestPlatform"
        assert env['SET_TOOL'] == "initialized"

    def test_Default_PLATFORM(self):
        """Test overriding the default PLATFORM variable"""
        class platform:
            def __str__(self):        return "DefaultTestPlatform"
            def __call__(self, env):  env['XYZZY'] = 888

        def tool(env):
            env['SET_TOOL'] = 'abcde'
            assert env['PLATFORM'] == "DefaultTestPlatform"

        import SCons.Defaults
        save = SCons.Defaults.ConstructionEnvironment.copy()
        try:
            import SCons.Defaults
            SCons.Defaults.ConstructionEnvironment.update({
                'PLATFORM' : platform(),
            })
            env = Environment(tools = [tool])
            assert env['XYZZY'] == 888, env
            assert env['PLATFORM'] == "DefaultTestPlatform"
            assert env['SET_TOOL'] == "abcde"
        finally:
            SCons.Defaults.ConstructionEnvironment = save

    def test_tools(self):
        """Test specifying a tool callable when instantiating."""
        def t1(env):
            env['TOOL1'] = 111
        def t2(env):
            env['TOOL2'] = 222
        def t3(env):
            env['AAA'] = env['XYZ']
        def t4(env):
            env['TOOL4'] = 444
        env = Environment(tools = [t1, t2, t3], XYZ = 'aaa')
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
    return 1
""")

        env = Environment(tools = [('faketool', {'a':1, 'b':2, 'c':3})],
                          toolpath = [test.workpath('')])
        assert env['a'] == 1, env['a']
        assert env['b'] == 2, env['b']
        assert env['c'] == 3, env['c']

    def test_Default_TOOLS(self):
        """Test overriding the default TOOLS variable"""
        def t5(env):
            env['TOOL5'] = 555
        def t6(env):
            env['TOOL6'] = 666
        def t7(env):
            env['BBB'] = env['XYZ']
        def t8(env):
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

    def test_null_tools(self):
        """Test specifying a tool of None is OK."""
        def t1(env):
            env['TOOL1'] = 111
        def t2(env):
            env['TOOL2'] = 222
        env = Environment(tools = [t1, None, t2], XYZ = 'aaa')
        assert env['TOOL1'] == 111, env['TOOL1']
        assert env['TOOL2'] == 222, env
        assert env['XYZ'] == 'aaa', env
        env = Environment(tools = [None], XYZ = 'xyz')
        assert env['XYZ'] == 'xyz', env
        env = Environment(tools = [t1, '', t2], XYZ = 'ddd')
        assert env['TOOL1'] == 111, env['TOOL1']
        assert env['TOOL2'] == 222, env
        assert env['XYZ'] == 'ddd', env

    def test_concat(self):
        "Test _concat()"
        e1 = Environment(PRE='pre', SUF='suf', STR='a b', LIST=['a', 'b'])
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

    def test_gvars(self):
        """Test the Environment gvars() method"""
        env = Environment(XXX = 'x', YYY = 'y', ZZZ = 'z')
        gvars = env.gvars()
        assert gvars['XXX'] == 'x', gvars['XXX']
        assert gvars['YYY'] == 'y', gvars['YYY']
        assert gvars['ZZZ'] == 'z', gvars['ZZZ']

    def test__update(self):
        """Test the _update() method"""
        env = Environment(X = 'x', Y = 'y', Z = 'z')
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



    def test_Append(self):
        """Test appending to construction variables in an Environment
        """

        b1 = Environment()['BUILDERS']
        b2 = Environment()['BUILDERS']
        assert b1 == b2, diff_dict(b1, b2)

        import UserList
        UL = UserList.UserList

        cases = [
            'a1',       'A1',           'a1A1',
            'a2',       ['A2'],         ['a2', 'A2'],
            'a3',       UL(['A3']),     UL(['a', '3', 'A3']),
            'a4',       '',             'a4',
            'a5',       [],             ['a5'],
            'a6',       UL([]),         UL(['a', '6']),
            'a7',       [''],           ['a7', ''],
            'a8',       UL(['']),       UL(['a', '8', '']),

            ['e1'],     'E1',           ['e1', 'E1'],
            ['e2'],     ['E2'],         ['e2', 'E2'],
            ['e3'],     UL(['E3']),     UL(['e3', 'E3']),
            ['e4'],     '',             ['e4'],
            ['e5'],     [],             ['e5'],
            ['e6'],     UL([]),         UL(['e6']),
            ['e7'],     [''],           ['e7', ''],
            ['e8'],     UL(['']),       UL(['e8', '']),

            UL(['i1']), 'I1',           UL(['i1', 'I', '1']),
            UL(['i2']), ['I2'],         UL(['i2', 'I2']),
            UL(['i3']), UL(['I3']),     UL(['i3', 'I3']),
            UL(['i4']), '',             UL(['i4']),
            UL(['i5']), [],             UL(['i5']),
            UL(['i6']), UL([]),         UL(['i6']),
            UL(['i7']), [''],           UL(['i7', '']),
            UL(['i8']), UL(['']),       UL(['i8', '']),

            '',         'M1',           'M1',
            '',         ['M2'],         ['M2'],
            '',         UL(['M3']),     UL(['M3']),
            '',         '',             '',
            '',         [],             [],
            '',         UL([]),         UL([]),
            '',         [''],           [''],
            '',         UL(['']),       UL(['']),

            [],         'N1',           ['N1'],
            [],         ['N2'],         ['N2'],
            [],         UL(['N3']),     UL(['N3']),
            [],         '',             [],
            [],         [],             [],
            [],         UL([]),         UL([]),
            [],         [''],           [''],
            [],         UL(['']),       UL(['']),

            UL([]),     'O1',           ['O', '1'],
            UL([]),     ['O2'],         ['O2'],
            UL([]),     UL(['O3']),     UL(['O3']),
            UL([]),     '',             UL([]),
            UL([]),     [],             UL([]),
            UL([]),     UL([]),         UL([]),
            UL([]),     [''],           UL(['']),
            UL([]),     UL(['']),       UL(['']),

            [''],       'P1',           ['', 'P1'],
            [''],       ['P2'],         ['', 'P2'],
            [''],       UL(['P3']),     UL(['', 'P3']),
            [''],       '',             [''],
            [''],       [],             [''],
            [''],       UL([]),         UL(['']),
            [''],       [''],           ['', ''],
            [''],       UL(['']),       UL(['', '']),

            UL(['']),   'Q1',           ['', 'Q', '1'],
            UL(['']),   ['Q2'],         ['', 'Q2'],
            UL(['']),   UL(['Q3']),     UL(['', 'Q3']),
            UL(['']),   '',             UL(['']),
            UL(['']),   [],             UL(['']),
            UL(['']),   UL([]),         UL(['']),
            UL(['']),   [''],           UL(['', '']),
            UL(['']),   UL(['']),       UL(['', '']),
        ]

        env = Environment()
        failed = 0
        while cases:
            input, append, expect = cases[:3]
            env['XXX'] = input
            env.Append(XXX = append)
            result = env['XXX']
            if result != expect:
                if failed == 0: print
                print "    %s Append %s => %s did not match %s" % \
                      (repr(input), repr(append), repr(result), repr(expect))
                failed = failed + 1
            del cases[:3]
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
            def __init__(self, name):
                self.name = name
            def __str__(self):
                return self.name
            def __cmp__(self, other):
                raise "should not compare"

        ccc = C('ccc')

        env2 = Environment(CCC1 = ['c1'], CCC2 = ccc)
        env2.Append(CCC1 = ccc, CCC2 = ['c2'])
        assert env2['CCC1'][0] == 'c1', env2['CCC1']
        assert env2['CCC1'][1] is ccc, env2['CCC1']
        assert env2['CCC2'][0] is ccc, env2['CCC2']
        assert env2['CCC2'][1] == 'c2', env2['CCC2']

        env3 = Environment(X = {'x1' : 7})
        env3.Append(X = {'x1' : 8, 'x2' : 9}, Y = {'y1' : 10})
        assert env3['X'] == {'x1': 8, 'x2': 9}, env3['X']
        assert env3['Y'] == {'y1': 10}, env3['Y']

        env4 = Environment(BUILDERS = {'z1' : 11})
        env4.Append(BUILDERS = {'z2' : 12})
        assert env4['BUILDERS'] == {'z1' : 11, 'z2' : 12}, env4['BUILDERS']
        assert hasattr(env4, 'z1')
        assert hasattr(env4, 'z2')

    def test_AppendENVPath(self):
        """Test appending to an ENV path."""
        env1 = Environment(ENV = {'PATH': r'C:\dir\num\one;C:\dir\num\two'},
                           MYENV = {'MYPATH': r'C:\mydir\num\one;C:\mydir\num\two'})
        # have to include the pathsep here so that the test will work on UNIX too.
        env1.AppendENVPath('PATH',r'C:\dir\num\two', sep = ';')
        env1.AppendENVPath('PATH',r'C:\dir\num\three', sep = ';')
        env1.AppendENVPath('MYPATH',r'C:\mydir\num\three','MYENV', sep = ';')
        env1.AppendENVPath('MYPATH',r'C:\mydir\num\one','MYENV', sep = ';')
        assert(env1['ENV']['PATH'] == r'C:\dir\num\one;C:\dir\num\two;C:\dir\num\three')
        assert(env1['MYENV']['MYPATH'] == r'C:\mydir\num\two;C:\mydir\num\three;C:\mydir\num\one')

    def test_AppendUnique(self):
        """Test appending to unique values to construction variables

        This strips values that are already present when lists are
        involved."""
        env = Environment(AAA1 = 'a1',
                          AAA2 = 'a2',
                          AAA3 = 'a3',
                          BBB1 = ['b1'],
                          BBB2 = ['b2'],
                          BBB3 = ['b3'],
                          CCC1 = '',
                          CCC2 = '')
        env.AppendUnique(AAA1 = 'a1',
                         AAA2 = ['a2'],
                         AAA3 = ['a3', 'b', 'c', 'a3'],
                         BBB1 = 'b1',
                         BBB2 = ['b2'],
                         BBB3 = ['b3', 'c', 'd', 'b3'],
                         CCC1 = 'c1',
                         CCC2 = ['c2'])

        assert env['AAA1'] == 'a1a1', env['AAA1']
        assert env['AAA2'] == ['a2'], env['AAA2']
        assert env['AAA3'] == ['a3', 'b', 'c'], env['AAA3']
        assert env['BBB1'] == ['b1'], env['BBB1']
        assert env['BBB2'] == ['b2'], env['BBB2']
        assert env['BBB3'] == ['b3', 'c', 'd'], env['BBB3']
        assert env['CCC1'] == 'c1', env['CCC1']
        assert env['CCC2'] == ['c2'], env['CCC2']

    def test_Copy(self):
        """Test construction Environment copying

        Update the copy independently afterwards and check that
        the original remains intact (that is, no dangling
        references point to objects in the copied environment).
        Copy the original with some construction variable
        updates and check that the original remains intact
        and the copy has the updated values.
        """
        env1 = Environment(XXX = 'x', YYY = 'y')
        env2 = env1.Copy()
        env1copy = env1.Copy()
        assert env1copy == env1copy
        assert env2 == env2
        env2.Replace(YYY = 'yyy')
        assert env2 == env2
        assert env1 != env2
        assert env1 == env1copy

        env3 = env1.Copy(XXX = 'x3', ZZZ = 'z3')
        assert env3 == env3
        assert env3.Dictionary('XXX') == 'x3'
        assert env3.Dictionary('YYY') == 'y'
        assert env3.Dictionary('ZZZ') == 'z3'
        assert env1 == env1copy

        # Ensure that lists and dictionaries are
        # deep copied, but not instances.
        class TestA:
            pass
        env1 = Environment(XXX=TestA(), YYY = [ 1, 2, 3 ],
                           ZZZ = { 1:2, 3:4 })
        env2=env1.Copy()
        env2.Dictionary('YYY').append(4)
        env2.Dictionary('ZZZ')[5] = 6
        assert env1.Dictionary('XXX') is env2.Dictionary('XXX')
        assert 4 in env2.Dictionary('YYY')
        assert not 4 in env1.Dictionary('YYY')
        assert env2.Dictionary('ZZZ').has_key(5)
        assert not env1.Dictionary('ZZZ').has_key(5)

        #
        env1 = Environment(BUILDERS = {'b1' : 1})
        assert hasattr(env1, 'b1'), "env1.b1 was not set"
        assert env1.b1.env == env1, "b1.env doesn't point to env1"
        env2 = env1.Copy(BUILDERS = {'b2' : 2})
        assert env2 is env2
        assert env2 == env2
        assert hasattr(env1, 'b1'), "b1 was mistakenly cleared from env1"
        assert env1.b1.env == env1, "b1.env was changed"
        assert not hasattr(env2, 'b1'), "b1 was not cleared from env2"
        assert hasattr(env2, 'b2'), "env2.b2 was not set"
        assert env2.b2.env == env2, "b2.env doesn't point to env2"

        # Ensure that specifying new tools in a copied environment
        # works.
        def foo(env): env['FOO'] = 1
        def bar(env): env['BAR'] = 2
        def baz(env): env['BAZ'] = 3
        env1 = Environment(tools=[foo])
        env2 = env1.Copy()
        env3 = env1.Copy(tools=[bar, baz])

        assert env1.get('FOO') is 1
        assert env1.get('BAR') is None
        assert env1.get('BAZ') is None
        assert env2.get('FOO') is 1
        assert env2.get('BAR') is None
        assert env2.get('BAZ') is None
        assert env3.get('FOO') is 1
        assert env3.get('BAR') is 2
        assert env3.get('BAZ') is 3

        # Ensure that recursive variable substitution when copying
        # environments works properly.
        env1 = Environment(CCFLAGS = '-DFOO', XYZ = '-DXYZ')
        env2 = env1.Copy(CCFLAGS = '$CCFLAGS -DBAR',
                         XYZ = ['-DABC', 'x $XYZ y', '-DDEF'])
        x = env2.get('CCFLAGS')
        assert x == '-DFOO -DBAR', x
        x = env2.get('XYZ')
        assert x == ['-DABC', 'x -DXYZ y', '-DDEF'], x

        # Ensure that special properties of a class don't get
        # lost on copying.
        env1 = Environment(FLAGS = CLVar('flag1 flag2'))
        x = env1.get('FLAGS')
        assert x == ['flag1', 'flag2'], x
        env2 = env1.Copy()
        env2.Append(FLAGS = 'flag3 flag4')
        x = env2.get('FLAGS')
        assert x == ['flag1', 'flag2', 'flag3', 'flag4'], x

    def test_Detect(self):
        """Test Detect()ing tools"""
        test = TestCmd.TestCmd(workdir = '')
        test.subdir('sub1', 'sub2')
        sub1 = test.workpath('sub1')
        sub2 = test.workpath('sub2')

        if sys.platform == 'win32':
            test.write(['sub1', 'xxx'], "sub1/xxx\n")
            test.write(['sub2', 'xxx'], "sub2/xxx\n")

            env = Environment(ENV = { 'PATH' : [sub1, sub2] })

            x = env.Detect('xxx.exe')
            assert x is None, x

            test.write(['sub2', 'xxx.exe'], "sub2/xxx.exe\n")

            env = Environment(ENV = { 'PATH' : [sub1, sub2] })

            x = env.Detect('xxx.exe')
            assert x == 'xxx.exe', x

            test.write(['sub1', 'xxx.exe'], "sub1/xxx.exe\n")

            x = env.Detect('xxx.exe')
            assert x == 'xxx.exe', x

        else:
            test.write(['sub1', 'xxx.exe'], "sub1/xxx.exe\n")
            test.write(['sub2', 'xxx.exe'], "sub2/xxx.exe\n")

            env = Environment(ENV = { 'PATH' : [sub1, sub2] })

            x = env.Detect('xxx.exe')
            assert x is None, x

            sub2_xxx_exe = test.workpath('sub2', 'xxx.exe')
            os.chmod(sub2_xxx_exe, 0755)

            env = Environment(ENV = { 'PATH' : [sub1, sub2] })

            x = env.Detect('xxx.exe')
            assert x == 'xxx.exe', x

            sub1_xxx_exe = test.workpath('sub1', 'xxx.exe')
            os.chmod(sub1_xxx_exe, 0755)

            x = env.Detect('xxx.exe')
            assert x == 'xxx.exe', x

        env = Environment(ENV = { 'PATH' : [] })
        x = env.Detect('xxx.exe')
        assert x is None, x

    def test_Dictionary(self):
	"""Test retrieval of known construction variables

	Fetch them from the Dictionary and check for well-known
	defaults that get inserted.
	"""
	env = Environment(XXX = 'x', YYY = 'y', ZZZ = 'z')
	assert env.Dictionary('XXX') == 'x'
	assert env.Dictionary('YYY') == 'y'
	assert env.Dictionary('XXX', 'ZZZ') == ['x', 'z']
	xxx, zzz = env.Dictionary('XXX', 'ZZZ')
	assert xxx == 'x'
	assert zzz == 'z'
	assert env.Dictionary().has_key('BUILDERS')
	assert env.Dictionary().has_key('CC')
	assert env.Dictionary().has_key('CCFLAGS')
	assert env.Dictionary().has_key('ENV')

	assert env['XXX'] == 'x'
	env['XXX'] = 'foo'
	assert env.Dictionary('XXX') == 'foo'
	del env['XXX']
	assert not env.Dictionary().has_key('XXX')

    def test_FindIxes(self):
        "Test FindIxes()"
        env = Environment(LIBPREFIX='lib',
                          LIBSUFFIX='.a',
                          SHLIBPREFIX='lib',
                          SHLIBSUFFIX='.so',
                          PREFIX='pre',
                          SUFFIX='post')

        paths = [os.path.join('dir', 'libfoo.a'),
                 os.path.join('dir', 'libfoo.so')]

        assert paths[0] == env.FindIxes(paths, 'LIBPREFIX', 'LIBSUFFIX')
        assert paths[1] == env.FindIxes(paths, 'SHLIBPREFIX', 'SHLIBSUFFIX')
        assert None == env.FindIxes(paths, 'PREFIX', 'POST')

        paths = ['libfoo.a', 'prefoopost']

        assert paths[0] == env.FindIxes(paths, 'LIBPREFIX', 'LIBSUFFIX')
        assert None == env.FindIxes(paths, 'SHLIBPREFIX', 'SHLIBSUFFIX')
        assert paths[1] == env.FindIxes(paths, 'PREFIX', 'SUFFIX')

    def test_ParseConfig(self):
        """Test the ParseConfig() method"""
        env = Environment(ASFLAGS='assembler',
                          COMMAND='command',
                          CPPFLAGS=[''],
                          CPPPATH='string',
                          LIBPATH=['list'],
                          LIBS='',
                          LINKFLAGS=[''],
                          CCFLAGS=[''])
        orig_popen = os.popen
        class my_popen:
            def __init__(self, save_command, output):
                self.save_command = save_command
                self.output = output
            def __call__(self, command):
                self.save_command.append(command)
                class fake_file:
                    def __init__(self, output):
                        self.output = output
                    def read(self):
                        return self.output
                return fake_file(self.output)
        try:
            save_command = []
            os.popen = my_popen(save_command, 
                                 "-I/usr/include/fum -I bar -X\n" + \
                                 "-L/usr/fax -L foo -lxxx -l yyy " + \
                                 "-Wa,-as -Wl,-link -Wp,-cpp abc " + \
                                 "-pthread -framework Carbon " + \
                                 "-mno-cygwin -mwindows")
            env.ParseConfig("fake $COMMAND")
            assert save_command == ['fake command'], save_command
            assert env['ASFLAGS'] == ['assembler', '-Wa,-as'], env['ASFLAGS']
            assert env['CPPPATH'] == ['string', '/usr/include/fum', 'bar'], env['CPPPATH']
            assert env['CPPFLAGS'] == ['', '-Wp,-cpp'], env['CPPFLAGS']
            assert env['LIBPATH'] == ['list', '/usr/fax', 'foo'], env['LIBPATH']
            assert env['LIBS'] == ['xxx', 'yyy', env.File('abc')], env['LIBS']
            assert env['LINKFLAGS'] == ['', '-Wl,-link', '-pthread', '-framework', 'Carbon', '-mno-cygwin', '-mwindows'], env['LINKFLAGS']
            assert env['CCFLAGS'] == ['', '-X', '-pthread', '-mno-cygwin'], env['CCFLAGS']

            os.popen = my_popen([], "-Ibar")
            env.ParseConfig("fake2")
            assert env['CPPPATH'] == ['string', '/usr/include/fum', 'bar'], env['CPPPATH']
            env.ParseConfig("fake2", unique=0)
            assert env['CPPPATH'] == ['string', '/usr/include/fum', 'bar', 'bar'], env['CPPPATH']
        finally:
            os.popen = orig_popen

    def test_ParseDepends(self):
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

        env = Environment(SINGLE = test.workpath('single'))

        tlist = []
        dlist = []
        def my_depends(target, dependency, tlist=tlist, dlist=dlist):
            tlist.extend(target)
            dlist.extend(dependency)

        env.Depends = my_depends

        env.ParseDepends(test.workpath('does_not_exist'))

        exc_caught = None
        try:
            env.ParseDepends(test.workpath('does_not_exist'), must_exist=1)
        except IOError:
            exc_caught = 1
        assert exc_caught, "did not catch expected IOError"

        del tlist[:]
        del dlist[:]

        env.ParseDepends('$SINGLE', only_one=1)
        t = map(str, tlist)
        d = map(str, dlist)
        assert t == ['f0'], t
        assert d == ['d1', 'd2', 'd3'], d

        del tlist[:]
        del dlist[:]

        env.ParseDepends(test.workpath('multiple'))
        t = map(str, tlist)
        d = map(str, dlist)
        assert t == ['f1', 'f2', 'f3', 'f4', 'f5'], t
        assert d == ['foo', 'bar', 'abc', 'def', 'ghi', 'jkl', 'mno'], d

        exc_caught = None
        try:
            env.ParseDepends(test.workpath('multiple'), only_one=1)
        except SCons.Errors.UserError:
            exc_caught = 1
        assert exc_caught, "did not catch expected UserError"

    def test_Platform(self):
        """Test the Platform() method"""
        env = Environment(WIN32='win32', NONE='no-such-platform')

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

    def test_Prepend(self):
        """Test prepending to construction variables in an Environment
        """
        import UserList
        UL = UserList.UserList

        cases = [
            'a1',       'A1',           'A1a1',
            'a2',       ['A2'],         ['A2', 'a2'],
            'a3',       UL(['A3']),     UL(['A3', 'a', '3']),
            'a4',       '',             'a4',
            'a5',       [],             ['a5'],
            'a6',       UL([]),         UL(['a', '6']),
            'a7',       [''],           ['', 'a7'],
            'a8',       UL(['']),       UL(['', 'a', '8']),

            ['e1'],     'E1',           ['E1', 'e1'],
            ['e2'],     ['E2'],         ['E2', 'e2'],
            ['e3'],     UL(['E3']),     UL(['E3', 'e3']),
            ['e4'],     '',             ['e4'],
            ['e5'],     [],             ['e5'],
            ['e6'],     UL([]),         UL(['e6']),
            ['e7'],     [''],           ['', 'e7'],
            ['e8'],     UL(['']),       UL(['', 'e8']),

            UL(['i1']), 'I1',           UL(['I', '1', 'i1']),
            UL(['i2']), ['I2'],         UL(['I2', 'i2']),
            UL(['i3']), UL(['I3']),     UL(['I3', 'i3']),
            UL(['i4']), '',             UL(['i4']),
            UL(['i5']), [],             UL(['i5']),
            UL(['i6']), UL([]),         UL(['i6']),
            UL(['i7']), [''],           UL(['', 'i7']),
            UL(['i8']), UL(['']),       UL(['', 'i8']),

            '',         'M1',           'M1',
            '',         ['M2'],         ['M2'],
            '',         UL(['M3']),     UL(['M3']),
            '',         '',             '',
            '',         [],             [],
            '',         UL([]),         UL([]),
            '',         [''],           [''],
            '',         UL(['']),       UL(['']),

            [],         'N1',           ['N1'],
            [],         ['N2'],         ['N2'],
            [],         UL(['N3']),     UL(['N3']),
            [],         '',             [],
            [],         [],             [],
            [],         UL([]),         UL([]),
            [],         [''],           [''],
            [],         UL(['']),       UL(['']),

            UL([]),     'O1',           UL(['O', '1']),
            UL([]),     ['O2'],         UL(['O2']),
            UL([]),     UL(['O3']),     UL(['O3']),
            UL([]),     '',             UL([]),
            UL([]),     [],             UL([]),
            UL([]),     UL([]),         UL([]),
            UL([]),     [''],           UL(['']),
            UL([]),     UL(['']),       UL(['']),

            [''],       'P1',           ['P1', ''],
            [''],       ['P2'],         ['P2', ''],
            [''],       UL(['P3']),     UL(['P3', '']),
            [''],       '',             [''],
            [''],       [],             [''],
            [''],       UL([]),         UL(['']),
            [''],       [''],           ['', ''],
            [''],       UL(['']),       UL(['', '']),

            UL(['']),   'Q1',           UL(['Q', '1', '']),
            UL(['']),   ['Q2'],         UL(['Q2', '']),
            UL(['']),   UL(['Q3']),     UL(['Q3', '']),
            UL(['']),   '',             UL(['']),
            UL(['']),   [],             UL(['']),
            UL(['']),   UL([]),         UL(['']),
            UL(['']),   [''],           UL(['', '']),
            UL(['']),   UL(['']),       UL(['', '']),
        ]

        env = Environment()
        failed = 0
        while cases:
            input, prepend, expect = cases[:3]
            env['XXX'] = input
            env.Prepend(XXX = prepend)
            result = env['XXX']
            if result != expect:
                if failed == 0: print
                print "    %s Prepend %s => %s did not match %s" % \
                      (repr(input), repr(prepend), repr(result), repr(expect))
                failed = failed + 1
            del cases[:3]
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

        env3 = Environment(X = {'x1' : 7})
        env3.Prepend(X = {'x1' : 8, 'x2' : 9}, Y = {'y1' : 10})
        assert env3['X'] == {'x1': 8, 'x2' : 9}, env3['X']
        assert env3['Y'] == {'y1': 10}, env3['Y']

        env4 = Environment(BUILDERS = {'z1' : 11})
        env4.Prepend(BUILDERS = {'z2' : 12})
        assert env4['BUILDERS'] == {'z1' : 11, 'z2' : 12}, env4['BUILDERS']
        assert hasattr(env4, 'z1')
        assert hasattr(env4, 'z2')

    def test_PrependENVPath(self):
        """Test prepending to an ENV path."""
        env1 = Environment(ENV = {'PATH': r'C:\dir\num\one;C:\dir\num\two'},
                           MYENV = {'MYPATH': r'C:\mydir\num\one;C:\mydir\num\two'})
        # have to include the pathsep here so that the test will work on UNIX too.
        env1.PrependENVPath('PATH',r'C:\dir\num\two',sep = ';')
        env1.PrependENVPath('PATH',r'C:\dir\num\three',sep = ';')
        env1.PrependENVPath('MYPATH',r'C:\mydir\num\three','MYENV',sep = ';')
        env1.PrependENVPath('MYPATH',r'C:\mydir\num\one','MYENV',sep = ';')
        assert(env1['ENV']['PATH'] == r'C:\dir\num\three;C:\dir\num\two;C:\dir\num\one')
        assert(env1['MYENV']['MYPATH'] == r'C:\mydir\num\one;C:\mydir\num\three;C:\mydir\num\two')

    def test_PrependENVPath(self):
        """Test prepending to an ENV path."""
        env1 = Environment(ENV = {'PATH': r'C:\dir\num\one;C:\dir\num\two'},
                           MYENV = {'MYPATH': r'C:\mydir\num\one;C:\mydir\num\two'})
        # have to include the pathsep here so that the test will work on UNIX too.
        env1.PrependENVPath('PATH',r'C:\dir\num\two',sep = ';')
        env1.PrependENVPath('PATH',r'C:\dir\num\three',sep = ';')
        env1.PrependENVPath('MYPATH',r'C:\mydir\num\three','MYENV',sep = ';')
        env1.PrependENVPath('MYPATH',r'C:\mydir\num\one','MYENV',sep = ';')
        assert(env1['ENV']['PATH'] == r'C:\dir\num\three;C:\dir\num\two;C:\dir\num\one')
        assert(env1['MYENV']['MYPATH'] == r'C:\mydir\num\one;C:\mydir\num\three;C:\mydir\num\two')

    def test_PrependUnique(self):
        """Test prepending unique values to construction variables

        This strips values that are already present when lists are
        involved."""
        env = Environment(AAA1 = 'a1',
                          AAA2 = 'a2',
                          AAA3 = 'a3',
                          BBB1 = ['b1'],
                          BBB2 = ['b2'],
                          BBB3 = ['b3'],
                          CCC1 = '',
                          CCC2 = '')
        env.PrependUnique(AAA1 = 'a1',
                          AAA2 = ['a2'],
                          AAA3 = ['a3', 'b', 'c', 'a3'],
                          BBB1 = 'b1',
                          BBB2 = ['b2'],
                          BBB3 = ['b3', 'b', 'c', 'b3'],
                          CCC1 = 'c1',
                          CCC2 = ['c2'])
        assert env['AAA1'] == 'a1a1', env['AAA1']
        assert env['AAA2'] == ['a2'], env['AAA2']
        assert env['AAA3'] == ['b', 'c', 'a3'], env['AAA3']
        assert env['BBB1'] == ['b1'], env['BBB1']
        assert env['BBB2'] == ['b2'], env['BBB2']
        assert env['BBB3'] == ['b', 'c', 'b3'], env['BBB3']
        assert env['CCC1'] == 'c1', env['CCC1']
        assert env['CCC2'] == ['c2'], env['CCC2']

    def test_Replace(self):
        """Test replacing construction variables in an Environment

        After creation of the Environment, of course.
        """
        env1 = Environment(AAA = 'a', BBB = 'b')
        env1.Replace(BBB = 'bbb', CCC = 'ccc')

        env2 = Environment(AAA = 'a', BBB = 'bbb', CCC = 'ccc')
        assert env1 == env2, diff_env(env1, env2)

        env3 = Environment(BUILDERS = {'b1' : 1})
        assert hasattr(env3, 'b1'), "b1 was not set"
        env3.Replace(BUILDERS = {'b2' : 2})
        assert not hasattr(env3, 'b1'), "b1 was not cleared"
        assert hasattr(env3, 'b2'), "b2 was not set"

    def test_ReplaceIxes(self):
        "Test ReplaceIxes()"
        env = Environment(LIBPREFIX='lib',
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

    def test_SetDefault(self):
        """Test the SetDefault method"""
        env = Environment(tools = [])
        env.SetDefault(V1 = 1)
        env.SetDefault(V1 = 2)
        assert env['V1'] == 1
        env['V2'] = 2
        env.SetDefault(V2 = 1)
        assert env['V2'] == 2

    def test_Tool(self):
        """Test the Tool() method"""
        env = Environment(LINK='link', NONE='no-such-tool')

        exc_caught = None
        try:
            env.Tool('does_not_exist')
        except SCons.Errors.UserError:
            exc_caught = 1
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

    def test_WhereIs(self):
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
        os.chmod(sub3_xxx_exe, 0777)

        test.write(sub4_xxx_exe, "\n")
        os.chmod(sub4_xxx_exe, 0777)

        env_path = os.environ['PATH']

        pathdirs_1234 = [ test.workpath('sub1'),
                          test.workpath('sub2'),
                          test.workpath('sub3'),
                          test.workpath('sub4'),
                        ] + string.split(env_path, os.pathsep)

        pathdirs_1243 = [ test.workpath('sub1'),
                          test.workpath('sub2'),
                          test.workpath('sub4'),
                          test.workpath('sub3'),
                        ] + string.split(env_path, os.pathsep)

        path = string.join(pathdirs_1234, os.pathsep)
        env = Environment(ENV = {'PATH' : path})
        wi = env.WhereIs('xxx.exe')
        assert wi == test.workpath(sub3_xxx_exe), wi
        wi = env.WhereIs('xxx.exe', pathdirs_1243)
        assert wi == test.workpath(sub4_xxx_exe), wi
        wi = env.WhereIs('xxx.exe', string.join(pathdirs_1243, os.pathsep))
        assert wi == test.workpath(sub4_xxx_exe), wi

        wi = env.WhereIs('xxx.exe', reject = sub3_xxx_exe)
        assert wi == test.workpath(sub4_xxx_exe), wi
        wi = env.WhereIs('xxx.exe', pathdirs_1243, reject = sub3_xxx_exe)
        assert wi == test.workpath(sub4_xxx_exe), wi

        path = string.join(pathdirs_1243, os.pathsep)
        env = Environment(ENV = {'PATH' : path})
        wi = env.WhereIs('xxx.exe')
        assert wi == test.workpath(sub4_xxx_exe), wi
        wi = env.WhereIs('xxx.exe', pathdirs_1234)
        assert wi == test.workpath(sub3_xxx_exe), wi
        wi = env.WhereIs('xxx.exe', string.join(pathdirs_1234, os.pathsep))
        assert wi == test.workpath(sub3_xxx_exe), wi

        if sys.platform == 'win32':
            wi = env.WhereIs('xxx', pathext = '')
            assert wi is None, wi

            wi = env.WhereIs('xxx', pathext = '.exe')
            assert wi == test.workpath(sub4_xxx_exe), wi

            wi = env.WhereIs('xxx', path = pathdirs_1234, pathext = '.BAT;.EXE')
            assert string.lower(wi) == string.lower(test.workpath(sub3_xxx_exe)), wi

            # Test that we return a normalized path even when
            # the path contains forward slashes.
            forward_slash = test.workpath('') + '/sub3'
            wi = env.WhereIs('xxx', path = forward_slash, pathext = '.EXE')
            assert string.lower(wi) == string.lower(test.workpath(sub3_xxx_exe)), wi



    def test_Action(self):
        """Test the Action() method"""
        import SCons.Action

        env = Environment(FOO = 'xyzzy')

        a = env.Action('foo')
        assert a, a
        assert a.__class__ is SCons.Action.CommandAction, a

        a = env.Action('$FOO')
        assert a, a
        assert a.__class__ is SCons.Action.LazyAction, a

        a = env.Action(['$FOO', 'foo'])
        assert a, a
        assert a.__class__ is SCons.Action.ListAction, a

        def func(arg):
            pass
        a = env.Action(func)
        assert a, a
        assert a.__class__ is SCons.Action.FunctionAction, a

    def test_AddPostAction(self):
        """Test the AddPostAction() method"""
        env = Environment(FOO='fff', BAR='bbb')

        n = env.AddPostAction('$FOO', lambda x: x)
        assert str(n[0]) == 'fff', n[0]

        n = env.AddPostAction(['ggg', '$BAR'], lambda x: x)
        assert str(n[0]) == 'ggg', n[0]
        assert str(n[1]) == 'bbb', n[1]

    def test_AddPreAction(self):
        """Test the AddPreAction() method"""
        env = Environment(FOO='fff', BAR='bbb')

        n = env.AddPreAction('$FOO', lambda x: x)
        assert str(n[0]) == 'fff', n[0]

        n = env.AddPreAction(['ggg', '$BAR'], lambda x: x)
        assert str(n[0]) == 'ggg', n[0]
        assert str(n[1]) == 'bbb', n[1]

    def test_Alias(self):
        """Test the Alias() method"""
        env = Environment(FOO='kkk', BAR='lll', EA='export_alias')

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
        assert len(tgt.sources) == 2, map(str, tgt.sources)
        assert str(tgt.sources[0]) == 'asrc1', map(str, tgt.sources)
        assert str(tgt.sources[1]) == 'kkk', map(str, tgt.sources)

        n = env.Alias(tgt, source = ['$BAR', 'asrc4'])[0]
        assert n is tgt, n
        assert len(tgt.sources) == 4, map(str, tgt.sources)
        assert str(tgt.sources[2]) == 'lll', map(str, tgt.sources)
        assert str(tgt.sources[3]) == 'asrc4', map(str, tgt.sources)

        n = env.Alias('$EA', 'asrc5')[0]
        assert n is tgt, n
        assert len(tgt.sources) == 5, map(str, tgt.sources)
        assert str(tgt.sources[4]) == 'asrc5', map(str, tgt.sources)

        t1, t2 = env.Alias(['t1', 't2'], ['asrc6', 'asrc7'])
        assert str(t1) == 't1', t1
        assert str(t2) == 't2', t2
        assert len(t1.sources) == 2, map(str, t1.sources)
        assert str(t1.sources[0]) == 'asrc6', map(str, t1.sources)
        assert str(t1.sources[1]) == 'asrc7', map(str, t1.sources)
        assert len(t2.sources) == 2, map(str, t2.sources)
        assert str(t2.sources[0]) == 'asrc6', map(str, t2.sources)
        assert str(t2.sources[1]) == 'asrc7', map(str, t2.sources)

        tgt = env.Alias('add', 's1')
        tgt = env.Alias('add', 's2')[0]
        s = map(str, tgt.sources)
        assert s == ['s1', 's2'], s
        tgt = env.Alias(tgt, 's3')[0]
        s = map(str, tgt.sources)
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

    def test_AlwaysBuild(self):
        """Test the AlwaysBuild() method"""
        env = Environment(FOO='fff', BAR='bbb')
        t = env.AlwaysBuild('a', 'b$FOO', ['c', 'd'], '$BAR')
        assert t[0].__class__.__name__ == 'File'
        assert t[0].path == 'a'
        assert t[0].always_build
        assert t[1].__class__.__name__ == 'File'
        assert t[1].path == 'bfff'
        assert t[1].always_build
        assert t[2].__class__.__name__ == 'File'
        assert t[2].path == 'c'
        assert t[2].always_build
        assert t[3].__class__.__name__ == 'File'
        assert t[3].path == 'd'
        assert t[3].always_build
        assert t[4].__class__.__name__ == 'File'
        assert t[4].path == 'bbb'
        assert t[4].always_build

    def test_BuildDir(self):
        """Test the BuildDir() method"""
        class MyFS:
             def Dir(self, name):
                 return name
             def BuildDir(self, build_dir, src_dir, duplicate):
                 self.build_dir = build_dir
                 self.src_dir = src_dir
                 self.duplicate = duplicate

        env = Environment(FOO = 'fff', BAR = 'bbb')
        env.fs = MyFS()

        env.BuildDir('build', 'src')
        assert env.fs.build_dir == 'build', env.fs.build_dir
        assert env.fs.src_dir == 'src', env.fs.src_dir
        assert env.fs.duplicate == 1, env.fs.duplicate

        env.BuildDir('build${FOO}', '${BAR}src', 0)
        assert env.fs.build_dir == 'buildfff', env.fs.build_dir
        assert env.fs.src_dir == 'bbbsrc', env.fs.src_dir
        assert env.fs.duplicate == 0, env.fs.duplicate

    def test_Builder(self):
        """Test the Builder() method"""
        env = Environment(FOO = 'xyzzy')

        b = env.Builder(action = 'foo')
        assert not b is None, b

        b = env.Builder(action = '$FOO')
        assert not b is None, b

        b = env.Builder(action = ['$FOO', 'foo'])
        assert not b is None, b

        def func(arg):
            pass
        b = env.Builder(action = func)
        assert not b is None, b
        b = env.Builder(generator = func)
        assert not b is None, b

    def test_CacheDir(self):
        """Test the CacheDir() method"""
        class MyFS:
            def CacheDir(self, path):
                self.CD = path

        env = Environment(CD = 'CacheDir')
        env.fs = MyFS()

        env.CacheDir('foo')
        assert env.fs.CD == 'foo', env.fs.CD

        env.CacheDir('$CD')
        assert env.fs.CD == 'CacheDir', env.fs.CD

    def test_Clean(self):
        """Test the Clean() method"""
        env = Environment(FOO = 'fff', BAR = 'bbb')

        CT = SCons.Environment.CleanTargets

        foo = env.arg2nodes('foo')[0]
        fff = env.arg2nodes('fff')[0]

        t = env.Clean('foo', 'aaa')
        l = map(str, CT[foo])
        assert l == ['aaa'], l

        t = env.Clean(foo, ['$BAR', 'ccc'])
        l = map(str, CT[foo])
        assert l == ['aaa', 'bbb', 'ccc'], l

        eee = env.arg2nodes('eee')[0]

        t = env.Clean('$FOO', 'ddd')
        l = map(str, CT[fff])
        assert l == ['ddd'], l
        t = env.Clean(fff, [eee, 'fff'])
        l = map(str, CT[fff])
        assert l == ['ddd', 'eee', 'fff'], l

    def test_Command(self):
        """Test the Command() method."""
        env = Environment()
        t = env.Command(target='foo.out', source=['foo1.in', 'foo2.in'],
                        action='buildfoo $target $source')[0]
        assert not t.builder is None
        assert t.builder.action.__class__.__name__ == 'CommandAction'
        assert t.builder.action.cmd_list == 'buildfoo $target $source'
        assert 'foo1.in' in map(lambda x: x.path, t.sources)
        assert 'foo2.in' in map(lambda x: x.path, t.sources)

        sub = SCons.Node.FS.default_fs.Dir('sub')
        t = env.Command(target='bar.out', source='sub',
                        action='buildbar $target $source')[0]
        assert 'sub' in map(lambda x: x.path, t.sources)

        def testFunc(env, target, source):
            assert str(target[0]) == 'foo.out'
            assert 'foo1.in' in map(str, source) and 'foo2.in' in map(str, source), map(str, source)
            return 0
        t = env.Command(target='foo.out', source=['foo1.in','foo2.in'],
                        action=testFunc)[0]
        assert not t.builder is None
        assert t.builder.action.__class__.__name__ == 'FunctionAction'
        t.build()
        assert 'foo1.in' in map(lambda x: x.path, t.sources)
        assert 'foo2.in' in map(lambda x: x.path, t.sources)

        x = []
        def test2(baz, x=x):
            x.append(baz)
        env = Environment(TEST2 = test2)
        t = env.Command(target='baz.out', source='baz.in',
                        action='${TEST2(XYZ)}',
                        XYZ='magic word')[0]
        assert not t.builder is None
        t.build()
        assert x[0] == 'magic word', x

        t = env.Command(target='${X}.out', source='${X}.in',
                        action = 'foo',
                        X = 'xxx')[0]
        assert str(t) == 'xxx.out', str(t)
        assert 'xxx.in' in map(lambda x: x.path, t.sources)

    def test_Configure(self):
        """Test the Configure() method"""
        # Configure() will write to a local temporary file.
        test = TestCmd.TestCmd(workdir = '')
        save = os.getcwd()
        # Configure() will test, if we are reading a SConscript file
        import SCons.Script.SConscript
        SCons.Script.SConscript.sconscript_reading = 1

        try:
            os.chdir(test.workpath())

            env = Environment(FOO = 'xyzzy')

            def func(arg):
                pass

            c = env.Configure()
            assert not c is None, c
            c.Finish()

            c = env.Configure(custom_tests = {'foo' : func, '$FOO' : func})
            assert not c is None, c
            assert hasattr(c, 'foo')
            assert hasattr(c, 'xyzzy')
            c.Finish()
        finally:
            os.chdir(save)

    def test_Depends(self):
        """Test the explicit Depends method."""
        env = Environment(FOO = 'xxx', BAR='yyy')
        env.Dir('dir1')
        env.Dir('dir2')
        env.File('xxx.py')
        env.File('yyy.py')
        t = env.Depends(target='EnvironmentTest.py',
                        dependency='Environment.py')[0]
        assert t.__class__.__name__ == 'Entry', t.__class__.__name__
        assert t.path == 'EnvironmentTest.py'
        assert len(t.depends) == 1
        d = t.depends[0]
        assert d.__class__.__name__ == 'Entry', d.__class__.__name__
        assert d.path == 'Environment.py'

        t = env.Depends(target='${FOO}.py', dependency='${BAR}.py')[0]
        assert t.__class__.__name__ == 'File', t.__class__.__name__
        assert t.path == 'xxx.py'
        assert len(t.depends) == 1
        d = t.depends[0]
        assert d.__class__.__name__ == 'File', d.__class__.__name__
        assert d.path == 'yyy.py'

        t = env.Depends(target='dir1', dependency='dir2')[0]
        assert t.__class__.__name__ == 'Dir', t.__class__.__name__
        assert t.path == 'dir1'
        assert len(t.depends) == 1
        d = t.depends[0]
        assert d.__class__.__name__ == 'Dir', d.__class__.__name__
        assert d.path == 'dir2'

    def test_Dir(self):
        """Test the Dir() method"""
        class MyFS:
            def Dir(self, name):
                return 'Dir(%s)' % name

        env = Environment(FOO = 'foodir', BAR = 'bardir')
        env.fs = MyFS()

        d = env.Dir('d')
        assert d == 'Dir(d)', d

        d = env.Dir('$FOO')
        assert d == 'Dir(foodir)', d

        d = env.Dir('${BAR}_$BAR')
        assert d == 'Dir(bardir_bardir)', d

    def test_Dump(self):
        """Test the Dump() method"""

        env = Environment(FOO = 'foo')
        assert env.Dump('FOO') == "'foo'", env.Dump('FOO')
        assert len(env.Dump()) > 200, env.Dump()    # no args version

    def test_Environment(self):
        """Test the Environment() method"""
        env = Environment(FOO = 'xxx', BAR = 'yyy')

        e2 = env.Environment(X = '$FOO', Y = '$BAR')
        assert e2['X'] == 'xxx', e2['X']
        assert e2['Y'] == 'yyy', e2['Y']

    def test_Execute(self):
        """Test the Execute() method"""

        class MyAction:
            def __init__(self, *args, **kw):
                self.args = args
            def __call__(self, target, source, env):
                return "%s executed" % self.args

        env = Environment()
        env.Action = MyAction

        result = env.Execute("foo")
        assert result == "foo executed", result

    def test_File(self):
        """Test the File() method"""
        class MyFS:
            def File(self, name):
                return 'File(%s)' % name

        env = Environment(FOO = 'foofile', BAR = 'barfile')
        env.fs = MyFS()

        f = env.File('f')
        assert f == 'File(f)', f

        f = env.File('$FOO')
        assert f == 'File(foofile)', f

        f = env.File('${BAR}_$BAR')
        assert f == 'File(barfile_barfile)', f

    def test_FindFile(self):
        """Test the FindFile() method"""
        env = Environment(FOO = 'fff', BAR = 'bbb')

        r = env.FindFile('foo', ['no_such_directory'])
        assert r is None, r

        # XXX

    def test_Flatten(self):
        """Test the Flatten() method"""
        env = Environment()
        l = env.Flatten([1])
        assert l == [1]
        l = env.Flatten([1, [2, [3, [4]]]])
        assert l == [1, 2, 3, 4], l

    def test_GetBuildPath(self):
        """Test the GetBuildPath() method."""
        env = Environment(MAGIC = 'xyzzy')

        p = env.GetBuildPath('foo')
        assert p == 'foo', p

        p = env.GetBuildPath('$MAGIC')
        assert p == 'xyzzy', p

    def test_Ignore(self):
        """Test the explicit Ignore method."""
        env = Environment(FOO='yyy', BAR='zzz')
        env.Dir('dir1')
        env.Dir('dir2')
        env.File('yyyzzz')
        env.File('zzzyyy')

        t = env.Ignore(target='targ.py', dependency='dep.py')[0]
        assert t.__class__.__name__ == 'Entry', t.__class__.__name__
        assert t.path == 'targ.py'
        assert len(t.ignore) == 1
        i = t.ignore[0]
        assert i.__class__.__name__ == 'Entry', i.__class__.__name__
        assert i.path == 'dep.py'

        t = env.Ignore(target='$FOO$BAR', dependency='$BAR$FOO')[0]
        assert t.__class__.__name__ == 'File', t.__class__.__name__
        assert t.path == 'yyyzzz'
        assert len(t.ignore) == 1
        i = t.ignore[0]
        assert i.__class__.__name__ == 'File', i.__class__.__name__
        assert i.path == 'zzzyyy'

        t = env.Ignore(target='dir1', dependency='dir2')[0]
        assert t.__class__.__name__ == 'Dir', t.__class__.__name__
        assert t.path == 'dir1'
        assert len(t.ignore) == 1
        i = t.ignore[0]
        assert i.__class__.__name__ == 'Dir', i.__class__.__name__
        assert i.path == 'dir2'

    def test_Install(self):
	"""Test the Install method"""
        env = Environment(FOO='iii', BAR='jjj')

        tgt = env.Install('export', [ 'build/foo1', 'build/foo2' ])
        paths = map(str, tgt)
        paths.sort()
        expect = map(os.path.normpath, [ 'export/foo1', 'export/foo2' ])
        assert paths == expect, paths
        for tnode in tgt:
            assert tnode.builder == InstallBuilder

        tgt = env.Install('$FOO', [ 'build/${BAR}1', 'build/${BAR}2' ])
        paths = map(str, tgt)
        paths.sort()
        expect = map(os.path.normpath, [ 'iii/jjj1', 'iii/jjj2' ])
        assert paths == expect, paths
        for tnode in tgt:
            assert tnode.builder == InstallBuilder

        exc_caught = None
        try:
            tgt = env.Install('export', 'export')
        except SCons.Errors.UserError, e:
            exc_caught = 1
        assert exc_caught, "UserError should be thrown when Install() target is not a file."
        match = str(e) == "Source `export' of Install() is not a file.  Install() source must be one or more files."
        assert match, e

        exc_caught = None
        try:
            tgt = env.Install('export', ['export', 'build/foo1'])
        except SCons.Errors.UserError, e:
            exc_caught = 1
        assert exc_caught, "UserError should be thrown when Install() target containins non-files."
        match = str(e) == "Source `['export', 'build/foo1']' of Install() contains one or more non-files.  Install() source must be one or more files."
        assert match, e

        exc_caught = None
        try:
            tgt = env.Install('export/foo1', 'build/foo1')
        except SCons.Errors.UserError, e:
            exc_caught = 1
        assert exc_caught, "UserError should be thrown reversing the order of Install() targets."
        match = str(e) == "Target `export/foo1' of Install() is a file, but should be a directory.  Perhaps you have the Install() arguments backwards?"
        assert match, e

    def test_InstallAs(self):
	"""Test the InstallAs method"""
        env = Environment(FOO='iii', BAR='jjj')

        tgt = env.InstallAs(target=string.split('foo1 foo2'),
                            source=string.split('bar1 bar2'))
        assert len(tgt) == 2, len(tgt)
        paths = map(lambda x: str(x.sources[0]), tgt)
        paths.sort()
        expect = map(os.path.normpath, [ 'bar1', 'bar2' ])
        assert paths == expect, paths
        for tnode in tgt:
            assert tnode.builder == InstallBuilder

        tgt = env.InstallAs(target='${FOO}.t', source='${BAR}.s')[0]
        assert tgt.path == 'iii.t'
        assert tgt.sources[0].path == 'jjj.s'
        assert tgt.builder == InstallBuilder

    def test_Literal(self):
        """Test the Literal() method"""
        env = Environment(FOO='fff', BAR='bbb')
        list = env.subst_list([env.Literal('$FOO'), '$BAR'])[0]
        assert list == ['$FOO', 'bbb'], list
        list = env.subst_list(['$FOO', env.Literal('$BAR')])[0]
        assert list == ['fff', '$BAR'], list

    def test_Local(self):
        """Test the Local() method."""
        env = Environment(FOO='lll')

        l = env.Local(env.fs.File('fff'))
        assert str(l[0]) == 'fff', l[0]

        l = env.Local('ggg', '$FOO')
        assert str(l[0]) == 'ggg', l[0]
        assert str(l[1]) == 'lll', l[1]

    def test_Precious(self):
        """Test the Precious() method"""
        env = Environment(FOO='ggg', BAR='hhh')
        env.Dir('p_hhhb')
        env.File('p_d')
        t = env.Precious('p_a', 'p_${BAR}b', ['p_c', 'p_d'], 'p_$FOO')

        assert t[0].__class__.__name__ == 'Entry', t[0].__class__.__name__
        assert t[0].path == 'p_a'
        assert t[0].precious
        assert t[1].__class__.__name__ == 'Dir', t[1].__class__.__name__
        assert t[1].path == 'p_hhhb'
        assert t[1].precious
        assert t[2].__class__.__name__ == 'Entry', t[2].__class__.__name__
        assert t[2].path == 'p_c'
        assert t[2].precious
        assert t[3].__class__.__name__ == 'File', t[3].__class__.__name__
        assert t[3].path == 'p_d'
        assert t[3].precious
        assert t[4].__class__.__name__ == 'Entry', t[4].__class__.__name__
        assert t[4].path == 'p_ggg'
        assert t[4].precious

    def test_Repository(self):
        """Test the Repository() method."""
        class MyFS:
            def __init__(self):
                self.list = []
            def Repository(self, *dirs):
                self.list.extend(list(dirs))
            def Dir(self, name):
                return name
        env = Environment(FOO='rrr', BAR='sss')
        env.fs = MyFS()
        env.Repository('/tmp/foo')
        env.Repository('/tmp/$FOO', '/tmp/$BAR/foo')
        expect = ['/tmp/foo', '/tmp/rrr', '/tmp/sss/foo']
        assert env.fs.list == expect, env.fs.list

    def test_Scanner(self):
        """Test the Scanner() method"""
        def scan(node, env, target, arg):
            pass

        env = Environment(FOO = scan)

        s = env.Scanner('foo')
        assert not s is None, s

        s = env.Scanner(function = 'foo')
        assert not s is None, s

        if 0:
            s = env.Scanner('$FOO')
            assert not s is None, s

            s = env.Scanner(function = '$FOO')
            assert not s is None, s

    def test_SConsignFile(self):
        """Test the SConsignFile() method"""
        import SCons.SConsign

        class MyFS:
            SConstruct_dir = os.sep + 'dir'

        env = Environment(FOO = 'SConsign',
                          BAR = os.path.join(os.sep, 'File'))
        env.fs = MyFS()

        try:
            fnames = []
            dbms = []
            def capture(name, dbm_module, fnames=fnames, dbms=dbms):
                fnames.append(name)
                dbms.append(dbm_module)

            save_SConsign_File = SCons.SConsign.File
            SCons.SConsign.File = capture

            env.SConsignFile('foo')
            assert fnames[0] == os.path.join(os.sep, 'dir', 'foo'), fnames
            assert dbms[0] == None, dbms

            env.SConsignFile('$FOO')
            assert fnames[1] == os.path.join(os.sep, 'dir', 'SConsign'), fnames
            assert dbms[1] == None, dbms

            env.SConsignFile('/$FOO')
            assert fnames[2] == '/SConsign', fnames
            assert dbms[2] == None, dbms

            env.SConsignFile('$BAR', 'x')
            assert fnames[3] == os.path.join(os.sep, 'File'), fnames
            assert dbms[3] == 'x', dbms

            env.SConsignFile('__$BAR', 7)
            assert fnames[4] == os.path.join(os.sep, 'dir', '__', 'File'), fnames
            assert dbms[4] == 7, dbms

            env.SConsignFile()
            assert fnames[5] == os.path.join(os.sep, 'dir', '.sconsign'), fnames
            assert dbms[5] == None, dbms
        finally:
            SCons.SConsign.File = save_SConsign_File

    def test_SideEffect(self):
        """Test the SideEffect() method"""
        env = Environment(LIB='lll', FOO='fff', BAR='bbb')
        env.File('mylll.pdb')
        env.Dir('mymmm.pdb')

        foo = env.Object('foo.obj', 'foo.cpp')[0]
        bar = env.Object('bar.obj', 'bar.cpp')[0]
        s = env.SideEffect('mylib.pdb', ['foo.obj', 'bar.obj'])[0]
        assert s.__class__.__name__ == 'Entry', s.__class__.__name__
        assert s.path == 'mylib.pdb'
        assert s.side_effect
        assert foo.side_effects == [s]
        assert bar.side_effects == [s]
        assert s.depends_on([bar])
        assert s.depends_on([foo])

        fff = env.Object('fff.obj', 'fff.cpp')[0]
        bbb = env.Object('bbb.obj', 'bbb.cpp')[0]
        s = env.SideEffect('my${LIB}.pdb', ['${FOO}.obj', '${BAR}.obj'])[0]
        assert s.__class__.__name__ == 'File', s.__class__.__name__
        assert s.path == 'mylll.pdb'
        assert s.side_effect
        assert fff.side_effects == [s], fff.side_effects
        assert bbb.side_effects == [s], bbb.side_effects
        assert s.depends_on([bbb])
        assert s.depends_on([fff])

        ggg = env.Object('ggg.obj', 'ggg.cpp')[0]
        ccc = env.Object('ccc.obj', 'ccc.cpp')[0]
        s = env.SideEffect('mymmm.pdb', ['ggg.obj', 'ccc.obj'])[0]
        assert s.__class__.__name__ == 'Dir', s.__class__.__name__
        assert s.path == 'mymmm.pdb'
        assert s.side_effect
        assert ggg.side_effects == [s], ggg.side_effects
        assert ccc.side_effects == [s], ccc.side_effects
        assert s.depends_on([ccc])
        assert s.depends_on([ggg])

    def test_SourceCode(self):
        """Test the SourceCode() method."""
        env = Environment(FOO='mmm', BAR='nnn')
        e = env.SourceCode('foo', None)[0]
        assert e.path == 'foo'
        s = e.src_builder()
        assert s is None, s

        b = Builder()
        e = env.SourceCode(e, b)[0]
        assert e.path == 'foo'
        s = e.src_builder()
        assert s is b, s

        e = env.SourceCode('$BAR$FOO', None)[0]
        assert e.path == 'nnnmmm'
        s = e.src_builder()
        assert s is None, s

    def test_SourceSignatures(type):
        """Test the SourceSignatures() method"""
        env = Environment(M = 'MD5', T = 'timestamp')

        exc_caught = None
        try:
            env.SourceSignatures('invalid_type')
        except SCons.Errors.UserError:
            exc_caught = 1
        assert exc_caught, "did not catch expected UserError"
        assert not hasattr(env, '_calc_module')

        env.SourceSignatures('MD5')
        m = env._calc_module

        env.SourceSignatures('$M')
        assert env._calc_module is m

        env.SourceSignatures('timestamp')
        t = env._calc_module

        env.SourceSignatures('$T')
        assert env._calc_module is t

    def test_Split(self):
        """Test the Split() method"""
        env = Environment(FOO='fff', BAR='bbb')
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

    def test_TargetSignatures(type):
        """Test the TargetSignatures() method"""
        env = Environment(B = 'build', C = 'content')

        exc_caught = None
        try:
            env.TargetSignatures('invalid_type')
        except SCons.Errors.UserError:
            exc_caught = 1
        assert exc_caught, "did not catch expected UserError"
        assert not hasattr(env, '_build_signature')

        env.TargetSignatures('build')
        assert env._build_signature == 1, env._build_signature

        env.TargetSignatures('content')
        assert env._build_signature == 0, env._build_signature

        env.TargetSignatures('$B')
        assert env._build_signature == 1, env._build_signature

        env.TargetSignatures('$C')
        assert env._build_signature == 0, env._build_signature

    def test_Value(self):
        """Test creating a Value() object
        """
        env = Environment()
        v1 = env.Value('a')
        assert v1.value == 'a', v1.value

        value2 = 'a'
        v2 = env.Value(value2)
        assert v2.value == value2, v2.value
        assert v2.value is value2, v2.value

        assert not v1 is v2
        assert v1.value == v2.value



    def test_Environment_global_variable(type):
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

    def test_bad_keywords(type):
        """Test trying to use reserved keywords in an Environment"""
        reserved = ['TARGETS','SOURCES', 'SOURCE','TARGET']
        added = []

        env = SCons.Environment.Environment(TARGETS = 'targets',
                                            SOURCES = 'sources',
                                            SOURCE = 'source',
                                            TARGET = 'target',
                                            INIT = 'init')
        added.append('INIT')
        for x in reserved:
            assert not env.has_key(x), env[x]
        for x in added:
            assert env.has_key(x), \
                   '%s is not reserved, but got omitted; see Environment.construction_var_name_ok'%x

        env.Append(TARGETS = 'targets',
                   SOURCES = 'sources',
                   SOURCE = 'source',
                   TARGET = 'target',
                   APPEND = 'append')
        added.append('APPEND')
        for x in reserved:
            assert not env.has_key(x), env[x]
        for x in added:
            assert env.has_key(x), \
                   '%s is not reserved, but got omitted; see Environment.construction_var_name_ok'%x

        env.AppendUnique(TARGETS = 'targets',
                         SOURCES = 'sources',
                         SOURCE = 'source',
                         TARGET = 'target',
                         APPENDUNIQUE = 'appendunique')
        added.append('APPENDUNIQUE')
        for x in reserved:
            assert not env.has_key(x), env[x]
        for x in added:
            assert env.has_key(x), \
                   '%s is not reserved, but got omitted; see Environment.construction_var_name_ok'%x

        env.Prepend(TARGETS = 'targets',
                    SOURCES = 'sources',
                    SOURCE = 'source',
                    TARGET = 'target',
                    PREPEND = 'prepend')
        added.append('PREPEND')
        for x in reserved:
            assert not env.has_key(x), env[x]
        for x in added:
            assert env.has_key(x), \
                   '%s is not reserved, but got omitted; see Environment.construction_var_name_ok'%x

        env.Prepend(TARGETS = 'targets',
                    SOURCES = 'sources',
                    SOURCE = 'source',
                    TARGET = 'target',
                    PREPENDUNIQUE = 'prependunique')
        added.append('PREPENDUNIQUE')
        for x in reserved:
            assert not env.has_key(x), env[x]
        for x in added:
            assert env.has_key(x), \
                   '%s is not reserved, but got omitted; see Environment.construction_var_name_ok'%x

        env.Replace(TARGETS = 'targets',
                    SOURCES = 'sources',
                    SOURCE = 'source',
                    TARGET = 'target',
                    REPLACE = 'replace')
        added.append('REPLACE')
        for x in reserved:
            assert not env.has_key(x), env[x]
        for x in added:
            assert env.has_key(x), \
                   '%s is not reserved, but got omitted; see Environment.construction_var_name_ok'%x

        copy = env.Copy(TARGETS = 'targets',
                        SOURCES = 'sources',
                        SOURCE = 'source',
                        TARGET = 'target',
                        COPY = 'copy')
        for x in reserved:
            assert not copy.has_key(x), env[x]
        for x in added + ['COPY']:
            assert copy.has_key(x), \
                   '%s is not reserved, but got omitted; see Environment.construction_var_name_ok'%x

        over = env.Override({'TARGETS' : 'targets',
                             'SOURCES' : 'sources',
                             'SOURCE' : 'source',
                             'TARGET' : 'target',
                             'OVERRIDE' : 'override'})
        for x in reserved:
            assert not over.has_key(x), over[x]
        for x in added + ['OVERRIDE']:
            assert over.has_key(x), \
                   '%s is not reserved, but got omitted; see Environment.construction_var_name_ok'%x



class OverrideEnvironmentTestCase(unittest.TestCase):

    def test___init__(self):
        """Test OverrideEnvironment initialization"""
        env = Environment(XXX = 'x', YYY = 'y')
        env2 = OverrideEnvironment(env, {'XXX' : 'x2'})
        env3 = OverrideEnvironment(env2, {'XXX' : 'x3', 'YYY' : 'y3'})
        assert env['XXX'] == 'x', env['XXX']
        assert env2['XXX'] == 'x2', env2['XXX']
        assert env3['XXX'] == 'x3', env3['XXX']
        assert env['YYY'] == 'y', env['YYY']
        assert env2['YYY'] == 'y', env2['YYY']
        assert env3['YYY'] == 'y3', env3['YYY']

    def test_get(self):
        """Test the OverrideEnvironment get() method"""
        env = Environment(XXX = 'x', YYY = 'y')
        env2 = OverrideEnvironment(env, {'XXX' : 'x2'})
        env3 = OverrideEnvironment(env2, {'XXX' : 'x3', 'YYY' : 'y3', 'ZZZ' : 'z3'})
        assert env.get('XXX') == 'x', env.get('XXX')
        assert env2.get('XXX') == 'x2', env2.get('XXX')
        assert env3.get('XXX') == 'x3', env3.get('XXX')
        assert env.get('YYY') == 'y', env.get('YYY')
        assert env2.get('YYY') == 'y', env2.get('YYY')
        assert env3.get('YYY') == 'y3', env3.get('YYY')
        assert env.get('ZZZ') == None, env.get('ZZZ')
        assert env2.get('ZZZ') == None, env2.get('ZZZ')
        assert env3.get('ZZZ') == 'z3', env3.get('ZZZ')

    def test_has_key(self):
        """Test the OverrideEnvironment has_key() method"""
        env = Environment(XXX = 'x', YYY = 'y')
        env2 = OverrideEnvironment(env, {'XXX' : 'x2'})
        env3 = OverrideEnvironment(env2, {'XXX' : 'x3', 'YYY' : 'y3', 'ZZZ' : 'z3'})
        assert env.has_key('XXX'), env.has_key('XXX')
        assert env2.has_key('XXX'), env2.has_key('XXX')
        assert env3.has_key('XXX'), env3.has_key('XXX')
        assert env.has_key('YYY'), env.has_key('YYY')
        assert env2.has_key('YYY'), env2.has_key('YYY')
        assert env3.has_key('YYY'), env3.has_key('YYY')
        assert not env.has_key('ZZZ'), env.has_key('ZZZ')
        assert not env2.has_key('ZZZ'), env2.has_key('ZZZ')
        assert env3.has_key('ZZZ'), env3.has_key('ZZZ')

    def test_items(self):
        """Test the OverrideEnvironment items() method"""
        env = Environment(WWW = 'w', XXX = 'x', YYY = 'y')
        env2 = OverrideEnvironment(env, {'XXX' : 'x2'})
        env3 = OverrideEnvironment(env2, {'XXX' : 'x3', 'YYY' : 'y3', 'ZZZ' : 'z3'})
        items = env.items()
        assert items == {'WWW' : 'w', 'XXX' : 'x', 'YYY' : 'y'}, items
        items = env2.items()
        assert items == {'WWW' : 'w', 'XXX' : 'x2', 'YYY' : 'y'}, items
        items = env3.items()
        assert items == {'WWW' : 'w', 'XXX' : 'x3', 'YYY' : 'y3', 'ZZZ' : 'z3'}, items

    def test_gvars(self):
        """Test the OverrideEnvironment gvars() method"""
        env = Environment(XXX = 'x', YYY = 'y')
        env2 = OverrideEnvironment(env, {'xxx' : 'x2'})
        env3 = OverrideEnvironment(env2, {'XXX' : 'x3', 'YYY' : 'y3'})
        gvars = env.gvars()
        assert gvars == {'XXX' : 'x', 'YYY' : 'y'}, gvars
        gvars = env2.gvars()
        assert gvars == {'XXX' : 'x2', 'YYY' : 'y'}, gvars
        gvars = env3.gvars()
        assert gvars == {'XXX' : 'x3', 'YYY' : 'y3'}, gvars

    def test_lvars(self):
        """Test the OverrideEnvironment lvars() method"""
        env = Environment(XXX = 'x', YYY = 'y')
        env2 = OverrideEnvironment(env, {'xxx' : 'x2'})
        env3 = OverrideEnvironment(env2, {'xxx' : 'x3', 'YYY' : 'y3'})
        lvars = env.lvars()
        assert lvars == {}, lvars
        lvars = env2.lvars()
        assert lvars == {'XXX' : 'x2', 'YYY' : 'y'}, lvars
        lvars = env3.lvars()
        assert lvars == {'XXX' : 'x3', 'YYY' : 'y3'}, lvars

    def test_Replace(self):
        """Test the OverrideEnvironment Replace() method"""
        env = Environment(XXX = 'x', YYY = 'y')
        env2 = OverrideEnvironment(env, {'xxx' : 'x2'})
        env3 = OverrideEnvironment(env2, {'xxx' : 'x3', 'YYY' : 'y3'})
        assert env['XXX'] == 'x', env['XXX']
        assert env2['XXX'] == 'x2', env2['XXX']
        assert env3['XXX'] == 'x3', env3['XXX']
        assert env['YYY'] == 'y', env['YYY']
        assert env2['YYY'] == 'y', env2['YYY']
        assert env3['YYY'] == 'y3', env3['YYY']

        env.Replace(YYY = 'y4')

        assert env['XXX'] == 'x', env['XXX']
        assert env2['XXX'] == 'x2', env2['XXX']
        assert env3['XXX'] == 'x3', env3['XXX']
        assert env['YYY'] == 'y4', env['YYY']
        assert env2['YYY'] == 'y4', env2['YYY']
        assert env3['YYY'] == 'y3', env3['YYY']




class NoSubstitutionProxyTestCase(unittest.TestCase):

    def test___init__(self):
        """Test NoSubstitutionProxy initialization"""
        env = Environment(XXX = 'x', YYY = 'y')
        assert env['XXX'] == 'x', env['XXX']
        assert env['YYY'] == 'y', env['YYY']

        proxy = NoSubstitutionProxy(env)
        assert proxy['XXX'] == 'x', proxy['XXX']
        assert proxy['YYY'] == 'y', proxy['YYY']

    def test_attributes(self):
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

    def test_subst(self):
        """Test the NoSubstitutionProxy.subst() method"""
        env = Environment(XXX = 'x', YYY = 'y')
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

    def test_subst_kw(self):
        """Test the NoSubstitutionProxy.subst_kw() method"""
        env = Environment(XXX = 'x', YYY = 'y')
        assert env['XXX'] == 'x', env['XXX']
        assert env['YYY'] == 'y', env['YYY']

        proxy = NoSubstitutionProxy(env)
        assert proxy['XXX'] == 'x', proxy['XXX']
        assert proxy['YYY'] == 'y', proxy['YYY']

        x = env.subst_kw({'$XXX':'$YYY'})
        assert x == {'x':'y'}, x
        x = proxy.subst_kw({'$XXX':'$YYY'})
        assert x == {'$XXX':'$YYY'}, x

    def test_subst_list(self):
        """Test the NoSubstitutionProxy.subst_list() method"""
        env = Environment(XXX = 'x', YYY = 'y')
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

    def test_subst_target_source(self):
        """Test the NoSubstitutionProxy.subst_target_source() method"""
        env = Environment(XXX = 'x', YYY = 'y')
        assert env['XXX'] == 'x', env['XXX']
        assert env['YYY'] == 'y', env['YYY']

        proxy = NoSubstitutionProxy(env)
        assert proxy['XXX'] == 'x', proxy['XXX']
        assert proxy['YYY'] == 'y', proxy['YYY']

        args = ('$XXX $TARGET $SOURCE $YYY',)
        kw = {'target' : DummyNode('ttt'), 'source' : DummyNode('sss')}
        x = apply(env.subst_target_source, args, kw)
        assert x == 'x ttt sss y', x
        x = apply(proxy.subst_target_source, args, kw)
        assert x == ' ttt sss ', x



if __name__ == "__main__":
    suite = unittest.TestSuite()
    tclasses = [ SubstitutionTestCase,
                 BaseTestCase,
                 NoSubstitutionProxyTestCase ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(map(tclass, names))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
