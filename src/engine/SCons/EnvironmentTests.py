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

    def __call__(self, env, **kw):
        global called_it
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
        scanned_it[filename] = 1

    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)



class EnvironmentTestCase(unittest.TestCase):

    def test___init__(self):
	"""Test construction Environments creation
	
	Create two with identical arguments and check that
	they compare the same.
	"""
	env1 = Environment(XXX = 'x', YYY = 'y')
	env2 = Environment(XXX = 'x', YYY = 'y')
	assert env1 == env2, diff_env(env1, env2)

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

    def test_arg2nodes(self):
        """Test the arg2nodes method
        """
        env = Environment()
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

        env_ll = env.Copy()
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

    def test_subst(self):
	"""Test substituting construction variables within strings
	
	Check various combinations, including recursive expansion
	of variables into other variables.
	"""
	env = Environment(AAA = 'a', BBB = 'b')
	mystr = env.subst("$AAA ${AAA}A $BBBB $BBB")
	assert mystr == "a aA b", str

        # Changed the tests below to reflect a bug fix in
        # subst()
        env = Environment(AAA = '$BBB', BBB = 'b', BBBA = 'foo')
	mystr = env.subst("$AAA ${AAA}A ${AAA}B $BBB")
	assert mystr == "b bA bB b", str
	env = Environment(AAA = '$BBB', BBB = '$CCC', CCC = 'c')
	mystr = env.subst("$AAA ${AAA}A ${AAA}B $BBB")
	assert mystr == "c cA cB c", str

        env = Environment(AAA = '$BBB', BBB = '$CCC', CCC = [ 'a', 'b\nc' ])
        lst = env.subst_list([ "$AAA", "B $CCC" ])
        assert lst == [ [ "a", "b" ], [ "c", "B a", "b" ], [ "c" ] ], lst

        class DummyNode:
            def __init__(self, name):
                self.name = name
            def __str__(self):
                return self.name
            def rfile(self):
                return self
            def get_subst_proxy(self):
                return self

        # Test callables in the Environment
        def foo(target, source, env, for_signature):
            assert str(target) == 't', target
            assert str(source) == 's', source
            return env["FOO"]

        env = Environment(BAR=foo, FOO='baz')

        subst = env.subst('test $BAR', target=DummyNode('t'), source=DummyNode('s'))
        assert subst == 'test baz', subst

        lst = env.subst_list('test $BAR', target=DummyNode('t'), source=DummyNode('s'))
        assert lst[0][0] == 'test', lst[0][0]
        assert lst[0][1] == 'baz', lst[0][1]

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
        env.builder1(target = 'out1')
        assert called_it['target'] == 'out1', called_it
        assert not called_it.has_key('source')

        called_it = {}
        env.builder2(target = 'out2', xyzzy = 1)
        assert called_it['target'] == 'out2', called_it
        assert called_it['xyzzy'] == 1, called_it
        assert not called_it.has_key('source')

        called_it = {}
        env.builder1(foo = 'bar')
        assert called_it['foo'] == 'bar', called_it
        assert not called_it.has_key('target')
        assert not called_it.has_key('source')



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
        """Test Scanner execution through different environments

        One environment is initialized with a single
        Scanner object, one with a list of a single Scanner
        object, and one with a list of two Scanner objects.
        """
#        global scanned_it
#
#	s1 = Scanner(name = 'scanner1', skeys = [".c", ".cc"])
#	s2 = Scanner(name = 'scanner2', skeys = [".m4"])
#
#	scanned_it = {}
#	env1 = Environment(SCANNERS = s1)
#        env1.scanner1(filename = 'out1')
#	assert scanned_it['out1']
#
#	scanned_it = {}
#	env2 = Environment(SCANNERS = [s1])
#        env1.scanner1(filename = 'out1')
#	assert scanned_it['out1']
#
#	scanned_it = {}
#        env3 = Environment()
#        env3.Replace(SCANNERS = [s1, s2])
#        env3.scanner1(filename = 'out1')
#        env3.scanner2(filename = 'out2')
#        env3.scanner1(filename = 'out3')
#	assert scanned_it['out1']
#	assert scanned_it['out2']
#	assert scanned_it['out3']
#
#	s = env3.get_scanner(".c")
#	assert s == s1, s
#	s = env3.get_scanner(skey=".m4")
#	assert s == s2, s
#	s = env3.get_scanner(".cxx")
#	assert s == None, s

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
        assert flags[0] == 'foofoobar', \
               flags[0]
        assert flags[1] == 'foobarbar', \
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
        assert flags[4] == os.path.normpath('xx/baz/barbar'), \
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
        assert flags[4] == os.path.normpath('xx/baz/barbar'), \
               flags[4]
        assert flags[5] == os.path.normpath('foo'), \
               flags[5]
        assert flags[6] == os.path.normpath('blatbar'), \
               flags[6]
        assert flags[7] == '$)', \
               flags[7]

        env = Environment(CPPPATH = '', F77PATH = '', LIBPATH = '',
                          RDirs=RDirs)
        assert len(env.subst_list('$_CPPINCFLAGS')[0]) == 0
        assert len(env.subst_list('$_F77INCFLAGS')[0]) == 0
        assert len(env.subst_list('$_LIBDIRFLAGS')[0]) == 0

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

    def test_concat(self):
        "Test _concat()"
        e1 = Environment(PRE='pre', SUF='suf', STR='a b', LIST=['a', 'b'])
        s = e1.subst
        assert s("${_concat('', '', '', __env__)}") == ''
        assert s("${_concat('', [], '', __env__)}") == ''
        assert s("${_concat(PRE, '', SUF, __env__)}") == ''
        assert s("${_concat(PRE, STR, SUF, __env__)}") == 'prea bsuf'
        assert s("${_concat(PRE, LIST, SUF, __env__)}") == 'preasuf prebsuf'



    def test_Append(self):
        """Test appending to construction variables in an Environment
        """

        b1 = Environment()['BUILDERS']
        b2 = Environment()['BUILDERS']
        assert b1 == b2, diff_dict(b1, b2)
        
        import UserList
        UL = UserList.UserList
        env1 = Environment(AAA = 'a', BBB = 'b', CCC = 'c', DDD = 'd',
                           EEE = ['e'], FFF = ['f'], GGG = ['g'], HHH = ['h'],
                           III = UL(['i']), JJJ = UL(['j']),
                           KKK = UL(['k']), LLL = UL(['l']))
        env1.Append(BBB = 'B', CCC = ['C'], DDD = UL(['D']),
                    FFF = 'F', GGG = ['G'], HHH = UL(['H']),
                    JJJ = 'J', KKK = ['K'], LLL = UL(['L']))
        env2 = Environment(AAA = 'a', BBB = 'bB',
                           CCC = ['c', 'C'], DDD = UL(['d', 'D']),
                           EEE = ['e'], FFF = ['f', 'F'],
                           GGG = ['g', 'G'], HHH = UL(['h', 'H']),
                           III = UL(['i']), JJJ = UL(['j', 'J']),
                           KKK = UL(['k', 'K']), LLL = UL(['l', 'L']))
        assert env1 == env2, diff_env(env1, env2)

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
	env2.Replace(YYY = 'yyy')
	assert env1 != env2
	assert env1 == env1copy

	env3 = env1.Copy(XXX = 'x3', ZZZ = 'z3')
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

    def test_Override(self):
        "Test overriding construction variables"
        env = Environment(ONE=1, TWO=2)
        assert env['ONE'] == 1
        assert env['TWO'] == 2
        env2 = env.Override({'TWO':'10'})
        assert env2['ONE'] == 1
        assert env2['TWO'] == '10'
        assert env['TWO'] == 2
        env2.Replace(ONE = "won")
        assert env2['ONE'] == "won"
        assert env['ONE'] == 1

    def test_Prepend(self):
        """Test prepending to construction variables in an Environment
        """
        import UserList
        UL = UserList.UserList
        env1 = Environment(AAA = 'a', BBB = 'b', CCC = 'c', DDD = 'd',
                           EEE = ['e'], FFF = ['f'], GGG = ['g'], HHH = ['h'],
                           III = UL(['i']), JJJ = UL(['j']),
                           KKK = UL(['k']), LLL = UL(['l']))
        env1.Prepend(BBB = 'B', CCC = ['C'], DDD = UL(['D']),
                    FFF = 'F', GGG = ['G'], HHH = UL(['H']),
                    JJJ = 'J', KKK = ['K'], LLL = UL(['L']))
        env2 = Environment(AAA = 'a', BBB = 'Bb',
                           CCC = ['C', 'c'], DDD = UL(['D', 'd']),
                           EEE = ['e'], FFF = ['F', 'f'],
                           GGG = ['G', 'g'], HHH = UL(['H', 'h']),
                           III = UL(['i']), JJJ = UL(['J', 'j']),
                           KKK = UL(['K', 'k']), LLL = UL(['L', 'l']))
        assert env1 == env2, diff_env(env1, env2)

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

    def test_Command(self):
        """Test the Command() method."""
        env = Environment()
        t = env.Command(target='foo.out', source=['foo1.in', 'foo2.in'],
                        action='buildfoo $target $source')
        assert not t.builder is None
        assert t.builder.action.__class__.__name__ == 'CommandAction'
        assert t.builder.action.cmd_list == 'buildfoo $target $source'
        assert 'foo1.in' in map(lambda x: x.path, t.sources)
        assert 'foo2.in' in map(lambda x: x.path, t.sources)

        sub = SCons.Node.FS.default_fs.Dir('sub')
        t = env.Command(target='bar.out', source='sub',
                        action='buildbar $target $source')
        assert 'sub' in map(lambda x: x.path, t.sources)

        def testFunc(env, target, source):
            assert str(target[0]) == 'foo.out'
            assert 'foo1.in' in map(str, source) and 'foo2.in' in map(str, source), map(str, source)
            return 0
        t = env.Command(target='foo.out', source=['foo1.in','foo2.in'],
                        action=testFunc)
        assert not t.builder is None
        assert t.builder.action.__class__.__name__ == 'FunctionAction'
        t.build()
        assert 'foo1.in' in map(lambda x: x.path, t.sources)
        assert 'foo2.in' in map(lambda x: x.path, t.sources)

    def test_Depends(self):
	"""Test the explicit Depends method."""
	env = Environment(FOO = 'xxx', BAR='yyy')
	t = env.Depends(target='EnvironmentTest.py', dependency='Environment.py')
	assert t.__class__.__name__ == 'File'
	assert t.path == 'EnvironmentTest.py'
	assert len(t.depends) == 1
	d = t.depends[0]
	assert d.__class__.__name__ == 'File'
	assert d.path == 'Environment.py'

	t = env.Depends(target='${FOO}.py', dependency='${BAR}.py')
	assert t.__class__.__name__ == 'File'
	assert t.path == 'xxx.py'
	assert len(t.depends) == 1
	d = t.depends[0]
	assert d.__class__.__name__ == 'File'
	assert d.path == 'yyy.py'

    def test_Ignore(self):
        """Test the explicit Ignore method."""
        env = Environment(FOO='yyy', BAR='zzz')
        t = env.Ignore(target='targ.py', dependency='dep.py')
        assert t.__class__.__name__ == 'File'
        assert t.path == 'targ.py'
        assert len(t.ignore) == 1
        i = t.ignore[0]
        assert i.__class__.__name__ == 'File'
        assert i.path == 'dep.py'
        t = env.Ignore(target='$FOO$BAR', dependency='$BAR$FOO')
        assert t.__class__.__name__ == 'File'
        assert t.path == 'yyyzzz'
        assert len(t.ignore) == 1
        i = t.ignore[0]
        assert i.__class__.__name__ == 'File'
        assert i.path == 'zzzyyy'

    def test_Install(self):
	"""Test Install and InstallAs methods"""
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

        tgt = env.InstallAs(target=string.split('foo1 foo2'),
                            source=string.split('bar1 bar2'))
        assert len(tgt) == 2, len(tgt)
        paths = map(lambda x: str(x.sources[0]), tgt)
        paths.sort()
        expect = map(os.path.normpath, [ 'bar1', 'bar2' ])
        assert paths == expect, paths
        for tnode in tgt:
            assert tnode.builder == InstallBuilder

        tgt = env.InstallAs(target='${FOO}.t', source='${BAR}.s')
        assert tgt.path == 'iii.t'
        assert tgt.sources[0].path == 'jjj.s'
        assert tgt.builder == InstallBuilder

    def test_Precious(self):
        """Test the Precious() method."""
        env = Environment(FOO='ggg', BAR='hhh')
        t = env.Precious('a', '${BAR}b', ['c', 'd'], '$FOO')
        assert t[0].__class__.__name__ == 'File'
        assert t[0].path == 'a'
        assert t[0].precious
        assert t[1].__class__.__name__ == 'File'
        assert t[1].path == 'hhhb'
        assert t[1].precious
        assert t[2].__class__.__name__ == 'File'
        assert t[2].path == 'c'
        assert t[2].precious
        assert t[3].__class__.__name__ == 'File'
        assert t[3].path == 'd'
        assert t[3].precious
        assert t[4].__class__.__name__ == 'File'
        assert t[4].path == 'ggg'
        assert t[4].precious

    def test_SideEffect(self):
        """Test the SideEffect() method"""
        env = Environment(LIB='lll', FOO='fff', BAR='bbb')

        foo = env.Object('foo.obj', 'foo.cpp')
        bar = env.Object('bar.obj', 'bar.cpp')
        s = env.SideEffect('mylib.pdb', ['foo.obj', 'bar.obj'])
        assert s.path == 'mylib.pdb'
        assert s.side_effect
        assert foo.side_effects == [s]
        assert bar.side_effects == [s]
        assert s.depends_on([bar])
        assert s.depends_on([foo])

        fff = env.Object('fff.obj', 'fff.cpp')
        bbb = env.Object('bbb.obj', 'bbb.cpp')
        s = env.SideEffect('my${LIB}.pdb', ['${FOO}.obj', '${BAR}.obj'])
        assert s.path == 'mylll.pdb'
        assert s.side_effect
        assert fff.side_effects == [s], fff.side_effects
        assert bbb.side_effects == [s], bbb.side_effects
        assert s.depends_on([bbb])
        assert s.depends_on([fff])

    def test_SourceCode(self):
        """Test the SourceCode() method."""
        env = Environment(FOO='mmm', BAR='nnn')
        e = env.SourceCode('foo', None)
        assert e.path == 'foo'
        s = e.src_builder()
        assert s is None, s

        b = Builder()
        e = env.SourceCode(e, b)
        assert e.path == 'foo'
        s = e.src_builder()
        assert s is b, s

        e = env.SourceCode('$BAR$FOO', None)
        assert e.path == 'nnnmmm'
        s = e.src_builder()
        assert s is None, s

        
if __name__ == "__main__":
    suite = unittest.makeSuite(EnvironmentTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
