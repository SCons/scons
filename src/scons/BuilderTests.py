__revision__ = "BuilderTests.py __REVISION__ __DATE__ __DEVELOPER__"

import sys
import unittest

from scons.Builder import Builder
from TestCmd import TestCmd


# Initial setup of the common environment for all tests,
# a temporary working directory containing a
# script for writing arguments to an output file.
#
# We don't do this as a setUp() method because it's
# unnecessary to create a separate directory and script
# for each test, they can just use the one.
test = TestCmd(workdir = '')

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
	"""Test the simple ability to create a Builder
	and retrieve the supplied action attribute.
	"""
	builder = Builder(action = "foo")
	assert builder.action == "foo"

    def test_cmp(self):
	"""Test simple comparisons of Builder objects.
	"""
	b1 = Builder(input_suffix = '.o')
	b2 = Builder(input_suffix = '.o')
	assert b1 == b2
	b3 = Builder(input_suffix = '.x')
	assert b1 != b3
	assert b2 != b3

    def test_execute(self):
	"""Test the ability to execute simple Builders, one
	a string that executes an external command, and one an
	internal function.
	"""
	cmd = "python %s %s xyzzy" % (act_py, outfile)
	builder = Builder(action = cmd)
	builder.execute()
	assert test.read(outfile) == "act.py: xyzzy\n"

	def function(kw):
	    import os, string, sys
	    f = open(kw['out'], 'w')
	    f.write("function\n")
	    f.close()
	    return not None

	builder = Builder(action = function)
	builder.execute(out = outfile)
	assert test.read(outfile) == "function\n"

    def test_insuffix(self):
	"""Test the ability to create a Builder with a specified
	input suffix, making sure that the '.' separator is
	appended to the beginning if it isn't already present.
	"""
	builder = Builder(input_suffix = '.c')
	assert builder.insuffix == '.c'
	builder = Builder(input_suffix = 'c')
	assert builder.insuffix == '.c'

    def test_name(self):
	"""Test the ability to create a Builder with a specified
	name.
	"""
	builder = Builder(name = 'foo')
	assert builder.name == 'foo'

    def test_node_class(self):
	"""Test the ability to create a Builder that creates nodes
	of the specified class.
	"""
	class Foo:
		pass
	builder = Builder(node_class = Foo)
	assert builder.node_class is Foo

    def test_outsuffix(self):
	"""Test the ability to create a Builder with a specified
	output suffix, making sure that the '.' separator is
	appended to the beginning if it isn't already present.
	"""
	builder = Builder(input_suffix = '.o')
	assert builder.insuffix == '.o'
	builder = Builder(input_suffix = 'o')
	assert builder.insuffix == '.o'



if __name__ == "__main__":
    suite = unittest.makeSuite(BuilderTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
