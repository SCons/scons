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

    def test_ENV(self):
	"""Test setting the external ENV in Environments
	"""
	env = Environment()
	assert env.Dictionary().has_key('ENV')

	env = Environment(ENV = { 'PATH' : '/foo:/bar' })
	assert env.Dictionary('ENV')['PATH'] == '/foo:/bar'

    def test_Environment(self):
	"""Test construction Environments creation
	
	Create two with identical arguments and check that
	they compare the same.
	"""
	env1 = Environment(XXX = 'x', YYY = 'y')
	env2 = Environment(XXX = 'x', YYY = 'y')
	assert env1 == env2, diff_env(env1, env2)

    def test_Install(self):
	"""Test Install and InstallAs methods"""
        env=Environment()
        tgt = env.Install('export', [ 'build/foo1', 'build/foo2' ])
        paths = map(str, tgt)
        paths.sort()
        expect = map(os.path.normpath, [ 'export/foo1', 'export/foo2' ])
        assert paths == expect, paths
        for tnode in tgt:
            assert tnode.builder == InstallBuilder

        tgt = env.InstallAs(target=string.split('foo1 foo2'),
                            source=string.split('bar1 bar2'))
        assert len(tgt) == 2, len(tgt)
        paths = map(lambda x: str(x.sources[0]), tgt)
        paths.sort()
        expect = map(os.path.normpath, [ 'bar1', 'bar2' ])
        assert paths == expect, paths
        for tnode in tgt:
            assert tnode.builder == InstallBuilder

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

    def test_Append(self):
        """Test appending to construction variables in an Environment
        """
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

    def test_Depends(self):
	"""Test the explicit Depends method."""
	env = Environment()
	t = env.Depends(target='EnvironmentTest.py', dependency='Environment.py')
	assert t.__class__.__name__ == 'File'
	assert t.path == 'EnvironmentTest.py'
	assert len(t.depends) == 1
	d = t.depends[0]
	assert d.__class__.__name__ == 'File'
	assert d.path == 'Environment.py'

    def test_Ignore(self):
        """Test the explicit Ignore method."""
        env = Environment()
        t = env.Ignore(target='targ.py', dependency='dep.py')
        assert t.__class__.__name__ == 'File'
        assert t.path == 'targ.py'
        assert len(t.ignore) == 1
        i = t.ignore[0]
        assert i.__class__.__name__ == 'File'
        assert i.path == 'dep.py'

    def test_Precious(self):
        """Test the Precious() method."""
        env = Environment()
        t = env.Precious('a', 'b', ['c', 'd'])
        assert t[0].__class__.__name__ == 'File'
        assert t[0].path == 'a'
        assert t[0].precious
        assert t[1].__class__.__name__ == 'File'
        assert t[1].path == 'b'
        assert t[1].precious
        assert t[2].__class__.__name__ == 'File'
        assert t[2].path == 'c'
        assert t[2].precious
        assert t[3].__class__.__name__ == 'File'
        assert t[3].path == 'd'
        assert t[3].precious

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

    def test_SourceCode(self):
        """Test the SourceCode() method."""
        env = Environment()
        e = env.SourceCode('foo', None)
        s = e.src_builder()
        assert s is None, s

        b = Builder()
        env.SourceCode(e, b)
        s = e.src_builder()
        assert s is b, s

    def test_SideEffect(self):
        """Test the SideEffect() method"""
        env = Environment()
        foo = env.Object('foo.obj', 'foo.cpp')
        bar = env.Object('bar.obj', 'bar.cpp')
        s = env.SideEffect('mylib.pdb', ['foo.obj', 'bar.obj'])
        assert s.side_effect
        assert foo.side_effects == [s]
        assert bar.side_effects == [s]
        assert s.depends_on([bar])
        assert s.depends_on([foo])

    def test_subst(self):
	"""Test substituting construction variables within strings
	
	Check various combinations, including recursive expansion
	of variables into other variables.
	"""
	env = Environment(AAA = 'a', BBB = 'b')
	str = env.subst("$AAA ${AAA}A $BBBB $BBB")
	assert str == "a aA b", str

        # Changed the tests below to reflect a bug fix in
        # subst()
        env = Environment(AAA = '$BBB', BBB = 'b', BBBA = 'foo')
	str = env.subst("$AAA ${AAA}A ${AAA}B $BBB")
	assert str == "b bA bB b", str
	env = Environment(AAA = '$BBB', BBB = '$CCC', CCC = 'c')
	str = env.subst("$AAA ${AAA}A ${AAA}B $BBB")
	assert str == "c cA cB c", str

        env = Environment(AAA = '$BBB', BBB = '$CCC', CCC = [ 'a', 'b\nc' ])
        lst = env.subst_list([ "$AAA", "B $CCC" ])
        assert lst == [ [ "a", "b" ], [ "c", "B a", "b" ], [ "c" ] ], lst

        # Test callables in the Environment
        def foo(target, source, env):
            assert target == 1, target
            assert source == 2, source
            return env["FOO"]

        env = Environment(BAR=foo, FOO='baz')

        subst = env.subst('test $BAR', target=1, source=2)
        assert subst == 'test baz', subst

        lst = env.subst_list('test $BAR', target=1, source=2)
        assert lst[0][0] == 'test', lst[0][0]
        assert lst[0][1] == 'baz', lst[0][1]

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

    def test_platform(self):
        """Test specifying a platform callable when instantiating."""
        def p(env):
            env['XYZZY'] = 777
        env = Environment(platform = p)
        assert env['XYZZY'] == 777, env

    def test_tools(self):
        """Test specifying a tool callable when instantiating."""
        def t1(env, platform):
            env['TOOL1'] = 111
        def t2(env, platform):
            env['TOOL2'] = 222
        def t3(env, platform):
            env['AAA'] = env['XYZ']
        env = Environment(tools = [t1, t2, t3], XYZ = 'aaa')
        assert env['TOOL1'] == 111, env['TOOL1']
        assert env['TOOL2'] == 222, env
        assert env['AAA'] == 'aaa', env

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

    def test_sig_dict(self):
        """Test the sig_dict() method"""
        d = Environment(XYZZY = 'foo').sig_dict()

        assert d['XYZZY'] == 'foo'

        s = str(d['TARGET'])
        assert s == '__t1__', s
        s = str(d['TARGET'].dir)
        assert s == '', s
        s = str(d['TARGETS'])
        assert s == '__t1__ __t2__', s
        s = str(d['TARGETS'][1])
        assert s == '__t2__', s
        s = str(d['TARGETS'][2])
        assert s == '__t3__', s
        s = str(d['TARGETS'][87])
        assert s == '__t88__', s
        s = str(d['TARGETS'][87].dir)
        assert s == '', s
        s = map(str, d['TARGETS'][3:5])
        assert s == ['__t4__', '__t5__'], s
        s = map(lambda x: os.path.normcase(str(x)), d['TARGETS'].abspath)
        assert s == map(os.path.normcase, [ os.path.join(os.getcwd(), '__t1__'),
                                            os.path.join(os.getcwd(), '__t2__') ])

        s = str(d['SOURCE'])
        assert s == '__s1__', s
        s = str(d['SOURCE'].dir)
        assert s == '', s
        s = str(d['SOURCES'])
        assert s == '__s1__ __s2__', s
        s = str(d['SOURCES'][1])
        assert s == '__s2__', s
        s = str(d['SOURCES'][2])
        assert s == '__s3__', s
        s = str(d['SOURCES'][87])
        assert s == '__s88__', s
        s = str(d['SOURCES'][87].dir)
        assert s == '', s
        s = map(str, d['SOURCES'][3:5])
        assert s == ['__s4__', '__s5__'], s
        s = map(lambda x: os.path.normcase(str(x)), d['SOURCES'].abspath)
        assert s == map(os.path.normcase, [ os.path.join(os.getcwd(), '__s1__'),
                                            os.path.join(os.getcwd(), '__s2__') ])

        
if __name__ == "__main__":
    suite = unittest.makeSuite(EnvironmentTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
