__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import sys
import unittest
import SCons.Node.FS
from SCons.Util import scons_str2nodes


class UtilTestCase(unittest.TestCase):
    def test_str2nodes(self):
	"""Test the str2nodes function."""
	nodes = scons_str2nodes("Util.py UtilTests.py")
	assert len(nodes) == 2
	assert isinstance(nodes[0], SCons.Node.FS.File)
	assert isinstance(nodes[1], SCons.Node.FS.File)
	assert nodes[0].path == "Util.py"
	assert nodes[1].path == "UtilTests.py"

	nodes = scons_str2nodes("Util.py UtilTests.py", SCons.Node.FS.FS())
	assert len(nodes) == 2
	assert isinstance(nodes[0], SCons.Node.FS.File)
	assert isinstance(nodes[1], SCons.Node.FS.File)
	assert nodes[0].path == "Util.py"
	assert nodes[1].path == "UtilTests.py"

	nodes = scons_str2nodes(["Util.py", "UtilTests.py"])
	assert len(nodes) == 2
	assert isinstance(nodes[0], SCons.Node.FS.File)
	assert isinstance(nodes[1], SCons.Node.FS.File)
	assert nodes[0].path == "Util.py"
	assert nodes[1].path == "UtilTests.py"

	n1 = SCons.Node.FS.default_fs.File("Util.py")
	nodes = scons_str2nodes([n1, "UtilTests.py"])
	assert len(nodes) == 2
	assert isinstance(nodes[0], SCons.Node.FS.File)
	assert isinstance(nodes[1], SCons.Node.FS.File)
	assert nodes[0].path == "Util.py"
	assert nodes[1].path == "UtilTests.py"


if __name__ == "__main__":
    suite = unittest.makeSuite(UtilTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
