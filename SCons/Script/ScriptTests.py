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

# Unit tests of functionality from SCons.Script._init__.py.
#
# Most of the tests of this functionality are actually end-to-end scripts
# in the test/ hierarchy.
#
# This module is for specific bits of functionality that seem worth
# testing here - particularly if there's private data involved.

import unittest

from SCons.Script import (
    _Add_Arguments,
    _Add_Targets,
    _Remove_Argument,
    _Remove_Target,
    ARGLIST,
    ARGUMENTS,
    BUILD_TARGETS,
    COMMAND_LINE_TARGETS,
    _build_plus_default,
)


class TestScriptFunctions(unittest.TestCase):
    def setUp(self):
        # Clear global state before each test
        ARGUMENTS.clear()
        ARGLIST.clear()
        del COMMAND_LINE_TARGETS[:]
        del BUILD_TARGETS[:]
        del _build_plus_default[:]

    def test_Add_Arguments(self):
        test_args = ['foo=bar', 'spam=eggs']

        _Add_Arguments(test_args)
        self.assertEqual(ARGUMENTS, {'foo': 'bar', 'spam': 'eggs'})
        self.assertEqual(ARGLIST, [('foo', 'bar'), ('spam', 'eggs')])

    def test_Add_Arguments_empty(self):
        # Adding am empty argument is a no-op, with no error
        _Add_Arguments([])
        self.assertEqual(ARGUMENTS, {})
        self.assertEqual(ARGLIST, [])

    def test_Add_Targets(self):
        test_targets = ['target1', 'target2']
        _Add_Targets(test_targets)

        self.assertEqual(COMMAND_LINE_TARGETS, ['target1', 'target2'])
        self.assertEqual(BUILD_TARGETS, ['target1', 'target2'])
        self.assertEqual(_build_plus_default, ['target1', 'target2'])

        # Test that methods were replaced
        self.assertEqual(BUILD_TARGETS._add_Default, BUILD_TARGETS._do_nothing)
        self.assertEqual(BUILD_TARGETS._clear, BUILD_TARGETS._do_nothing)
        self.assertEqual(
            _build_plus_default._add_Default, _build_plus_default._do_nothing
        )
        self.assertEqual(
            _build_plus_default._clear, _build_plus_default._do_nothing
        )

    def test_Add_Targets_empty(self):
        # Adding am empty argument is a no-op, with no error
        _Add_Targets([])
        self.assertEqual(COMMAND_LINE_TARGETS, [])
        self.assertEqual(BUILD_TARGETS, [])
        self.assertEqual(_build_plus_default, [])

    def test_Remove_Argument(self):
        ARGLIST.extend([
            ('key1', 'value1'),
            ('key2', 'value2')
        ])
        ARGUMENTS.update({'key1': 'value1', 'key2': 'value2'})

        _Remove_Argument('key1=value1')
        self.assertEqual(ARGUMENTS, {'key2': 'value2'})
        self.assertEqual(ARGLIST, [('key2', 'value2')])

    def test_Remove_Argument_key_with_multiple_values(self):
        ARGLIST.extend([
            ('key1', 'value1'),
            ('key1', 'value2')
        ])
        ARGUMENTS['key1'] = 'value2'  # ARGUMENTS only keeps last, emulate

        _Remove_Argument('key1=value1')
        self.assertEqual(ARGLIST, [('key1', 'value2')])
        # ARGUMENTS must be reconstructed
        self.assertEqual(ARGUMENTS, {'key1': 'value2'})

    def test_Remove_Argument_nonexistent(self):
        # Removing a nonexistent argument is a no-op with no error
        ARGUMENTS['key1'] = 'value1'
        ARGLIST.append(('key1', 'value1'))

        _Remove_Argument('nonexistent=value')
        self.assertEqual(ARGUMENTS, {'key1': 'value1'})
        self.assertEqual(ARGLIST, [('key1', 'value1')])

    def test_Remove_Argument_empty(self):
        # Removing an empty argument is also a no-op with no error
        ARGUMENTS['key1'] = 'value1'
        ARGLIST.append(('key1', 'value1'))

        _Remove_Argument('')
        self.assertEqual(ARGUMENTS, {'key1': 'value1'})
        self.assertEqual(ARGLIST, [('key1', 'value1')])

    # XXX where does TARGETS come in?
    def test_Remove_Target(self):
        BUILD_TARGETS.extend(['target1', 'target2', 'target3'])
        COMMAND_LINE_TARGETS.extend(['target1', 'target2', 'target3'])

        _Remove_Target('target2')
        self.assertEqual(BUILD_TARGETS, ['target1', 'target3'])
        self.assertEqual(COMMAND_LINE_TARGETS, ['target1', 'target3'])

    def test_Remove_Target_duplicated(self):
        # Targets can be duplicated, only one should be removed
        # There is not a good way to determine which instance was added
        # "in error" so all we can do is check *something* was removed.
        BUILD_TARGETS.extend(['target1', 'target1'])
        COMMAND_LINE_TARGETS.extend(['target1', 'target1'])

        _Remove_Target('target1')
        self.assertEqual(BUILD_TARGETS, ['target1'])
        self.assertEqual(COMMAND_LINE_TARGETS, ['target1'])

    def test_Remove_Target_nonexistent(self):
        # Asking to remove a nonexistent argument is a no-op with no error
        BUILD_TARGETS.append('target1')
        COMMAND_LINE_TARGETS.append('target1')

        _Remove_Target('nonexistent')
        self.assertEqual(BUILD_TARGETS, ['target1'])
        self.assertEqual(COMMAND_LINE_TARGETS, ['target1'])

    def test_Remove_Target_empty(self):
        # Asking to remove an empty argument is also a no-op with no error
        BUILD_TARGETS.append('target1')
        COMMAND_LINE_TARGETS.append('target1')

        _Remove_Target('')
        self.assertEqual(BUILD_TARGETS, ['target1'])
        self.assertEqual(COMMAND_LINE_TARGETS, ['target1'])


if __name__ == '__main__':
    unittest.main()
