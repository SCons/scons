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
import SCons.Action
import SCons.Node.FS
import SCons.Tool.ninja_tool
from SCons.Environment import Base as BaseEnvironment
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
    """Minimal stand-in for NINJA_STATE; only ninja_file is consulted by the translator."""
    ninja_file = None


class TestActionToNinjaBuildPrePostActions(unittest.TestCase):
    """Test that AddPreAction/AddPostAction actions are translated into the ninja build."""

    def setUp(self):
        # Each test builds 'out.txt' with different actions, so use a fresh
        # default filesystem to avoid the global node cache leaking between tests.
        SCons.Node.FS.default_fs = None
        self.env = BaseEnvironment()
        self.env[NINJA_CUSTOM_HANDLERS] = {}
        self._saved_ninja_state = SCons.Tool.ninja_tool.NINJA_STATE
        SCons.Tool.ninja_tool.NINJA_STATE = _NinjaStateStub()
        self.translator = SConsToNinjaTranslator(self.env)

    def tearDown(self):
        SCons.Tool.ninja_tool.NINJA_STATE = self._saved_ninja_state
        SCons.Node.FS.default_fs = None

    def _command_node(self):
        return self.env.Command('out.txt', 'in.txt', 'cat $SOURCE > $TARGET')[0]

    def test_no_pre_post_actions(self):
        """A plain command builder still produces only its own command."""
        node = self._command_node()
        build = self.translator.action_to_ninja_build(node)
        self.assertEqual(build['rule'], 'GENERATED_CMD')
        self.assertEqual(build['variables']['cmd'], 'cat in.txt > out.txt')

    def test_pre_and_post_command_actions(self):
        """Pre and post command actions are merged in order with the main command."""
        node = self._command_node()
        self.env.AddPreAction('out.txt', 'echo pre > pre.txt')
        self.env.AddPostAction('out.txt', 'echo post > post.txt')
        build = self.translator.action_to_ninja_build(node)
        self.assertEqual(build['rule'], 'GENERATED_CMD')
        self.assertEqual(
            build['variables']['cmd'],
            'echo pre > pre.txt && cat in.txt > out.txt && echo post > post.txt',
        )

    def test_pre_action_only(self):
        """A pre action alone is still included in the ninja command."""
        node = self._command_node()
        self.env.AddPreAction('out.txt', 'echo pre > pre.txt')
        build = self.translator.action_to_ninja_build(node)
        self.assertEqual(
            build['variables']['cmd'],
            'echo pre > pre.txt && cat in.txt > out.txt',
        )

    def test_post_action_only(self):
        """A post action alone is still included in the ninja command."""
        node = self._command_node()
        self.env.AddPostAction('out.txt', 'echo post > post.txt')
        build = self.translator.action_to_ninja_build(node)
        self.assertEqual(
            build['variables']['cmd'],
            'cat in.txt > out.txt && echo post > post.txt',
        )

    def test_list_action_with_pre_and_post_actions(self):
        """Pre and post actions wrap a builder whose action is a list of commands."""
        node = self.env.Command('out.txt', 'in.txt', ['echo a > $TARGET', 'echo b >> $TARGET'])[0]
        self.env.AddPreAction('out.txt', 'echo pre > pre.txt')
        self.env.AddPostAction('out.txt', 'echo post >> $TARGET')
        build = self.translator.action_to_ninja_build(node)
        self.assertEqual(build['rule'], 'GENERATED_CMD')
        self.assertEqual(
            build['variables']['cmd'],
            'echo pre > pre.txt && echo a > out.txt && echo b >> out.txt && echo post >> out.txt',
        )

    def test_nested_list_action_with_pre_and_post_actions(self):
        """A nested ListAction inside the action list merges with pre and post actions."""
        inner = SCons.Action.ListAction(['echo a > $TARGET', 'echo b >> $TARGET'])
        node = self.env.Command('out.txt', 'in.txt', inner)[0]
        self.env.AddPreAction('out.txt', 'echo pre > pre.txt')
        self.env.AddPostAction('out.txt', 'echo post >> $TARGET')
        build = self.translator.action_to_ninja_build(node)
        self.assertEqual(build['rule'], 'GENERATED_CMD')
        self.assertEqual(
            build['variables']['cmd'],
            'echo pre > pre.txt && echo a > out.txt && echo b >> out.txt && echo post >> out.txt',
        )

    def test_unhandled_function_main_action_falls_back_to_template(self):
        """An unhandled Python function as the builder's action becomes a TEMPLATE rule."""
        def main_func(target, source, env):
            return 0

        node = self.env.Command('out.txt', 'in.txt', main_func)[0]
        build = self.translator.action_to_ninja_build(node)
        self.assertEqual(build['rule'], 'TEMPLATE')

    def test_unhandled_function_in_list_action_falls_back_to_template(self):
        """A function action mixed into a command list must not drop the commands."""
        def mid_func(target, source, env):
            return 0

        node = self.env.Command('out.txt', 'in.txt', ['echo a > $TARGET', mid_func])[0]
        build = self.translator.action_to_ninja_build(node)
        self.assertEqual(build['rule'], 'TEMPLATE')

    def test_unhandled_function_pre_action_falls_back_to_template(self):
        """An unhandled Python function pre action must not be silently dropped.

        The node falls back to a TEMPLATE rule so SCons runs the full action list.
        """
        def pre_func(target, source, env):
            return 0

        node = self._command_node()
        self.env.AddPreAction('out.txt', pre_func)
        build = self.translator.action_to_ninja_build(node)
        self.assertEqual(build['rule'], 'TEMPLATE')


if __name__ == "__main__":
    unittest.main()
