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

"""Test List Variables elements."""

import copy
import unittest

import SCons.Errors
import SCons.Variables

class ListVariableTestCase(unittest.TestCase):
    def test_ListVariable(self) -> None:
        """Test ListVariable creation"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.ListVariable('test', 'test option help', 'all',
                                          ['one', 'two', 'three']))

        o = opts.options[0]
        assert o.key == 'test', o.key
        assert o.help == 'test option help\n    (all|none|comma-separated list of names)\n    allowed names: one two three', repr(o.help)
        assert o.default == 'all', o.default
        assert o.validator is not None, o.validator
        assert o.converter is not None, o.converter

        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.ListVariable('test2', 'test2 help',
                                          ['one', 'three'],
                                          ['one', 'two', 'three']))

        o = opts.options[0]
        assert o.default == 'one,three'

    def test_converter(self) -> None:
        """Test the ListVariable converter.

        There is now a separate validator (for a long time validation was
        in the converter), but it depends on the _ListVariable instance the
        converter creates, so it's easier to test them in the same function.
        """
        opts = SCons.Variables.Variables()
        opts.Add(
            SCons.Variables.ListVariable(
                'test',
                'test option help',
                default='all',
                names=['one', 'two', 'three'],
                map={'ONE': 'one', 'TWO': 'two'},
            )
        )
        o = opts.options[0]

        x = o.converter('all')
        assert str(x) == 'all', x

        x = o.converter('none')
        assert str(x) == 'none', x

        x = o.converter('one')
        assert str(x) == 'one', x
        x = o.converter('ONE')
        assert str(x) == 'one', x

        x = o.converter('two')
        assert str(x) == 'two', x
        x = o.converter('TWO')
        assert str(x) == 'two', x

        x = o.converter('three')
        assert str(x) == 'three', x

        x = o.converter('one,two')
        assert str(x) == 'one,two', x
        x = o.converter('two,one')
        assert str(x) == 'one,two', x

        x = o.converter('one,three')
        assert str(x) == 'one,three', x
        x = o.converter('three,one')
        assert str(x) == 'one,three', x

        x = o.converter('two,three')
        assert str(x) == 'three,two', x
        x = o.converter('three,two')
        assert str(x) == 'three,two', x

        x = o.converter('one,two,three')
        assert str(x) == 'all', x

        x = o.converter('three,two,one')
        assert str(x) == 'all', x

        x = o.converter('three,ONE,TWO')
        assert str(x) == 'all', x

        # invalid value should convert (no change) without error
        x = o.converter('no_match')
        assert str(x) == 'no_match', x

        # validator checks

        # first, the one we just set up
        with self.assertRaises(SCons.Errors.UserError):
            o.validator('test', 'no_match', {"test": x})

        # now a new option, this time with a name w/ space in it (issue #4585)
        opts.Add(
            SCons.Variables.ListVariable(
                'test2',
                help='test2 option help',
                default='two',
                names=['one', 'two', 'three', 'four space'],
            )
        )
        o = opts.options[1]

        def test_valid(opt, seq):
            """Validate a ListVariable value.

            Call the converter manually, since we need the _ListVariable
            object to pass to the validator - this would normally be done
            by the Variables.Update method.
            """
            x = opt.converter(seq)
            self.assertIsNone(opt.validator(opt.key, x, {opt.key: x}))

        with self.subTest():
            test_valid(o, 'one')
        with self.subTest():
            test_valid(o, 'one,two,three')
        with self.subTest():
            test_valid(o, 'all')
        with self.subTest():
            test_valid(o, 'none')
        with self.subTest():
            test_valid(o, 'four space')
        with self.subTest():
            test_valid(o, 'one,four space')


    def test_copy(self) -> None:
        """Test copying a ListVariable like an Environment would"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.ListVariable('test', 'test option help', 'all',
                                          ['one', 'two', 'three']))

        o = opts.options[0]
        res = o.converter('all')
        _ = res.__class__(copy.copy(res))

if __name__ == "__main__":
    unittest.main()
