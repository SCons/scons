#
# Copyright (c) 2001 Steven Knight
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

from SCons.Environment import *



built_it = {}

class Builder:
    """A dummy Builder class for testing purposes.  "Building"
    a target is simply setting a value in the dictionary.
    """
    def __init__(self, name = None):
    	self.name = name

    def execute(self, target = None, **kw):
	built_it[target] = 1



scanned_it = {}

class Scanner:
    """A dummy Scanner class for testing purposes.  "Scanning"
    a target is simply setting a value in the dictionary.
    """
    def __init__(self, name, skeys=[]):
        self.name = name
        self.skeys = skeys

    def scan(self, filename):
        scanned_it[filename] = 1

    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)



class EnvironmentTestCase(unittest.TestCase):

    def test_Builders(self):
	"""Test Builder execution through different environments

	One environment is initialized with a single
	Builder object, one with a list of a single Builder
	object, and one with a list of two Builder objects.
	"""
	global built_it

	b1 = Builder(name = 'builder1')
	b2 = Builder(name = 'builder2')

	built_it = {}
	env1 = Environment(BUILDERS = b1)
	env1.builder1.execute(target = 'out1')
	assert built_it['out1']

	built_it = {}
	env2 = Environment(BUILDERS = [b1])
	env1.builder1.execute(target = 'out1')
	assert built_it['out1']

	built_it = {}
        env3 = Environment()
        env3.Update(BUILDERS = [b1, b2])
	env3.builder1.execute(target = 'out1')
	env3.builder2.execute(target = 'out2')
	env3.builder1.execute(target = 'out3')
	assert built_it['out1']
	assert built_it['out2']
	assert built_it['out3']

        env4 = env3.Copy()
        assert env4.builder1.env is env4
        assert env4.builder2.env is env4

    def test_Scanners(self):
        """Test Scanner execution through different environments

        One environment is initialized with a single
        Scanner object, one with a list of a single Scanner
        object, and one with a list of two Scanner objects.
        """
        global scanned_it

	s1 = Scanner(name = 'scanner1', skeys = [".c", ".cc"])
	s2 = Scanner(name = 'scanner2', skeys = [".m4"])

	scanned_it = {}
	env1 = Environment(SCANNERS = s1)
	env1.scanner1.scan(filename = 'out1')
	assert scanned_it['out1']

	scanned_it = {}
	env2 = Environment(SCANNERS = [s1])
	env1.scanner1.scan(filename = 'out1')
	assert scanned_it['out1']

	scanned_it = {}
        env3 = Environment()
        env3.Update(SCANNERS = [s1, s2])
	env3.scanner1.scan(filename = 'out1')
	env3.scanner2.scan(filename = 'out2')
	env3.scanner1.scan(filename = 'out3')
	assert scanned_it['out1']
	assert scanned_it['out2']
	assert scanned_it['out3']

	s = env3.get_scanner(".c")
	assert s == s1, s
	s = env3.get_scanner(skey=".m4")
	assert s == s2, s
	s = env3.get_scanner(".cxx")
	assert s == None, s

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
	env2.Update(YYY = 'yyy')
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
	assert env1 == env2

    def test_Install(self):
	"""Test Install method"""
        env=Environment()
        tgt = env.Install('export', [ 'build/foo1', 'build/foo2' ])
        paths = map(str, tgt)
        paths.sort()
        expect = map(os.path.normpath, [ 'export/foo1', 'export/foo2' ])
        assert paths == expect, paths
        for tnode in tgt:
            assert tnode.builder == InstallBuilder

    def test_InstallAs(self):
	pass	# XXX

    def test_Update(self):
	"""Test updating an Environment with new construction variables

	After creation of the Environment, of course.
	"""
	env1 = Environment(AAA = 'a', BBB = 'b')
	env1.Update(BBB = 'bbb', CCC = 'ccc')
	env2 = Environment(AAA = 'a', BBB = 'bbb', CCC = 'c')
	assert env1 != env2

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

    def test_Command(self):
        """Test the Command() method."""
        env = Environment()
        t = env.Command(target='foo.out', source=['foo1.in', 'foo2.in'],
                        action='buildfoo $target $source')
        assert t.builder
        assert t.builder.action.__class__.__name__ == 'CommandAction'
        assert t.builder.action.command == 'buildfoo $target $source'
        assert 'foo1.in' in map(lambda x: x.path, t.sources)
        assert 'foo2.in' in map(lambda x: x.path, t.sources)

        def testFunc(env, target, source):
            assert target == 'foo.out'
            assert 'foo1.in' in source and 'foo2.in' in source, source
            return 0
        t = env.Command(target='foo.out', source=['foo1.in','foo2.in'],
                        action=testFunc)
        assert t.builder
        assert t.builder.action.__class__.__name__ == 'FunctionAction'
        t.build()
        assert 'foo1.in' in map(lambda x: x.path, t.sources)
        assert 'foo2.in' in map(lambda x: x.path, t.sources)

    def test_subst(self):
	"""Test substituting construction variables within strings
	
	Check various combinations, including recursive expansion
	of variables into other variables.
	"""
	env = Environment(AAA = 'a', BBB = 'b')
	str = env.subst("$AAA ${AAA}A $BBBB $BBB")
	assert str == "a aA b", str
	env = Environment(AAA = '$BBB', BBB = 'b', BBBA = 'foo')
	str = env.subst("$AAA ${AAA}A ${AAA}B $BBB")
	assert str == "b foo b", str
	env = Environment(AAA = '$BBB', BBB = '$CCC', CCC = 'c')
	str = env.subst("$AAA ${AAA}A ${AAA}B $BBB")
	assert str == "c c", str



if __name__ == "__main__":
    suite = unittest.makeSuite(EnvironmentTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
