#
# __COPYRIGHT__
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


class OutBuffer:
    def __init__(self):
        self.buffer = ""

    def write(self, str):
        self.buffer = self.buffer + str

class DummyEnv:
    def __init__(self, dict={}):
        self.dict = dict

    def Dictionary(self, key = None):
        if not key:
            return self.dict
        return self.dict[key]

    def sig_dict(self):
        dict = self.dict.copy()
        dict["TARGETS"] = 'tsig'
        dict["SOURCES"] = 'ssig'
        return dict

def CmdGen1(target, source, env):
    # Nifty trick...since Environment references are interpolated,
    # instantiate an instance of a callable class with this one,
    # which will then get evaluated.
    assert target == 't', target
    assert source == 's', source
    return "${CMDGEN2('foo')}"

class CmdGen2:
    def __init__(self, mystr):
        self.mystr = mystr

    def __call__(self, target, source, env):
        assert target == 't', target
        assert source == 's', source
        return [ self.mystr, env.Dictionary('BAR') ]

class UtilTestCase(unittest.TestCase):
    def test_subst(self):
        """Test the subst function"""
        loc = {}
        target = [ "./foo/bar.exe",
                   "/bar/baz.obj",
                   "../foo/baz.obj" ]
        source = [ "./foo/blah.cpp",
                   "/bar/ack.cpp",
                   "../foo/ack.c" ]
        loc['xxx'] = None
        loc['zero'] = 0
        loc['one'] = 1
        loc['BAR'] = 'baz'

        loc['CMDGEN1'] = CmdGen1
        loc['CMDGEN2'] = CmdGen2

        env = DummyEnv(loc)

        if os.sep == '/':
            def cvt(str):
                return str
        else:
            def cvt(str):
                return string.replace(str, '/', os.sep)

        newcom = scons_subst("test $TARGETS $SOURCES", env,
                             target=target, source=source)
        assert newcom == cvt("test foo/bar.exe /bar/baz.obj ../foo/baz.obj foo/blah.cpp /bar/ack.cpp ../foo/ack.c")

        newcom = scons_subst("test ${TARGETS[:]} ${SOURCES[0]}", env,
                             target=target, source=source)
        assert newcom == cvt("test foo/bar.exe /bar/baz.obj ../foo/baz.obj foo/blah.cpp")

        newcom = scons_subst("test ${TARGETS[1:]}v", env,
                             target=target, source=source)
        assert newcom == cvt("test /bar/baz.obj ../foo/baz.objv")

        newcom = scons_subst("test $TARGET", env,
                             target=target, source=source)
        assert newcom == cvt("test foo/bar.exe")

        newcom = scons_subst("test $TARGET$FOO[0]", env,
                             target=target, source=source)
        assert newcom == cvt("test foo/bar.exe[0]")

        newcom = scons_subst("test ${TARGET.file}", env,
                             target=target, source=source)
        assert newcom == cvt("test bar.exe")

        newcom = scons_subst("test ${TARGET.filebase}", env,
                             target=target, source=source)
        assert newcom == cvt("test bar")

        newcom = scons_subst("test ${TARGET.suffix}", env,
                             target=target, source=source)
        assert newcom == cvt("test .exe")

        newcom = scons_subst("test ${TARGET.base}", env,
                             target=target, source=source)
        assert newcom == cvt("test foo/bar")

        newcom = scons_subst("test ${TARGET.dir}", env,
                             target=target, source=source)
        assert newcom == cvt("test foo")

        newcom = scons_subst("test ${TARGET.abspath}", env,
                             target=target, source=source)
        assert newcom == cvt("test %s/foo/bar.exe"%SCons.Util.updrive(os.getcwd())), newcom

        newcom = scons_subst("test ${SOURCES.abspath}", env,
                             target=target, source=source)
        assert newcom == cvt("test %s/foo/blah.cpp %s %s/foo/ack.c"%(SCons.Util.updrive(os.getcwd()),
                                                                     SCons.Util.updrive(os.path.abspath(os.path.normpath("/bar/ack.cpp"))),
                                                                     SCons.Util.updrive(os.path.normpath(os.getcwd()+"/..")))), newcom

        newcom = scons_subst("test ${SOURCE.abspath}", env,
                             target=target, source=source)
        assert newcom == cvt("test %s/foo/blah.cpp"%SCons.Util.updrive(os.getcwd())), newcom

        newcom = scons_subst("test $xxx", env)
        assert newcom == cvt("test"), newcom

        newcom = scons_subst("test $($xxx$)", env)
        assert newcom == cvt("test $($)"), newcom

        newcom = scons_subst("test $( $xxx $)", env)
        assert newcom == cvt("test $( $)"), newcom

        newcom = scons_subst("test $($xxx$)", env, re.compile('\$[()]'))
        assert newcom == cvt("test"), newcom

        newcom = scons_subst("test $( $xxx $)", env, re.compile('\$[()]'))
        assert newcom == cvt("test"), newcom

        newcom = scons_subst("test $zero", env)
        assert newcom == cvt("test 0"), newcom

        newcom = scons_subst("test $one", env)
        assert newcom == cvt("test 1"), newcom

        newcom = scons_subst("test aXbXcXd", env, re.compile('X'))
        assert newcom == cvt("test abcd"), newcom

        newcom = scons_subst("test $CMDGEN1 $SOURCES $TARGETS",
                             env, target='t', source='s')
        assert newcom == cvt("test foo baz s t"), newcom

        # Test against a former bug in scons_subst_list()
        glob = { "FOO" : "$BAR",
                 "BAR" : "BAZ",
                 "BLAT" : "XYX",
                 "BARXYX" : "BADNEWS" }
        newcom = scons_subst("$FOO$BLAT", DummyEnv(glob))
        assert newcom == "BAZXYX", newcom

        # Test for double-dollar-sign behavior
        glob = { "FOO" : "BAR",
                 "BAZ" : "BLAT" }
        newcom = scons_subst("$$FOO$BAZ", DummyEnv(glob))
        assert newcom == "$FOOBLAT", newcom

    def test_splitext(self):
        assert splitext('foo') == ('foo','')
        assert splitext('foo.bar') == ('foo','.bar')
        assert splitext(os.path.join('foo.bar', 'blat')) == (os.path.join('foo.bar', 'blat'),'')

    def test_subst_list(self):
        """Testing the scons_subst_list() method..."""

        class Node:
            def __init__(self, name):
                self.name = name
            def __str__(self):
                return self.name
            def is_literal(self):
                return 1
        
        loc = {}
        target = [ "./foo/bar.exe",
                   "/bar/baz with spaces.obj",
                   "../foo/baz.obj" ]
        source = [ "./foo/blah with spaces.cpp",
                   "/bar/ack.cpp",
                   "../foo/ack.c" ]
        loc['xxx'] = None
        loc['NEWLINE'] = 'before\nafter'

        loc['DO'] = Node('do something')
        loc['FOO'] = Node('foo.in')
        loc['BAR'] = Node('bar with spaces.out')
        loc['CRAZY'] = Node('crazy\nfile.in')

        loc['CMDGEN1'] = CmdGen1
        loc['CMDGEN2'] = CmdGen2

        env = DummyEnv(loc)

        if os.sep == '/':
            def cvt(str):
                return str
        else:
            def cvt(str):
                return string.replace(str, '/', os.sep)

        cmd_list = scons_subst_list("$TARGETS", env,
                                    target=target,
                                    source=source)
        assert cmd_list[0][1] == cvt("/bar/baz with spaces.obj"), cmd_list[0][1]

        cmd_list = scons_subst_list("$SOURCES $NEWLINE $TARGETS", env,
                                    target=target,
                                    source=source)
        assert len(cmd_list) == 2, cmd_list
        assert cmd_list[0][0] == cvt('foo/blah with spaces.cpp'), cmd_list[0][0]
        assert cmd_list[1][2] == cvt("/bar/baz with spaces.obj"), cmd_list[1]

        cmd_list = scons_subst_list("$SOURCES$NEWLINE", env,
                                    target=target,
                                    source=source)
        assert len(cmd_list) == 2, cmd_list
        assert cmd_list[1][0] == 'after', cmd_list[1][0]
        assert cmd_list[0][2] == cvt('../foo/ack.cbefore'), cmd_list[0][2]

        cmd_list = scons_subst_list("$DO --in=$FOO --out=$BAR", env)
        assert len(cmd_list) == 1, cmd_list
        assert len(cmd_list[0]) == 3, cmd_list
        assert cmd_list[0][0] == 'do something', cmd_list[0][0]
        assert cmd_list[0][1] == '--in=foo.in', cmd_list[0][1]
        assert cmd_list[0][2] == '--out=bar with spaces.out', cmd_list[0][2]

        # This test is now fixed, and works like it should.
        cmd_list = scons_subst_list("$DO --in=$CRAZY --out=$BAR", env)
        assert len(cmd_list) == 1, map(str, cmd_list[0])
        assert len(cmd_list[0]) == 3, cmd_list
        assert cmd_list[0][0] == 'do something', cmd_list[0][0]
        assert cmd_list[0][1] == '--in=crazy\nfile.in', cmd_list[0][1]
        assert cmd_list[0][2] == '--out=bar with spaces.out', cmd_list[0][2]
        
        # Test inputting a list to scons_subst_list()
        cmd_list = scons_subst_list([ "$SOURCES$NEWLINE", "$TARGETS",
                                        "This is a test" ],
                                    env,
                                    target=target,
                                    source=source)
        assert len(cmd_list) == 2, len(cmd_list)
        assert cmd_list[0][0] == cvt('foo/blah with spaces.cpp'), cmd_list[0][0]
        assert cmd_list[1][0] == cvt("after"), cmd_list[1]
        assert cmd_list[1][4] == "This is a test", cmd_list[1]

        # Test interpolating a callable.
        cmd_list = scons_subst_list("testing $CMDGEN1 $TARGETS $SOURCES", env,
                                    target='t', source='s')
        assert len(cmd_list) == 1, len(cmd_list)
        assert cmd_list[0][0] == 'testing', cmd_list[0][0]
        assert cmd_list[0][1] == 'foo', cmd_list[0][1]
        assert cmd_list[0][2] == 'bar with spaces.out', cmd_list[0][2]
        assert cmd_list[0][3] == 't', cmd_list[0][3]
        assert cmd_list[0][4] == 's', cmd_list[0][4]


        # Test against a former bug in scons_subst_list()
        glob = { "FOO" : "$BAR",
                 "BAR" : "BAZ",
                 "BLAT" : "XYX",
                 "BARXYX" : "BADNEWS" }
        cmd_list = scons_subst_list("$FOO$BLAT", DummyEnv(glob))
        assert cmd_list[0][0] == "BAZXYX", cmd_list[0][0]

        # Test for double-dollar-sign behavior
        glob = { "FOO" : "BAR",
                 "BAZ" : "BLAT" }
        cmd_list = scons_subst_list("$$FOO$BAZ", DummyEnv(glob))
        assert cmd_list[0][0] == "$FOOBLAT", cmd_list[0][0]

        # Now test escape functionality
        def escape_func(foo):
            return '**' + foo + '**'
        def quote_func(foo):
            return foo
        glob = { "FOO" : PathList([ 'foo\nwith\nnewlines',
                                    'bar\nwith\nnewlines' ]) }
        cmd_list = scons_subst_list("$FOO", DummyEnv(glob))
        assert cmd_list[0][0] == 'foo\nwith\nnewlines', cmd_list[0][0]
        cmd_list[0][0].escape(escape_func)
        assert cmd_list[0][0] == '**foo\nwith\nnewlines**', cmd_list[0][0]
        assert cmd_list[0][1] == 'bar\nwith\nnewlines', cmd_list[0][0]
        cmd_list[0][1].escape(escape_func)
        assert cmd_list[0][1] == '**bar\nwith\nnewlines**', cmd_list[0][0]

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
        
        bar_h = Node('bar.h', [stdlib_h])
        blat_h = Node('blat.h', [stdlib_h])
        blat_c = Node('blat.c', [blat_h, bar_h])
        blat_o = Node('blat.o', [blat_c])

        expect = """\
+-blat.o
  +-blat.c
    +-blat.h
    | +-stdlib.h
    +-bar.h
"""

        actual = render_tree(blat_o, get_children, 1)
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

    def test_Split(self):
        assert Split("foo bar") == ["foo", "bar"]
        assert Split(["foo", "bar"]) == ["foo", "bar"]
        assert Split("foo") == ["foo"]

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
        assert get_environment_var("$FOO_BAR1234") == "FOO_BAR1234", get_environment_var("$FOO_BAR1234")
        assert get_environment_var("${BAR_FOO1234}") == "BAR_FOO1234", get_environment_var("${BAR_FOO1234}")
        assert get_environment_var("${BAR}FOO") == None, get_environment_var("${BAR}FOO")
        assert get_environment_var("$BAR ") == None, get_environment_var("$BAR ")
        assert get_environment_var("FOO$BAR") == None, get_environment_var("FOO$BAR")
        assert get_environment_var("$FOO[0]") == None, get_environment_var("$FOO[0]")
        assert get_environment_var("${some('complex expression')}") == None, get_environment_var("${some('complex expression')}")

    def test_Proxy(self):
        """Test generic Proxy class."""
        class Subject:
            def foo(self):
                return 1
            def bar(self):
                return 2

        s=Subject()
        s.baz = 3

        class ProxyTest(Proxy):
            def bar(self):
                return 4

        p=ProxyTest(s)

        assert p.foo() == 1, p.foo()
        assert p.bar() == 4, p.bar()
        assert p.baz == 3, p.baz

        p.baz = 5
        s.baz = 6

        assert p.baz == 5, p.baz

    def test_Literal(self):
        """Test the Literal() function."""
        cmd_list = [ '$FOO', Literal('$BAR') ]
        cmd_list = scons_subst_list(cmd_list,
                                    DummyEnv({ 'FOO' : 'BAZ',
                                               'BAR' : 'BLAT' }))
        def escape_func(cmd):
            return '**' + cmd + '**'

        map(lambda x, e=escape_func: x.escape(e), cmd_list[0])
        cmd_list = map(str, cmd_list[0])
        assert cmd_list[0] == 'BAZ', cmd_list[0]
        assert cmd_list[1] == '**$BAR**', cmd_list[1]

    def test_mapPaths(self):
        """Test the mapPaths function"""
        fs = SCons.Node.FS.FS()
        dir=fs.Dir('foo')
        file=fs.File('bar/file')
        
        class DummyEnv:
            def subst(self, arg):
                return 'bar'

        res = mapPaths([ file, 'baz', 'blat/boo', '#test' ], dir)
        assert res[0] == file, res[0]
        assert res[1] == os.path.join('foo', 'baz'), res[1]
        assert res[2] == os.path.join('foo', 'blat/boo'), res[2]
        assert res[3] == '#test', res[3]

        env=DummyEnv()
        res=mapPaths('bleh', dir, env)
        assert res[0] == os.path.normpath('foo/bar'), res[1]

    def test_display(self):
        old_stdout = sys.stdout
        sys.stdout = OutBuffer()
        SCons.Util.display("line1")
        display.set_mode(0)
        SCons.Util.display("line2")
        display.set_mode(1)
        SCons.Util.display("line3")

        assert sys.stdout.buffer == "line1\nline3\n"
        sys.stdout = old_stdout

    def test_fs_delete(self):
        test = TestCmd.TestCmd(workdir = '')
        base = test.workpath('')
        xxx = test.workpath('xxx.xxx')
        sub1_yyy = test.workpath('sub1', 'yyy.yyy')
        test.subdir('sub1')
        test.write(xxx, "\n")
        test.write(sub1_yyy, "\n")

        old_stdout = sys.stdout
        sys.stdout = OutBuffer()

        exp = "Removed " + os.path.join(base, sub1_yyy) + '\n' + \
              "Removed directory " + os.path.join(base, 'sub1') + '\n' + \
              "Removed " + os.path.join(base, xxx) + '\n' + \
              "Removed directory " + base + '\n'

        SCons.Util.fs_delete(base, remove=0)
        assert sys.stdout.buffer == exp
        assert os.path.exists(sub1_yyy)

        sys.stdout.buffer = ""
        SCons.Util.fs_delete(base, remove=1)
        assert sys.stdout.buffer == exp
        assert not os.path.exists(base)

        test._dirlist = None
        sys.stdout = old_stdout

    def test_subst_dict(self):
        """Test substituting dictionary values in an Action
        """
        d = subst_dict([], [], DummyEnv({'a' : 'A', 'b' : 'B'}))
        assert d['a'] == 'A', d
        assert d['b'] == 'B', d

        d = subst_dict(target = 't', source = 's', env=DummyEnv())
        assert str(d['TARGETS']) == 't', d['TARGETS']
        assert str(d['TARGET']) == 't', d['TARGET']
        assert str(d['SOURCES']) == 's', d['SOURCES']
        assert str(d['SOURCE']) == 's', d['SOURCE']

        d = subst_dict(target = ['t1', 't2'],
                       source = ['s1', 's2'],
                       env = DummyEnv())
        TARGETS = map(lambda x: str(x), d['TARGETS'])
        TARGETS.sort()
        assert TARGETS == ['t1', 't2'], d['TARGETS']
        assert str(d['TARGET']) == 't1', d['TARGET']
        SOURCES = map(lambda x: str(x), d['SOURCES'])
        SOURCES.sort()
        assert SOURCES == ['s1', 's2'], d['SOURCES']
        assert str(d['SOURCE']) == 's1', d['SOURCE']

        class N:
            def __init__(self, name):
                self.name = name
            def __str__(self):
                return self.name
            def rstr(self):
                return 'rstr-' + self.name

        d = subst_dict(target = [N('t3'), 't4'],
                       source = ['s3', N('s4')],
                       env = DummyEnv())
        TARGETS = map(lambda x: str(x), d['TARGETS'])
        TARGETS.sort()
        assert TARGETS == ['t3', 't4'], d['TARGETS']
        SOURCES = map(lambda x: str(x), d['SOURCES'])
        SOURCES.sort()
        assert SOURCES == ['rstr-s4', 's3'], d['SOURCES']


if __name__ == "__main__":
    suite = unittest.makeSuite(UtilTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
