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
import os.path
import unittest
import SCons.Node
import SCons.Node.FS
from SCons.Util import scons_str2nodes, scons_varrepl, PathList


class UtilTestCase(unittest.TestCase):
    def test_str2nodes(self):
	"""Test the str2nodes function."""
	nodes = scons_str2nodes("Util.py UtilTests.py")
	assert len(nodes) == 2
	assert isinstance(nodes[0], SCons.Node.FS.File)
	assert isinstance(nodes[1], SCons.Node.FS.File)
	assert nodes[0].path == "Util.py"
	assert nodes[1].path == "UtilTests.py"

	nodes = scons_str2nodes("Util.py UtilTests.py", SCons.Node.FS.FS().File)
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

	class SConsNode(SCons.Node.Node):
	    pass
	node = scons_str2nodes(SConsNode())

	class OtherNode:
	    pass
	node = scons_str2nodes(OtherNode())


    def test_varrepl(self):
	"""Test the varrepl function."""
        targets = PathList(map(os.path.normpath, [ "./foo/bar.exe",
                                                   "/bar/baz.obj",
                                                   "../foo/baz.obj" ]))
        sources = PathList(map(os.path.normpath, [ "./foo/blah.cpp",
                                                   "/bar/ack.cpp",
                                                   "../foo/ack.c" ]))

        newcom = scons_varrepl("test $targets $sources", targets, sources)
	assert newcom == "test foo/bar.exe /bar/baz.obj ../foo/baz.obj foo/blah.cpp /bar/ack.cpp ../foo/ack.c"

        newcom = scons_varrepl("test $targets[:] $sources[0]", targets, sources)
	assert newcom == "test foo/bar.exe /bar/baz.obj ../foo/baz.obj foo/blah.cpp"

        newcom = scons_varrepl("test ${targets[1:]}v", targets, sources)
	assert newcom == "test /bar/baz.obj ../foo/baz.objv"

        newcom = scons_varrepl("test $target", targets, sources)
	assert newcom == "test foo/bar.exe"

        newcom = scons_varrepl("test $target$source[0]", targets, sources)
	assert newcom == "test foo/bar.exe$source[0]"

        newcom = scons_varrepl("test ${target.file}", targets, sources)
	assert newcom == "test bar.exe"

        newcom = scons_varrepl("test ${target.filebase}", targets, sources)
	assert newcom == "test bar"

        newcom = scons_varrepl("test ${target.suffix}", targets, sources)
	assert newcom == "test .exe"

        newcom = scons_varrepl("test ${target.base}", targets, sources)
	assert newcom == "test foo/bar"

        newcom = scons_varrepl("test ${target.dir}", targets, sources)
	assert newcom == "test foo"



if __name__ == "__main__":
    suite = unittest.makeSuite(UtilTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
