#
# Copyright (c) 2001, 2002 Steven Knight
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
import re
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

        newcom = scons_subst("test $($xxx$)", loc, {})
        assert newcom == cvt("test $($)"), newcom

        newcom = scons_subst("test $( $xxx $)", loc, {})
        assert newcom == cvt("test $( $)"), newcom

        newcom = scons_subst("test $($xxx$)", loc, {}, re.compile('\$[()]'))
        assert newcom == cvt("test"), newcom

        newcom = scons_subst("test $( $xxx $)", loc, {}, re.compile('\$[()]'))
        assert newcom == cvt("test"), newcom

        newcom = scons_subst("test aXbXcXd", loc, {}, re.compile('X'))
        assert newcom == cvt("test abcd"), newcom

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

    def test_find_file(self):
        """Testing find_file function."""
        test = TestCmd.TestCmd(workdir = '')
        test.write('./foo', 'Some file\n')
        fs = SCons.Node.FS.FS(test.workpath(""))
        os.chdir(test.workpath("")) # FS doesn't like the cwd to be something other than it's root
        node_derived = fs.File(test.workpath('bar/baz'))
        node_derived.builder_set(1) # Any non-zero value.
        paths = map(fs.Dir, ['.', './bar'])
        nodes = [find_file('foo', paths, fs.File), 
                 find_file('baz', paths, fs.File)] 
        file_names = map(str, nodes)
        file_names = map(os.path.normpath, file_names)
        assert os.path.normpath('./foo') in file_names, file_names
        assert os.path.normpath('./bar/baz') in file_names, file_names

    def test_autogenerate(dict):
        """Test autogenerating variables in a dictionary."""
        dict = {'LIBS'          : [ 'foo', 'bar', 'baz' ],
                'LIBLINKPREFIX' : 'foo',
                'LIBLINKSUFFIX' : 'bar'}
        autogenerate(dict, dir = SCons.Node.FS.default_fs.Dir('/xx'))
        assert len(dict['_LIBFLAGS']) == 3, dict('_LIBFLAGS')
        assert dict['_LIBFLAGS'][0] == 'foofoobar', \
               dict['_LIBFLAGS'][0]
        assert dict['_LIBFLAGS'][1] == 'foobarbar', \
               dict['_LIBFLAGS'][1]
        assert dict['_LIBFLAGS'][2] == 'foobazbar', \
               dict['_LIBFLAGS'][2]

        blat = SCons.Node.FS.default_fs.File('blat')
        dict = {'CPPPATH'   : [ 'foo', 'bar', 'baz', '$FOO/bar', blat],
                'INCPREFIX' : 'foo',
                'INCSUFFIX' : 'bar',
                'FOO'       : 'baz' }
        autogenerate(dict, dir = SCons.Node.FS.default_fs.Dir('/xx'))
        assert len(dict['_INCFLAGS']) == 7, dict['_INCFLAGS']
        assert dict['_INCFLAGS'][0] == '$(', \
               dict['_INCFLAGS'][0]
        assert dict['_INCFLAGS'][1] == os.path.normpath('foo/xx/foobar'), \
               dict['_INCFLAGS'][1]
        assert dict['_INCFLAGS'][2] == os.path.normpath('foo/xx/barbar'), \
               dict['_INCFLAGS'][2]
        assert dict['_INCFLAGS'][3] == os.path.normpath('foo/xx/bazbar'), \
               dict['_INCFLAGS'][3]
        assert dict['_INCFLAGS'][4] == os.path.normpath('foo/xx/baz/barbar'), \
               dict['_INCFLAGS'][4]
        
        assert dict['_INCFLAGS'][5] == os.path.normpath('fooblatbar'), \
               dict['_INCFLAGS'][5]
        assert dict['_INCFLAGS'][6] == '$)', \
               dict['_INCFLAGS'][6]

    def test_render_tree(self):
        class Node:
            def __init__(self, name, children=[]):
                self.children = children
                self.name = name
            def __str__(self):
                return self.name

        def get_children(node):
            return node.children

        windows_h = Node("windows.h")
        stdlib_h = Node("stdlib.h")
        stdio_h = Node("stdio.h")
        bar_c = Node("bar.c", [stdlib_h, windows_h])
        bar_o = Node("bar.o", [bar_c])
        foo_c = Node("foo.c", [stdio_h])
        foo_o = Node("foo.o", [foo_c])
        foo = Node("foo", [foo_o, bar_o])

        expect = """\
+-foo
  +-foo.o
  | +-foo.c
  |   +-stdio.h
  +-bar.o
    +-bar.c
      +-stdlib.h
      +-windows.h
"""

        actual = render_tree(foo, get_children)
        assert expect == actual, (expect, actual)

    def test_is_Dict(self):
        assert is_Dict({})
        import UserDict
        assert is_Dict(UserDict.UserDict())
        assert not is_Dict([])
        assert not is_Dict("")

    def test_is_List(self):
        assert is_List([])
        import UserList
        assert is_List(UserList.UserList())
        assert not is_List({})
        assert not is_List("")

    def test_is_String(self):
        assert is_String("")
        try:
            import UserString
        except:
            pass
        else:
            assert is_String(UserString.UserString(''))
        assert not is_String({})
        assert not is_String([])

if __name__ == "__main__":
    suite = unittest.makeSuite(UtilTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
