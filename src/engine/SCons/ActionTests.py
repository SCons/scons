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

import sys
import types
import unittest

import SCons.Action
import TestCmd

import UserDict

import SCons.Environment
def Environment(dict):
    return apply(SCons.Environment.Environment, (), dict)

class ActionTestCase(unittest.TestCase):

    def runTest(self):
        """Test the Action factory
        """
        def foo():
            pass
        a1 = SCons.Action.Action(foo)
        assert isinstance(a1, SCons.Action.FunctionAction), a1

        a2 = SCons.Action.Action("string")
        assert isinstance(a2, SCons.Action.CommandAction), a2

        if hasattr(types, 'UnicodeType'):
            exec "a3 = SCons.Action.Action(u'string')"
            exec "assert isinstance(a3, SCons.Action.CommandAction), a3"

        a4 = SCons.Action.Action(["x", "y", "z", [ "a", "b", "c"]])
        assert isinstance(a4, SCons.Action.ListAction), a4
        assert isinstance(a4.list[0], SCons.Action.CommandAction), a4.list[0]
        assert isinstance(a4.list[1], SCons.Action.CommandAction), a4.list[1]
        assert isinstance(a4.list[2], SCons.Action.CommandAction), a4.list[2]
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

    def test_subst_dict(self):
        """Test substituting dictionary values in an Action
        """
        a = SCons.Action.Action("x")

        d = a.subst_dict([],[],Environment({'a' : 'A', 'b' : 'B'}))
        assert d['a'] == 'A', d
        assert d['b'] == 'B', d

        d = a.subst_dict(target = 't', source = 's',env=Environment({}))
        assert str(d['TARGETS']) == 't', d['TARGETS']
        assert str(d['TARGET']) == 't', d['TARGET']
        assert str(d['SOURCES']) == 's', d['SOURCES']
        assert str(d['SOURCE']) == 's', d['SOURCE']


        d = a.subst_dict(target = ['t1', 't2'], source = ['s1', 's2'], env=Environment({}))
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

        d = a.subst_dict(target = [N('t3'), 't4'], source = ['s3', N('s4')], env=Environment({}))
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
        """Test executing a command Action
        """
        self.test_set_handler()
        pass

    def test_set_handler(self):
        """Test setting the command handler...
        """
        class Test:
            def __init__(self):
                self.executed = 0
        t=Test()
        def func(cmd, args, env, test=t):
            test.executed = 1
            return 0
        SCons.Action.SetCommandHandler(func)
        assert SCons.Action.spawn is func
        a = SCons.Action.CommandAction(["xyzzy"])
        a.execute([],[],Environment({}))
        assert t.executed == 1

    def test_get_raw_contents(self):
        """Test fetching the contents of a command Action
        """
        a = SCons.Action.CommandAction(["|", "$(", "$foo", "|", "$bar",
                                        "$)", "|"])
        c = a.get_contents(target=[], source=[],
                           foo = 'FFF', bar = 'BBB')
        assert c == "| $( FFF | BBB $) |"

    def test_get_contents(self):
        """Test fetching the contents of a command Action
        """
        a = SCons.Action.CommandAction(["|", "$(", "$foo", "|", "$bar",
                                        "$)", "|"])
        c = a.get_contents(target=[], source=[],
                           env=Environment({'foo':'FFF', 'bar':'BBB'}))
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
            assert env.subst("$FOO $( bar $) baz") == 'foo baz\nbar ack bar baz', env.subst("$FOO $( bar $) baz")
            assert env.subst("$FOO $( bar $) baz", raw=1) == 'foo baz\nbar ack $( bar $) baz', env.subst("$FOO $( bar $) baz", raw=1)
            assert env.subst_list("$FOO $( bar $) baz") == [ [ 'foo', 'baz' ],
                                                             [ 'bar', 'ack', 'bar', 'baz' ] ], env.subst_list("$FOO $( bar $) baz")
            assert env.subst_list("$FOO $( bar $) baz",
                                  raw=1) == [ [ 'foo', 'baz' ],
                                              [ 'bar', 'ack', '$(', 'bar', '$)', 'baz' ] ], env.subst_list("$FOO $( bar $) baz", raw=1)
            return "$FOO"
        def func_action(target, source,env, self=self):
            dummy=env['dummy']
            assert env.subst('$foo $( bar $)') == 'bar bar', env.subst('$foo $( bar $)')
            assert env.subst('$foo $( bar $)',
                             raw=1) == 'bar $( bar $)', env.subst('$foo $( bar $)', raw=1)
            assert env.subst_list([ '$foo', '$(', 'bar', '$)' ]) == [[ 'bar', 'bar' ]], env.subst_list([ '$foo', '$(', 'bar', '$)' ])
            assert env.subst_list([ '$foo', '$(', 'bar', '$)' ],
                                  raw=1) == [[ 'bar', '$(', 'bar', '$)' ]], env.subst_list([ '$foo', '$(', 'bar', '$)' ], raw=1)
            self.dummy=dummy
        def f2(target, source, env, for_signature, f=func_action):
            return f
        def ch(cmd, args, env, self=self):
            self.cmd.append(cmd)
            self.args.append(args)

        a = SCons.Action.CommandGeneratorAction(f)
        self.dummy = 0
        old_hdl = SCons.Action.GetCommandHandler()
        self.cmd = []
        self.args = []
        try:
            SCons.Action.SetCommandHandler(ch)
            a.execute([],[],env=Environment({ 'FOO' : 'foo baz\nbar ack' , 'dummy':1}))
        finally:
            SCons.Action.SetCommandHandler(old_hdl)
        assert self.dummy == 1
        assert self.cmd == [ 'foo', 'bar'], self.cmd
        assert self.args == [ [ 'foo', 'baz' ], [ 'bar', 'ack' ] ], self.args

        b=SCons.Action.CommandGeneratorAction(f2)
        self.dummy = 0
        b.execute(target=[], source=[], env=Environment({ 'foo' : 'bar','dummy':2 }))
        assert self.dummy==2, self.dummy
        del self.dummy

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
                           env=Environment({'foo':'FFF', 'bar' : 'BBB'}))
        assert c == "guux FFF BBB", c


class FunctionActionTestCase(unittest.TestCase):

    def test_init(self):
        """Test creation of a function Action
        """
        def func():
            pass
        a = SCons.Action.FunctionAction(func)
        assert a.function == func

    def test_execute(self):
        """Test executing a function Action
        """
        self.inc = 0
        def f(target, source, env):
            s = env['s']
            s.inc = s.inc + 1
            s.target = target
            s.source=source
            assert env.subst("foo$BAR") == 'foofoo bar', env.subst("foo$BAR")
            assert env.subst_list("foo$BAR") == [ [ 'foofoo', 'bar' ] ], \
                   env.subst_list("foo$BAR")
            return 0
        a = SCons.Action.FunctionAction(f)
        a.execute(target=1, source=2, env=Environment({'BAR':'foo bar','s':self}))
        assert self.inc == 1, self.inc
        assert self.source == [2], self.source
        assert self.target == [1], self.target

    def test_get_contents(self):
        """Test fetching the contents of a function Action
        """
        a = SCons.Action.FunctionAction(Func)
        c = a.get_contents(target=[], source=[], env=Environment({}))
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

    def test_execute(self):
        """Test executing a list of subsidiary Actions
        """
        self.inc = 0
        def f(target,source,env):
            s = env['s']
            s.inc = s.inc + 1
        a = SCons.Action.ListAction([f, f, f])
        a.execute([],[],Environment({'s':self}))
        assert self.inc == 3, self.inc

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
        c = a.get_contents(target=[], source=[], env=Environment({'s':self}))
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
        """Test executing a lazy-evalueation Action
        """
        def f(target, source, env):
            s = env['s']
            s.test=1
            return 0
        a = SCons.Action.Action('$BAR')
        a.execute([],[], env=Environment({'BAR':f,'s':self}))
        assert self.test == 1, self.test

    def test_get_contents(self):
        """Test fetching the contents of a lazy-evaluation Action
        """
        a = SCons.Action.Action("${FOO}")
        c = a.get_contents(target=[], source=[],
                           env=Environment({'FOO':[["This", "is", "$(", "a", "$)", "test"]]}))
        assert c == "This is test", c


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(ActionTestCase())
    suite.addTest(ActionBaseTestCase("test_cmp"))
    suite.addTest(ActionBaseTestCase("test_subst_dict"))
    for tclass in [CommandActionTestCase,
                   CommandGeneratorActionTestCase,
                   FunctionActionTestCase,
                   ListActionTestCase,
                   LazyActionTestCase]:
        for func in ["test_init", "test_execute", "test_get_contents"]:
            suite.addTest(tclass(func))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
