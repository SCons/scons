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

import TestCmd
import SCons.Builder


# Initial setup of the common environment for all tests,
# a temporary working directory containing a
# script for writing arguments to an output file.
#
# We don't do this as a setUp() method because it's
# unnecessary to create a separate directory and script
# for each test, they can just use the one.
test = TestCmd.TestCmd(workdir = '')

test.write('act.py', """import os, string, sys
f = open(sys.argv[1], 'w')
f.write("act.py: " + string.join(sys.argv[2:]) + "\\n")
f.close()
sys.exit(0)
""")

act_py = test.workpath('act.py')
outfile = test.workpath('outfile')

class Environment:
            def subst(self, s):
                return s
env = Environment()

class BuilderTestCase(unittest.TestCase):

    def test__call__(self):
	"""Test calling a builder to establish source dependencies
	"""
	env = Environment()
	class Node:
	    def __init__(self, name):
		self.name = name
		self.sources = []
		self.derived = 0
	    def builder_set(self, builder):
		self.builder = builder
	    def env_set(self, env):
		self.env = env
	    def add_source(self, source):
		self.sources.extend(source)
	builder = SCons.Builder.Builder(action = "foo")
	n1 = Node("n1");
	n2 = Node("n2");
	builder(env, target = n1, source = n2)
	assert n1.env == env
	assert n1.builder == builder
	assert n1.sources == [n2]
	assert n1.derived == 1

    def test_action(self):
	"""Test Builder creation

	Verify that we can retrieve the supplied action attribute.
	"""
	builder = SCons.Builder.Builder(action = "foo")
	assert builder.action.command == "foo"

    def test_cmp(self):
	"""Test simple comparisons of Builder objects
	"""
	b1 = SCons.Builder.Builder(input_suffix = '.o')
	b2 = SCons.Builder.Builder(input_suffix = '.o')
	assert b1 == b2
	b3 = SCons.Builder.Builder(input_suffix = '.x')
	assert b1 != b3
	assert b2 != b3

    def test_execute(self):
	"""Test execution of simple Builder objects
	
	One Builder is a string that executes an external command,
	one is an internal Python function, one is a list
	containing one of each.
	"""

	cmd1 = "python %s %s xyzzy" % (act_py, outfile)

	builder = SCons.Builder.Builder(action = cmd1)
	r = builder.execute()
	assert r == 0
	c = test.read(outfile, 'r')
	assert c == "act.py: xyzzy\n", c

	cmd2 = "python %s %s $target" % (act_py, outfile)

	builder = SCons.Builder.Builder(action = cmd2)
	r = builder.execute(target = 'foo')
	assert r == 0
	c = test.read(outfile, 'r')
	assert c == "act.py: foo\n", c

	cmd3 = "python %s %s ${targets}" % (act_py, outfile)

	builder = SCons.Builder.Builder(action = cmd3)
	r = builder.execute(target = ['aaa', 'bbb'])
	assert r == 0
	c = test.read(outfile, 'r')
	assert c == "act.py: aaa bbb\n", c

	cmd4 = "python %s %s $sources" % (act_py, outfile)

	builder = SCons.Builder.Builder(action = cmd4)
	r = builder.execute(source = ['one', 'two'])
	assert r == 0
	c = test.read(outfile, 'r')
	assert c == "act.py: one two\n", c

	cmd4 = "python %s %s ${sources[:2]}" % (act_py, outfile)

	builder = SCons.Builder.Builder(action = cmd4)
	r = builder.execute(source = ['three', 'four', 'five'])
	assert r == 0
	c = test.read(outfile, 'r')
	assert c == "act.py: three four\n", c

	def function1(kw):
	    open(kw['out'], 'w').write("function1\n")
	    return 1

	builder = SCons.Builder.Builder(action = function1)
	r = builder.execute(out = outfile)
	assert r == 1
	c = test.read(outfile, 'r')
	assert c == "function1\n", c

	class class1a:
	    def __init__(self, kw):
		open(kw['out'], 'w').write("class1a\n")

	builder = SCons.Builder.Builder(action = class1a)
	r = builder.execute(out = outfile)
	assert r.__class__ == class1a
	c = test.read(outfile, 'r')
	assert c == "class1a\n", c

	class class1b:
	    def __call__(self, kw):
		open(kw['out'], 'w').write("class1b\n")
		return 2

	builder = SCons.Builder.Builder(action = class1b())
	r = builder.execute(out = outfile)
	assert r == 2
	c = test.read(outfile, 'r')
	assert c == "class1b\n", c

	cmd2 = "python %s %s syzygy" % (act_py, outfile)

	def function2(kw):
	    open(kw['out'], 'a').write("function2\n")
	    return 0

	class class2a:
	    def __call__(self, kw):
		open(kw['out'], 'a').write("class2a\n")
		return 0

	class class2b:
	    def __init__(self, kw):
		open(kw['out'], 'a').write("class2b\n")

	builder = SCons.Builder.Builder(action = [cmd2, function2, class2a(), class2b])
	r = builder.execute(out = outfile)
	assert r.__class__ == class2b
	c = test.read(outfile, 'r')
	assert c == "act.py: syzygy\nfunction2\nclass2a\nclass2b\n", c

    def test_insuffix(self):
	"""Test Builder creation with a specified input suffix
	
	Make sure that the '.' separator is appended to the
	beginning if it isn't already present.
	"""
	builder = SCons.Builder.Builder(input_suffix = '.c')
	assert builder.insuffix == '.c'
	builder = SCons.Builder.Builder(input_suffix = 'c')
	assert builder.insuffix == '.c'

    def test_name(self):
	"""Test Builder creation with a specified name
	"""
	builder = SCons.Builder.Builder(name = 'foo')
	assert builder.name == 'foo'

    def test_node_factory(self):
	"""Test a Builder that creates nodes of a specified class
	"""
	class Foo:
	    pass
	def FooFactory(target):
	    return Foo(target)
	builder = SCons.Builder.Builder(node_factory = FooFactory)
	assert builder.node_factory is FooFactory

    def test_outsuffix(self):
	"""Test Builder creation with a specified output suffix

	Make sure that the '.' separator is appended to the
	beginning if it isn't already present.
	"""
	builder = SCons.Builder.Builder(input_suffix = '.o')
	assert builder.insuffix == '.o'
	builder = SCons.Builder.Builder(input_suffix = 'o')
	assert builder.insuffix == '.o'

    def test_TargetNamingBuilder(self):
        """Testing the TargetNamingBuilder class."""
        builder = SCons.Builder.Builder(action='foo')
        proxy = SCons.Builder.TargetNamingBuilder(builder=builder,
                                                  prefix='foo',
                                                  suffix='bar')
        tgt = proxy(env, target='baz', source='bleh')
        assert tgt.path == 'foobazbar', \
               "Target has unexpected name: %s" % tgt[0].path
        assert tgt.builder == builder

    def test_MultiStepBuilder(self):
        """Testing MultiStepBuilder class."""
        builder1 = SCons.Builder.Builder(action='foo',
                                        input_suffix='.bar',
                                        output_suffix='.foo')
        builder2 = SCons.Builder.MultiStepBuilder(action='foo',
                                                  builders = [ builder1 ])
        tgt = builder2(env, target='baz', source='test.bar test2.foo test3.txt')
        flag = 0
        for snode in tgt.sources:
            if snode.path == 'test.foo':
                flag = 1
                assert snode.sources[0].path == 'test.bar'
        assert flag


if __name__ == "__main__":
    suite = unittest.makeSuite(BuilderTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
