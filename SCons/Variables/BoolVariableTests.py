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

import unittest

import SCons.Errors
import SCons.Variables

class BoolVariableTestCase(unittest.TestCase):
    def test_BoolVariable(self) -> None:
        """Test BoolVariable creation"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.BoolVariable('test', 'test option help', False))

        o = opts.options[0]
        assert o.key == 'test', o.key
        assert o.help == 'test option help (yes|no)', o.help
        assert o.default == 0, o.default
        assert o.validator is not None, o.validator
        assert o.converter is not None, o.converter

    def test_converter(self) -> None:
        """Test the BoolVariable converter"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.BoolVariable('test', 'test option help', False))
        o = opts.options[0]

        true_values = [
                'y',    'Y',
                'yes',  'YES',
                't',    'T',
                'true', 'TRUE',
                'on',   'ON',
                'all',  'ALL',
                '1',
        ]
        false_values = [
                'n',    'N',
                'no',   'NO',
                'f',    'F',
                'false', 'FALSE',
                'off',  'OFF',
                'none', 'NONE',
                '0',
        ]

        for t in true_values:
            x = o.converter(t)
            assert x, f"converter returned False for {t!r}"

        for f in false_values:
            x = o.converter(f)
            assert not x, f"converter returned True for {f!r}"

        with self.assertRaises(ValueError):
            o.converter('x')

        # Synthesize the case where the variable is created with subst=False:
        # Variables code won't subst before calling the converter,
        # and we might have pulled a bool from the option default.
        with self.subTest():
            x = o.converter(True)
            assert x, f"converter returned False for {t!r}"
        with self.subTest():
            x = o.converter(False)
            assert not x, f"converter returned False for {t!r}"


    def test_validator(self) -> None:
        """Test the BoolVariable validator"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.BoolVariable('test', 'test option help', False))

        o = opts.options[0]

        env = {
            'T' : True,
            'F' : False,
            'N' : 'xyzzy',
        }

        # positive checks
        o.validator('T', 0, env)
        o.validator('F', 0, env)

        # negative checks
        with self.assertRaises(SCons.Errors.UserError):
            o.validator('N', 0, env)

        with self.assertRaises(KeyError):
            o.validator('NOSUCHKEY', 0, env)


if __name__ == "__main__":
    unittest.main()
