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

import unittest
import TestSCons
import SCons.Options
import sys
import string


class Environment:
    def __init__(self):
        self.dict = {}
    def subst(self, x):
        return self.dict[x[2:-1]]
    def __setitem__(self, key, value):
        self.dict[key] = value
    def __getitem__(self, key):
        return self.dict[key]
    def has_key(self, key):
        return self.dict.has_key(key)


def check(key,value, env):
    assert value == 6 * 9,key
    
# Check saved option file by executing and comparing against
# the expected dictionary
def checkSave(file, expected):
    gdict = {}
    ldict = {}
    execfile(file, gdict, ldict)
    assert expected == ldict

class OptionsTestCase(unittest.TestCase):
    def test_Add(self):
        opts = SCons.Options.Options()

        opts.Add('VAR')
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "42",
                 check,
                 lambda x: int(x) + 12)

        o = opts.options[0]
        assert o.key == 'VAR'
        assert o.help == ''
        assert o.default == None
        assert o.validater == None
        assert o.converter == None
        assert o.should_save == 0

        o = opts.options[1]
        assert o.key == 'ANSWER'
        assert o.help == 'THE answer to THE question'
        assert o.default == "42"
        o.validater(o.key, o.converter(o.default), {})

        def test_it(var, opts=opts):
            exc_caught = None
            try:
                opts.Add(var)
            except SCons.Errors.UserError:
                exc_caught = 1
            assert exc_caught, "did not catch UserError for '%s'" % var
        test_it('foo/bar')
        test_it('foo-bar')
        test_it('foo.bar')

    def test_Update(self):

        test = TestSCons.TestSCons()
        file = test.workpath('custom.py')
        opts = SCons.Options.Options(file)
        
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "42",
                 check,
                 lambda x: int(x) + 12)

        env = Environment()
        opts.Update(env, {})
        assert env['ANSWER'] == 54

        test = TestSCons.TestSCons()
        file = test.workpath('custom.py')
        test.write('custom.py', 'ANSWER=54')
        opts = SCons.Options.Options(file)
        
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "42",
                 check,
                 lambda x: int(x) + 12)

        env = Environment()
        try:
            opts.Update(env, {})
        except AssertionError:
            pass

        test = TestSCons.TestSCons()
        file = test.workpath('custom.py')
        test.write('custom.py', 'ANSWER=42')
        opts = SCons.Options.Options(file)
        
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "54",
                 check,
                 lambda x: int(x) + 12)

        env = Environment()
        opts.Update(env, {})
        assert env['ANSWER'] == 54

        test = TestSCons.TestSCons()
        file = test.workpath('custom.py')
        test.write('custom.py', 'ANSWER=54')
        opts = SCons.Options.Options(file)
        
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "54",
                 check,
                 lambda x: int(x) + 12)

        env = Environment()
        opts.Update(env, {'ANSWER':'42'})
        assert env['ANSWER'] == 54


    def test_Save(self):

        test = TestSCons.TestSCons()
        cache_file = test.workpath('cached.options')
        opts = SCons.Options.Options()
        
        # test saving out empty file
        opts.Add('OPT_VAL',
                 'An option to test',
                 21,
                 None,
                 None)

        env = Environment()
        opts.Update(env, {})
        assert env['OPT_VAL'] == 21
        opts.Save(cache_file, env)
        checkSave(cache_file, {})


    def test_GenerateHelpText(self):
        opts = SCons.Options.Options()

        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "42",
                 check,
                 lambda x: int(x) + 12)

        opts.Add('B',
                 'b - alpha test',
                 "42",
                 check,
                 lambda x: int(x) + 12)

        opts.Add('A',
                 'a - alpha test',
                 "42",
                 check,
                 lambda x: int(x) + 12)

        env = Environment()
        opts.Update(env, {})

        expect = """
ANSWER: THE answer to THE question
    default: 42
    actual: 54

B: b - alpha test
    default: 42
    actual: 54

A: a - alpha test
    default: 42
    actual: 54
"""

        text = opts.GenerateHelpText(env)
        assert text == expect, text

        expectAlpha = """
A: a - alpha test
    default: 42
    actual: 54

ANSWER: THE answer to THE question
    default: 42
    actual: 54

B: b - alpha test
    default: 42
    actual: 54
"""
        text = opts.GenerateHelpText(env, sort=cmp)
        assert text == expectAlpha, text
        
if __name__ == "__main__":
    suite = unittest.makeSuite(OptionsTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
