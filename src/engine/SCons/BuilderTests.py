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


class BuilderTestCase(unittest.TestCase):

    def test__call__(self):
	"""Test calling a builder to establish source dependencies
	"""
	class Environment:
	    pass
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
	assert test.read(outfile, 'r') == "act.py: xyzzy\n"

	def function1(kw):
	    open(kw['out'], 'w').write("function1\n")
	    return 1

	builder = SCons.Builder.Builder(action = function1)
	r = builder.execute(out = outfile)
	assert r == 1
	assert test.read(outfile, 'r') == "function1\n"

	class class1a:
	    def __init__(self, kw):
		open(kw['out'], 'w').write("class1a\n")

	builder = SCons.Builder.Builder(action = class1a)
	r = builder.execute(out = outfile)
	assert r.__class__ == class1a
	assert test.read(outfile, 'r') == "class1a\n"

	class class1b:
	    def __call__(self, kw):
		open(kw['out'], 'w').write("class1b\n")
		return 2

	builder = SCons.Builder.Builder(action = class1b())
	r = builder.execute(out = outfile)
	assert r == 2
	assert test.read(outfile, 'r') == "class1b\n"

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
	assert test.read(outfile, 'r') == "act.py: syzygy\nfunction2\nclass2a\nclass2b\n"

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



if __name__ == "__main__":
    suite = unittest.makeSuite(BuilderTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
