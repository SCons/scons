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
import types
import unittest
import SCons.Node
import SCons.Node.FS
from SCons.Util import *
import TestCmd

class UtilTestCase(unittest.TestCase):
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
        loc['SOURCE'] = loc['SOURCES'][0]
        loc['xxx'] = None
        loc['zero'] = 0
        loc['one'] = 1

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

        newcom = scons_subst("test $TARGET$FOO[0]", loc, {})
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

        newcom = scons_subst("test ${TARGET.abspath}", loc, {})
        assert newcom == cvt("test %s/foo/bar.exe"%os.getcwd()), newcom

        newcom = scons_subst("test ${SOURCES.abspath}", loc, {})
        assert newcom == cvt("test %s/foo/blah.cpp %s %s/foo/ack.c"%(os.getcwd(),
                                                                     os.path.abspath(os.path.normpath("/bar/ack.cpp")),
                                                                     os.path.normpath(os.getcwd()+"/.."))), newcom

        newcom = scons_subst("test ${SOURCE.abspath}", loc, {})
        assert newcom == cvt("test %s/foo/blah.cpp"%os.getcwd()), newcom

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

        newcom = scons_subst("test $zero", loc, {})
        assert newcom == cvt("test 0"), newcom

        newcom = scons_subst("test $one", loc, {})
        assert newcom == cvt("test 1"), newcom

        newcom = scons_subst("test aXbXcXd", loc, {}, re.compile('X'))
        assert newcom == cvt("test abcd"), newcom

        glob = { 'a' : 1, 'b' : 2 }
        loc = {'a' : 3, 'c' : 4 }
        newcom = scons_subst("test $a $b $c $d test", glob, loc)
        assert newcom == "test 3 2 4 test", newcom

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

        # Test inputting a list to scons_subst_list()
        cmd_list = scons_subst_list([ "$SOURCES$NEWLINE", "$TARGETS",
                                        "This is a test" ],
                                    loc, {})
        assert len(cmd_list) == 2, len(cmd_list)
        assert cmd_list[0][0] == cvt('foo/blah with spaces.cpp'), cmd_list[0][0]
        assert cmd_list[1][0] == cvt("after"), cmd_list[1]
        assert cmd_list[1][4] == "This is a test", cmd_list[1]

        glob = { 'a' : 1, 'b' : 2 }
        loc = {'a' : 3, 'c' : 4 }
        cmd_list = scons_subst_list("test $a $b $c $d test", glob, loc)
        assert len(cmd_list) == 1, cmd_list
        assert cmd_list[0] == ['test', '3', '2', '4', 'test'], cmd_list

    def test_quote_spaces(self):
        """Testing the quote_spaces() method..."""
	q = quote_spaces('x')
	assert q == 'x', q

	q = quote_spaces('x x')
	assert q == '"x x"', q

	q = quote_spaces('x\tx')
	assert q == '"x\tx"', q

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
        if hasattr(types, 'UnicodeType'):
            exec "assert not is_Dict(u'')"

    def test_is_List(self):
        assert is_List([])
        import UserList
        assert is_List(UserList.UserList())
        assert not is_List({})
        assert not is_List("")
        if hasattr(types, 'UnicodeType'):
            exec "assert not is_List(u'')"

    def test_argmunge(self):
        assert argmunge("foo bar") == ["foo", "bar"]
        assert argmunge(["foo", "bar"]) == ["foo", "bar"]
        assert argmunge("foo") == ["foo"]

    def test_is_String(self):
        assert is_String("")
        if hasattr(types, 'UnicodeType'):
            exec "assert is_String(u'')"
        try:
            import UserString
        except:
            pass
        else:
            assert is_String(UserString.UserString(''))
        assert not is_String({})
        assert not is_String([])

    def test_to_String(self):
        """Test the to_String() method."""
        assert to_String(1) == "1", to_String(1)
        assert to_String([ 1, 2, 3]) == str([1, 2, 3]), to_String([1,2,3])
        assert to_String("foo") == "foo", to_String("foo")

        try:
            import UserString

            s1=UserString.UserString('blah')
            assert to_String(s1) == s1, s1
            assert to_String(s1) == 'blah', s1

            class Derived(UserString.UserString):
                pass
            s2 = Derived('foo')
            assert to_String(s2) == s2, s2
            assert to_String(s2) == 'foo', s2

            if hasattr(types, 'UnicodeType'):
                s3=UserString.UserString(unicode('bar'))
                assert to_String(s3) == s3, s3
                assert to_String(s3) == unicode('bar'), s3
                assert type(to_String(s3)) is types.UnicodeType, \
                       type(to_String(s3))
        except ImportError:
            pass

        if hasattr(types, 'UnicodeType'):
            s4 = unicode('baz')
            assert to_String(s4) == unicode('baz'), to_String(s4)
            assert type(to_String(s4)) is types.UnicodeType, \
                   type(to_String(s4))

    def test_WhereIs(self):
        test = TestCmd.TestCmd(workdir = '')

        sub1_xxx_exe = test.workpath('sub1', 'xxx.exe')
        sub2_xxx_exe = test.workpath('sub2', 'xxx.exe')
        sub3_xxx_exe = test.workpath('sub3', 'xxx.exe')
        sub4_xxx_exe = test.workpath('sub4', 'xxx.exe')

        test.subdir('subdir', 'sub1', 'sub2', 'sub3', 'sub4')

        if sys.platform != 'win32':
            test.write(sub1_xxx_exe, "\n")

        os.mkdir(sub2_xxx_exe)

        test.write(sub3_xxx_exe, "\n")
        os.chmod(sub3_xxx_exe, 0777)

        test.write(sub4_xxx_exe, "\n")
        os.chmod(sub4_xxx_exe, 0777)

        env_path = os.environ['PATH']

        pathdirs_1234 = [ test.workpath('sub1'),
                          test.workpath('sub2'),
                          test.workpath('sub3'),
                          test.workpath('sub4'),
                        ] + string.split(env_path, os.pathsep)

        pathdirs_1243 = [ test.workpath('sub1'),
                          test.workpath('sub2'),
                          test.workpath('sub4'),
                          test.workpath('sub3'),
                        ] + string.split(env_path, os.pathsep)

        os.environ['PATH'] = string.join(pathdirs_1234, os.pathsep)
        wi = WhereIs('xxx.exe')
        assert wi == test.workpath(sub3_xxx_exe), wi
        wi = WhereIs('xxx.exe', pathdirs_1243)
        assert wi == test.workpath(sub4_xxx_exe), wi
        wi = WhereIs('xxx.exe', string.join(pathdirs_1243, os.pathsep))
        assert wi == test.workpath(sub4_xxx_exe), wi

        os.environ['PATH'] = string.join(pathdirs_1243, os.pathsep)
        wi = WhereIs('xxx.exe')
        assert wi == test.workpath(sub4_xxx_exe), wi
        wi = WhereIs('xxx.exe', pathdirs_1234)
        assert wi == test.workpath(sub3_xxx_exe), wi
        wi = WhereIs('xxx.exe', string.join(pathdirs_1234, os.pathsep))
        assert wi == test.workpath(sub3_xxx_exe), wi

	if sys.platform == 'win32':
	    wi = WhereIs('xxx', pathext = '')
	    assert wi is None, wi

	    wi = WhereIs('xxx', pathext = '.exe')
	    assert wi == test.workpath(sub4_xxx_exe), wi

	    wi = WhereIs('xxx', path = pathdirs_1234, pathext = '.BAT;.EXE')
	    assert string.lower(wi) == string.lower(test.workpath(sub3_xxx_exe)), wi

    def test_get_env_var(self):
        """Testing get_environment_var()."""
        assert get_environment_var("$FOO") == "FOO", get_environment_var("$FOO")
        assert get_environment_var("${BAR}") == "BAR", get_environment_var("${BAR}")
        assert get_environment_var("${BAR}FOO") == None, get_environment_var("${BAR}FOO")
        assert get_environment_var("$BAR ") == None, get_environment_var("$BAR ")
        assert get_environment_var("FOO$BAR") == None, get_environment_var("FOO$BAR")

if __name__ == "__main__":
    suite = unittest.makeSuite(UtilTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
