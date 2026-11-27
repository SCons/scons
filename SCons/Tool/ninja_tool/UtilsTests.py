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

# Tests for the Ninja tool's Utility functions

from __future__ import annotations

import unittest

import TestCmd

from SCons.Action import CommandAction, ListAction
from SCons.Action import CommandGeneratorAction, FunctionAction, LazyAction
from SCons.Environment import Base as BaseEnvironment
import SCons.Node.FS
import SCons.Tool.ninja_tool
from SCons.Tool.ninja_tool import NINJA_CUSTOM_HANDLERS
from SCons.Tool.ninja_tool.NinjaState import SConsToNinjaTranslator
from SCons.Tool.ninja_tool.Utils import generate_command


class TestGenerateCommand(unittest.TestCase):
    """Test that generate_command returns reasonable results for Actions."""

    def setUp(self):
        self.env = BaseEnvironment()
        self.target = ["target.o"]
        self.source = ["source.c"]

    def test_command_action(self):
        """Test basic CommandAction handling."""
        action = CommandAction("gcc -c -o $TARGET $SOURCE")
        cmd = generate_command(self.env, None, action, self.target, self.source)
        self.assertEqual(cmd, f"gcc -c -o {self.target[0]} {self.source[0]}")

    def test_list_action(self):
        """Test ListAction concatenation."""
        actions = [
            CommandAction("mkdir -p build"),
            CommandAction("gcc -c -o $TARGET $SOURCE"),
        ]
        action = ListAction(actions)
        cmd = generate_command(self.env, None, action, self.target, self.source)
        self.assertEqual(cmd, f"mkdir -p build && gcc -c -o {self.target[0]} {self.source[0]}")

    def test_dollar_escaping(self):
        """Test dollar signs get properly escaped."""
        action = CommandAction("echo $DOLLAR_VAR")
        self.env['DOLLAR_VAR'] = "$5"
        cmd = generate_command(self.env, None, action, self.target, self.source)
        self.assertEqual(cmd, "echo $$5")

    def test_command_generator_action(self):
        """Test CommandGeneratorAction handling."""

        def generator(target, source, env, for_signature):
            return f"gcc -c -o {target[0]} {source[0]}"

        action = CommandGeneratorAction(generator, kw={})
        cmd = generate_command(self.env, None, action, self.target, self.source)
        self.assertEqual(cmd, f"gcc -c -o {self.target[0]} {self.source[0]}")

    def test_function_action_simple(self):
        """Test FunctionAction with a simple function."""

        def build_func(target, source, env):
            return 0

        action = FunctionAction(build_func, kw={})
        cmd = generate_command(self.env, None, action, self.target, self.source)
        # we could be less precise here, really just care it returns *something*
        self.assertEqual(cmd, "build_func(target, source, env)")

    def test_function_action_with_args(self):
        """Test FunctionAction with function taking arguments."""

        def build_func(target, source, env, arg1="default"):
            return 0

        action = FunctionAction(build_func, kw={'vars': ['arg1']})
        cmd = generate_command(self.env, None, action, self.target, self.source)
        self.assertIsNotNone(cmd)

    def test_lazy_action_str(self):
        """Test LazyAction functionality with a string value."""
        self.env['CCCOM'] = 'gcc -c -o $TARGET $SOURCE'
        action = LazyAction("CCCOM", kw={})
        cmd = generate_command(self.env, None, action, self.target, self.source)
        self.assertEqual(cmd, f"gcc -c -o {self.target[0]} {self.source[0]}")

    def test_lazy_action_function(self):
        """Test LazyAction functionality with a function value."""

        def generator(target, source, env, for_signature):
            return f"gcc -c -o {target[0]} {source[0]}"

        self.env['CCCOM'] = generator
        action = LazyAction("CCCOM", kw={})
        cmd = generate_command(self.env, None, action, self.target, self.source)
        self.assertEqual(cmd, f"gcc -c -o {self.target[0]} {self.source[0]}")


class _NinjaStateStub:
    """Stand-in for NINJA_STATE; the translator only reads ninja_file."""

    ninja_file = None


class TestActionToNinjaBuildPrePostActions(unittest.TestCase):
    """Test that AddPreAction/AddPostAction actions are in the ninja build."""

    def setUp(self) -> None:
        # Each test builds 'out.txt' with different actions, so use a fresh
        # default filesystem to avoid the global node cache leaking between tests.
        SCons.Node.FS.default_fs = None
        self.env = BaseEnvironment()
        self.env[NINJA_CUSTOM_HANDLERS] = {}
        self._saved_ninja_state = SCons.Tool.ninja_tool.NINJA_STATE
        SCons.Tool.ninja_tool.NINJA_STATE = _NinjaStateStub()
        self.translator = SConsToNinjaTranslator(self.env)

    def tearDown(self) -> None:
        SCons.Tool.ninja_tool.NINJA_STATE = self._saved_ninja_state
        SCons.Node.FS.default_fs = None

    def _command_node(self, action='cat $SOURCE > $TARGET'):
        return self.env.Command('out.txt', 'in.txt', action)[0]

    def _build(self, node):
        return self.translator.action_to_ninja_build(node)

    def test_no_pre_post_actions(self) -> None:
        """A plain command builder produces only its own command."""
        build = self._build(self._command_node())
        self.assertEqual(build['rule'], 'GENERATED_CMD')
        self.assertEqual(build['variables']['cmd'], 'cat in.txt > out.txt')
        self.assertNotIn('pre', build['variables'])
        self.assertNotIn('post', build['variables'])

    def test_pre_and_post_command_actions(self) -> None:
        """Pre and post commands are joined in order around the command."""
        node = self._command_node()
        self.env.AddPreAction(node, 'echo pre1 > pre.txt')
        self.env.AddPreAction(node, 'echo pre2 >> pre.txt')
        self.env.AddPostAction(node, 'echo post > post.txt')
        build = self._build(node)
        self.assertEqual(build['rule'], 'GENERATED_CMD')
        self.assertEqual(
            build['variables']['cmd'],
            'echo pre1 > pre.txt && echo pre2 >> pre.txt && '
            'cat in.txt > out.txt && echo post > post.txt',
        )

    def test_pre_action_only(self) -> None:
        node = self._command_node()
        self.env.AddPreAction(node, 'echo pre > pre.txt')
        self.assertEqual(
            self._build(node)['variables']['cmd'],
            'echo pre > pre.txt && cat in.txt > out.txt',
        )

    def test_post_action_only(self) -> None:
        node = self._command_node()
        self.env.AddPostAction(node, 'echo post > post.txt')
        self.assertEqual(
            self._build(node)['variables']['cmd'],
            'cat in.txt > out.txt && echo post > post.txt',
        )

    def test_list_action_with_pre_and_post_actions(self) -> None:
        """Pre and post actions wrap a builder whose action is a list."""
        node = self._command_node(['echo a > $TARGET', 'echo b >> $TARGET'])
        self.env.AddPreAction(node, 'echo pre > pre.txt')
        self.env.AddPostAction(node, ['echo post1 >> $TARGET', 'echo post2 >> $TARGET'])
        build = self._build(node)
        self.assertEqual(build['rule'], 'GENERATED_CMD')
        self.assertEqual(
            build['variables']['cmd'],
            'echo pre > pre.txt && echo a > out.txt && echo b >> out.txt && '
            'echo post1 >> out.txt && echo post2 >> out.txt',
        )

    def test_unhandled_function_main_action(self) -> None:
        """An unhandled Python function action becomes a TEMPLATE rule."""
        def main_func(target, source, env) -> int:
            return 0

        self.assertEqual(self._build(self._command_node(main_func))['rule'], 'TEMPLATE')

    def test_unhandled_function_in_list_action(self) -> None:
        """A function mixed into a command list must not be dropped."""
        def mid_func(target, source, env) -> int:
            return 0

        node = self._command_node(['echo a > $TARGET', mid_func])
        self.assertEqual(self._build(node)['rule'], 'TEMPLATE')

    def test_unhandled_function_pre_action(self) -> None:
        """A function pre action must not be dropped."""
        def pre_func(target, source, env) -> int:
            return 0

        node = self._command_node()
        self.env.AddPreAction(node, pre_func)
        self.assertEqual(self._build(node)['rule'], 'TEMPLATE')

    def test_unhandled_function_post_action(self) -> None:
        """A function post action must not be dropped."""
        def post_func(target, source, env) -> int:
            return 0

        node = self._command_node()
        self.env.AddPostAction(node, post_func)
        self.assertEqual(self._build(node)['rule'], 'TEMPLATE')


if __name__ == "__main__":
    unittest.main()
