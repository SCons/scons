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

import TestCmd

class PackageVariableTestCase(unittest.TestCase):
    def test_PackageVariable(self):
        """Test PackageVariable creation"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PackageVariable('test', 'test option help', '/default/path'))

        o = opts.options[0]
        assert o.key == 'test', o.key
        assert o.help == 'test option help\n    ( yes | no | /path/to/test )', repr(o.help)
        assert o.default == '/default/path', o.default
        assert o.validator is not None, o.validator
        assert o.converter is not None, o.converter

    def test_converter(self):
        """Test the PackageVariable converter"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PackageVariable('test', 'test option help', '/default/path'))

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
            assert x, "converter returned false for '%s'" % t

        for f in false_values:
            x = o.converter(f)
            assert not x, "converter returned true for '%s'" % f

        x = o.converter('/explicit/path')
        assert x == '/explicit/path', x

        # Make sure the converter returns True if we give it str(True) and
        # False when we give it str(False).  This assures consistent operation
        # through a cycle of Variables.Save(<file>) -> Variables(<file>).
        x = o.converter(str(True))
        assert x == True, "converter returned a string when given str(True)"

        x = o.converter(str(False))
        assert x == False, "converter returned a string when given str(False)"

    def test_validator(self):
        """Test the PackageVariable validator"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PackageVariable('test', 'test option help', '/default/path'))

        test = TestCmd.TestCmd(workdir='')
        test.write('exists', 'exists\n')

        o = opts.options[0]

        env = {'F':False, 'T':True, 'X':'x'}

        exists = test.workpath('exists')
        does_not_exist = test.workpath('does_not_exist')

        o.validator('F', '/path', env)
        o.validator('T', '/path', env)
        o.validator('X', exists, env)

        caught = None
        try:
            o.validator('X', does_not_exist, env)
        except SCons.Errors.UserError:
            caught = 1
        assert caught, "did not catch expected UserError"


if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
