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

__revision__ = "src/engine/SCons/ActionTests.py __REVISION__ __DATE__ __DEVELOPER__"

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

        a4 = SCons.Action.Action(["x", a2, "y"])
        assert isinstance(a4, SCons.Action.ListAction), a4

        a5 = SCons.Action.Action(1)
        assert a5 is None, a5

        a6 = SCons.Action.Action(a1)
        assert a6 is a1

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

        d = a.subst_dict(env = {'a' : 'A', 'b' : 'B'})
        assert d['a'] == 'A', d
        assert d['b'] == 'B', d

        d = a.subst_dict(target = 't', source = 's')
        assert str(d['TARGETS']) == 't', d['TARGETS']
        assert str(d['TARGET']) == 't', d['TARGET']
        assert str(d['SOURCES']) == 's', d['SOURCES']

        d = a.subst_dict(target = ['t1', 't2'], source = ['s1', 's2'])
        TARGETS = map(lambda x: str(x), d['TARGETS'])
        TARGETS.sort()
        assert TARGETS == ['t1', 't2'], d['TARGETS']
        assert str(d['TARGET']) == 't1', d['TARGET']
        SOURCES = map(lambda x: str(x), d['SOURCES'])
        SOURCES.sort()
        assert SOURCES == ['s1', 's2'], d['SOURCES']

class CommandActionTestCase(unittest.TestCase):

    def test_init(self):
        """Test creation of a command Action
        """
        a = SCons.Action.CommandAction("xyzzy")
        assert a.command == "xyzzy"

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
        a = SCons.Action.CommandAction("xyzzy")
        a.execute()
        assert t.executed == 1

    def test_get_raw_contents(self):
        """Test fetching the contents of a command Action
        """
        a = SCons.Action.CommandAction("| $( $foo | $bar $) |")
        c = a.get_contents(foo = 'FFF', bar = 'BBB')
        assert c == "| $( FFF | BBB $) |"

    def test_get_contents(self):
        """Test fetching the contents of a command Action
        """
        a = SCons.Action.CommandAction("| $foo $( | $) $bar |")
        c = a.get_contents(foo = 'FFF', bar = 'BBB')
        assert c == "| FFF BBB |"

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

        def f(dummy, env, self=self):
            self.dummy = dummy
            assert env.subst('$FOO') == 'foo baz\nbar ack', env.subst('$FOO')
            assert env.subst_list('$FOO') == [ [ 'foo', 'baz' ],
                                               [ 'bar', 'ack' ] ], env.subst_list('$FOO')
            return [["$FOO"]]
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
            a.execute(dummy=1, env={ 'FOO' : 'foo baz\nbar ack' })
        finally:
            SCons.Action.SetCommandHandler(old_hdl)
        assert self.dummy == 1
        assert self.cmd == [ 'foo', 'bar'], self.cmd
        assert self.args == [ [ 'foo', 'baz' ], [ 'bar', 'ack' ] ], self.args
        del self.dummy

    def test_get_contents(self):
        """Test fetching the contents of a command generator Action
        """
        def f(target, source, foo, bar):
            return [["guux", foo, "$(", "ignore", "$)", bar]]

        a = SCons.Action.CommandGeneratorAction(f)
        c = a.get_contents(foo = 'FFF', bar = 'BBB')
        assert c == [["guux", 'FFF', 'BBB']], c


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
        def f(s, target, source, env):
            s.inc = s.inc + 1
            s.target = target
            s.source=source
            assert env.subst("foo$BAR") == 'foofoo bar', env.subst("foo$BAR")
            assert env.subst_list("foo$BAR") == [ [ 'foofoo', 'bar' ] ], \
                   env.subst_list("foo$BAR")
            return 0
        a = SCons.Action.FunctionAction(f)
        a.execute(s = self, target=1, source=2, env={'BAR':'foo bar'})
        assert self.inc == 1, self.inc
        assert self.source == [2], self.source
        assert self.target == [1], self.target

    def test_get_contents(self):
        """Test fetching the contents of a function Action
        """
        a = SCons.Action.FunctionAction(Func)
        c = a.get_contents()
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
        assert isinstance(a.list[2].list[0], SCons.Action.CommandAction)
        assert isinstance(a.list[2].list[1], SCons.Action.CommandAction)

    def test_execute(self):
        """Test executing a list of subsidiary Actions
        """
        self.inc = 0
        def f(s):
            s.inc = s.inc + 1
            return 0
        a = SCons.Action.ListAction([f, f, f])
        a.execute(s = self)
        assert self.inc == 3, self.inc

    def test_get_contents(self):
        """Test fetching the contents of a list of subsidiary Actions
        """
        a = SCons.Action.ListAction(["x", "y", "z"])
        c = a.get_contents()
        assert c == "xyz", c


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(ActionTestCase())
    suite.addTest(ActionBaseTestCase("test_cmp"))
    suite.addTest(ActionBaseTestCase("test_subst_dict"))
    for tclass in [CommandActionTestCase,
                   CommandGeneratorActionTestCase,
                   FunctionActionTestCase,
                   ListActionTestCase]:
        for func in ["test_init", "test_execute", "test_get_contents"]:
            suite.addTest(tclass(func))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
