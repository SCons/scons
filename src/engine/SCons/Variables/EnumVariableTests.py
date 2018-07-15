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

class EnumVariableTestCase(unittest.TestCase):
    def test_EnumVariable(self):
        """Test EnumVariable creation"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.EnumVariable('test', 'test option help', 0,
                                          ['one', 'two', 'three'],
                                          {}))

        o = opts.options[0]
        assert o.key == 'test', o.key
        assert o.help == 'test option help (one|two|three)', o.help
        assert o.default == 0, o.default
        assert o.validator is not None, o.validator
        assert o.converter is not None, o.converter

    def test_converter(self):
        """Test the EnumVariable converter"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.EnumVariable('test', 'test option help', 0,
                                          ['one', 'two', 'three']))

        o = opts.options[0]

        for a in ['one', 'two', 'three', 'no_match']:
            x = o.converter(a)
            assert x == a, x

        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.EnumVariable('test', 'test option help', 0,
                                          ['one', 'two', 'three'],
                                          {'1' : 'one',
                                           '2' : 'two',
                                           '3' : 'three'}))

        o = opts.options[0]

        x = o.converter('one')
        assert x == 'one', x
        x = o.converter('1')
        assert x == 'one', x

        x = o.converter('two')
        assert x == 'two', x
        x = o.converter('2')
        assert x == 'two', x

        x = o.converter('three')
        assert x == 'three', x
        x = o.converter('3')
        assert x == 'three', x

        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.EnumVariable('test0', 'test option help', 0,
                                          ['one', 'two', 'three'],
                                          {'a' : 'one',
                                           'b' : 'two',
                                           'c' : 'three'},
                                          ignorecase=0))
        opts.Add(SCons.Variables.EnumVariable('test1', 'test option help', 0,
                                          ['one', 'two', 'three'],
                                          {'a' : 'one',
                                           'b' : 'two',
                                           'c' : 'three'},
                                          ignorecase=1))
        opts.Add(SCons.Variables.EnumVariable('test2', 'test option help', 0,
                                          ['one', 'two', 'three'],
                                          {'a' : 'one',
                                           'b' : 'two',
                                           'c' : 'three'},
                                          ignorecase=2))

        o0 = opts.options[0]
        o1 = opts.options[1]
        o2 = opts.options[2]

        table = {
            'one'   : ['one',   'one',   'one'],
            'One'   : ['One',   'One',   'one'],
            'ONE'   : ['ONE',   'ONE',   'one'],
            'two'   : ['two',   'two',   'two'],
            'twO'   : ['twO',   'twO',   'two'],
            'TWO'   : ['TWO',   'TWO',   'two'],
            'three' : ['three', 'three', 'three'],
            'thRee' : ['thRee', 'thRee', 'three'],
            'THREE' : ['THREE', 'THREE', 'three'],
            'a'     : ['one',   'one',   'one'],
            'A'     : ['A',     'one',   'one'],
            'b'     : ['two',   'two',   'two'],
            'B'     : ['B',     'two',   'two'],
            'c'     : ['three', 'three', 'three'],
            'C'     : ['C',     'three', 'three'],
        }

        for k, l in table.items():
            x = o0.converter(k)
            assert x == l[0], "o0 got %s, expected %s" % (x, l[0])
            x = o1.converter(k)
            assert x == l[1], "o1 got %s, expected %s" % (x, l[1])
            x = o2.converter(k)
            assert x == l[2], "o2 got %s, expected %s" % (x, l[2])

    def test_validator(self):
        """Test the EnumVariable validator"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.EnumVariable('test0', 'test option help', 0,
                                          ['one', 'two', 'three'],
                                          {'a' : 'one',
                                           'b' : 'two',
                                           'c' : 'three'},
                                          ignorecase=0))
        opts.Add(SCons.Variables.EnumVariable('test1', 'test option help', 0,
                                          ['one', 'two', 'three'],
                                          {'a' : 'one',
                                           'b' : 'two',
                                           'c' : 'three'},
                                          ignorecase=1))
        opts.Add(SCons.Variables.EnumVariable('test2', 'test option help', 0,
                                          ['one', 'two', 'three'],
                                          {'a' : 'one',
                                           'b' : 'two',
                                           'c' : 'three'},
                                          ignorecase=2))

        o0 = opts.options[0]
        o1 = opts.options[1]
        o2 = opts.options[2]

        def valid(o, v):
            o.validator('X', v, {})

        def invalid(o, v):
            caught = None
            try:
                o.validator('X', v, {})
            except SCons.Errors.UserError:
                caught = 1
            assert caught, "did not catch expected UserError for o = %s, v = %s" % (o.key, v)

        table = {
            'one'   : [  valid,   valid,   valid],
            'One'   : [invalid,   valid,   valid],
            'ONE'   : [invalid,   valid,   valid],
            'two'   : [  valid,   valid,   valid],
            'twO'   : [invalid,   valid,   valid],
            'TWO'   : [invalid,   valid,   valid],
            'three' : [  valid,   valid,   valid],
            'thRee' : [invalid,   valid,   valid],
            'THREE' : [invalid,   valid,   valid],
            'a'     : [invalid, invalid, invalid],
            'A'     : [invalid, invalid, invalid],
            'b'     : [invalid, invalid, invalid],
            'B'     : [invalid, invalid, invalid],
            'c'     : [invalid, invalid, invalid],
            'C'     : [invalid, invalid, invalid],
            'no_v'  : [invalid, invalid, invalid],
        }

        for v, l in table.items():
            l[0](o0, v)
            l[1](o1, v)
            l[2](o2, v)


if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
