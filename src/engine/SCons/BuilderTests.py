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
	and one is an internal Python function.
	"""
	cmd = "python %s %s xyzzy" % (act_py, outfile)
	builder = SCons.Builder.Builder(action = cmd)
	builder.execute()
	assert test.read(outfile, 'r') == "act.py: xyzzy\n"

	def function(kw):
	    import os, string, sys
	    f = open(kw['out'], 'w')
	    f.write("function\n")
	    f.close()
	    return not None

	builder = SCons.Builder.Builder(action = function)
	builder.execute(out = outfile)
	assert test.read(outfile, 'r') == "function\n"

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

    def test_node_class(self):
	"""Test a Builder that creates nodes of a specified class
	"""
	class Foo:
		pass
	builder = SCons.Builder.Builder(node_class = Foo)
	assert builder.node_class is Foo

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
