# MIT License
#
# Copyright The SCons Foundation
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

# Define a null function and a null class for use as builder actions.
# Where these are defined in the file seems to affect their byte-code
# contents, so try to minimize changes by defining them here, before we
# even import anything.

from __future__ import annotations

def GlobalFunc() -> None:
    pass


class GlobalActFunc:
    def __call__(self) -> None:
        pass


import io
import os
import sys
import types
import unittest
from unittest import mock
from subprocess import PIPE
from typing import TYPE_CHECKING

# If assertEqual truncates strings so it's hard to see the diff, enable this:
# if 'unittest.util' in __import__('sys').modules:
#     __import__('sys').modules['unittest.util']._MAX_LENGTH = 99999999

import SCons.Action
import SCons.Environment
import SCons.Errors
from SCons.Action import scons_subproc_run

if TYPE_CHECKING:
    from SCons.Executor import Executor

import TestCmd

# Initial setup of the common environment for all tests,
# a temporary working directory containing a
# script for writing arguments to an output file.
#
# We don't do this as a setUp() method because it's
# unnecessary to create a separate directory and script
# for each test, they can just use the one.
test = TestCmd.TestCmd(workdir='')

test.write('act.py', """\
import os, string, sys

with open(sys.argv[1], 'w') as f:
    f.write("act.py: '" + "' '".join(sys.argv[2:]) + "'\\n")
    try:
        if sys.argv[3]:
            f.write("act.py: '" + os.environ[sys.argv[3]] + "'\\n")
    except:
        pass

if 'ACTPY_PIPE' in os.environ:
    if 'PIPE_STDOUT_FILE' in os.environ:
        with open(os.environ['PIPE_STDOUT_FILE'], 'r') as f:
            stdout_msg = f.read()
    else:
        stdout_msg = "act.py: stdout: executed act.py %s\\n" % ' '.join(sys.argv[1:])
    sys.stdout.write(stdout_msg)
    if 'PIPE_STDERR_FILE' in os.environ:
        with open(os.environ['PIPE_STDERR_FILE'], 'r') as f:
            stderr_msg = f.read()
    else:
        stderr_msg = "act.py: stderr: executed act.py %s\\n" % ' '.join(sys.argv[1:])
    sys.stderr.write(stderr_msg)
sys.exit(0)
""")

test.write('exit.py', """\
import sys
sys.exit(int(sys.argv[1]))
""")

act_py = test.workpath('act.py')
exit_py = test.workpath('exit.py')

outfile = test.workpath('outfile')
outfile2 = test.workpath('outfile2')
pipe_file = test.workpath('pipe.out')

scons_env = SCons.Environment.Environment()

# Capture all the stuff the Actions will print,
# so it doesn't clutter the output.
sys.stdout = io.StringIO()


class CmdStringHolder:
    def __init__(self, cmd, literal=None) -> None:
        self.data = str(cmd)
        self.literal = literal

    def is_literal(self) -> bool:
        return self.literal

    def escape(self, escape_func):
        """Escape the string with the supplied function.

        The function is expected to take an arbitrary string, then
        return it with all special characters escaped and ready
        for passing to the command interpreter.

        After calling this function, the next call to str() will
        return the escaped string.
        """

        if self.is_literal():
            return escape_func(self.data)
        elif ' ' in self.data or '\t' in self.data:
            return '"%s"' % self.data
        else:
            return self.data


class Environment:
    def __init__(self, **kw) -> None:
        self.d = {}
        self.d['SHELL'] = scons_env['SHELL']
        self.d['SPAWN'] = scons_env['SPAWN']
        self.d['PSPAWN'] = scons_env['PSPAWN']
        self.d['ESCAPE'] = scons_env['ESCAPE']
        for k, v in kw.items():
            self.d[k] = v

    # Just use the underlying scons_subst*() utility methods.
    def subst(self, strSubst, raw: int=0, target=[], source=[], conv=None, overrides: bool=False):
        return SCons.Subst.scons_subst(strSubst, self, raw,
                                       target, source, self.d, conv=conv, overrides=overrides)

    subst_target_source = subst

    def subst_list(self, strSubst, raw: int=0, target=[], source=[], conv=None, overrides: bool=False):
        return SCons.Subst.scons_subst_list(strSubst, self, raw,
                                            target, source, self.d, conv=conv, overrides=overrides)

    def __getitem__(self, item):
        return self.d[item]

    def __setitem__(self, item, value) -> None:
        self.d[item] = value

    def __contains__(self, key) -> bool:
        return key in self.d

    def get(self, key, value=None):
        return self.d.get(key, value)

    def items(self):
        return list(self.d.items())

    def Dictionary(self):
        return self.d

    def Clone(self, **kw):
        res = Environment()
        res.d = SCons.Util.semi_deepcopy(self.d)
        for k, v in kw.items():
            res.d[k] = v
        return res

    def sig_dict(self):
        d = {}
        for k, v in self.items(): d[k] = v
        d['TARGETS'] = ['__t1__', '__t2__', '__t3__', '__t4__', '__t5__', '__t6__']
        d['TARGET'] = d['TARGETS'][0]
        d['SOURCES'] = ['__s1__', '__s2__', '__s3__', '__s4__', '__s5__', '__s6__']
        d['SOURCE'] = d['SOURCES'][0]
        return d


class DummyNode:
    def __init__(self, name) -> None:
        self.name = name

    def str_for_display(self):
        return '"' + self.name + '"'

    def __str__(self) -> str:
        return self.name

    def rfile(self):
        return self

    def get_subst_proxy(self):
        return self


if os.name == 'java':
    python = os.path.join(sys.prefix, 'jython')
else:
    python = os.environ.get('python_executable', sys.executable)
_python_ = test.escape(python)

_null = SCons.Action._null


def test_varlist(pos_call, str_call, cmd, cmdstrfunc, **kw) -> None:
    def call_action(a, pos_call=pos_call, str_call=str_call, kw=kw):
        a = SCons.Action.Action(*a, **kw)
        # returned object must provide these entry points
        assert hasattr(a, '__call__')
        assert hasattr(a, 'get_contents')
        assert hasattr(a, 'genstring')
        pos_call(a)
        str_call(a)
        return a

    a = call_action((cmd, cmdstrfunc))
    assert a.varlist == (), a.varlist

    a = call_action((cmd, cmdstrfunc, 'foo'))
    assert a.varlist == ('foo',), a.varlist

    a = call_action((cmd, cmdstrfunc, 'a', 'b', 'c'))
    assert a.varlist == ('a', 'b', 'c'), a.varlist

    a = call_action((cmd, cmdstrfunc, ['a', 'b', 'c']))
    assert a.varlist == ('a', 'b', 'c'), a.varlist

    kw['varlist'] = 'foo'
    a = call_action((cmd, cmdstrfunc))
    assert a.varlist == ('foo',), a.varlist

    kw['varlist'] = ['x', 'y', 'z']
    a = call_action((cmd, cmdstrfunc))
    assert a.varlist == ('x', 'y', 'z'), a.varlist

    a = call_action((cmd, cmdstrfunc, 'foo'))
    assert a.varlist == ('foo', 'x', 'y', 'z'), a.varlist

    a = call_action((cmd, cmdstrfunc, 'a', 'b', 'c'))
    assert a.varlist == ('a', 'b', 'c', 'x', 'y', 'z'), a.varlist


def test_positional_args(pos_callback, cmd, **kw):
    """Test that Action returns the expected type and positional args work."""

    act = SCons.Action.Action(cmd, **kw)
    pos_callback(act)
    assert act.varlist == (), act.varlist

    if not isinstance(act, SCons.Action._ActionAction):
        # only valid cmdstrfunc is None
        def none(a) -> None:
            pass

        test_varlist(pos_callback, none, cmd, None, **kw)
    else:
        # _ActionAction should have set these
        assert hasattr(act, 'strfunction')
        assert act.cmdstr is _null, act.cmdstr
        assert act.presub is _null, act.presub
        assert act.chdir is None, act.chdir
        assert act.exitstatfunc is SCons.Action.default_exitstatfunc, \
            act.exitstatfunc

        def cmdstr(a) -> None:
            assert hasattr(a, 'strfunction')
            assert a.cmdstr == 'cmdstr', a.cmdstr

        test_varlist(pos_callback, cmdstr, cmd, 'cmdstr', **kw)

        def fun() -> None:
            pass

        def strfun(a, fun=fun) -> None:
            assert a.strfunction is fun, a.strfunction
            assert a.cmdstr == _null, a.cmdstr

        test_varlist(pos_callback, strfun, cmd, fun, **kw)

        def none(a) -> None:
            assert hasattr(a, 'strfunction')
            assert a.cmdstr is None, a.cmdstr

        test_varlist(pos_callback, none, cmd, None, **kw)

        # Test handling of bad cmdstrfunc arguments
        try:
            a = SCons.Action.Action(cmd, [], **kw)
        except SCons.Errors.UserError as e:
            s = str(e)
            m = 'Invalid command display variable'
            assert m in s, f'Unexpected string: {s}'
        else:
            raise Exception("did not catch expected UserError")

    return act


class ActionTestCase(unittest.TestCase):
    """Test the Action() factory function"""

    def test_FunctionAction(self) -> None:
        """Test the Action() factory's creation of FunctionAction objects."""

        def foo() -> None:
            pass

        def func_action(a, foo=foo) -> None:
            assert isinstance(a, SCons.Action.FunctionAction), a
            assert a.execfunction == foo, a.execfunction

        test_positional_args(func_action, foo)
        # a singleton list returns the contained action
        test_positional_args(func_action, [foo])

    def test_CommandAction(self) -> None:
        """Test the Action() factory's creation of CommandAction objects."""

        def cmd_action(a) -> None:
            assert isinstance(a, SCons.Action.CommandAction), a
            assert a.cmd_list == "string", a.cmd_list

        test_positional_args(cmd_action, "string")
        # a singleton list returns the contained action
        test_positional_args(cmd_action, ["string"])

        def line_action(a) -> None:
            assert isinstance(a, SCons.Action.CommandAction), a
            assert a.cmd_list == ["explicit", "command", "line"], a.cmd_list

        test_positional_args(line_action, [["explicit", "command", "line"]])

    def test_ListAction(self) -> None:
        """Test the Action() factory's creation of ListAction objects."""

        a1 = SCons.Action.Action(["x", "y", "z", ["a", "b", "c"]])
        assert isinstance(a1, SCons.Action.ListAction), f"a1 is {type(a1)}"
        assert a1.varlist == (), a1.varlist
        assert isinstance(a1.list[0], SCons.Action.CommandAction), a1.list[0]
        assert a1.list[0].cmd_list == "x", a1.list[0].cmd_list
        assert isinstance(a1.list[1], SCons.Action.CommandAction), a1.list[1]
        assert a1.list[1].cmd_list == "y", a1.list[1].cmd_list
        assert isinstance(a1.list[2], SCons.Action.CommandAction), a1.list[2]
        assert a1.list[2].cmd_list == "z", a1.list[2].cmd_list
        assert isinstance(a1.list[3], SCons.Action.CommandAction), a1.list[3]
        assert a1.list[3].cmd_list == ["a", "b", "c"], a1.list[3].cmd_list

        a2 = SCons.Action.Action("x\ny\nz")
        assert isinstance(a2, SCons.Action.ListAction), f"a2 is {type(a2)}"
        assert a2.varlist == (), a2.varlist
        assert isinstance(a2.list[0], SCons.Action.CommandAction), a2.list[0]
        assert a2.list[0].cmd_list == "x", a2.list[0].cmd_list
        assert isinstance(a2.list[1], SCons.Action.CommandAction), a2.list[1]
        assert a2.list[1].cmd_list == "y", a2.list[1].cmd_list
        assert isinstance(a2.list[2], SCons.Action.CommandAction), a2.list[2]
        assert a2.list[2].cmd_list == "z", a2.list[2].cmd_list

        def foo() -> None:
            pass

        a3 = SCons.Action.Action(["x", foo, "z"])
        assert isinstance(a3, SCons.Action.ListAction), f"a3 is {type(a3)}"
        assert a3.varlist == (), a3.varlist
        assert isinstance(a3.list[0], SCons.Action.CommandAction), a3.list[0]
        assert a3.list[0].cmd_list == "x", a3.list[0].cmd_list
        assert isinstance(a3.list[1], SCons.Action.FunctionAction), a3.list[1]
        assert a3.list[1].execfunction == foo, a3.list[1].execfunction
        assert isinstance(a3.list[2], SCons.Action.CommandAction), a3.list[2]
        assert a3.list[2].cmd_list == "z", a3.list[2].cmd_list

        a4 = SCons.Action.Action(["x", "y"], strfunction=foo)
        assert isinstance(a4, SCons.Action.ListAction), f"a4 is {type(a4)}"
        assert a4.varlist == (), a4.varlist
        assert isinstance(a4.list[0], SCons.Action.CommandAction), a4.list[0]
        assert a4.list[0].cmd_list == "x", a4.list[0].cmd_list
        assert a4.list[0].strfunction == foo, a4.list[0].strfunction
        assert isinstance(a4.list[1], SCons.Action.CommandAction), a4.list[1]
        assert a4.list[1].cmd_list == "y", a4.list[1].cmd_list
        assert a4.list[1].strfunction == foo, a4.list[1].strfunction

        a5 = SCons.Action.Action("x\ny", strfunction=foo)
        assert isinstance(a5, SCons.Action.ListAction), f"a5 is {type(a5)}"
        assert a5.varlist == (), a5.varlist
        assert isinstance(a5.list[0], SCons.Action.CommandAction), a5.list[0]
        assert a5.list[0].cmd_list == "x", a5.list[0].cmd_list
        assert a5.list[0].strfunction == foo, a5.list[0].strfunction
        assert isinstance(a5.list[1], SCons.Action.CommandAction), a5.list[1]
        assert a5.list[1].cmd_list == "y", a5.list[1].cmd_list
        assert a5.list[1].strfunction == foo, a5.list[1].strfunction

        a6 = SCons.Action.Action(["action with space"])
        assert isinstance(a6, SCons.Action.CommandAction), f"a6 is {type(a6)}"

    def test_CommandGeneratorAction(self) -> None:
        """Test the Action factory's creation of CommandGeneratorAction objects."""

        def foo() -> None: pass

        def gen_action(a, foo=foo) -> None:
            assert isinstance(a, SCons.Action.CommandGeneratorAction), a
            assert a.generator is foo, a.generator

        test_positional_args(gen_action, foo, generator=1)

    def test_LazyCmdGeneratorAction(self) -> None:
        """Test the Action factory's creation of lazy CommandGeneratorAction objects."""

        def lazy_action(a) -> None:
            assert isinstance(a, SCons.Action.LazyAction), a
            assert a.var == "FOO", a.var
            assert a.cmd_list == "${FOO}", a.cmd_list

        test_positional_args(lazy_action, "$FOO")
        test_positional_args(lazy_action, "${FOO}")

    def test_no_action(self) -> None:
        """Test when the Action() factory can't create an action object."""

        try:
            a5 = SCons.Action.Action(1)
        except TypeError:
            pass
        else:
            assert 0, "Should have thrown a TypeError creating Action from an int."

    def test_reentrance(self) -> None:
        """Test the Action factory when the action is already an Action object."""

        a1 = SCons.Action.Action("foo")
        a2 = SCons.Action.Action(a1)
        assert a2 is a1, a2


class _ActionActionTestCase(unittest.TestCase):

    def test__init__(self) -> None:
        """Test creation of _ActionAction objects."""

        def func1() -> None:
            pass

        def func2() -> None:
            pass

        def func3() -> None:
            pass

        a = SCons.Action._ActionAction()
        assert not hasattr(a, 'strfunction')
        assert a.cmdstr is _null, a.cmdstr
        assert a.varlist == (), a.varlist
        assert a.presub is _null, a.presub
        assert a.chdir is None, a.chdir
        assert a.exitstatfunc is SCons.Action.default_exitstatfunc, a.exitstatfunc

        assert SCons.Action._ActionAction(kwarg=1)
        assert not hasattr(a, 'kwarg')
        assert not hasattr(a, 'strfunction')
        assert a.cmdstr is _null, a.cmdstr
        assert a.varlist == (), a.varlist
        assert a.presub is _null, a.presub
        assert a.chdir is None, a.chdir
        assert a.exitstatfunc is SCons.Action.default_exitstatfunc, a.exitstatfunc

        a = SCons.Action._ActionAction(strfunction=func1)
        assert a.strfunction is func1, a.strfunction

        a = SCons.Action._ActionAction(strfunction=None)
        assert not hasattr(a, 'strfunction')
        assert a.cmdstr is None, a.cmdstr

        a = SCons.Action._ActionAction(cmdstr='cmdstr')
        assert not hasattr(a, 'strfunction')
        assert a.cmdstr == 'cmdstr', a.cmdstr

        a = SCons.Action._ActionAction(cmdstr=None)
        assert not hasattr(a, 'strfunction')
        assert a.cmdstr is None, a.cmdstr

        t = ('a', 'b', 'c')
        a = SCons.Action._ActionAction(varlist=t)
        assert a.varlist == t, a.varlist

        a = SCons.Action._ActionAction(presub=func1)
        assert a.presub is func1, a.presub

        a = SCons.Action._ActionAction(chdir=1)
        assert a.chdir == 1, a.chdir

        a = SCons.Action._ActionAction(exitstatfunc=func1)
        assert a.exitstatfunc is func1, a.exitstatfunc

        a = SCons.Action._ActionAction(
            # alphabetical order ...
            chdir='x',
            cmdstr='cmdstr',
            exitstatfunc=func3,
            presub=func2,
            strfunction=func1,
            varlist=t,
        )
        assert a.chdir == 'x', a.chdir
        assert a.cmdstr == 'cmdstr', a.cmdstr
        assert a.exitstatfunc is func3, a.exitstatfunc
        assert a.presub is func2, a.presub
        assert a.strfunction is func1, a.strfunction
        assert a.varlist is t, a.varlist

    def test_dup_keywords(self):
        """Test handling of both cmdstr and strfunction arguments."""

        def func() -> None:
            pass

        try:
            a = SCons.Action.Action('foo', cmdstr='string', strfunction=func)
        except SCons.Errors.UserError as e:
            s = str(e)
            m = 'Cannot have both strfunction and cmdstr args to Action()'
            assert m in s, f'Unexpected string: {s}'
        else:
            raise Exception("did not catch expected UserError")

    def test___cmp__(self) -> None:
        """Test Action comparison."""

        a1 = SCons.Action.Action("x")
        a2 = SCons.Action.Action("x")
        assert a1 == a2
        a3 = SCons.Action.Action("y")
        assert a1 != a3
        assert a2 != a3

    def test_print_cmd_lines(self) -> None:
        """Test the print_cmd_lines() method."""

        save_stdout = sys.stdout

        try:
            def execfunc(target, source, env) -> None:
                pass

            a = SCons.Action.Action(execfunc)

            sio = io.StringIO()
            sys.stdout = sio
            a.print_cmd_line("foo bar", None, None, None)
            s = sio.getvalue()
            assert s == "foo bar\n", s

        finally:
            sys.stdout = save_stdout

    def test___call__(self) -> None:
        """Test calling an Action."""

        save_stdout = sys.stdout

        save_print_actions = SCons.Action.print_actions
        save_print_actions_presub = SCons.Action.print_actions_presub
        save_execute_actions = SCons.Action.execute_actions
        # SCons.Action.print_actions = 0

        test = TestCmd.TestCmd(workdir='')
        test.subdir('sub', 'xyz')
        os.chdir(test.workpath())

        try:
            env = Environment()

            def execfunc(target, source, env) -> int:
                assert isinstance(target, list), type(target)
                assert isinstance(source, list), type(source)
                return 7

            a = SCons.Action.Action(execfunc)

            def firstfunc(target, source, env) -> int:
                assert isinstance(target, list), type(target)
                assert isinstance(source, list), type(source)
                return 0

            def lastfunc(target, source, env) -> int:
                assert isinstance(target, list), type(target)
                assert isinstance(source, list), type(source)
                return 9

            b = SCons.Action.Action([firstfunc, execfunc, lastfunc])

            sio = io.StringIO()
            sys.stdout = sio
            result = a("out", "in", env)
            assert result.status == 7, result
            s = sio.getvalue()
            assert s == "execfunc(['out'], ['in'])\n", s

            a.chdir = 'xyz'
            expect = "os.chdir(%s)\nexecfunc(['out'], ['in'])\nos.chdir(%s)\n"

            sio = io.StringIO()
            sys.stdout = sio
            result = a("out", "in", env)
            assert result.status == 7, result.status
            s = sio.getvalue()
            assert s == expect % (repr('xyz'), repr(test.workpath())), s

            sio = io.StringIO()
            sys.stdout = sio
            result = a("out", "in", env, chdir='sub')
            assert result.status == 7, result.status
            s = sio.getvalue()
            assert s == expect % (repr('sub'), repr(test.workpath())), s

            a.chdir = None

            sio = io.StringIO()
            sys.stdout = sio
            result = b("out", "in", env)
            assert result.status == 7, result.status
            s = sio.getvalue()
            assert s == "firstfunc(['out'], ['in'])\nexecfunc(['out'], ['in'])\n", s

            SCons.Action.execute_actions = 0

            sio = io.StringIO()
            sys.stdout = sio
            result = a("out", "in", env)
            assert result == 0, result
            s = sio.getvalue()
            assert s == "execfunc(['out'], ['in'])\n", s

            sio = io.StringIO()
            sys.stdout = sio
            result = b("out", "in", env)
            assert result == 0, result
            s = sio.getvalue()
            assert s == "firstfunc(['out'], ['in'])\nexecfunc(['out'], ['in'])\nlastfunc(['out'], ['in'])\n", s

            SCons.Action.print_actions_presub = 1
            SCons.Action.execute_actions = 1

            sio = io.StringIO()
            sys.stdout = sio
            result = a("out", "in", env)
            assert result.status == 7, result.status
            s = sio.getvalue()
            assert s == "Building out with action:\n  execfunc(target, source, env)\nexecfunc(['out'], ['in'])\n", s

            sio = io.StringIO()
            sys.stdout = sio
            result = a("out", "in", env, presub=0)
            assert result.status == 7, result.status
            s = sio.getvalue()
            assert s == "execfunc(['out'], ['in'])\n", s

            sio = io.StringIO()
            sys.stdout = sio
            result = a("out", "in", env, presub=1)
            assert result.status == 7, result.status
            s = sio.getvalue()
            assert s == "Building out with action:\n  execfunc(target, source, env)\nexecfunc(['out'], ['in'])\n", s

            sio = io.StringIO()
            sys.stdout = sio
            result = b(["out"], "in", env, presub=1)
            assert result.status == 7, result.status
            s = sio.getvalue()
            assert s == "Building out with action:\n  firstfunc(target, source, env)\nfirstfunc(['out'], ['in'])\nBuilding out with action:\n  execfunc(target, source, env)\nexecfunc(['out'], ['in'])\n", s

            sio = io.StringIO()
            sys.stdout = sio
            result = b(["out", "list"], "in", env, presub=1)
            assert result.status == 7, result.status
            s = sio.getvalue()
            assert s == "Building out and list with action:\n  firstfunc(target, source, env)\nfirstfunc(['out', 'list'], ['in'])\nBuilding out and list with action:\n  execfunc(target, source, env)\nexecfunc(['out', 'list'], ['in'])\n", s

            a2 = SCons.Action.Action(execfunc)

            sio = io.StringIO()
            sys.stdout = sio
            result = a2("out", "in", env)
            assert result.status == 7, result.status
            s = sio.getvalue()
            assert s == "Building out with action:\n  execfunc(target, source, env)\nexecfunc(['out'], ['in'])\n", s

            sio = io.StringIO()
            sys.stdout = sio
            result = a2("out", "in", env, presub=0)
            assert result.status == 7, result.status
            s = sio.getvalue()
            assert s == "execfunc(['out'], ['in'])\n", s

            SCons.Action.execute_actions = 0

            sio = io.StringIO()
            sys.stdout = sio
            result = a2("out", "in", env, presub=0)
            assert result == 0, result
            s = sio.getvalue()
            assert s == "execfunc(['out'], ['in'])\n", s

            sio = io.StringIO()
            sys.stdout = sio
            result = a("out", "in", env, presub=0, execute=1, show=0)
            assert result.status == 7, result.status
            s = sio.getvalue()
            assert s == '', s

            sys.stdout = save_stdout
            exitstatfunc_result = []

            def exitstatfunc(stat, result=exitstatfunc_result):
                result.append(stat)
                return stat

            result = a("out", "in", env, exitstatfunc=exitstatfunc)
            assert result == 0, result
            assert exitstatfunc_result == [], exitstatfunc_result

            result = a("out", "in", env, execute=1, exitstatfunc=exitstatfunc)
            assert result.status == 7, result.status
            assert exitstatfunc_result == [7], exitstatfunc_result

            SCons.Action.execute_actions = 1

            result = []

            def my_print_cmd_line(s, target, source, env, result=result) -> None:
                result.append(s)

            env['PRINT_CMD_LINE_FUNC'] = my_print_cmd_line
            a("output", "input", env)
            assert result == ["execfunc(['output'], ['input'])"], result


        finally:
            sys.stdout = save_stdout
            SCons.Action.print_actions = save_print_actions
            SCons.Action.print_actions_presub = save_print_actions_presub
            SCons.Action.execute_actions = save_execute_actions

    def test_presub_lines(self) -> None:
        """Test the presub_lines() method."""

        env = Environment()
        a = SCons.Action.Action("x")
        s = a.presub_lines(env)
        assert s == ['x'], s

        a = SCons.Action.Action(["y", "z"])
        s = a.presub_lines(env)
        assert s == ['y', 'z'], s

        def func() -> None:
            pass

        a = SCons.Action.Action(func)
        s = a.presub_lines(env)
        assert s == ["func(target, source, env)"], s

        def gen(target, source, env, for_signature):
            return 'generat' + env.get('GEN', 'or')

        a = SCons.Action.Action(gen, generator=1)
        s = a.presub_lines(env)
        assert s == ["generator"], s
        s = a.presub_lines(Environment(GEN='ed'))
        assert s == ["generated"], s

        a = SCons.Action.Action("$ACT")
        s = a.presub_lines(env)
        assert s == [''], s
        s = a.presub_lines(Environment(ACT='expanded action'))
        assert s == ['expanded action'], s

    def test_add(self) -> None:
        """Test adding Actions to stuff."""

        # Adding actions to other Actions or to stuff that can
        # be converted into an Action should produce a ListAction
        # containing all the Actions.
        def bar():
            return None

        baz = SCons.Action.Action(bar, generator=1)
        act1 = SCons.Action.Action('foo bar')
        act2 = SCons.Action.Action(['foo', bar])

        sum = act1 + act2
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 3, len(sum.list)
        assert [isinstance(x, SCons.Action.ActionBase) for x in sum.list] == [1, 1, 1]

        sum = act1 + act1
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 2, len(sum.list)

        sum = act2 + act2
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 4, len(sum.list)

        # Should also be able to add command generators to each other
        # or to actions
        sum = baz + baz
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 2, len(sum.list)

        sum = baz + act1
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 2, len(sum.list)

        sum = act2 + baz
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 3, len(sum.list)

        # Also should be able to add Actions to anything that can
        # be converted into an action.
        sum = act1 + bar
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 2, len(sum.list)
        assert isinstance(sum.list[1], SCons.Action.FunctionAction)

        sum = 'foo bar' + act2
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 3, len(sum.list)
        assert isinstance(sum.list[0], SCons.Action.CommandAction)

        sum = ['foo', 'bar'] + act1
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 3, sum.list
        assert isinstance(sum.list[0], SCons.Action.CommandAction)
        assert isinstance(sum.list[1], SCons.Action.CommandAction)

        sum = act2 + [baz, bar]
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 4, len(sum.list)
        assert isinstance(sum.list[2], SCons.Action.CommandGeneratorAction)
        assert isinstance(sum.list[3], SCons.Action.FunctionAction)

        # OK to add None on either side (should be ignored)
        sum = act1 + None
        assert sum == act1

        sum = None + act1
        assert sum == act1

        try:
            sum = act2 + 1
        except TypeError:
            pass
        else:
            assert 0, "Should have thrown a TypeError adding to an int."

        try:
            sum = 1 + act2
        except TypeError:
            pass
        else:
            assert 0, "Should have thrown a TypeError adding to an int."


class CommandActionTestCase(unittest.TestCase):

    def test___init__(self) -> None:
        """Test creation of a command Action."""

        a = SCons.Action.CommandAction(["xyzzy"])
        assert a.cmd_list == ["xyzzy"], a.cmd_list
        assert a.cmdstr is _null, a.cmdstr

        a = SCons.Action.CommandAction(["abra"], cmdstr="cadabra")
        assert a.cmd_list == ["abra"], a.cmd_list
        assert a.cmdstr == "cadabra", a.cmdstr

    def test___str__(self) -> None:
        """Test fetching the pre-substitution string for command Actions."""

        env = Environment()
        act = SCons.Action.CommandAction('xyzzy $TARGET $SOURCE')
        s = str(act)
        assert s == 'xyzzy $TARGET $SOURCE', s

        act = SCons.Action.CommandAction(['xyzzy',
                                          '$TARGET', '$SOURCE',
                                          '$TARGETS', '$SOURCES'])
        s = str(act)
        assert s == "xyzzy $TARGET $SOURCE $TARGETS $SOURCES", s

    def test_genstring(self) -> None:
        """Test the genstring() method for command Actions."""

        env = Environment()
        t1 = DummyNode('t1')
        t2 = DummyNode('t2')
        s1 = DummyNode('s1')
        s2 = DummyNode('s2')
        act = SCons.Action.CommandAction('xyzzy $TARGET $SOURCE')
        expect = 'xyzzy $TARGET $SOURCE'
        s = act.genstring([], [], env)
        assert s == expect, s
        s = act.genstring([t1], [s1], env)
        assert s == expect, s
        s = act.genstring([t1, t2], [s1, s2], env)
        assert s == expect, s

        act = SCons.Action.CommandAction('xyzzy $TARGETS $SOURCES')
        expect = 'xyzzy $TARGETS $SOURCES'
        s = act.genstring([], [], env)
        assert s == expect, s
        s = act.genstring([t1], [s1], env)
        assert s == expect, s
        s = act.genstring([t1, t2], [s1, s2], env)
        assert s == expect, s

        act = SCons.Action.CommandAction(['xyzzy',
                                          '$TARGET', '$SOURCE',
                                          '$TARGETS', '$SOURCES'])
        expect = "xyzzy $TARGET $SOURCE $TARGETS $SOURCES"
        s = act.genstring([], [], env)
        assert s == expect, s
        s = act.genstring([t1], [s1], env)
        assert s == expect, s
        s = act.genstring([t1, t2], [s1, s2], env)
        assert s == expect, s

    def test_strfunction(self) -> None:
        """Test fetching the string representation of command Actions."""

        env = Environment()
        t1 = DummyNode('t1')
        t2 = DummyNode('t2')
        s1 = DummyNode('s1')
        s2 = DummyNode('s2')
        act = SCons.Action.CommandAction('xyzzy $TARGET $SOURCE')
        s = act.strfunction([], [], env)
        assert s == 'xyzzy', s
        s = act.strfunction([t1], [s1], env)
        assert s == 'xyzzy t1 s1', s
        s = act.strfunction([t1, t2], [s1, s2], env)
        assert s == 'xyzzy t1 s1', s

        act = SCons.Action.CommandAction('xyzzy $TARGET $SOURCE',
                                         cmdstr='cmdstr - $SOURCE - $TARGET -')
        s = act.strfunction([], [], env)
        assert s == 'cmdstr -  -  -', s
        s = act.strfunction([t1], [s1], env)
        assert s == 'cmdstr - s1 - t1 -', s
        s = act.strfunction([t1, t2], [s1, s2], env)
        assert s == 'cmdstr - s1 - t1 -', s

        act = SCons.Action.CommandAction('xyzzy $TARGETS $SOURCES')
        s = act.strfunction([], [], env)
        assert s == 'xyzzy', s
        s = act.strfunction([t1], [s1], env)
        assert s == 'xyzzy t1 s1', s
        s = act.strfunction([t1, t2], [s1, s2], env)
        assert s == 'xyzzy t1 t2 s1 s2', s

        act = SCons.Action.CommandAction('xyzzy $TARGETS $SOURCES',
                                         cmdstr='cmdstr = $SOURCES = $TARGETS =')
        s = act.strfunction([], [], env)
        assert s == 'cmdstr =  =  =', s
        s = act.strfunction([t1], [s1], env)
        assert s == 'cmdstr = s1 = t1 =', s
        s = act.strfunction([t1, t2], [s1, s2], env)
        assert s == 'cmdstr = s1 s2 = t1 t2 =', s

        act = SCons.Action.CommandAction(['xyzzy',
                                          '$TARGET', '$SOURCE',
                                          '$TARGETS', '$SOURCES'])
        s = act.strfunction([], [], env)
        assert s == 'xyzzy', s
        s = act.strfunction([t1], [s1], env)
        assert s == 'xyzzy t1 s1 t1 s1', s
        s = act.strfunction([t1, t2], [s1, s2], env)
        assert s == 'xyzzy t1 s1 t1 t2 s1 s2', s

        act = SCons.Action.CommandAction('xyzzy $TARGETS $SOURCES',
                                         cmdstr='cmdstr\t$TARGETS\n$SOURCES   ')

        s = act.strfunction([], [], env)
        assert s == 'cmdstr\t\n   ', s
        s = act.strfunction([t1], [s1], env)
        assert s == 'cmdstr\tt1\ns1   ', s
        s = act.strfunction([t1, t2], [s1, s2], env)
        assert s == 'cmdstr\tt1 t2\ns1 s2   ', s

        def sf(target, source, env) -> str:
            return "sf was called"

        act = SCons.Action.CommandAction('foo', strfunction=sf)
        s = act.strfunction([], [], env)
        assert s == "sf was called", s

        class actclass1:
            def __init__(self, targets, sources, env) -> None:
                pass

            def __call__(self) -> int:
                return 1

        class actclass2:
            def __init__(self, targets, sources, env) -> None:
                self.strfunction = 5

            def __call__(self) -> int:
                return 2

        class actclass3:
            def __init__(self, targets, sources, env) -> None:
                pass

            def __call__(self) -> int:
                return 3

            def strfunction(self, targets, sources, env) -> str:
                return 'actclass3 on %s to get %s' % (str(sources[0]),
                                                      str(targets[0]))

        class actclass4:
            def __init__(self, targets, sources, env) -> None:
                pass

            def __call__(self) -> int:
                return 4

            strfunction = None

        act1 = SCons.Action.Action(actclass1([t1], [s1], env))
        s = act1.strfunction([t1], [s1], env)
        assert s == 'actclass1(["t1"], ["s1"])', s

        act2 = SCons.Action.Action(actclass2([t1], [s1], env))
        s = act2.strfunction([t1], [s1], env)
        assert s == 'actclass2(["t1"], ["s1"])', s

        act3 = SCons.Action.Action(actclass3([t1], [s1], env))
        s = act3.strfunction([t1], [s1], env)
        assert s == 'actclass3 on s1 to get t1', s

        act4 = SCons.Action.Action(actclass4([t1], [s1], env))
        s = act4.strfunction([t1], [s1], env)
        assert s is None, s

        act = SCons.Action.CommandAction("@foo bar")
        s = act.strfunction([], [], env)
        assert s == "", s

        act = SCons.Action.CommandAction("@-foo bar")
        s = act.strfunction([], [], env)
        assert s == "", s

        act = SCons.Action.CommandAction("-@foo bar")
        s = act.strfunction([], [], env)
        assert s == "", s

        act = SCons.Action.CommandAction("-foo bar")
        s = act.strfunction([], [], env)
        assert s == "foo bar", s

        act = SCons.Action.CommandAction("@ foo bar")
        s = act.strfunction([], [], env)
        assert s == "", s

        act = SCons.Action.CommandAction("@- foo bar")
        s = act.strfunction([], [], env)
        assert s == "", s

        act = SCons.Action.CommandAction("-@ foo bar")
        s = act.strfunction([], [], env)
        assert s == "", s

        act = SCons.Action.CommandAction("- foo bar")
        s = act.strfunction([], [], env)
        assert s == "foo bar", s

    def test_execute(self) -> None:
        """Test execution of command Actions."""

        try:
            env = self.env
        except AttributeError:
            env = Environment()

        cmd1 = r'%s %s %s xyzzy' % (_python_, act_py, outfile)

        act = SCons.Action.CommandAction(cmd1)
        r = act([], [], env.Clone())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'xyzzy'\n", c

        cmd2 = r'%s %s %s $TARGET' % (_python_, act_py, outfile)

        act = SCons.Action.CommandAction(cmd2)
        r = act(DummyNode('foo'), [], env.Clone())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'foo'\n", c

        cmd3 = r'%s %s %s ${TARGETS}' % (_python_, act_py, outfile)

        act = SCons.Action.CommandAction(cmd3)
        r = act(list(map(DummyNode, ['aaa', 'bbb'])), [], env.Clone())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'aaa' 'bbb'\n", c

        cmd4 = r'%s %s %s $SOURCES' % (_python_, act_py, outfile)

        act = SCons.Action.CommandAction(cmd4)
        r = act([], [DummyNode('one'), DummyNode('two')], env.Clone())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'one' 'two'\n", c

        cmd4 = r'%s %s %s ${SOURCES[:2]}' % (_python_, act_py, outfile)

        act = SCons.Action.CommandAction(cmd4)
        sources = [DummyNode('three'), DummyNode('four'), DummyNode('five')]
        env2 = env.Clone()
        r = act([], source=sources, env=env2)
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'three' 'four'\n", c

        cmd5 = r'%s %s %s $TARGET XYZZY' % (_python_, act_py, outfile)

        act = SCons.Action.CommandAction(cmd5)
        env5 = Environment()
        if 'ENV' in scons_env:
            env5['ENV'] = scons_env['ENV']
            PATH = scons_env['ENV'].get('PATH', '')
        else:
            env5['ENV'] = {}
            PATH = ''

        env5['ENV']['XYZZY'] = 'xyzzy'
        r = act(target=DummyNode('out5'), source=[], env=env5)

        act = SCons.Action.CommandAction(cmd5)
        r = act(target=DummyNode('out5'),
                source=[],
                env=env.Clone(ENV={'XYZZY': 'xyzzy5',
                                   'PATH': PATH}))
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'out5' 'XYZZY'\nact.py: 'xyzzy5'\n", c

        class Obj:
            def __init__(self, str) -> None:
                self._str = str

            def __str__(self) -> str:
                return self._str

            def rfile(self):
                return self

            def get_subst_proxy(self):
                return self

        cmd6 = r'%s %s %s ${TARGETS[1]} $TARGET ${SOURCES[:2]}' % (_python_, act_py, outfile)

        act = SCons.Action.CommandAction(cmd6)
        r = act(target=[Obj('111'), Obj('222')],
                source=[Obj('333'), Obj('444'), Obj('555')],
                env=env.Clone())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: '222' '111' '333' '444'\n", c

        if os.name == 'nt':
            # NT treats execs of directories and non-executable files
            # as "file not found" errors
            expect_nonexistent = 1
            expect_nonexecutable_file = 1
            expect_nonexecutable_dir = 1
        elif sys.platform == 'cygwin':
            expect_nonexistent = 127
            # Newer cygwin seems to return 126 for following
            expect_nonexecutable_file = 126
            expect_nonexecutable_dir = 127
        else:
            expect_nonexistent = 127
            expect_nonexecutable_file = 126
            expect_nonexecutable_dir = 126

        # Test that a nonexistent command returns 127
        act = SCons.Action.CommandAction(python + "_no_such_command_")
        r = act([], [], env.Clone(out=outfile))
        assert r.status == expect_nonexistent, r.status

        # Test that trying to execute a directory returns 126
        dir, tail = os.path.split(python)
        act = SCons.Action.CommandAction(dir)
        r = act([], [], env.Clone(out=outfile))
        assert r.status == expect_nonexecutable_file, r.status

        # Test that trying to execute a non-executable file returns 126
        act = SCons.Action.CommandAction(outfile)
        r = act([], [], env.Clone(out=outfile))
        assert r.status == expect_nonexecutable_dir, r.status

        act = SCons.Action.CommandAction('%s %s 1' % (_python_, exit_py))
        r = act([], [], env)
        assert r.status == 1, r.status

        act = SCons.Action.CommandAction('@%s %s 1' % (_python_, exit_py))
        r = act([], [], env)
        assert r.status == 1, r.status

        act = SCons.Action.CommandAction('@-%s %s 1' % (_python_, exit_py))
        r = act([], [], env)
        assert r == 0, r

        act = SCons.Action.CommandAction('-%s %s 1' % (_python_, exit_py))
        r = act([], [], env)
        assert r == 0, r

        act = SCons.Action.CommandAction('@ %s %s 1' % (_python_, exit_py))
        r = act([], [], env)
        assert r.status == 1, r.status

        act = SCons.Action.CommandAction('@- %s %s 1' % (_python_, exit_py))
        r = act([], [], env)
        assert r == 0, r

        act = SCons.Action.CommandAction('- %s %s 1' % (_python_, exit_py))
        r = act([], [], env)
        assert r == 0, r

    def test_set_handler(self) -> None:
        """Test setting the command handler..."""

        class Test:
            def __init__(self) -> None:
                self.executed = 0

        t = Test()

        def func(sh, escape, cmd, args, env, test=t) -> int:
            test.executed = args
            test.shell = sh
            return 0

        def escape_func(cmd):
            return '**' + cmd + '**'

        class LiteralStr:
            def __init__(self, x) -> None:
                self.data = x

            def __str__(self) -> str:
                return self.data

            def escape(self, escape_func):
                return escape_func(self.data)

            def is_literal(self) -> bool:
                return True

        a = SCons.Action.CommandAction(["xyzzy"])
        e = Environment(SPAWN=func)
        a([], [], e)
        assert t.executed == ['xyzzy'], t.executed

        a = SCons.Action.CommandAction(["xyzzy"])
        e = Environment(SPAWN='$FUNC', FUNC=func)
        a([], [], e)
        assert t.executed == ['xyzzy'], t.executed

        a = SCons.Action.CommandAction(["xyzzy"])
        e = Environment(SPAWN=func, SHELL='fake shell')
        a([], [], e)
        assert t.executed == ['xyzzy'], t.executed
        assert t.shell == 'fake shell', t.shell

        a = SCons.Action.CommandAction([LiteralStr("xyzzy")])
        e = Environment(SPAWN=func, ESCAPE=escape_func)
        a([], [], e)
        assert t.executed == ['**xyzzy**'], t.executed

    def test_get_contents(self) -> None:
        """Test fetching the contents of a command Action."""

        def CmdGen(target, source, env, for_signature) -> str:
            assert for_signature
            return "%s %s" % \
                   (env["foo"], env["bar"])

        # The number 1 is there to make sure all args get converted to strings.
        a = SCons.Action.CommandAction(["|", "$(", "$foo", "|", "$(", "$bar",
                                        "$)", "stuff", "$)", "|", "$baz", 1])
        c = a.get_contents(target=[], source=[],
                           env=Environment(foo='FFF', bar='BBB',
                                           baz=CmdGen))
        assert c == b"| | FFF BBB 1", c

        # Make sure that CommandActions use an Environment's
        # subst_target_source() method for substitution.
        class SpecialEnvironment(Environment):
            def subst_target_source(self, strSubst, raw: int=0, target=[], source=[]):
                return 'subst_target_source: ' + strSubst

        c = a.get_contents(target=DummyNode('ttt'), source=DummyNode('sss'),
                           env=SpecialEnvironment(foo='GGG', bar='CCC',
                                                  baz='ZZZ'))
        assert c == b'subst_target_source: | $( $foo | $( $bar $) stuff $) | $baz 1', c

        # We've discussed using the real target and source names in a
        # CommandAction's signature contents.  This would have have the
        # advantage of recompiling when a file's name changes (keeping
        # debug info current), but it would currently break repository
        # logic that will change the file name based on whether the
        # files come from a repository or locally.  If we ever move to
        # that scheme, then all of the '__t1__' and '__s6__' file names
        # in the asserts below would change to 't1' and 's6' and the
        # like.
        t = list(map(DummyNode, ['t1', 't2', 't3', 't4', 't5', 't6']))
        s = list(map(DummyNode, ['s1', 's2', 's3', 's4', 's5', 's6']))
        env = Environment()

        a = SCons.Action.CommandAction(["$TARGET"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == b"t1", c

        a = SCons.Action.CommandAction(["$TARGETS"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == b"t1 t2 t3 t4 t5 t6", c

        a = SCons.Action.CommandAction(["${TARGETS[2]}"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == b"t3", c

        a = SCons.Action.CommandAction(["${TARGETS[3:5]}"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == b"t4 t5", c

        a = SCons.Action.CommandAction(["$SOURCE"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == b"s1", c

        a = SCons.Action.CommandAction(["$SOURCES"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == b"s1 s2 s3 s4 s5 s6", c

        a = SCons.Action.CommandAction(["${SOURCES[2]}"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == b"s3", c

        a = SCons.Action.CommandAction(["${SOURCES[3:5]}"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == b"s4 s5", c

    def test_get_implicit_deps(self) -> None:
        """Test getting the implicit dependencies of a command Action."""

        class SpecialEnvironment(Environment):
            def WhereIs(self, prog):
                return prog

            class fs:
                def File(name):
                    return name

        env = SpecialEnvironment()
        a = SCons.Action.CommandAction([_python_, exit_py])
        self.assertEqual(a.get_implicit_deps(target=[], source=[], env=env), [_python_])

        for false_like_value in [False, 0, None, "None", "False", "0", "NONE", "FALSE", "off", "OFF", "NO", "no"]:
            env = SpecialEnvironment(IMPLICIT_COMMAND_DEPENDENCIES=false_like_value)
            a = SCons.Action.CommandAction([_python_, exit_py])
            self.assertEqual(a.get_implicit_deps(target=[], source=[], env=env), [])

            env = SpecialEnvironment(IMPLICIT_COMMAND_DEPENDENCIES="$SUBST_VALUE", SUBST_VALUE=false_like_value)
            a = SCons.Action.CommandAction([_python_, exit_py])
            self.assertEqual(a.get_implicit_deps(target=[], source=[], env=env), [])

        for true_like_value in [True, 1, "True", "TRUE", "1"]:
            env = SpecialEnvironment(IMPLICIT_COMMAND_DEPENDENCIES=true_like_value)
            a = SCons.Action.CommandAction([_python_, exit_py])
            self.assertEqual(a.get_implicit_deps(target=[], source=[], env=env), [_python_])

            env = SpecialEnvironment(IMPLICIT_COMMAND_DEPENDENCIES="$SUBST_VALUE", SUBST_VALUE=true_like_value)
            a = SCons.Action.CommandAction([_python_, exit_py])
            self.assertEqual(a.get_implicit_deps(target=[], source=[], env=env), [_python_])

        for all_like_Value in ["all", "ALL", 2, "2"]:
            env = SpecialEnvironment(IMPLICIT_COMMAND_DEPENDENCIES=all_like_Value)
            a = SCons.Action.CommandAction([_python_, exit_py])
            self.assertEqual(a.get_implicit_deps(target=[], source=[], env=env), [_python_, exit_py])


class CommandGeneratorActionTestCase(unittest.TestCase):

    def factory(self, act, **kw):
        """Pass any keywords as a dict"""

        return SCons.Action.CommandGeneratorAction(act, kw)

    def test___init__(self) -> None:
        """Test creation of a command generator Action."""

        def f(target, source, env) -> None:
            pass

        a = self.factory(f)
        assert a.generator == f

    def test___str__(self) -> None:
        """Test the pre-substitution strings for command generator Actions."""

        def f(target, source, env, for_signature, self=self) -> str:
            # See if "env" is really a construction environment (or
            # looks like one) by accessing the FindIxes attribute.
            # (The Tool/mingw.py module has a generator that uses this,
            # and the __str__() method used to cause problems by passing
            # us a regular dictionary as a fallback.)

            env.FindIxes
            return "FOO"

        a = self.factory(f)
        s = str(a)
        assert s == 'FOO', s

    def test_genstring(self) -> None:
        """Test the command generator Action genstring() method."""

        def f(target, source, env, for_signature, self=self) -> str:
            dummy = env['dummy']
            self.dummy = dummy
            return "$FOO $TARGET $SOURCE $TARGETS $SOURCES"

        a = self.factory(f)
        self.dummy = 0
        s = a.genstring([], [], env=Environment(FOO='xyzzy', dummy=1))
        assert self.dummy == 1, self.dummy
        assert s == "$FOO $TARGET $SOURCE $TARGETS $SOURCES", s

    def test_execute(self) -> None:
        """Test executing a command generator Action."""

        def f(target, source, env, for_signature, self=self) -> str:
            dummy = env['dummy']
            self.dummy = dummy
            s = env.subst("$FOO")
            assert s == 'foo baz\nbar ack', s
            return "$FOO"

        def func_action(target, source, env, self=self) -> None:
            dummy = env['dummy']
            s = env.subst('$foo')
            assert s == 'bar', s
            self.dummy = dummy

        def f2(target, source, env, for_signature, f=func_action):
            return f

        def ch(sh, escape, cmd, args, env, self=self) -> None:
            self.cmd.append(cmd)
            self.args.append(args)

        a = self.factory(f)
        self.dummy = 0
        self.cmd = []
        self.args = []
        a([], [], env=Environment(FOO='foo baz\nbar ack',
                                  dummy=1,
                                  SPAWN=ch))
        assert self.dummy == 1, self.dummy
        assert self.cmd == ['foo', 'bar'], self.cmd
        assert self.args == [['foo', 'baz'], ['bar', 'ack']], self.args

        b = self.factory(f2)
        self.dummy = 0
        b(target=[], source=[], env=Environment(foo='bar',
                                                dummy=2))
        assert self.dummy == 2, self.dummy
        del self.dummy

        class DummyFile:
            def __init__(self, t) -> None:
                self.t = t

            def rfile(self):
                self.t.rfile_called = 1
                return self

            def get_subst_proxy(self):
                return self

        def f3(target, source, env, for_signature) -> str:
            return ''

        c = self.factory(f3)
        c(target=[], source=DummyFile(self), env=Environment())
        assert self.rfile_called

    def test_get_contents(self) -> None:
        """Test fetching the contents of a command generator Action."""

        def f(target, source, env, for_signature):
            foo = env['foo']
            bar = env['bar']
            assert for_signature, for_signature
            return [["guux", foo, "$(", "$ignore", "$)", bar,
                     '${test("$( foo $bar $)")}']]

        def test(mystr) -> str:
            assert mystr == "$( foo $bar $)", mystr
            return "test"

        env = Environment(foo='FFF', bar='BBB',
                          ignore='foo', test=test)
        a = self.factory(f)
        c = a.get_contents(target=[], source=[], env=env)
        assert c == b"guux FFF BBB test", c

    def test_get_contents_of_function_action(self) -> None:
        """Test contents of a CommandGeneratorAction-generated FunctionAction."""

        def LocalFunc() -> None:
            pass

        # Since the python bytecode has per version differences, we need different expected results per version
        func_matches = {
            (3, 7): bytearray(b'0, 0, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 8): bytearray(b'0, 0, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 9): bytearray(b'0, 0, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 10): bytearray(b'0, 0, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 11): bytearray(b'0, 0, 0, 0,(),(),(\x97\x00d\x00S\x00),(),()'),
            (3, 12): bytearray(b'0, 0, 0, 0,(),(),(\x97\x00y\x00),(),()'),
            (3, 13): bytearray(b'0, 0, 0, 0,(),(),(\x95\x00g\x00),(),()'),
            (3, 14): bytearray(b'0, 0, 0, 0,(),(),(\x80\x00R\x00#\x00),(),()'),
        }

        meth_matches = [
            b"1, 1, 0, 0,(),(),(d\000\000S),(),()",
            b"1, 1, 0, 0,(),(),(d\x00\x00S),(),()",
        ]

        def f_global(target, source, env, for_signature):
            return SCons.Action.Action(GlobalFunc)

        def f_local(target, source, env, for_signature):
            return SCons.Action.Action(LocalFunc)

        env = Environment(XYZ='foo')

        with self.subTest():
            a = self.factory(f_global)
            c = a.get_contents(target=[], source=[], env=env)
            self.assertEqual(c, func_matches[sys.version_info[:2]])

        with self.subTest():
            a = self.factory(f_local)
            c = a.get_contents(target=[], source=[], env=env)
            self.assertEqual(c, func_matches[sys.version_info[:2]])

        def f_global2(target, source, env, for_signature):
            return SCons.Action.Action(GlobalFunc, varlist=['XYZ'])

        def f_local2(target, source, env, for_signature):
            return SCons.Action.Action(LocalFunc, varlist=['XYZ'])

        matches_foo = func_matches[sys.version_info[:2]] + b'foo'

        with self.subTest():
            a = self.factory(f_global2)
            c = a.get_contents(target=[], source=[], env=env)
            self.assertIn(c, matches_foo)

        with self.subTest():
            a = self.factory(f_local2)
            c = a.get_contents(target=[], source=[], env=env)
            self.assertIn(c, matches_foo)


class FunctionActionTestCase(unittest.TestCase):

    def test___init__(self) -> None:
        """Test creation of a function Action."""

        def func1() -> None:
            pass

        def func2() -> None:
            pass

        def func3() -> None:
            pass

        def func4() -> None:
            pass

        a = SCons.Action.FunctionAction(func1, {})
        assert a.execfunction == func1, a.execfunction
        assert isinstance(a.strfunction, types.MethodType), type(a.strfunction)

        a = SCons.Action.FunctionAction(func2, {'strfunction': func3})
        assert a.execfunction == func2, a.execfunction
        assert a.strfunction == func3, a.strfunction

    def test___str__(self) -> None:
        """Test the __str__() method for function Actions."""

        def func1() -> None:
            pass

        a = SCons.Action.FunctionAction(func1, {})
        s = str(a)
        assert s == "func1(target, source, env)", s

        class class1:
            def __call__(self) -> None:
                pass

        a = SCons.Action.FunctionAction(class1(), {})
        s = str(a)
        assert s == "class1(target, source, env)", s

    def test_execute(self) -> None:
        """Test executing a function Action."""

        self.inc = 0

        def f(target, source, env) -> int:
            s = env['s']
            s.inc = s.inc + 1
            s.target = target
            s.source = source
            assert env.subst("$BAR") == 'foo bar', env.subst("$BAR")
            return 0

        a = SCons.Action.FunctionAction(f, {})
        a(target=1, source=2, env=Environment(BAR='foo bar',
                                              s=self))
        assert self.inc == 1, self.inc
        assert self.source == [2], self.source
        assert self.target == [1], self.target

        global count
        count = 0

        def function1(target, source, env) -> int:
            global count
            count = count + 1
            for t in target:
                with open(t, 'w') as f:
                    f.write("function1\n")
            return 1

        act = SCons.Action.FunctionAction(function1, {})
        r = act(target=[outfile, outfile2], source=[], env=Environment())
        assert r.status == 1, r.status

        assert count == 1, count
        c = test.read(outfile, 'r')
        assert c == "function1\n", c
        c = test.read(outfile2, 'r')
        assert c == "function1\n", c

        class class1a:
            def __init__(self, target, source, env) -> None:
                with open(env['out'], 'w') as f:
                    f.write("class1a\n")

        act = SCons.Action.FunctionAction(class1a, {})
        r = act([], [], Environment(out=outfile))
        assert isinstance(r.status, class1a), r.status
        c = test.read(outfile, 'r')
        assert c == "class1a\n", c

        class class1b:
            def __call__(self, target, source, env) -> int:
                with open(env['out'], 'w') as f:
                    f.write("class1b\n")
                return 2

        act = SCons.Action.FunctionAction(class1b(), {})
        r = act([], [], Environment(out=outfile))
        assert r.status == 2, r.status
        c = test.read(outfile, 'r')
        assert c == "class1b\n", c

        def build_it(target, source, env, executor: Executor | None = None, self=self) -> int:
            self.build_it = 1
            return 0

        def string_it(target, source, env, executor: Executor | None = None, self=self):
            self.string_it = 1
            return None

        act = SCons.Action.FunctionAction(build_it,
                                          {'strfunction': string_it})
        r = act([], [], Environment())
        assert r == 0, r
        assert self.build_it
        assert self.string_it

    def test_get_contents(self) -> None:
        """Test fetching the contents of a function Action."""

        def LocalFunc() -> None:
            pass

        func_matches = {
            (3, 7): bytearray(b'0, 0, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 8): bytearray(b'0, 0, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 9): bytearray(b'0, 0, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 10): bytearray(b'0, 0, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 11): bytearray(b'0, 0, 0, 0,(),(),(\x97\x00d\x00S\x00),(),()'),
            (3, 12): bytearray(b'0, 0, 0, 0,(),(),(\x97\x00y\x00),(),()'),
            (3, 13): bytearray(b'0, 0, 0, 0,(),(),(\x95\x00g\x00),(),()'),
            (3, 14): bytearray(b'0, 0, 0, 0,(),(),(\x80\x00R\x00#\x00),(),()'),

        }

        meth_matches = {
            (3, 7): bytearray(b'1, 1, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 8): bytearray(b'1, 1, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 9): bytearray(b'1, 1, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 10): bytearray(b'1, 1, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 11): bytearray(b'1, 1, 0, 0,(),(),(\x97\x00d\x00S\x00),(),()'),
            (3, 12): bytearray(b'1, 1, 0, 0,(),(),(\x97\x00y\x00),(),()'),
            (3, 13): bytearray(b'1, 1, 0, 0,(),(),(\x95\x00g\x00),(),()'),
            (3, 14): bytearray(b'1, 1, 0, 0,(),(),(\x80\x00R\x00#\x00),(),()'),
        }

        def factory(act, **kw):
            return SCons.Action.FunctionAction(act, kw)

        with self.subTest():
            a = factory(GlobalFunc)
            c = a.get_contents(target=[], source=[], env=Environment())
            self.assertEqual(c, func_matches[sys.version_info[:2]])

        with self.subTest():
            a = factory(LocalFunc)
            c = a.get_contents(target=[], source=[], env=Environment())
            self.assertEqual(c, func_matches[sys.version_info[:2]])

        matches_foo = func_matches[sys.version_info[:2]] + b'foo'

        with self.subTest():
            a = factory(GlobalFunc, varlist=['XYZ'])
            c = a.get_contents(target=[], source=[], env=Environment())
            self.assertEqual(c, func_matches[sys.version_info[:2]])

        with self.subTest():
            c = a.get_contents(target=[], source=[], env=Environment(XYZ='foo'))
            self.assertEqual(c, matches_foo)

        ##TODO: is this set of tests still needed?
        # Make sure a bare string varlist works
        with self.subTest():
            a = factory(GlobalFunc, varlist='XYZ')
            c = a.get_contents(target=[], source=[], env=Environment())
            self.assertEqual(c, func_matches[sys.version_info[:2]])

        with self.subTest():
            c = a.get_contents(target=[], source=[], env=Environment(XYZ='foo'))
            self.assertIn(c, matches_foo)

        class Foo:
            def get_contents(self, target, source, env) -> bytes:
                return b'xyzzy'

        with self.subTest():
            a = factory(Foo())
            c = a.get_contents(target=[], source=[], env=Environment())
            self.assertEqual(c, b'xyzzy')

        class LocalClass:
            def LocalMethod(self) -> None:
                pass

        with self.subTest():
            lc = LocalClass()
            a = factory(lc.LocalMethod)
            c = a.get_contents(target=[], source=[], env=Environment())
            self.assertEqual(c, meth_matches[sys.version_info[:2]])

    def test_strfunction(self) -> None:
        """Test the FunctionAction.strfunction() method."""

        def func() -> None:
            pass

        def factory(act, **kw):
            return SCons.Action.FunctionAction(act, kw)

        a = factory(func)
        s = a.strfunction(target=[], source=[], env=Environment())
        assert s == 'func([], [])', s

        a = factory(func, strfunction=None)
        s = a.strfunction(target=[], source=[], env=Environment())
        assert s is None, s

        a = factory(func, cmdstr='function')
        s = a.strfunction(target=[], source=[], env=Environment())
        assert s == 'function', s


class ListActionTestCase(unittest.TestCase):

    def test___init__(self) -> None:
        """Test creation of a list of subsidiary Actions."""

        def func() -> None:
            pass

        a = SCons.Action.ListAction(["x", func, ["y", "z"]])
        assert isinstance(a.list[0], SCons.Action.CommandAction)
        assert isinstance(a.list[1], SCons.Action.FunctionAction)
        assert isinstance(a.list[2], SCons.Action.ListAction)
        assert a.list[2].list[0].cmd_list == 'y'

    def test___str__(self) -> None:
        """Test the __str__() method for a list of subsidiary Actions."""

        def f(target, source, env) -> None:
            pass

        def g(target, source, env) -> None:
            pass

        a = SCons.Action.ListAction([f, g, "XXX", f])
        s = str(a)
        assert s == "f(target, source, env)\ng(target, source, env)\nXXX\nf(target, source, env)", s

    def test_genstring(self) -> None:
        """Test the genstring() method for a list of subsidiary Actions."""

        def f(target, source, env) -> None:
            pass

        def g(target, source, env, for_signature) -> str:
            return 'generated %s %s' % (target[0], source[0])

        g = SCons.Action.Action(g, generator=1)
        a = SCons.Action.ListAction([f, g, "XXX", f])
        s = a.genstring(['foo.x'], ['bar.y'], Environment())
        assert s == "f(target, source, env)\ngenerated foo.x bar.y\nXXX\nf(target, source, env)", s

    def test_execute(self) -> None:
        """Test executing a list of subsidiary Actions."""
        self.inc = 0

        def f(target, source, env) -> None:
            s = env['s']
            s.inc = s.inc + 1

        a = SCons.Action.ListAction([f, f, f])
        a([], [], Environment(s=self))
        assert self.inc == 3, self.inc

        cmd2 = r'%s %s %s syzygy' % (_python_, act_py, outfile)

        def function2(target, source, env) -> int:
            with open(env['out'], 'a') as f:
                f.write("function2\n")
            return 0

        class class2a:
            def __call__(self, target, source, env) -> int:
                with open(env['out'], 'a') as f:
                    f.write("class2a\n")
                return 0

        class class2b:
            def __init__(self, target, source, env) -> None:
                with open(env['out'], 'a') as f:
                    f.write("class2b\n")

        act = SCons.Action.ListAction([cmd2, function2, class2a(), class2b])
        r = act([], [], Environment(out=outfile))
        assert isinstance(r.status, class2b), r.status
        c = test.read(outfile, 'r')
        assert c == "act.py: 'syzygy'\nfunction2\nclass2a\nclass2b\n", c

    def test_get_contents(self) -> None:
        """Test fetching the contents of a list of subsidiary Actions."""

        self.foo = 0

        def gen(target, source, env, for_signature) -> str:
            s = env['s']
            s.foo = 1
            return "y"

        a = SCons.Action.ListAction(["x",
                                     SCons.Action.Action(gen, generator=1),
                                     "z"])
        c = a.get_contents(target=[], source=[], env=Environment(s=self))
        assert self.foo == 1, self.foo
        assert c == b"xyz", c


class LazyActionTestCase(unittest.TestCase):
    def test___init__(self) -> None:
        """Test creation of a lazy-evaluation Action."""

        # Environment variable references should create a special type
        # of LazyAction that lazily evaluates the variable for whether
        # it's a string or something else before doing anything.
        a9 = SCons.Action.Action('$FOO')
        assert isinstance(a9, SCons.Action.LazyAction), a9
        assert a9.var == 'FOO', a9.var

        a10 = SCons.Action.Action('${FOO}')
        assert isinstance(a10, SCons.Action.LazyAction), a10
        assert a10.var == 'FOO', a10.var

    def test_genstring(self) -> None:
        """Test the lazy-evaluation Action genstring() method."""

        def f(target, source, env) -> None:
            pass

        a = SCons.Action.Action('$BAR')
        env1 = Environment(BAR=f, s=self)
        env2 = Environment(BAR='xxx', s=self)
        s = a.genstring([], [], env=env1)
        assert s == "f(target, source, env)", s
        s = a.genstring([], [], env=env2)
        assert s == 'xxx', s

    def test_execute(self) -> None:
        """Test executing a lazy-evaluation Action."""

        def f(target, source, env) -> int:
            s = env['s']
            s.test = 1
            return 0

        a = SCons.Action.Action('$BAR')
        a([], [], env=Environment(BAR=f, s=self))
        assert self.test == 1, self.test
        cmd = r'%s %s %s lazy' % (_python_, act_py, outfile)
        a([], [], env=Environment(BAR=cmd, s=self))
        c = test.read(outfile, 'r')
        assert c == "act.py: 'lazy'\n", c

    def test_get_contents(self) -> None:
        """Test fetching the contents of a lazy-evaluation Action."""

        a = SCons.Action.Action("${FOO}")
        env = Environment(FOO=[["This", "is", "a", "test"]])
        c = a.get_contents(target=[], source=[], env=env)
        assert c == b"This is a test", c

    def test_get_contents_of_function_action(self) -> None:
        """Test fetching the contents of a lazy-evaluation FunctionAction."""

        def LocalFunc() -> None:
            pass

        func_matches = {
            (3, 7): bytearray(b'0, 0, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 8): bytearray(b'0, 0, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 9): bytearray(b'0, 0, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 10): bytearray(b'0, 0, 0, 0,(),(),(d\x00S\x00),(),()'),
            (3, 11): bytearray(b'0, 0, 0, 0,(),(),(\x97\x00d\x00S\x00),(),()'),
            (3, 12): bytearray(b'0, 0, 0, 0,(),(),(\x97\x00y\x00),(),()'),
            (3, 13): bytearray(b'0, 0, 0, 0,(),(),(\x95\x00g\x00),(),()'),
            (3, 14): bytearray(b'0, 0, 0, 0,(),(),(\x80\x00R\x00#\x00),(),()'),
        }

        meth_matches = [
            b"1, 1, 0, 0,(),(),(d\000\000S),(),()",
            b"1, 1, 0, 0,(),(),(d\x00\x00S),(),()",
        ]

        def factory(act, **kw):
            return SCons.Action.FunctionAction(act, kw)

        a = SCons.Action.Action("${FOO}")

        with self.subTest():
            env = Environment(FOO=factory(GlobalFunc))
            c = a.get_contents(target=[], source=[], env=env)
            self.assertEqual(c, func_matches[sys.version_info[:2]])

        with self.subTest():
            env = Environment(FOO=factory(LocalFunc))
            c = a.get_contents(target=[], source=[], env=env)
            self.assertEqual(c, func_matches[sys.version_info[:2]])

        # matches_foo = [x + b"foo" for x in func_matches]
        matches_foo = func_matches[sys.version_info[:2]] + b'foo'

        with self.subTest():
            env = Environment(FOO=factory(GlobalFunc, varlist=['XYZ']))
            c = a.get_contents(target=[], source=[], env=env)
            self.assertEqual(c, func_matches[sys.version_info[:2]])

        with self.subTest():
            env['XYZ'] = 'foo'
            c = a.get_contents(target=[], source=[], env=env)
            self.assertIn(c, matches_foo)


class ActionCallerTestCase(unittest.TestCase):
    def test___init__(self) -> None:
        """Test creation of an ActionCaller"""

        ac = SCons.Action.ActionCaller(1, [2, 3], {'FOO': 4, 'BAR': 5})
        assert ac.parent == 1, ac.parent
        assert ac.args == [2, 3], ac.args
        assert ac.kw == {'FOO': 4, 'BAR': 5}, ac.kw

    def test_get_contents(self) -> None:
        """Test fetching the contents of an ActionCaller"""

        def strfunc() -> None:
            pass

        def LocalFunc() -> None:
            pass

        matches = {
            (3, 7): b'd\x00S\x00',
            (3, 8): b'd\x00S\x00',
            (3, 9): b'd\x00S\x00',
            (3, 10): b'd\x00S\x00',
            (3, 11): b'\x97\x00d\x00S\x00',
            (3, 12): b'\x97\x00y\x00',
            (3, 13): b'\x95\x00g\x00',
            (3, 14): b'\x80\x00R\x00#\x00',
        }

        with self.subTest():
            af = SCons.Action.ActionFactory(GlobalFunc, strfunc)
            ac = SCons.Action.ActionCaller(af, [], {})
            c = ac.get_contents([], [], Environment())
            self.assertEqual(c, matches[sys.version_info[:2]])

        with self.subTest():
            af = SCons.Action.ActionFactory(LocalFunc, strfunc)
            ac = SCons.Action.ActionCaller(af, [], {})
            c = ac.get_contents([], [], Environment())
            self.assertEqual(c, matches[sys.version_info[:2]])

        class LocalActFunc:
            def __call__(self) -> None:
                pass

        with self.subTest():
            af = SCons.Action.ActionFactory(GlobalActFunc(), strfunc)
            ac = SCons.Action.ActionCaller(af, [], {})
            c = ac.get_contents([], [], Environment())
            self.assertEqual(c, matches[sys.version_info[:2]])

        with self.subTest():
            af = SCons.Action.ActionFactory(LocalActFunc(), strfunc)
            ac = SCons.Action.ActionCaller(af, [], {})
            c = ac.get_contents([], [], Environment())
            self.assertEqual(c, matches[sys.version_info[:2]])

        matches = [
            b"<built-in function str>",
            b"<type 'str'>",
        ]

        with self.subTest():
            af = SCons.Action.ActionFactory(str, strfunc)
            ac = SCons.Action.ActionCaller(af, [], {})
            c = ac.get_contents([], [], Environment())
            self.assertIn(c, ("<built-in function str>", "<type 'str'>", "<class 'str'>"))
            # ^^ class str for python3

    def test___call__(self) -> None:
        """Test calling an ActionCaller"""

        actfunc_args = []

        def actfunc(a1, a2, a3, args=actfunc_args) -> None:
            args.extend([a1, a2, a3])

        def strfunc(a1, a2, a3) -> None:
            pass

        e = Environment(FOO=2, BAR=5)

        af = SCons.Action.ActionFactory(actfunc, strfunc)
        ac = SCons.Action.ActionCaller(af, ['$__env__', '$FOO', 3], {})
        ac([], [], e)
        assert actfunc_args[0] is e, actfunc_args
        assert actfunc_args[1] == '2', actfunc_args
        assert actfunc_args[2] == 3, actfunc_args
        del actfunc_args[:]

        ac = SCons.Action.ActionCaller(af, [], {'a3': '$__env__', 'a2': '$BAR', 'a1': 4})
        ac([], [], e)
        assert actfunc_args[0] == 4, actfunc_args
        assert actfunc_args[1] == '5', actfunc_args
        assert actfunc_args[2] is e, actfunc_args
        del actfunc_args[:]

    def test_strfunction(self) -> None:
        """Test calling the ActionCaller strfunction() method"""

        strfunc_args = []

        def actfunc(a1, a2, a3, a4) -> None:
            pass

        def strfunc(a1, a2, a3, a4, args=strfunc_args) -> None:
            args.extend([a1, a2, a3, a4])

        af = SCons.Action.ActionFactory(actfunc, strfunc)
        ac = SCons.Action.ActionCaller(af, [1, '$FOO', 3, '$WS'], {})
        ac.strfunction([], [], Environment(FOO=2, WS='white   space'))
        assert strfunc_args == [1, '2', 3, 'white   space'], strfunc_args

        del strfunc_args[:]
        d = {'a3': 6, 'a2': '$BAR', 'a1': 4, 'a4': '$WS'}
        ac = SCons.Action.ActionCaller(af, [], d)
        ac.strfunction([], [], Environment(BAR=5, WS='w   s'))
        assert strfunc_args == [4, '5', 6, 'w   s'], strfunc_args


class ActionFactoryTestCase(unittest.TestCase):
    def test___init__(self) -> None:
        """Test creation of an ActionFactory"""

        def actfunc() -> None:
            pass

        def strfunc() -> None:
            pass

        ac = SCons.Action.ActionFactory(actfunc, strfunc)
        assert ac.actfunc is actfunc, ac.actfunc
        assert ac.strfunc is strfunc, ac.strfunc

    def test___call__(self) -> None:
        """Test calling whatever's returned from an ActionFactory"""

        actfunc_args = []
        strfunc_args = []

        def actfunc(a1, a2, a3, args=actfunc_args) -> None:
            args.extend([a1, a2, a3])

        def strfunc(a1, a2, a3, args=strfunc_args) -> None:
            args.extend([a1, a2, a3])

        af = SCons.Action.ActionFactory(actfunc, strfunc)
        af(3, 6, 9)([], [], Environment())
        assert actfunc_args == [3, 6, 9], actfunc_args
        assert strfunc_args == [3, 6, 9], strfunc_args


class ActionCompareTestCase(unittest.TestCase):
    def test_1_solo_name(self) -> None:
        """Test Lazy Cmd Generator Action get_name alone.

        Basically ensures we can locate the builder, comparing it to
        itself along the way."""

        bar = SCons.Builder.Builder(action={})
        env = Environment(BUILDERS={'BAR': bar})
        name = bar.get_name(env)
        assert name == 'BAR', name

    def test_2_multi_name(self) -> None:
        """Test LazyCmdGenerator Action get_name multi builders.

        Ensure that we can compare builders (and thereby actions) to
        each other safely."""

        foo = SCons.Builder.Builder(action='$FOO', suffix='.foo')
        bar = SCons.Builder.Builder(action={})
        assert foo != bar
        assert foo.action != bar.action
        env = Environment(BUILDERS={'FOO': foo, 'BAR': bar})
        name = foo.get_name(env)
        assert name == 'FOO', name
        name = bar.get_name(env)
        assert name == 'BAR', name

    def test_3_dict_names(self) -> None:
        """Test Action/Suffix dicts with get_name.

        Verifies that Action/Suffix dictionaries work correctly,
        especially two builders that can generate the same suffix,
        where one of the builders has a suffix dictionary with a None
        key."""

        foo = SCons.Builder.Builder(action='$FOO', suffix='.foo')
        bar = SCons.Builder.Builder(action={}, suffix={None: '.bar'})
        bar.add_action('.cow', "$MOO")
        dog = SCons.Builder.Builder(suffix='.bar')
        env = Environment(BUILDERS={'FOO': foo, 'BAR': bar, 'DOG': dog})

        assert foo.get_name(env) == 'FOO', foo.get_name(env)
        assert bar.get_name(env) == 'BAR', bar.get_name(env)
        assert dog.get_name(env) == 'DOG', dog.get_name(env)


class TestClass:
    """A test class used by ObjectContentsTestCase.test_object_contents"""

    def __init__(self) -> None:
        self.a = "a"
        self.b = "b"

    def method(self, arg) -> None:
        pass


class ObjectContentsTestCase(unittest.TestCase):
    def test_function_contents(self) -> None:
        """Test that Action._function_contents works"""

        def func1(a, b, c):
            """A test function"""
            return a

        # Since the python bytecode has per version differences,
        # we need different expected results per version
        # Note unlike the others, this result is a tuple, use assertIn
        expected = {
            (3, 7): (bytearray(b"3, 3, 0, 0,(),(),(|\x00S\x00),(),()"),),
            (3, 8): (bytearray(b"3, 3, 0, 0,(),(),(|\x00S\x00),(),()"),),
            (3, 9): (bytearray(b"3, 3, 0, 0,(),(),(|\x00S\x00),(),()"),),
            (3, 10): (  # 3.10.1, 3.10.2
                bytearray(b"3, 3, 0, 0,(N.),(),(|\x00S\x00),(),()"),
                bytearray(b"3, 3, 0, 0,(),(),(|\x00S\x00),(),()"),
            ),
            (3, 11): (bytearray(b"3, 3, 0, 0,(),(),(\x97\x00|\x00S\x00),(),()"),),
            (3, 12): (bytearray(b"3, 3, 0, 0,(),(),(\x97\x00|\x00S\x00),(),()"),),
            (3, 13): (bytearray(b"3, 3, 0, 0,(),(),(\x95\x00U\x00$\x00),(),()"),),
            (3, 14): (bytearray(b"3, 3, 0, 0,(),(),(\x80\x00V\x00#\x00),(),()"),),
        }

        c = SCons.Action._function_contents(func1)
        self.assertIn(c, expected[sys.version_info[:2]])

    def test_object_contents(self) -> None:
        """Test that Action._object_contents works"""

        # See definition above
        o = TestClass()
        c = SCons.Action._object_contents(o)

        # c = SCons.Action._object_instance_content(o)

        # Since the python bytecode has per version differences,
        # we need different expected results per version
        expected = {
            (3, 7): bytearray(
                b"{TestClass:__main__}[[[(<class 'object'>, ()), [(<class '__main__.TestClass'>, (<class 'object'>,))]]]]{{1, 1, 0, 0,(a,b),(a,b),(d\x01|\x00_\x00d\x02|\x00_\x01d\x00S\x00),(),(),2, 2, 0, 0,(),(),(d\x00S\x00),(),()}}{{{a=a,b=b}}}"
            ),
            (3, 8): bytearray(
                b"{TestClass:__main__}[[[(<class 'object'>, ()), [(<class '__main__.TestClass'>, (<class 'object'>,))]]]]{{1, 1, 0, 0,(a,b),(a,b),(d\x01|\x00_\x00d\x02|\x00_\x01d\x00S\x00),(),(),2, 2, 0, 0,(),(),(d\x00S\x00),(),()}}{{{a=a,b=b}}}"
            ),
            (3, 9): bytearray(
                b"{TestClass:__main__}[[[(<class 'object'>, ()), [(<class '__main__.TestClass'>, (<class 'object'>,))]]]]{{1, 1, 0, 0,(a,b),(a,b),(d\x01|\x00_\x00d\x02|\x00_\x01d\x00S\x00),(),(),2, 2, 0, 0,(),(),(d\x00S\x00),(),()}}{{{a=a,b=b}}}"
            ),
            (3, 10): bytearray(
                b"{TestClass:__main__}[[[(<class 'object'>, ()), [(<class '__main__.TestClass'>, (<class 'object'>,))]]]]{{1, 1, 0, 0,(a,b),(a,b),(d\x01|\x00_\x00d\x02|\x00_\x01d\x00S\x00),(),(),2, 2, 0, 0,(),(),(d\x00S\x00),(),()}}{{{a=a,b=b}}}"
            ),
            (3, 11): bytearray(
                b"{TestClass:__main__}[[[(<class 'object'>, ()), [(<class '__main__.TestClass'>, (<class 'object'>,))]]]]{{1, 1, 0, 0,(a,b),(a,b),(\x97\x00d\x01|\x00_\x00\x00\x00\x00\x00\x00\x00\x00\x00d\x02|\x00_\x01\x00\x00\x00\x00\x00\x00\x00\x00d\x00S\x00),(),(),2, 2, 0, 0,(),(),(\x97\x00d\x00S\x00),(),()}}{{{a=a,b=b}}}"
            ),
            (3, 12): bytearray(
                b"{TestClass:__main__}[[[(<class 'object'>, ()), [(<class '__main__.TestClass'>, (<class 'object'>,))]]]]{{1, 1, 0, 0,(a,b),(a,b),(\x97\x00d\x01|\x00_\x00\x00\x00\x00\x00\x00\x00\x00\x00d\x02|\x00_\x01\x00\x00\x00\x00\x00\x00\x00\x00y\x00),(),(),2, 2, 0, 0,(),(),(\x97\x00y\x00),(),()}}{{{a=a,b=b}}}"
            ),
            (3, 13): bytearray(
                b"{TestClass:__main__}[[[(<class 'object'>, ()), [(<class '__main__.TestClass'>, (<class 'object'>,))]]]]{{1, 1, 0, 0,(a,b),(a,b),(\x95\x00S\x01U\x00l\x00\x00\x00\x00\x00\x00\x00\x00\x00S\x02U\x00l\x01\x00\x00\x00\x00\x00\x00\x00\x00g\x00),(),(),2, 2, 0, 0,(),(),(\x95\x00g\x00),(),()}}{{{a=a,b=b}}}"
            ),
            (3, 14): bytearray(
                b"{TestClass:__main__}[[[(<class 'object'>, ()), [(<class '__main__.TestClass'>, (<class 'object'>,))]]]]{{1, 1, 0, 0,(a,b),(a,b),(\x80\x00R\x00V\x00n\x00\x00\x00\x00\x00\x00\x00\x00\x00R\x01V\x00n\x01\x00\x00\x00\x00\x00\x00\x00\x00R\x02#\x00),(),(),2, 2, 0, 0,(),(),(\x80\x00R\x00#\x00),(),()}}{{{a=a,b=b}}}"
            ),
        }
        self.assertEqual(c, expected[sys.version_info[:2]])

    def test_code_contents(self) -> None:
        """Test that Action._code_contents works"""

        code = compile("print('Hello, World!')", '<string>', 'exec')
        c = SCons.Action._code_contents(code)

        # Since the python bytecode has per version differences, we need different expected results per version
        expected = {
            (3, 7): bytearray(
                b"0, 0, 0, 0,(Hello, World!),(print),(e\x00d\x00\x83\x01\x01\x00d\x01S\x00)"
            ),
            (3, 8): bytearray(
                b"0, 0, 0, 0,(Hello, World!),(print),(e\x00d\x00\x83\x01\x01\x00d\x01S\x00)"
            ),
            (3, 9): bytearray(
                b"0, 0, 0, 0,(Hello, World!),(print),(e\x00d\x00\x83\x01\x01\x00d\x01S\x00)"
            ),
            (3, 10): bytearray(
                b"0, 0, 0, 0,(Hello, World!),(print),(e\x00d\x00\x83\x01\x01\x00d\x01S\x00)"
            ),
            (3, 11): bytearray(
                b"0, 0, 0, 0,(Hello, World!),(print),(\x97\x00\x02\x00e\x00d\x00\xa6\x01\x00\x00\xab\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00d\x01S\x00)"
            ),
            (3, 12): bytearray(
                b"0, 0, 0, 0,(Hello, World!),(print),(\x97\x00\x02\x00e\x00d\x00\xab\x01\x00\x00\x00\x00\x00\x00\x01\x00y\x01)"
            ),
            (3, 13): bytearray(
                b'0, 0, 0, 0,(Hello, World!),(print),(\x95\x00\\\x00"\x00S\x005\x01\x00\x00\x00\x00\x00\x00 \x00g\x01)'
            ),
            (3, 14): bytearray(
                b"0, 0, 0, 0,(Hello, World!),(print),(\x80\x00]\x00!\x00R\x004\x01\x00\x00\x00\x00\x00\x00\x1f\x00R\x01#\x00)"
            ),
        }

        self.assertEqual(c, expected[sys.version_info[:2]])

    def test_uncaught_exception_bubbles(self):
        """Test that scons_subproc_run bubbles uncaught exceptions"""
        try:
            cp = scons_subproc_run(Environment(), None, stdout=PIPE)
        except EnvironmentError:
            pass
        except Exception:
            # pass the test
            return

        raise Exception("expected a non-EnvironmentError exception")

    def mock_subprocess_run(*args, **kwargs):
        """Replacement subprocess.run: return kwargs for checking."""
        kwargs.pop("env")  # the value of env isn't interesting here
        return kwargs

    @mock.patch("subprocess.run", mock_subprocess_run)
    def test_scons_subproc_run(self):
        """Test the argument remapping options."""
        env = Environment()
        self.assertEqual(scons_subproc_run(env), {"check": False})
        with self.subTest():
            self.assertEqual(
                scons_subproc_run(env, error="raise"),
                {"check": True}
            )
        with self.subTest():
            self.assertEqual(
                scons_subproc_run(env, capture_output=True),
                {"capture_output": True, "check": False},
            )
        with self.subTest():
            self.assertEqual(
                scons_subproc_run(env, text=True),
                {"text": True, "check": False},
            )


if __name__ == "__main__":
    unittest.main()
