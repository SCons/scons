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

import copy
import sys
import unittest

import SCons.Errors
import SCons.Variables

class ListVariableTestCase(unittest.TestCase):
    def test_ListVariable(self):
        """Test ListVariable creation"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.ListVariable('test', 'test option help', 'all',
                                          ['one', 'two', 'three']))

        o = opts.options[0]
        assert o.key == 'test', o.key
        assert o.help == 'test option help\n    (all|none|comma-separated list of names)\n    allowed names: one two three', repr(o.help)
        assert o.default == 'all', o.default
        assert o.validator is None, o.validator
        assert not o.converter is None, o.converter

        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.ListVariable('test2', 'test2 help',
                                          ['one', 'three'],
                                          ['one', 'two', 'three']))

        o = opts.options[0]
        assert o.default == 'one,three'

    def test_converter(self):
        """Test the ListVariable converter"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.ListVariable('test', 'test option help', 'all',
                                          ['one', 'two', 'three'],
                                          {'ONE':'one', 'TWO':'two'}))

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

        caught = None
        try:
            x = o.converter('no_match')
        except ValueError:
            caught = 1
        assert caught, "did not catch expected ValueError"

    def test_copy(self):
        """Test copying a ListVariable like an Environment would"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.ListVariable('test', 'test option help', 'all',
                                          ['one', 'two', 'three']))

        o = opts.options[0]

        l = o.converter('all')
        n = l.__class__(copy.copy(l))

if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
