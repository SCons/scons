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

# Define a null function for use as a builder action.
# Where this is defined in the file seems to affect its
# byte-code contents, so try to minimize changes by
# defining it here, before we even import anything.
def Func():
    pass

import os
import sys
import types
import unittest
import UserDict

import SCons.Action
import SCons.Environment
import SCons.Errors

import TestCmd

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
f.write("act.py: '" + string.join(sys.argv[2:], "' '") + "'\\n")
try:
    if sys.argv[3]:
        f.write("act.py: '" + os.environ[sys.argv[3]] + "'\\n")
except:
    pass
f.close()
sys.exit(0)
""")

act_py = test.workpath('act.py')

outfile = test.workpath('outfile')
outfile2 = test.workpath('outfile2')

scons_env = SCons.Environment.Environment()

class Environment:
    def __init__(self, **kw):
        self.d = {}
        self.d['SHELL'] = scons_env['SHELL']
        self.d['SPAWN'] = scons_env['SPAWN']
        self.d['ESCAPE'] = scons_env['ESCAPE']
        for k, v in kw.items():
            self.d[k] = v
    def subst(self, s):
        if not SCons.Util.is_String(s):
            return s
        try:
            if s[0] == '$':
                return self.d.get(s[1:], '')
        except IndexError:
            pass
        return self.d.get(s, s)
    def __getitem__(self, item):
        return self.d[item]
    def has_key(self, item):
        return self.d.has_key(item)
    def get(self, key, value):
        return self.d.get(key, value)
    def items(self):
        return self.d.items()

if os.name == 'java':
    python = os.path.join(sys.prefix, 'jython')
else:
    python = sys.executable

class ActionTestCase(unittest.TestCase):

    def test_factory(self):
        """Test the Action factory
        """
        def foo():
            pass
        def bar():
            pass
        a1 = SCons.Action.Action(foo)
        assert isinstance(a1, SCons.Action.FunctionAction), a1
        assert a1.execfunction == foo, a1.execfunction

        a2 = SCons.Action.Action("string")
        assert isinstance(a2, SCons.Action.CommandAction), a2
        assert a2.cmd_list == ["string"], a2.cmd_list

        if hasattr(types, 'UnicodeType'):
            exec "a3 = SCons.Action.Action(u'string')"
            exec "assert isinstance(a3, SCons.Action.CommandAction), a3"

        a4 = SCons.Action.Action(["x", "y", "z", [ "a", "b", "c"]])
        assert isinstance(a4, SCons.Action.ListAction), a4
        assert isinstance(a4.list[0], SCons.Action.CommandAction), a4.list[0]
        assert a4.list[0].cmd_list == ["x"], a4.list[0].cmd_list
        assert isinstance(a4.list[1], SCons.Action.CommandAction), a4.list[1]
        assert a4.list[1].cmd_list == ["y"], a4.list[1].cmd_list
        assert isinstance(a4.list[2], SCons.Action.CommandAction), a4.list[2]
        assert a4.list[2].cmd_list == ["z"], a4.list[2].cmd_list
        assert isinstance(a4.list[3], SCons.Action.CommandAction), a4.list[3]
        assert a4.list[3].cmd_list == [ "a", "b", "c" ], a4.list[3].cmd_list

        a5 = SCons.Action.Action(1)
        assert a5 is None, a5

        a6 = SCons.Action.Action(a1)
        assert a6 is a1, a6

        a7 = SCons.Action.Action([[ "explicit", "command", "line" ]])
        assert isinstance(a7, SCons.Action.CommandAction), a7
        assert a7.cmd_list == [ "explicit", "command", "line" ], a7.cmd_list

        a8 = SCons.Action.Action(["a8"])
        assert isinstance(a8, SCons.Action.CommandAction), a8
        assert a8.cmd_list == [ "a8" ], a8.cmd_list

        a9 = SCons.Action.Action("x\ny\nz")
        assert isinstance(a9, SCons.Action.ListAction), a9
        assert isinstance(a9.list[0], SCons.Action.CommandAction), a9.list[0]
        assert a9.list[0].cmd_list == ["x"], a9.list[0].cmd_list
        assert isinstance(a9.list[1], SCons.Action.CommandAction), a9.list[1]
        assert a9.list[1].cmd_list == ["y"], a9.list[1].cmd_list
        assert isinstance(a9.list[2], SCons.Action.CommandAction), a9.list[2]
        assert a9.list[2].cmd_list == ["z"], a9.list[2].cmd_list

        a10 = SCons.Action.Action(["x", foo, "z"])
        assert isinstance(a10, SCons.Action.ListAction), a10
        assert isinstance(a10.list[0], SCons.Action.CommandAction), a10.list[0]
        assert a10.list[0].cmd_list == ["x"], a10.list[0].cmd_list
        assert isinstance(a10.list[1], SCons.Action.FunctionAction), a10.list[1]
        assert a10.list[1].execfunction == foo, a10.list[1].execfunction
        assert isinstance(a10.list[2], SCons.Action.CommandAction), a10.list[2]
        assert a10.list[2].cmd_list == ["z"], a10.list[2].cmd_list

        a11 = SCons.Action.Action(foo, strfunction=bar)
        assert isinstance(a11, SCons.Action.FunctionAction), a11
        assert a11.execfunction == foo, a11.execfunction
        assert a11.strfunction == bar, a11.strfunction

class ActionBaseTestCase(unittest.TestCase):

    def test_cmp(self):
        """Test Action comparison
        """
        a1 = SCons.Action.Action("x")
        a2 = SCons.Action.Action("x")
        assert a1 == a2
        a3 = SCons.Action.Action("y")
        assert a1 != a3
        assert a2 != a3

    def test_get_actions(self):
        """Test the get_actions() method
        """
        a = SCons.Action.Action("x")
        l = a.get_actions()
        assert l == [a], l

    def test_subst_dict(self):
        """Test substituting dictionary values in an Action
        """
        a = SCons.Action.Action("x")

        d = a.subst_dict([], [], Environment(a = 'A', b = 'B'))
        assert d['a'] == 'A', d
        assert d['b'] == 'B', d

        d = a.subst_dict(target = 't', source = 's', env = Environment())
        assert str(d['TARGETS']) == 't', d['TARGETS']
        assert str(d['TARGET']) == 't', d['TARGET']
        assert str(d['SOURCES']) == 's', d['SOURCES']
        assert str(d['SOURCE']) == 's', d['SOURCE']

        d = a.subst_dict(target = ['t1', 't2'],
                         source = ['s1', 's2'],
                         env = Environment())
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

        d = a.subst_dict(target = [N('t3'), 't4'],
                         source = ['s3', N('s4')],
                         env = Environment())
        TARGETS = map(lambda x: str(x), d['TARGETS'])
        TARGETS.sort()
        assert TARGETS == ['t3', 't4'], d['TARGETS']
        SOURCES = map(lambda x: str(x), d['SOURCES'])
        SOURCES.sort()
        assert SOURCES == ['rstr-s4', 's3'], d['SOURCES']

class CommandActionTestCase(unittest.TestCase):

    def test_init(self):
        """Test creation of a command Action
        """
        a = SCons.Action.CommandAction(["xyzzy"])
        assert a.cmd_list == [ "xyzzy" ], a.cmd_list

    def test_execute(self):
        """Test execution of command Actions

        """
        cmd1 = r'%s %s %s xyzzy' % (python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd1)
        r = act([], [], Environment())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'xyzzy'\n", c

        cmd2 = r'%s %s %s $TARGET' % (python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd2)
        r = act('foo', [], Environment())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'foo'\n", c

        cmd3 = r'%s %s %s ${TARGETS}' % (python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd3)
        r = act(['aaa', 'bbb'], [], Environment())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'aaa' 'bbb'\n", c

        cmd4 = r'%s %s %s $SOURCES' % (python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd4)
        r = act([], ['one', 'two'], Environment())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'one' 'two'\n", c

        cmd4 = r'%s %s %s ${SOURCES[:2]}' % (python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd4)
        r = act([],
                        source = ['three', 'four', 'five'],
                        env = Environment())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'three' 'four'\n", c

        cmd5 = r'%s %s %s $TARGET XYZZY' % (python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd5)
        r = act(target = 'out5',
                        source = [],
                        env = Environment(ENV = {'XYZZY' : 'xyzzy'}))
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'out5' 'XYZZY'\nact.py: 'xyzzy'\n", c

        class Obj:
            def __init__(self, str):
                self._str = str
            def __str__(self):
                return self._str

        cmd6 = r'%s %s %s ${TARGETS[1]} $TARGET ${SOURCES[:2]}' % (python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd6)
        r = act(target = [Obj('111'), Obj('222')],
                        source = [Obj('333'), Obj('444'), Obj('555')],
                        env = Environment())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: '222' '111' '333' '444'\n", c

        cmd7 = '%s %s %s one\n\n%s %s %s two' % (python, act_py, outfile,
                                                 python, act_py, outfile)
        expect7 = '%s %s %s one\n%s %s %s two\n' % (python, act_py, outfile,
                                                    python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd7)

        global show_string
        show_string = ""
        def my_show(string):
            global show_string
            show_string = show_string + string + "\n"
        act.show = my_show

        r = act([], [], Environment())
        assert r == 0
        assert show_string == expect7, show_string

        if os.name == 'nt':
            # NT treats execs of directories and non-executable files
            # as "file not found" errors
            expect_nonexistent = 1
            expect_nonexecutable = 1
        else:
            expect_nonexistent = 127
            expect_nonexecutable = 126

        # Test that a nonexistent command returns 127
        act = SCons.Action.CommandAction(python + "_XyZzY_")
        r = act([], [], Environment(out = outfile))
        assert r == expect_nonexistent, "r == %d" % r

        # Test that trying to execute a directory returns 126
        dir, tail = os.path.split(python)
        act = SCons.Action.CommandAction(dir)
        r = act([], [], Environment(out = outfile))
        assert r == expect_nonexecutable, "r == %d" % r

        # Test that trying to execute a non-executable file returns 126
        act = SCons.Action.CommandAction(outfile)
        r = act([], [], Environment(out = outfile))
        assert r == expect_nonexecutable, "r == %d" % r

    def test_set_handler(self):
        """Test setting the command handler...
        """
        class Test:
            def __init__(self):
                self.executed = 0
        t=Test()
        def func(sh, escape, cmd, args, env, test=t):
            test.executed = args
            test.shell = sh
            return 0
        def escape_func(cmd):
            return '**' + cmd + '**'

        class LiteralStr:
            def __init__(self, x):
                self.data = x
            def __str__(self):
                return self.data
            def is_literal(self):
                return 1

        try:
            SCons.Action.SetCommandHandler(func)
        except SCons.Errors.UserError:
            pass
        else:
            assert 0, "should have gotten user error"
            
        a = SCons.Action.CommandAction(["xyzzy"])
        a([], [], Environment(SPAWN = func))
        assert t.executed == [ 'xyzzy' ]

        a = SCons.Action.CommandAction(["xyzzy"])
        a([], [], Environment(SPAWN = func, SHELL = 'fake shell'))
        assert t.executed == [ 'xyzzy' ]
        assert t.shell == 'fake shell'

        a = SCons.Action.CommandAction([ LiteralStr("xyzzy") ])
        a([], [], Environment(SPAWN = func, ESCAPE = escape_func))
        assert t.executed == [ '**xyzzy**' ], t.executed

    def test_get_raw_contents(self):
        """Test fetching the contents of a command Action
        """
        a = SCons.Action.CommandAction(["|", "$(", "$foo", "|", "$bar",
                                        "$)", "|"])
        c = a.get_raw_contents(target=[], source=[],
                               env=Environment(foo = 'FFF', bar = 'BBB'))
        assert c == "| $( FFF | BBB $) |", c

    def test_get_contents(self):
        """Test fetching the contents of a command Action
        """
        a = SCons.Action.CommandAction(["|", "$(", "$foo", "|", "$bar",
                                        "$)", "|"])
        c = a.get_contents(target=[], source=[],
                           env=Environment(foo = 'FFF', bar = 'BBB'))
        assert c == "| |", c

class CommandGeneratorActionTestCase(unittest.TestCase):

    def test_init(self):
        """Test creation of a command generator Action
        """
        def f(target, source, env):
            pass
        a = SCons.Action.CommandGeneratorAction(f)
        assert a.generator == f

    def test_execute(self):
        """Test executing a command generator Action
        """

        def f(target, source, env, for_signature, self=self):
            dummy = env['dummy']
            self.dummy = dummy
            s = env.subst("$FOO")
            assert s == 'foo baz\nbar ack', s
            return "$FOO"
        def func_action(target, source, env, self=self):
            dummy=env['dummy']
            s = env.subst('$foo')
            assert s == 'bar', s
            self.dummy=dummy
        def f2(target, source, env, for_signature, f=func_action):
            return f
        def ch(sh, escape, cmd, args, env, self=self):
            self.cmd.append(cmd)
            self.args.append(args)

        a = SCons.Action.CommandGeneratorAction(f)
        self.dummy = 0
        self.cmd = []
        self.args = []
        a([], [], env=Environment(FOO = 'foo baz\nbar ack',
                                          dummy = 1,
                                          SPAWN = ch))
        assert self.dummy == 1, self.dummy
        assert self.cmd == ['foo', 'bar'], self.cmd
        assert self.args == [[ 'foo', 'baz' ], [ 'bar', 'ack' ]], self.args

        b = SCons.Action.CommandGeneratorAction(f2)
        self.dummy = 0
        b(target=[], source=[], env=Environment(foo =  'bar',
                                                        dummy =  2 ))
        assert self.dummy==2, self.dummy
        del self.dummy

        class DummyFile:
            def __init__(self, t):
                self.t = t
            def rfile(self):
                self.t.rfile_called = 1
        def f3(target, source, env, for_signature):
            return ''
        c = SCons.Action.CommandGeneratorAction(f3)
        c(target=[], source=DummyFile(self), env=Environment())
        assert self.rfile_called

    def test_get_contents(self):
        """Test fetching the contents of a command generator Action
        """
        def f(target, source, env, for_signature):
            foo = env['foo']
            bar = env['bar']
            assert for_signature, for_signature
            return [["guux", foo, "$(", "ignore", "$)", bar]]

        a = SCons.Action.CommandGeneratorAction(f)
        c = a.get_contents(target=[], source=[],
                           env=Environment(foo = 'FFF', bar =  'BBB'))
        assert c == "guux FFF BBB", c


class FunctionActionTestCase(unittest.TestCase):

    def test_init(self):
        """Test creation of a function Action
        """
        def func1():
            pass
        def func2():
            pass
        def func3():
            pass
        def func4():
            pass

        a = SCons.Action.FunctionAction(func1)
        assert a.execfunction == func1, a.execfunction
        assert isinstance(a.strfunction, types.FunctionType)

        a = SCons.Action.FunctionAction(func2, strfunction=func3)
        assert a.execfunction == func2, a.execfunction
        assert a.strfunction == func3, a.strfunction

        a = SCons.Action.FunctionAction(func3, func4)
        assert a.execfunction == func3, a.execfunction
        assert a.strfunction == func4, a.strfunction

        a = SCons.Action.FunctionAction(func4, None)
        assert a.execfunction == func4, a.execfunction
        assert a.strfunction is None, a.strfunction

    def test_execute(self):
        """Test executing a function Action
        """
        self.inc = 0
        def f(target, source, env):
            s = env['s']
            s.inc = s.inc + 1
            s.target = target
            s.source=source
            assert env.subst("$BAR") == 'foo bar', env.subst("$BAR")
            return 0
        a = SCons.Action.FunctionAction(f)
        a(target=1, source=2, env=Environment(BAR = 'foo bar',
                                                      s = self))
        assert self.inc == 1, self.inc
        assert self.source == [2], self.source
        assert self.target == [1], self.target

        global count
        count = 0
        def function1(target, source, env):
            global count
            count = count + 1
            for t in target:
                open(t, 'w').write("function1\n")
            return 1

        act = SCons.Action.FunctionAction(function1)
        r = None
        try:
            r = act(target = [outfile, outfile2], source=[], env=Environment())
        except SCons.Errors.BuildError:
            pass
        assert r == 1
        assert count == 1
        c = test.read(outfile, 'r')
        assert c == "function1\n", c
        c = test.read(outfile2, 'r')
        assert c == "function1\n", c

        class class1a:
            def __init__(self, target, source, env):
                open(env['out'], 'w').write("class1a\n")

        act = SCons.Action.FunctionAction(class1a)
        r = act([], [], Environment(out = outfile))
        assert r.__class__ == class1a
        c = test.read(outfile, 'r')
        assert c == "class1a\n", c

        class class1b:
            def __call__(self, target, source, env):
                open(env['out'], 'w').write("class1b\n")
                return 2

        act = SCons.Action.FunctionAction(class1b())
        r = act([], [], Environment(out = outfile))
        assert r == 2
        c = test.read(outfile, 'r')
        assert c == "class1b\n", c

        def build_it(target, source, env, self=self):
            self.build_it = 1
            return 0
        def string_it(target, source, self=self):
            self.string_it = 1
            return None
        act = SCons.Action.FunctionAction(build_it, string_it)
        r = act([], [], Environment())
        assert r == 0, r
        assert self.build_it
        assert self.string_it

    def test_get_contents(self):
        """Test fetching the contents of a function Action
        """
        a = SCons.Action.FunctionAction(Func)
        c = a.get_contents(target=[], source=[], env=Environment())
        assert c == "\177\036\000\177\037\000d\000\000S", repr(c)

class ListActionTestCase(unittest.TestCase):

    def test_init(self):
        """Test creation of a list of subsidiary Actions
        """
        def func():
            pass
        a = SCons.Action.ListAction(["x", func, ["y", "z"]])
        assert isinstance(a.list[0], SCons.Action.CommandAction)
        assert isinstance(a.list[1], SCons.Action.FunctionAction)
        assert isinstance(a.list[2], SCons.Action.ListAction)
        assert a.list[2].list[0].cmd_list == [ 'y' ]

    def test_get_actions(self):
        """Test the get_actions() method for ListActions
        """
        a = SCons.Action.ListAction(["x", "y"])
        l = a.get_actions()
        assert len(l) == 2, l
        assert isinstance(l[0], SCons.Action.CommandAction), l[0]
        g = l[0].get_actions()
        assert g == [l[0]], g
        assert isinstance(l[1], SCons.Action.CommandAction), l[1]
        g = l[1].get_actions()
        assert g == [l[1]], g

    def test_execute(self):
        """Test executing a list of subsidiary Actions
        """
        self.inc = 0
        def f(target,source,env):
            s = env['s']
            s.inc = s.inc + 1
        a = SCons.Action.ListAction([f, f, f])
        a([], [], Environment(s = self))
        assert self.inc == 3, self.inc

        cmd2 = r'%s %s %s syzygy' % (python, act_py, outfile)

        def function2(target, source, env):
            open(env['out'], 'a').write("function2\n")
            return 0

        class class2a:
            def __call__(self, target, source, env):
                open(env['out'], 'a').write("class2a\n")
                return 0

        class class2b:
            def __init__(self, target, source, env):
                open(env['out'], 'a').write("class2b\n")
        act = SCons.Action.ListAction([cmd2, function2, class2a(), class2b])
        r = act([], [], Environment(out = outfile))
        assert r.__class__ == class2b
        c = test.read(outfile, 'r')
        assert c == "act.py: 'syzygy'\nfunction2\nclass2a\nclass2b\n", c

    def test_get_contents(self):
        """Test fetching the contents of a list of subsidiary Actions
        """
        self.foo=0
        def gen(target, source, env, for_signature):
            s = env['s']
            s.foo=1
            return "y"
        a = SCons.Action.ListAction(["x",
                                     SCons.Action.CommandGenerator(gen),
                                     "z"])
        c = a.get_contents(target=[], source=[], env=Environment(s = self))
        assert self.foo==1, self.foo
        assert c == "xyz", c

class LazyActionTestCase(unittest.TestCase):
    def test_init(self):
        """Test creation of a lazy-evaluation Action
        """
        # Environment variable references should create a special
        # type of CommandGeneratorAction that lazily evaluates the
        # variable.
        a9 = SCons.Action.Action('$FOO')
        assert isinstance(a9, SCons.Action.CommandGeneratorAction), a9
        assert a9.generator.var == 'FOO', a9.generator.var

        a10 = SCons.Action.Action('${FOO}')
        assert isinstance(a9, SCons.Action.CommandGeneratorAction), a10
        assert a10.generator.var == 'FOO', a10.generator.var

    def test_execute(self):
        """Test executing a lazy-evaluation Action
        """
        def f(target, source, env):
            s = env['s']
            s.test=1
            return 0
        a = SCons.Action.Action('$BAR')
        a([], [], env=Environment(BAR = f, s = self))
        assert self.test == 1, self.test

    def test_get_contents(self):
        """Test fetching the contents of a lazy-evaluation Action
        """
        a = SCons.Action.Action("${FOO}")
        c = a.get_contents(target=[], source=[],
                           env = Environment(FOO = [["This", "is", "$(", "a", "$)", "test"]]))
        assert c == "This is test", c


if __name__ == "__main__":
    suite = unittest.TestSuite()
    tclasses = [ ActionTestCase,
                 ActionBaseTestCase,
                 CommandActionTestCase,
                 CommandGeneratorActionTestCase,
                 FunctionActionTestCase,
                 ListActionTestCase,
                 LazyActionTestCase ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(map(tclass, names))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
