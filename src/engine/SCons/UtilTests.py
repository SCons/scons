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

import os
import os.path
import string
import sys
import unittest
import SCons.Node
import SCons.Node.FS
from SCons.Util import *
import TestCmd

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


    def test_subst(self):
	"""Test the subst function."""
	loc = {}
        loc['TARGETS'] = PathList(map(os.path.normpath, [ "./foo/bar.exe",
                                                          "/bar/baz.obj",
                                                          "../foo/baz.obj" ]))
        loc['TARGET'] = loc['TARGETS'][0]
        loc['SOURCES'] = PathList(map(os.path.normpath, [ "./foo/blah.cpp",
                                                          "/bar/ack.cpp",
                                                          "../foo/ack.c" ]))
        loc['xxx'] = None

        if os.sep == '/':
            def cvt(str):
                return str
        else:
            def cvt(str):
                return string.replace(str, '/', os.sep)


        newcom = scons_subst("test $TARGETS $SOURCES", loc, {})
        assert newcom == cvt("test foo/bar.exe /bar/baz.obj ../foo/baz.obj foo/blah.cpp /bar/ack.cpp ../foo/ack.c")

        newcom = scons_subst("test ${TARGETS[:]} ${SOURCES[0]}", loc, {})
        assert newcom == cvt("test foo/bar.exe /bar/baz.obj ../foo/baz.obj foo/blah.cpp")

        newcom = scons_subst("test ${TARGETS[1:]}v", loc, {})
        assert newcom == cvt("test /bar/baz.obj ../foo/baz.objv")

        newcom = scons_subst("test $TARGET", loc, {})
        assert newcom == cvt("test foo/bar.exe")

        newcom = scons_subst("test $TARGET$SOURCE[0]", loc, {})
        assert newcom == cvt("test foo/bar.exe[0]")

        newcom = scons_subst("test ${TARGET.file}", loc, {})
        assert newcom == cvt("test bar.exe")

        newcom = scons_subst("test ${TARGET.filebase}", loc, {})
        assert newcom == cvt("test bar")

        newcom = scons_subst("test ${TARGET.suffix}", loc, {})
        assert newcom == cvt("test .exe")

        newcom = scons_subst("test ${TARGET.base}", loc, {})
        assert newcom == cvt("test foo/bar")

        newcom = scons_subst("test ${TARGET.dir}", loc, {})
        assert newcom == cvt("test foo")

        newcom = scons_subst("test $xxx", loc, {})
        assert newcom == cvt("test"), newcom

    def test_subst_list(self):
        """Testing the scons_subst_list() method..."""
        loc = {}
        loc['TARGETS'] = PathList(map(os.path.normpath, [ "./foo/bar.exe",
                                                          "/bar/baz with spaces.obj",
                                                          "../foo/baz.obj" ]))
        loc['TARGET'] = loc['TARGETS'][0]
        loc['SOURCES'] = PathList(map(os.path.normpath, [ "./foo/blah with spaces.cpp",
                                                          "/bar/ack.cpp",
                                                          "../foo/ack.c" ]))
        loc['xxx'] = None
        loc['NEWLINE'] = 'before\nafter'

        if os.sep == '/':
            def cvt(str):
                return str
        else:
            def cvt(str):
                return string.replace(str, '/', os.sep)

        cmd_list = scons_subst_list("$TARGETS", loc, {})
        assert cmd_list[0][1] == cvt("/bar/baz with spaces.obj"), cmd_list[0][1]

        cmd_list = scons_subst_list("$SOURCES $NEWLINE $TARGETS", loc, {})
        assert len(cmd_list) == 2, cmd_list
        assert cmd_list[0][0] == cvt('foo/blah with spaces.cpp'), cmd_list[0][0]
        assert cmd_list[1][2] == cvt("/bar/baz with spaces.obj"), cmd_list[1]

        cmd_list = scons_subst_list("$SOURCES$NEWLINE", loc, {})
        assert len(cmd_list) == 2, cmd_list
        assert cmd_list[1][0] == 'after', cmd_list[1][0]
        assert cmd_list[0][2] == cvt('../foo/ack.cbefore'), cmd_list[0][2]

    def test_find_files(self):
        """Testing find_files function."""
        test = TestCmd.TestCmd(workdir = '')
        test.write('./foo', 'Some file\n')
        fs = SCons.Node.FS.FS(test.workpath(""))
        node_derived = fs.File(test.workpath('./bar/baz'))
        node_derived.builder_set(1) # Any non-zero value.
        nodes = find_files(['foo', 'baz'],
                           map(test.workpath, ['./', './bar' ]), fs.File)
        file_names = map(str, nodes)
        file_names = map(os.path.normpath, file_names)
        assert os.path.normpath('./foo') in file_names, file_names
        assert os.path.normpath('./bar/baz') in file_names, file_names
        
        
if __name__ == "__main__":
    suite = unittest.makeSuite(UtilTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
