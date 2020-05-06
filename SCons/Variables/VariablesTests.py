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

import TestSCons

import SCons.Variables
import SCons.Subst
import SCons.Warnings
from SCons.Util import cmp


class Environment(object):
    def __init__(self):
        self.dict = {}
    def subst(self, x):
        return SCons.Subst.scons_subst(x, self, gvars=self.dict)
    def __setitem__(self, key, value):
        self.dict[key] = value
    def __getitem__(self, key):
        return self.dict[key]
    def __contains__(self, key):
        return self.dict.__contains__(key)
    def has_key(self, key):
        return key in self.dict




def check(key, value, env):
    assert int(value) == 6 * 9, "key %s = %s" % (key, repr(value))
    
# Check saved option file by executing and comparing against
# the expected dictionary
def checkSave(file, expected):
    gdict = {}
    ldict = {}
    with open(file, 'r') as f:
        exec(f.read(), gdict, ldict)

    assert expected == ldict, "%s\n...not equal to...\n%s" % (expected, ldict)

class VariablesTestCase(unittest.TestCase):

    def test_keys(self):
        """Test the Variables.keys() method"""
        opts = SCons.Variables.Variables()

        opts.Add('VAR1')
        opts.Add('VAR2',
                 'THE answer to THE question',
                 "42",
                 check,
                 lambda x: int(x) + 12)
        keys = list(opts.keys())
        assert keys == ['VAR1', 'VAR2'], keys

    def test_Add(self):
        """Test adding to a Variables object"""
        opts = SCons.Variables.Variables()

        opts.Add('VAR')
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "42",
                 check,
                 lambda x: int(x) + 12)

        o = opts.options[0]
        assert o.key == 'VAR'
        assert o.help == ''
        assert o.default is None
        assert o.validator is None
        assert o.converter is None

        o = opts.options[1]
        assert o.key == 'ANSWER'
        assert o.help == 'THE answer to THE question'
        assert o.default == "42"
        o.validator(o.key, o.converter(o.default), {})

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

    def test_AddVariables(self):
        """Test adding a list of options to a Variables object"""
        opts = SCons.Variables.Variables()

        opts.AddVariables(('VAR2',),
                        ('ANSWER2',
                         'THE answer to THE question',
                         "42",
                         check,
                         lambda x: int(x) + 12))

        o = opts.options[0]
        assert o.key == 'VAR2', o.key
        assert o.help == '', o.help
        assert o.default is None, o.default
        assert o.validator is None, o.validator
        assert o.converter is None, o.converter

        o = opts.options[1]
        assert o.key == 'ANSWER2', o.key
        assert o.help == 'THE answer to THE question', o.help
        assert o.default == "42", o.default
        o.validator(o.key, o.converter(o.default), {})

    def test_Update(self):
        """Test updating an Environment"""

        # Test that a default value is validated correctly.
        test = TestSCons.TestSCons()
        file = test.workpath('custom.py')
        opts = SCons.Variables.Variables(file)
        
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "42",
                 check,
                 lambda x: int(x) + 12)

        env = Environment()
        opts.Update(env)
        assert env['ANSWER'] == 54

        env = Environment()
        opts.Update(env, {})
        assert env['ANSWER'] == 54

        # Test that a bad value from the file is used and
        # validation fails correctly.
        test = TestSCons.TestSCons()
        file = test.workpath('custom.py')
        test.write('custom.py', 'ANSWER=54')
        opts = SCons.Variables.Variables(file)
        
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "42",
                 check,
                 lambda x: int(x) + 12)

        env = Environment()
        exc_caught = None
        try:
            opts.Update(env)
        except AssertionError:
            exc_caught = 1
        assert exc_caught, "did not catch expected assertion"

        env = Environment()
        exc_caught = None
        try:
            opts.Update(env, {})
        except AssertionError:
            exc_caught = 1
        assert exc_caught, "did not catch expected assertion"

        # Test that a good value from the file is used and validated.
        test = TestSCons.TestSCons()
        file = test.workpath('custom.py')
        test.write('custom.py', 'ANSWER=42')
        opts = SCons.Variables.Variables(file)
        
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "10",
                 check,
                 lambda x: int(x) + 12)

        env = Environment()
        opts.Update(env)
        assert env['ANSWER'] == 54

        env = Environment()
        opts.Update(env, {})
        assert env['ANSWER'] == 54

        # Test that a bad value from an args dictionary passed to
        # Update() is used and validation fails correctly.
        test = TestSCons.TestSCons()
        file = test.workpath('custom.py')
        test.write('custom.py', 'ANSWER=10')
        opts = SCons.Variables.Variables(file)
        
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "12",
                 check,
                 lambda x: int(x) + 12)

        env = Environment()
        exc_caught = None
        try:
            opts.Update(env, {'ANSWER':'54'})
        except AssertionError:
            exc_caught = 1
        assert exc_caught, "did not catch expected assertion"

        # Test that a good value from an args dictionary
        # passed to Update() is used and validated.
        test = TestSCons.TestSCons()
        file = test.workpath('custom.py')
        test.write('custom.py', 'ANSWER=10')
        opts = SCons.Variables.Variables(file)
        
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "12",
                 check,
                 lambda x: int(x) + 12)

        env = Environment()
        opts.Update(env, {'ANSWER':'42'})
        assert env['ANSWER'] == 54

        # Test against a former bug.  If we supply a converter,
        # but no default, the value should *not* appear in the
        # Environment if no value is specified in the options file
        # or args.
        test = TestSCons.TestSCons()
        file = test.workpath('custom.py')
        opts = SCons.Variables.Variables(file)
        
        opts.Add('ANSWER',
                 help='THE answer to THE question',
                 converter=str)

        env = Environment()
        opts.Update(env, {})
        assert 'ANSWER' not in env

        # Test that a default value of None is all right.
        test = TestSCons.TestSCons()
        file = test.workpath('custom.py')
        opts = SCons.Variables.Variables(file)

        opts.Add('ANSWER',
                 "This is the answer",
                 None,
                 check)

        env = Environment()
        opts.Update(env, {})
        assert 'ANSWER' not in env

    def test_noaggregation(self):
        """Test that the 'files' and 'args' attributes of the Variables class
           don't aggregate entries from one instance to another.
           This used to be a bug in SCons version 2.4.1 and earlier.
        """

        opts = SCons.Variables.Variables()
        opts.files.append('custom.py')
        opts.args['ANSWER'] = 54
        nopts = SCons.Variables.Variables()

        # Ensure that both attributes are initialized to
        # an empty list and dict, respectively. 
        assert len(nopts.files) == 0
        assert len(nopts.args) == 0        

    def test_args(self):
        """Test updating an Environment with arguments overridden"""

        # Test that a bad (command-line) argument is used
        # and the validation fails correctly.
        test = TestSCons.TestSCons()
        file = test.workpath('custom.py')
        test.write('custom.py', 'ANSWER=42')
        opts = SCons.Variables.Variables(file, {'ANSWER':54})
        
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "42",
                 check,
                 lambda x: int(x) + 12)

        env = Environment()
        exc_caught = None
        try:
            opts.Update(env)
        except AssertionError:
            exc_caught = 1
        assert exc_caught, "did not catch expected assertion"

        # Test that a good (command-line) argument is used and validated.
        test = TestSCons.TestSCons()
        file = test.workpath('custom.py')
        test.write('custom.py', 'ANSWER=54')
        opts = SCons.Variables.Variables(file, {'ANSWER':42})
        
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "54",
                 check,
                 lambda x: int(x) + 12)

        env = Environment()
        opts.Update(env)
        assert env['ANSWER'] == 54

        # Test that a (command-line) argument is overridden by a dictionary
        # supplied to Update() and the dictionary value is validated correctly.
        test = TestSCons.TestSCons()
        file = test.workpath('custom.py')
        test.write('custom.py', 'ANSWER=54')
        opts = SCons.Variables.Variables(file, {'ANSWER':54})
        
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "54",
                 check,
                 lambda x: int(x) + 12)

        env = Environment()
        opts.Update(env, {'ANSWER':42})
        assert env['ANSWER'] == 54

    def test_Save(self):
        """Testing saving Variables"""

        test = TestSCons.TestSCons()
        cache_file = test.workpath('cached.options')
        opts = SCons.Variables.Variables()

        def bool_converter(val):
            if val in [1, 'y']: val = 1
            if val in [0, 'n']: val = 0
            return val
        
        # test saving out empty file
        opts.Add('OPT_VAL',
                 'An option to test',
                 21,
                 None,
                 None)
        opts.Add('OPT_VAL_2',
                 default='foo')
        opts.Add('OPT_VAL_3',
                 default=1)
        opts.Add('OPT_BOOL_0',
                 default='n',
                 converter=bool_converter)
        opts.Add('OPT_BOOL_1',
                 default='y',
                 converter=bool_converter)
        opts.Add('OPT_BOOL_2',
                 default=0,
                 converter=bool_converter)

        env = Environment()
        opts.Update(env, {'OPT_VAL_3' : 2})
        assert env['OPT_VAL'] == 21, env['OPT_VAL']
        assert env['OPT_VAL_2'] == 'foo', env['OPT_VAL_2']
        assert env['OPT_VAL_3'] == 2, env['OPT_VAL_3']
        assert env['OPT_BOOL_0'] == 0, env['OPT_BOOL_0']
        assert env['OPT_BOOL_1'] == 1, env['OPT_BOOL_1']
        assert env['OPT_BOOL_2'] == '0', env['OPT_BOOL_2']

        env['OPT_VAL_2'] = 'bar'
        env['OPT_BOOL_0'] = 0
        env['OPT_BOOL_1'] = 1
        env['OPT_BOOL_2'] = 2

        opts.Save(cache_file, env)
        checkSave(cache_file, { 'OPT_VAL_2' : 'bar',
                                'OPT_VAL_3' : 2,
                                'OPT_BOOL_2' : 2})

        # Test against some old bugs
        class Foo(object):
            def __init__(self, x):
                self.x = x
            def __str__(self):
                return self.x
            
        test = TestSCons.TestSCons()
        cache_file = test.workpath('cached.options')
        opts = SCons.Variables.Variables()
        
        opts.Add('THIS_USED_TO_BREAK',
                 'An option to test',
                 "Default")

        opts.Add('THIS_ALSO_BROKE',
                 'An option to test',
                 "Default2")
        
        opts.Add('THIS_SHOULD_WORK',
                 'An option to test',
                 Foo('bar'))
        
        env = Environment()
        opts.Update(env, { 'THIS_USED_TO_BREAK' : "Single'Quotes'In'String",
                           'THIS_ALSO_BROKE' : "\\Escape\nSequences\t",
                           'THIS_SHOULD_WORK' : Foo('baz') })
        opts.Save(cache_file, env)
        checkSave(cache_file, { 'THIS_USED_TO_BREAK' : "Single'Quotes'In'String",
                                'THIS_ALSO_BROKE' : "\\Escape\nSequences\t",
                                'THIS_SHOULD_WORK' : 'baz' })

    def test_GenerateHelpText(self):
        """Test generating the default format help text"""
        opts = SCons.Variables.Variables()

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

        expectBackwards = """
B: b - alpha test
    default: 42
    actual: 54

ANSWER: THE answer to THE question
    default: 42
    actual: 54

A: a - alpha test
    default: 42
    actual: 54
"""
        text = opts.GenerateHelpText(env, sort=cmp)
        assert text == expectAlpha, text

        textBool = opts.GenerateHelpText(env, sort=True)
        assert text == expectAlpha, text

        textBackwards = opts.GenerateHelpText(env, sort=lambda x, y: cmp(y, x))
        assert textBackwards == expectBackwards, "Expected:\n%s\nGot:\n%s\n"%(textBackwards, expectBackwards) 

    def test_FormatVariableHelpText(self):
        """Test generating custom format help text"""
        opts = SCons.Variables.Variables()

        def my_format(env, opt, help, default, actual, aliases):
            return '%s %s %s %s %s\n' % (opt, default, actual, help, aliases)

        opts.FormatVariableHelpText = my_format

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

        expect = """\
ANSWER 42 54 THE answer to THE question ['ANSWER']
B 42 54 b - alpha test ['B']
A 42 54 a - alpha test ['A']
"""

        text = opts.GenerateHelpText(env)
        assert text == expect, text

        expectAlpha = """\
A 42 54 a - alpha test ['A']
ANSWER 42 54 THE answer to THE question ['ANSWER']
B 42 54 b - alpha test ['B']
"""
        text = opts.GenerateHelpText(env, sort=cmp)
        assert text == expectAlpha, text
        
    def test_Aliases(self):
        """Test option aliases"""
        # test alias as a tuple
        opts = SCons.Variables.Variables()
        opts.AddVariables(
                (('ANSWER', 'ANSWERALIAS'),
                 'THE answer to THE question',
                 "42"),
                )
        
        env = Environment()
        opts.Update(env, {'ANSWER' : 'answer'})
        
        assert 'ANSWER' in env
        
        env = Environment()
        opts.Update(env, {'ANSWERALIAS' : 'answer'})
        
        assert 'ANSWER' in env and 'ANSWERALIAS' not in env
        
        # test alias as a list
        opts = SCons.Variables.Variables()
        opts.AddVariables(
                (['ANSWER', 'ANSWERALIAS'],
                 'THE answer to THE question',
                 "42"),
                )
        
        env = Environment()
        opts.Update(env, {'ANSWER' : 'answer'})
        
        assert 'ANSWER' in env
        
        env = Environment()
        opts.Update(env, {'ANSWERALIAS' : 'answer'})
        
        assert 'ANSWER' in env and 'ANSWERALIAS' not in env



class UnknownVariablesTestCase(unittest.TestCase):

    def test_unknown(self):
        """Test the UnknownVariables() method"""
        opts = SCons.Variables.Variables()
        
        opts.Add('ANSWER',
                 'THE answer to THE question',
                 "42")

        args = {
            'ANSWER'    : 'answer',
            'UNKNOWN'   : 'unknown',
        }

        env = Environment()
        opts.Update(env, args)

        r = opts.UnknownVariables()
        assert r == {'UNKNOWN' : 'unknown'}, r
        assert env['ANSWER'] == 'answer', env['ANSWER']
        
    def test_AddOptionUpdatesUnknown(self):
        """Test updating of the 'unknown' dict"""
        opts = SCons.Variables.Variables()
        
        opts.Add('A',
                 'A test variable',
                 "1")
        
        args = {
            'A'             : 'a',
            'ADDEDLATER'    : 'notaddedyet',
        }
        
        env = Environment()
        opts.Update(env,args)
        
        r = opts.UnknownVariables()
        assert r == {'ADDEDLATER' : 'notaddedyet'}, r
        assert env['A'] == 'a', env['A']
        
        opts.Add('ADDEDLATER',
                 'An option not present initially',
                 "1")
                 
        args = {
            'A'             : 'a',
            'ADDEDLATER'    : 'added',
        }
        
        opts.Update(env, args)
        
        r = opts.UnknownVariables()
        assert len(r) == 0, r
        assert env['ADDEDLATER'] == 'added', env['ADDEDLATER']

    def test_AddOptionWithAliasUpdatesUnknown(self):
        """Test updating of the 'unknown' dict (with aliases)"""
        opts = SCons.Variables.Variables()
        
        opts.Add('A',
                 'A test variable',
                 "1")
        
        args = {
            'A'                 : 'a',
            'ADDEDLATERALIAS'   : 'notaddedyet',
        }
        
        env = Environment()
        opts.Update(env,args)
        
        r = opts.UnknownVariables()
        assert r == {'ADDEDLATERALIAS' : 'notaddedyet'}, r
        assert env['A'] == 'a', env['A']
        
        opts.AddVariables(
            (('ADDEDLATER', 'ADDEDLATERALIAS'),
             'An option not present initially',
             "1"),
            )
        
        args['ADDEDLATERALIAS'] = 'added'
        
        opts.Update(env, args)
        
        r = opts.UnknownVariables()
        assert len(r) == 0, r
        assert env['ADDEDLATER'] == 'added', env['ADDEDLATER']


if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
