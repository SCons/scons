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


if __name__ == "__main__":
    unittest.main()
