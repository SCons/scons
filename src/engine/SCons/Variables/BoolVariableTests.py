#
# __COPYRIGHT__
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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import sys
import unittest

import SCons.Errors
import SCons.Variables

class BoolVariableTestCase(unittest.TestCase):
    def test_BoolVariable(self):
        """Test BoolVariable creation"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.BoolVariable('test', 'test option help', 0))

        o = opts.options[0]
        assert o.key == 'test', o.key
        assert o.help == 'test option help (yes|no)', o.help
        assert o.default == 0, o.default
        assert o.validator is not None, o.validator
        assert o.converter is not None, o.converter

    def test_converter(self):
        """Test the BoolVariable converter"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.BoolVariable('test', 'test option help', 0))

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
            assert x, "converter returned false for '%s'" % t

        for f in false_values:
            x = o.converter(f)
            assert not x, "converter returned true for '%s'" % f

        caught = None
        try:
            o.converter('x')
        except ValueError:
            caught = 1
        assert caught, "did not catch expected ValueError"

    def test_validator(self):
        """Test the BoolVariable validator"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.BoolVariable('test', 'test option help', 0))

        o = opts.options[0]

        env = {
            'T' : True,
            'F' : False,
            'N' : 'xyzzy',
        }

        o.validator('T', 0, env)

        o.validator('F', 0, env)

        caught = None
        try:
            o.validator('N', 0, env)
        except SCons.Errors.UserError:
            caught = 1
        assert caught, "did not catch expected UserError for N"

        caught = None
        try:
            o.validator('NOSUCHKEY', 0, env)
        except KeyError:
            caught = 1
        assert caught, "did not catch expected KeyError for NOSUCHKEY"


if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
