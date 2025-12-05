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

import TestCmd

class PackageVariableTestCase(unittest.TestCase):
    def test_PackageVariable(self) -> None:
        """Test PackageVariable creation"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PackageVariable('test', 'test build variable help', '/default/path'))

        o = opts.options[0]
        assert o.key == 'test', o.key
        assert o.help == 'test build variable help\n    ( yes | no | /path/to/test )', repr(o.help)
        assert o.default == '/default/path', o.default
        assert o.validator is not None, o.validator
        assert o.converter is not None, o.converter

    def test_converter(self) -> None:
        """Test the PackageVariable converter"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PackageVariable('test', 'test build variable help', '/default/path'))

        o = opts.options[0]

        true_values = [
                'yes',    'YES',
                'true',   'TRUE',
                'on',     'ON',
                'enable', 'ENABLE',
                'search', 'SEARCH',
        ]
        false_values = [
                'no',      'NO',
                'false',   'FALSE',
                'off',     'OFF',
                'disable', 'DISABLE',
        ]

        for t in true_values:
            x = o.converter(t)
            assert x, f"converter returned False for {t!r}"

        for f in false_values:
            x = o.converter(f)
            assert not x, f"converter returned True for {f!r}"

        x = o.converter('/explicit/path')
        assert x == '/explicit/path', x

        # Make sure the converter returns True if we give it str(True) and
        # False when we give it str(False).  This assures consistent operation
        # through a cycle of Variables.Save(<file>) -> Variables(<file>).
        x = o.converter(str(True))
        assert x, "converter returned a string when given str(True)"

        x = o.converter(str(False))
        assert not x, "converter returned a string when given str(False)"

        # Synthesize the case where the variable is created with subst=False:
        # Variables code won't subst before calling the converter,
        # and we might have pulled a bool from the option default.
        with self.subTest():
            x = o.converter(True)
            assert x, f"converter returned False for {t!r}"
        with self.subTest():
            x = o.converter(False)
            assert not x, f"converter returned False for {t!r}"

        # When the variable is created with boolean string make sure the converter
        # returns the correct result i.e. a bool or a passed path
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PackageVariable('test', 'test build variable help', 'yes'))
        o = opts.options[0]

        x = o.converter(str(True))
        assert not isinstance(x, str), "converter with default str(yes) returned a string when given str(True)"
        assert x, "converter with default str(yes) returned False for str(True)"
        x = o.converter(str(False))
        assert not isinstance(x, str), "converter with default str(yes) returned a string when given str(False)"
        assert not x, "converter with default str(yes) returned True for str(False)"
        x = o.converter('/explicit/path')
        assert x == '/explicit/path', "converter with default str(yes) did not return path"

        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PackageVariable('test', 'test build variable help', 'no'))
        o = opts.options[0]

        x = o.converter(str(True))
        assert not isinstance(x, str), "converter with default str(no) returned a string when given str(True)"
        assert x, "converter with default str(no) returned False for str(True)"
        x = o.converter(str(False))
        assert not isinstance(x, str), "converter with default str(no) returned a string when given str(False)"
        assert not x, "converter with default str(no) returned True for str(False)"
        x = o.converter('/explicit/path')
        assert x == '/explicit/path', "converter with default str(no) did not return path"

    def test_validator(self) -> None:
        """Test the PackageVariable validator"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PackageVariable('test', 'test build variable help', '/default/path'))

        test = TestCmd.TestCmd(workdir='')
        test.write('exists', 'exists\n')

        o = opts.options[0]

        env = {'F':False, 'T':True, 'X':'x'}

        exists = test.workpath('exists')
        does_not_exist = test.workpath('does_not_exist')

        o.validator('F', '/path', env)
        o.validator('T', '/path', env)
        o.validator('X', exists, env)

        with self.assertRaises(SCons.Errors.UserError):
            o.validator('X', does_not_exist, env)


if __name__ == "__main__":
    unittest.main()
