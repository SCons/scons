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
from __future__ import print_function

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import SCons.compat

import os
import sys
import unittest

from collections import UserDict

import SCons.Errors

from SCons.Subst import *

class DummyNode(object):
    """Simple node work-alike."""
    def __init__(self, name):
        self.name = os.path.normpath(name)
    def __str__(self):
        return self.name
    def is_literal(self):
        return 1
    def rfile(self):
        return self
    def get_subst_proxy(self):
        return self

class DummyEnv(object):
    def __init__(self, dict={}):
        self.dict = dict

    def Dictionary(self, key = None):
        if not key:
            return self.dict
        return self.dict[key]

    def __getitem__(self, key):
        return self.dict[key]

    def get(self, key, default):
        return self.dict.get(key, default)

    def sig_dict(self):
        dict = self.dict.copy()
        dict["TARGETS"] = 'tsig'
        dict["SOURCES"] = 'ssig'
        return dict

def cs(target=None, source=None, env=None, for_signature=None):
    return 'cs'

def cl(target=None, source=None, env=None, for_signature=None):
    return ['cl']

def CmdGen1(target, source, env, for_signature):
    # Nifty trick...since Environment references are interpolated,
    # instantiate an instance of a callable class with this one,
    # which will then get evaluated.
    assert str(target) == 't', target
    assert str(source) == 's', source
    return "${CMDGEN2('foo', %d)}" % for_signature

class CmdGen2(object):
    def __init__(self, mystr, forsig):
        self.mystr = mystr
        self.expect_for_signature = forsig

    def __call__(self, target, source, env, for_signature):
        assert str(target) == 't', target
        assert str(source) == 's', source
        assert for_signature == self.expect_for_signature, for_signature
        return [ self.mystr, env.Dictionary('BAR') ]

if os.sep == '/':
    def cvt(str):
        return str
else:
    def cvt(str):
        return str.replace('/', os.sep)

class SubstTestCase(unittest.TestCase):
    class MyNode(DummyNode):
        """Simple node work-alike with some extra stuff for testing."""
        def __init__(self, name):
            DummyNode.__init__(self, name)
            class Attribute(object):
                pass
            self.attribute = Attribute()
            self.attribute.attr1 = 'attr$1-' + os.path.basename(name)
            self.attribute.attr2 = 'attr$2-' + os.path.basename(name)
        def get_stuff(self, extra):
            return self.name + extra
        foo = 1

    class TestLiteral(object):
        def __init__(self, literal):
            self.literal = literal
        def __str__(self):
            return self.literal
        def is_literal(self):
            return 1

    class TestCallable(object):
        def __init__(self, value):
            self.value = value
        def __call__(self):
            pass
        def __str__(self):
            return self.value

    def function_foo(arg):
        pass

    target = [ MyNode("./foo/bar.exe"),
               MyNode("/bar/baz with spaces.obj"),
               MyNode("../foo/baz.obj") ]
    source = [ MyNode("./foo/blah with spaces.cpp"),
               MyNode("/bar/ack.cpp"),
               MyNode("../foo/ack.c") ]

    callable_object_1 = TestCallable('callable-1')
    callable_object_2 = TestCallable('callable-2')

    def _defines(defs):
        l = []
        for d in defs:
            if SCons.Util.is_List(d) or isinstance(d, tuple):
                l.append(str(d[0]) + '=' + str(d[1]))
            else:
                l.append(str(d))
        return l

    loc = {
        'xxx'       : None,
        'NEWLINE'   : 'before\nafter',

        'null'      : '',
        'zero'      : 0,
        'one'       : 1,
        'BAZ'       : 'baz',
        'ONE'       : '$TWO',
        'TWO'       : '$THREE',
        'THREE'     : 'four',

        'AAA'       : 'a',
        'BBB'       : 'b',
        'CCC'       : 'c',

        'DO'        : DummyNode('do something'),
        'FOO'       : DummyNode('foo.in'),
        'BAR'       : DummyNode('bar with spaces.out'),
        'CRAZY'     : DummyNode('crazy\nfile.in'),

        # $XXX$HHH should expand to GGGIII, not BADNEWS.
        'XXX'       : '$FFF',
        'FFF'       : 'GGG',
        'HHH'       : 'III',
        'FFFIII'    : 'BADNEWS',

        'THING1'    : "$(STUFF$)",
        'THING2'    : "$THING1",

        'LITERAL'   : TestLiteral("$XXX"),

        # Test that we can expand to and return a function.
        #'FUNCTION'  : function_foo,

        'CMDGEN1'   : CmdGen1,
        'CMDGEN2'   : CmdGen2,

        'LITERALS'  : [ Literal('foo\nwith\nnewlines'),
                        Literal('bar\nwith\nnewlines') ],

        'NOTHING'   : "",
        'NONE'      : None,

        # Test various combinations of strings, lists and functions.
        'N'         : None,
        'X'         : 'x',
        'Y'         : '$X',
        'R'         : '$R',
        'S'         : 'x y',
        'LS'        : ['x y'],
        'L'         : ['x', 'y'],
        'TS'        : ('x y'),
        'T'         : ('x', 'y'),
        'CS'        : cs,
        'CL'        : cl,
        'US'        : collections.UserString('us'),

        # Test function calls within ${}.
        'FUNCCALL'  : '${FUNC1("$AAA $FUNC2 $BBB")}',
        'FUNC1'     : lambda x: x,
        'FUNC2'     : lambda target, source, env, for_signature: ['x$CCC'],

        # Various tests refactored from ActionTests.py.
        'LIST'      : [["This", "is", "$(", "$a", "$)", "test"]],

        # Test recursion.
        'RECURSE'   : 'foo $RECURSE bar',
        'RRR'       : 'foo $SSS bar',
        'SSS'       : '$RRR',

        # Test callables that don't match the calling arguments.
        'CALLABLE1' : callable_object_1,
        'CALLABLE2' : callable_object_2,

        '_defines'  : _defines,
        'DEFS'      : [ ('Q1', '"q1"'), ('Q2', '"$AAA"') ],
    }

    def basic_comparisons(self, function, convert):
        env = DummyEnv(self.loc)
        cases = self.basic_cases[:]
        kwargs = {'target' : self.target, 'source' : self.source,
                  'gvars' : env.Dictionary()}

        failed = 0
        while cases:
            input, expect = cases[:2]
            expect = convert(expect)
            try:
                result = function(input, env, **kwargs)
            except Exception as e:
                fmt = "    input %s generated %s (%s)"
                print(fmt % (repr(input), e.__class__.__name__, repr(e)))
                failed = failed + 1
            else:
                if result != expect:
                    if failed == 0: print()
                    print("    input %s => \n%s did not match \n%s" % (repr(input), repr(result), repr(expect)))
                    failed = failed + 1
            del cases[:2]
        fmt = "%d %s() cases failed"
        assert failed == 0, fmt % (failed, function.__name__)

class scons_subst_TestCase(SubstTestCase):

    # Basic tests of substitution functionality.
    basic_cases = [
        # Basics:  strings without expansions are left alone, and
        # the simplest possible expansion to a null-string value.
        "test",                 "test",
        "$null",                "",

        # Test expansion of integer values.
        "test $zero",           "test 0",
        "test $one",            "test 1",

        # Test multiple re-expansion of values.
        "test $ONE",            "test four",

        # Test a whole bunch of $TARGET[S] and $SOURCE[S] expansions.
        "test $TARGETS $SOURCES",
        "test foo/bar.exe /bar/baz with spaces.obj ../foo/baz.obj foo/blah with spaces.cpp /bar/ack.cpp ../foo/ack.c",

        "test ${TARGETS[:]} ${SOURCES[0]}",
        "test foo/bar.exe /bar/baz with spaces.obj ../foo/baz.obj foo/blah with spaces.cpp",

        "test ${TARGETS[1:]}v",
        "test /bar/baz with spaces.obj ../foo/baz.objv",

        "test $TARGET",
        "test foo/bar.exe",

        "test $TARGET$NO_SUCH_VAR[0]",
        "test foo/bar.exe[0]",

        "test $TARGETS.foo",
        "test 1 1 1",

        "test ${SOURCES[0:2].foo}",
        "test 1 1",

        "test $SOURCE.foo",
        "test 1",

        "test ${TARGET.get_stuff('blah')}",
        "test foo/bar.exeblah",

        "test ${SOURCES.get_stuff('blah')}",
        "test foo/blah with spaces.cppblah /bar/ack.cppblah ../foo/ack.cblah",

        "test ${SOURCES[0:2].get_stuff('blah')}",
        "test foo/blah with spaces.cppblah /bar/ack.cppblah",

        "test ${SOURCES[0:2].get_stuff('blah')}",
        "test foo/blah with spaces.cppblah /bar/ack.cppblah",

        "test ${SOURCES.attribute.attr1}",
        "test attr$1-blah with spaces.cpp attr$1-ack.cpp attr$1-ack.c",

        "test ${SOURCES.attribute.attr2}",
        "test attr$2-blah with spaces.cpp attr$2-ack.cpp attr$2-ack.c",

        # Test adjacent expansions.
        "foo$BAZ",
        "foobaz",

        "foo${BAZ}",
        "foobaz",

        # Test that adjacent expansions don't get re-interpreted
        # together.  The correct disambiguated expansion should be:
        #   $XXX$HHH => ${FFF}III => GGGIII
        # not:
        #   $XXX$HHH => ${FFFIII} => BADNEWS
        "$XXX$HHH",             "GGGIII",

        # Test double-dollar-sign behavior.
        "$$FFF$HHH",            "$FFFIII",

        # Test double-dollar-sign before open paren. It's not meant
        # to be signature escaping
        'echo $$(pwd) > XYZ',   'echo $(pwd) > XYZ',

        # Test that a Literal will stop dollar-sign substitution.
        "$XXX $LITERAL $FFF",   "GGG $XXX GGG",

        # Test that we don't blow up even if they subscript
        # something in ways they "can't."
        "${FFF[0]}",            "G",
        "${FFF[7]}",            "",
        "${NOTHING[1]}",        "",

        # Test various combinations of strings and lists.
        #None,                   '',
        '',                     '',
        'x',                    'x',
        'x y',                  'x y',
        '$N',                   '',
        '$X',                   'x',
        '$Y',                   'x',
        '$R',                   '',
        '$S',                   'x y',
        '$LS',                  'x y',
        '$L',                   'x y',
        '$TS',                  'x y',
        '$T',                   'x y',
        '$S z',                 'x y z',
        '$LS z',                'x y z',
        '$L z',                 'x y z',
        '$TS z',                'x y z',
        '$T z',                 'x y z',
        #cs,                     'cs',
        #cl,                     'cl',
        '$CS',                  'cs',
        '$CL',                  'cl',

        # Various uses of UserString.
        collections.UserString('x'),         'x',
        collections.UserString('$X'),        'x',
        collections.UserString('$US'),       'us',
        '$US',                              'us',

        # Test function calls within ${}.
        '$FUNCCALL',            'a xc b',

        # Bug reported by Christoph Wiedemann.
        cvt('$xxx/bin'),        '/bin',

        # Tests callables that don't match our calling arguments.
        '$CALLABLE1',            'callable-1',

        # Test handling of quotes.
        'aaa "bbb ccc" ddd',    'aaa "bbb ccc" ddd',
    ]

    def test_scons_subst(self):
        """Test scons_subst():  basic substitution"""
        return self.basic_comparisons(scons_subst, cvt)

    subst_cases = [
        "test $xxx",
            "test ",
            "test",
            "test",

        "test $($xxx$)",
            "test $($)",
            "test",
            "test",

        "test $( $xxx $)",
            "test $(  $)",
            "test",
            "test",

        "test $( $THING2 $)",
            "test $( $(STUFF$) $)",
            "test STUFF",
            "test",

        "$AAA ${AAA}A $BBBB $BBB",
            "a aA  b",
            "a aA b",
            "a aA b",

        "$RECURSE",
           "foo  bar",
           "foo bar",
           "foo bar",

        "$RRR",
           "foo  bar",
           "foo bar",
           "foo bar",

        # Verify what happens with no target or source nodes.
        "$TARGET $SOURCES",
            " ",
            "",
            "",

        "$TARGETS $SOURCE",
            " ",
            "",
            "",

        # Various tests refactored from ActionTests.py.
        "${LIST}",
           "This is $(  $) test",
           "This is test",
           "This is test",

        ["|", "$(", "$AAA", "|", "$BBB", "$)", "|", "$CCC", 1],
            ["|", "$(", "a", "|", "b", "$)", "|", "c", "1"],
            ["|", "a", "|", "b", "|", "c", "1"],
            ["|", "|", "c", "1"],
    ]

    def test_subst_env(self):
        """Test scons_subst():  expansion dictionary"""
        # The expansion dictionary no longer comes from the construction
        # environment automatically.
        env = DummyEnv(self.loc)
        s = scons_subst('$AAA', env)
        assert s == '', s

    def test_subst_SUBST_modes(self):
        """Test scons_subst():  SUBST_* modes"""
        env = DummyEnv(self.loc)
        subst_cases = self.subst_cases[:]

        gvars = env.Dictionary()

        failed = 0
        while subst_cases:
            input, eraw, ecmd, esig = subst_cases[:4]
            result = scons_subst(input, env, mode=SUBST_RAW, gvars=gvars)
            if result != eraw:
                if failed == 0: print()
                print("    input %s => RAW %s did not match %s" % (repr(input), repr(result), repr(eraw)))
                failed = failed + 1
            result = scons_subst(input, env, mode=SUBST_CMD, gvars=gvars)
            if result != ecmd:
                if failed == 0: print()
                print("    input %s => CMD %s did not match %s" % (repr(input), repr(result), repr(ecmd)))
                failed = failed + 1
            result = scons_subst(input, env, mode=SUBST_SIG, gvars=gvars)
            if result != esig:
                if failed == 0: print()
                print("    input %s => SIG %s did not match %s" % (repr(input), repr(result), repr(esig)))
                failed = failed + 1
            del subst_cases[:4]
        assert failed == 0, "%d subst() mode cases failed" % failed

    def test_subst_target_source(self):
        """Test scons_subst():  target= and source= arguments"""
        env = DummyEnv(self.loc)
        t1 = self.MyNode('t1')
        t2 = self.MyNode('t2')
        s1 = self.MyNode('s1')
        s2 = self.MyNode('s2')
        result = scons_subst("$TARGET $SOURCES", env,
                                  target=[t1, t2],
                                  source=[s1, s2])
        assert result == "t1 s1 s2", result
        result = scons_subst("$TARGET $SOURCES", env,
                                  target=[t1, t2],
                                  source=[s1, s2],
                                  gvars={})
        assert result == "t1 s1 s2", result

        result = scons_subst("$TARGET $SOURCES", env, target=[], source=[])
        assert result == " ", result
        result = scons_subst("$TARGETS $SOURCE", env, target=[], source=[])
        assert result == " ", result

    def test_subst_callable_expansion(self):
        """Test scons_subst():  expanding a callable"""
        env = DummyEnv(self.loc)
        gvars = env.Dictionary()
        newcom = scons_subst("test $CMDGEN1 $SOURCES $TARGETS", env,
                             target=self.MyNode('t'), source=self.MyNode('s'),
                             gvars=gvars)
        assert newcom == "test foo bar with spaces.out s t", newcom

    def test_subst_attribute_errors(self):
        """Test scons_subst():  handling attribute errors"""
        env = DummyEnv(self.loc)
        try:
            class Foo(object):
                pass
            scons_subst('${foo.bar}', env, gvars={'foo':Foo()})
        except SCons.Errors.UserError as e:
            expect = [
                "AttributeError `bar' trying to evaluate `${foo.bar}'",
                "AttributeError `Foo instance has no attribute 'bar'' trying to evaluate `${foo.bar}'",
                "AttributeError `'Foo' instance has no attribute 'bar'' trying to evaluate `${foo.bar}'",
                "AttributeError `'Foo' object has no attribute 'bar'' trying to evaluate `${foo.bar}'",
            ]
            assert str(e) in expect, e
        else:
            raise AssertionError("did not catch expected UserError")

    def test_subst_syntax_errors(self):
        """Test scons_subst():  handling syntax errors"""
        env = DummyEnv(self.loc)
        try:
            scons_subst('$foo.bar.3.0', env)
        except SCons.Errors.UserError as e:
            expect = [
                # Python 2.3, 2.4
                "SyntaxError `invalid syntax (line 1)' trying to evaluate `$foo.bar.3.0'",
                # Python 2.5
                "SyntaxError `invalid syntax (<string>, line 1)' trying to evaluate `$foo.bar.3.0'",
            ]
            assert str(e) in expect, e
        else:
            raise AssertionError("did not catch expected UserError")

    def test_subst_balance_errors(self):
        """Test scons_subst():  handling syntax errors"""
        env = DummyEnv(self.loc)
        try:
            scons_subst('$(', env, mode=SUBST_SIG)
        except SCons.Errors.UserError as e:
            assert str(e) == "Unbalanced $(/$) in: $(", str(e)
        else:
            raise AssertionError("did not catch expected UserError")

        try:
            scons_subst('$)', env, mode=SUBST_SIG)
        except SCons.Errors.UserError as e:
            assert str(e) == "Unbalanced $(/$) in: $)", str(e)
        else:
            raise AssertionError("did not catch expected UserError")

    def test_subst_type_errors(self):
        """Test scons_subst():  handling type errors"""
        env = DummyEnv(self.loc)
        try:
            scons_subst("${NONE[2]}", env, gvars={'NONE':None})
        except SCons.Errors.UserError as e:
            expect = [
                # Python 2.3, 2.4
                "TypeError `unsubscriptable object' trying to evaluate `${NONE[2]}'",
                # Python 2.5, 2.6
                "TypeError `'NoneType' object is unsubscriptable' trying to evaluate `${NONE[2]}'",
                # Python 2.7 and later
                "TypeError `'NoneType' object is not subscriptable' trying to evaluate `${NONE[2]}'",
                # Python 2.7 and later under Fedora
                "TypeError `'NoneType' object has no attribute '__getitem__'' trying to evaluate `${NONE[2]}'",
            ]
            assert str(e) in expect, e
        else:
            raise AssertionError("did not catch expected UserError")

        try:
            def func(a, b, c):
                pass
            scons_subst("${func(1)}", env, gvars={'func':func})
        except SCons.Errors.UserError as e:
            expect = [
                # Python 2.3, 2.4, 2.5
                "TypeError `func() takes exactly 3 arguments (1 given)' trying to evaluate `${func(1)}'",

                # Python 3.5 (and 3.x?)
                "TypeError `func() missing 2 required positional arguments: 'b' and 'c'' trying to evaluate `${func(1)}'"
            ]
            assert str(e) in expect, repr(str(e))
        else:
            raise AssertionError("did not catch expected UserError")

    def test_subst_raw_function(self):
        """Test scons_subst():  fetch function with SUBST_RAW plus conv"""
        # Test that the combination of SUBST_RAW plus a pass-through
        # conversion routine allows us to fetch a function through the
        # dictionary.  CommandAction uses this to allow delayed evaluation
        # of $SPAWN variables.
        env = DummyEnv(self.loc)
        gvars = env.Dictionary()
        x = lambda x: x
        r = scons_subst("$CALLABLE1", env, mode=SUBST_RAW, conv=x, gvars=gvars)
        assert r is self.callable_object_1, repr(r)
        r = scons_subst("$CALLABLE1", env, mode=SUBST_RAW, gvars=gvars)
        assert r == 'callable-1', repr(r)

        # Test how we handle overriding the internal conversion routines.
        def s(obj):
            return obj

        n1 = self.MyNode('n1')
        env = DummyEnv({'NODE' : n1})
        gvars = env.Dictionary()
        node = scons_subst("$NODE", env, mode=SUBST_RAW, conv=s, gvars=gvars)
        assert node is n1, node
        node = scons_subst("$NODE", env, mode=SUBST_CMD, conv=s, gvars=gvars)
        assert node is n1, node
        node = scons_subst("$NODE", env, mode=SUBST_SIG, conv=s, gvars=gvars)
        assert node is n1, node

    def test_subst_overriding_gvars(self):
        """Test scons_subst():  supplying an overriding gvars dictionary"""
        env = DummyEnv({'XXX' : 'xxx'})
        result = scons_subst('$XXX', env, gvars=env.Dictionary())
        assert result == 'xxx', result
        result = scons_subst('$XXX', env, gvars={'XXX' : 'yyy'})
        assert result == 'yyy', result

class CLVar_TestCase(unittest.TestCase):
    def test_CLVar(self):
        """Test scons_subst() and scons_subst_list() with CLVar objects"""

        loc = {}
        loc['FOO'] = 'foo'
        loc['BAR'] = SCons.Util.CLVar('bar')
        loc['CALL'] = lambda target, source, env, for_signature: 'call'
        env = DummyEnv(loc)

        cmd = SCons.Util.CLVar("test $FOO $BAR $CALL test")

        newcmd = scons_subst(cmd, env, gvars=env.Dictionary())
        assert newcmd == ['test', 'foo', 'bar', 'call', 'test'], newcmd

        cmd_list = scons_subst_list(cmd, env, gvars=env.Dictionary())
        assert len(cmd_list) == 1, cmd_list
        assert cmd_list[0][0] == "test", cmd_list[0][0]
        assert cmd_list[0][1] == "foo", cmd_list[0][1]
        assert cmd_list[0][2] == "bar", cmd_list[0][2]
        assert cmd_list[0][3] == "call", cmd_list[0][3]
        assert cmd_list[0][4] == "test", cmd_list[0][4]

class scons_subst_list_TestCase(SubstTestCase):

    basic_cases = [
        "$TARGETS",
        [
            ["foo/bar.exe", "/bar/baz with spaces.obj", "../foo/baz.obj"],
        ],

        "$SOURCES $NEWLINE $TARGETS",
        [
            ["foo/blah with spaces.cpp", "/bar/ack.cpp", "../foo/ack.c", "before"],
            ["after", "foo/bar.exe", "/bar/baz with spaces.obj", "../foo/baz.obj"],
        ],

        "$SOURCES$NEWLINE",
        [
            ["foo/blah with spaces.cpp", "/bar/ack.cpp", "../foo/ack.cbefore"],
            ["after"],
        ],

        "foo$FFF",
        [
            ["fooGGG"],
        ],

        "foo${FFF}",
        [
            ["fooGGG"],
        ],

        "test ${SOURCES.attribute.attr1}",
        [
            ["test", "attr$1-blah with spaces.cpp", "attr$1-ack.cpp", "attr$1-ack.c"],
        ],

        "test ${SOURCES.attribute.attr2}",
        [
            ["test", "attr$2-blah with spaces.cpp", "attr$2-ack.cpp", "attr$2-ack.c"],
        ],

        "$DO --in=$FOO --out=$BAR",
        [
            ["do something", "--in=foo.in", "--out=bar with spaces.out"],
        ],

        # This test is now fixed, and works like it should.
        "$DO --in=$CRAZY --out=$BAR",
        [
            ["do something", "--in=crazy\nfile.in", "--out=bar with spaces.out"],
        ],

        # Try passing a list to scons_subst_list().
        [ "$SOURCES$NEWLINE", "$TARGETS", "This is a test"],
        [
            ["foo/blah with spaces.cpp", "/bar/ack.cpp", "../foo/ack.cbefore"],
            ["after", "foo/bar.exe", "/bar/baz with spaces.obj", "../foo/baz.obj", "This is a test"],
        ],

        # Test against a former bug in scons_subst_list().
        "$XXX$HHH",
        [
            ["GGGIII"],
        ],

        # Test double-dollar-sign behavior.
        "$$FFF$HHH",
        [
            ["$FFFIII"],
        ],

        # Test various combinations of strings, lists and functions.
        None,                   [[]],
        [None],                 [[]],
        '',                     [[]],
        [''],                   [[]],
        'x',                    [['x']],
        ['x'],                  [['x']],
        'x y',                  [['x', 'y']],
        ['x y'],                [['x y']],
        ['x', 'y'],             [['x', 'y']],
        '$N',                   [[]],
        ['$N'],                 [[]],
        '$X',                   [['x']],
        ['$X'],                 [['x']],
        '$Y',                   [['x']],
        ['$Y'],                 [['x']],
        #'$R',                   [[]],
        #['$R'],                 [[]],
        '$S',                   [['x', 'y']],
        '$S z',                 [['x', 'y', 'z']],
        ['$S'],                 [['x', 'y']],
        ['$S z'],               [['x', 'y z']],     # XXX - IS THIS BEST?
        ['$S', 'z'],            [['x', 'y', 'z']],
        '$LS',                  [['x y']],
        '$LS z',                [['x y', 'z']],
        ['$LS'],                [['x y']],
        ['$LS z'],              [['x y z']],
        ['$LS', 'z'],           [['x y', 'z']],
        '$L',                   [['x', 'y']],
        '$L z',                 [['x', 'y', 'z']],
        ['$L'],                 [['x', 'y']],
        ['$L z'],               [['x', 'y z']],     # XXX - IS THIS BEST?
        ['$L', 'z'],            [['x', 'y', 'z']],
        cs,                     [['cs']],
        [cs],                   [['cs']],
        cl,                     [['cl']],
        [cl],                   [['cl']],
        '$CS',                  [['cs']],
        ['$CS'],                [['cs']],
        '$CL',                  [['cl']],
        ['$CL'],                [['cl']],

        # Various uses of UserString.
        collections.UserString('x'),         [['x']],
        [collections.UserString('x')],       [['x']],
        collections.UserString('$X'),        [['x']],
        [collections.UserString('$X')],      [['x']],
        collections.UserString('$US'),       [['us']],
        [collections.UserString('$US')],     [['us']],
        '$US',                              [['us']],
        ['$US'],                            [['us']],

        # Test function calls within ${}.
        '$FUNCCALL',            [['a', 'xc', 'b']],

        # Test handling of newlines in white space.
        'foo\nbar',             [['foo'], ['bar']],
        'foo\n\nbar',           [['foo'], ['bar']],
        'foo \n \n bar',        [['foo'], ['bar']],
        'foo \nmiddle\n bar',   [['foo'], ['middle'], ['bar']],

        # Bug reported by Christoph Wiedemann.
        cvt('$xxx/bin'),        [['/bin']],

        # Test variables smooshed together with different prefixes.
        'foo$AAA',              [['fooa']],
        '<$AAA',                [['<', 'a']],
        '>$AAA',                [['>', 'a']],
        '|$AAA',                [['|', 'a']],

        # Test callables that don't match our calling arguments.
        '$CALLABLE2',            [['callable-2']],

        # Test handling of quotes.
        # XXX Find a way to handle this in the future.
        #'aaa "bbb ccc" ddd',    [['aaa', 'bbb ccc', 'ddd']],

        '${_defines(DEFS)}',     [['Q1="q1"', 'Q2="a"']],
    ]

    def test_scons_subst_list(self):
        """Test scons_subst_list():  basic substitution"""
        def convert_lists(expect):
            return [list(map(cvt, l)) for l in expect]
        return self.basic_comparisons(scons_subst_list, convert_lists)

    subst_list_cases = [
        "test $xxx",
            [["test"]],
            [["test"]],
            [["test"]],

        "test $($xxx$)",
            [["test", "$($)"]],
            [["test"]],
            [["test"]],

        "test $( $xxx $)",
            [["test", "$(", "$)"]],
            [["test"]],
            [["test"]],

        "$AAA ${AAA}A $BBBB $BBB",
            [["a", "aA", "b"]],
            [["a", "aA", "b"]],
            [["a", "aA", "b"]],

        "$RECURSE",
            [["foo", "bar"]],
            [["foo", "bar"]],
            [["foo", "bar"]],

        "$RRR",
            [["foo", "bar"]],
            [["foo", "bar"]],
            [["foo", "bar"]],

        # Verify what happens with no target or source nodes.
        "$TARGET $SOURCES",
            [[]],
            [[]],
            [[]],

        "$TARGETS $SOURCE",
            [[]],
            [[]],
            [[]],

        # Various test refactored from ActionTests.py
        "${LIST}",
            [['This', 'is', '$(', '$)', 'test']],
            [['This', 'is', 'test']],
            [['This', 'is', 'test']],

        ["|", "$(", "$AAA", "|", "$BBB", "$)", "|", "$CCC", 1],
            [["|", "$(", "a", "|", "b", "$)", "|", "c", "1"]],
            [["|", "a", "|", "b", "|", "c", "1"]],
            [["|", "|", "c", "1"]],
    ]

    def test_subst_env(self):
        """Test scons_subst_list():  expansion dictionary"""
        # The expansion dictionary no longer comes from the construction
        # environment automatically.
        env = DummyEnv()
        s = scons_subst_list('$AAA', env)
        assert s == [[]], s

    def test_subst_target_source(self):
        """Test scons_subst_list():  target= and source= arguments"""
        env = DummyEnv(self.loc)
        gvars = env.Dictionary()
        t1 = self.MyNode('t1')
        t2 = self.MyNode('t2')
        s1 = self.MyNode('s1')
        s2 = self.MyNode('s2')
        result = scons_subst_list("$TARGET $SOURCES", env,
                                  target=[t1, t2],
                                  source=[s1, s2],
                                  gvars=gvars)
        assert result == [['t1', 's1', 's2']], result
        result = scons_subst_list("$TARGET $SOURCES", env,
                                  target=[t1, t2],
                                  source=[s1, s2],
                                  gvars={})
        assert result == [['t1', 's1', 's2']], result

        # Test interpolating a callable.
        _t = DummyNode('t')
        _s = DummyNode('s')
        cmd_list = scons_subst_list("testing $CMDGEN1 $TARGETS $SOURCES",
                                    env, target=_t, source=_s,
                                    gvars=gvars)
        assert cmd_list == [['testing', 'foo', 'bar with spaces.out', 't', 's']], cmd_list

    def test_subst_escape(self):
        """Test scons_subst_list():  escape functionality"""
        env = DummyEnv(self.loc)
        gvars = env.Dictionary()
        def escape_func(foo):
            return '**' + foo + '**'
        cmd_list = scons_subst_list("abc $LITERALS xyz", env, gvars=gvars)
        assert cmd_list == [['abc',
                             'foo\nwith\nnewlines',
                             'bar\nwith\nnewlines',
                             'xyz']], cmd_list
        c = cmd_list[0][0].escape(escape_func)
        assert c == 'abc', c
        c = cmd_list[0][1].escape(escape_func)
        assert c == '**foo\nwith\nnewlines**', c
        c = cmd_list[0][2].escape(escape_func)
        assert c == '**bar\nwith\nnewlines**', c
        c = cmd_list[0][3].escape(escape_func)
        assert c == 'xyz', c

        # We used to treat literals smooshed together like the whole
        # thing was literal and escape it as a unit.  The commented-out
        # asserts below are in case we ever have to find a way to
        # resurrect that functionality in some way.
        cmd_list = scons_subst_list("abc${LITERALS}xyz", env, gvars=gvars)
        c = cmd_list[0][0].escape(escape_func)
        #assert c == '**abcfoo\nwith\nnewlines**', c
        assert c == 'abcfoo\nwith\nnewlines', c
        c = cmd_list[0][1].escape(escape_func)
        #assert c == '**bar\nwith\nnewlinesxyz**', c
        assert c == 'bar\nwith\nnewlinesxyz', c

        _t = DummyNode('t')

        cmd_list = scons_subst_list('echo "target: $TARGET"', env,
                                    target=_t, gvars=gvars)
        c = cmd_list[0][0].escape(escape_func)
        assert c == 'echo', c
        c = cmd_list[0][1].escape(escape_func)
        assert c == '"target:', c
        c = cmd_list[0][2].escape(escape_func)
        assert c == 't"', c

    def test_subst_SUBST_modes(self):
        """Test scons_subst_list():  SUBST_* modes"""
        env = DummyEnv(self.loc)
        subst_list_cases = self.subst_list_cases[:]
        gvars = env.Dictionary()

        r = scons_subst_list("$TARGET $SOURCES", env, mode=SUBST_RAW, gvars=gvars)
        assert r == [[]], r

        failed = 0
        while subst_list_cases:
            input, eraw, ecmd, esig = subst_list_cases[:4]
            result = scons_subst_list(input, env, mode=SUBST_RAW, gvars=gvars)
            if result != eraw:
                if failed == 0: print()
                print("    input %s => RAW %s did not match %s" % (repr(input), repr(result), repr(eraw)))
                failed = failed + 1
            result = scons_subst_list(input, env, mode=SUBST_CMD, gvars=gvars)
            if result != ecmd:
                if failed == 0: print()
                print("    input %s => CMD %s did not match %s" % (repr(input), repr(result), repr(ecmd)))
                failed = failed + 1
            result = scons_subst_list(input, env, mode=SUBST_SIG, gvars=gvars)
            if result != esig:
                if failed == 0: print()
                print("    input %s => SIG %s did not match %s" % (repr(input), repr(result), repr(esig)))
                failed = failed + 1
            del subst_list_cases[:4]
        assert failed == 0, "%d subst() mode cases failed" % failed

    def test_subst_attribute_errors(self):
        """Test scons_subst_list():  handling attribute errors"""
        env = DummyEnv()
        try:
            class Foo(object):
                pass
            scons_subst_list('${foo.bar}', env, gvars={'foo':Foo()})
        except SCons.Errors.UserError as e:
            expect = [
                "AttributeError `bar' trying to evaluate `${foo.bar}'",
                "AttributeError `Foo instance has no attribute 'bar'' trying to evaluate `${foo.bar}'",
                "AttributeError `'Foo' instance has no attribute 'bar'' trying to evaluate `${foo.bar}'",
                "AttributeError `'Foo' object has no attribute 'bar'' trying to evaluate `${foo.bar}'",
            ]
            assert str(e) in expect, e
        else:
            raise AssertionError("did not catch expected UserError")

    def test_subst_syntax_errors(self):
        """Test scons_subst_list():  handling syntax errors"""
        env = DummyEnv()
        try:
            scons_subst_list('$foo.bar.3.0', env)
        except SCons.Errors.UserError as e:
            expect = [
                "SyntaxError `invalid syntax' trying to evaluate `$foo.bar.3.0'",
                "SyntaxError `invalid syntax (line 1)' trying to evaluate `$foo.bar.3.0'",
                "SyntaxError `invalid syntax (<string>, line 1)' trying to evaluate `$foo.bar.3.0'",
            ]
            assert str(e) in expect, e
        else:
            raise AssertionError("did not catch expected SyntaxError")

    def test_subst_raw_function(self):
        """Test scons_subst_list():  fetch function with SUBST_RAW plus conv"""
        # Test that the combination of SUBST_RAW plus a pass-through
        # conversion routine allows us to fetch a function through the
        # dictionary.
        env = DummyEnv(self.loc)
        gvars = env.Dictionary()
        x = lambda x: x
        r = scons_subst_list("$CALLABLE2", env, mode=SUBST_RAW, conv=x, gvars=gvars)
        assert r == [[self.callable_object_2]], repr(r)
        r = scons_subst_list("$CALLABLE2", env, mode=SUBST_RAW, gvars=gvars)
        assert r == [['callable-2']], repr(r)

    def test_subst_list_overriding_gvars(self):
        """Test scons_subst_list():  overriding conv()"""
        env = DummyEnv()
        def s(obj):
            return obj

        n1 = self.MyNode('n1')
        env = DummyEnv({'NODE' : n1})
        gvars=env.Dictionary()
        node = scons_subst_list("$NODE", env, mode=SUBST_RAW, conv=s, gvars=gvars)
        assert node == [[n1]], node
        node = scons_subst_list("$NODE", env, mode=SUBST_CMD, conv=s, gvars=gvars)
        assert node == [[n1]], node
        node = scons_subst_list("$NODE", env, mode=SUBST_SIG, conv=s, gvars=gvars)
        assert node == [[n1]], node

    def test_subst_list_overriding_gvars(self):
        """Test scons_subst_list():  supplying an overriding gvars dictionary"""
        env = DummyEnv({'XXX' : 'xxx'})
        result = scons_subst_list('$XXX', env, gvars=env.Dictionary())
        assert result == [['xxx']], result
        result = scons_subst_list('$XXX', env, gvars={'XXX' : 'yyy'})
        assert result == [['yyy']], result

class scons_subst_once_TestCase(unittest.TestCase):

    loc = {
        'CCFLAGS'           : '-DFOO',
        'ONE'               : 1,
        'RECURSE'           : 'r $RECURSE r',
        'LIST'              : ['a', 'b', 'c'],
    }

    basic_cases = [
        '$CCFLAGS -DBAR',
        'OTHER_KEY',
        '$CCFLAGS -DBAR',

        '$CCFLAGS -DBAR',
        'CCFLAGS',
        '-DFOO -DBAR',

        'x $ONE y',
        'ONE',
        'x 1 y',

        'x $RECURSE y',
        'RECURSE',
        'x r $RECURSE r y',

        '$LIST',
        'LIST',
        'a b c',

        ['$LIST'],
        'LIST',
        ['a', 'b', 'c'],

        ['x', '$LIST', 'y'],
        'LIST',
        ['x', 'a', 'b', 'c', 'y'],

        ['x', 'x $LIST y', 'y'],
        'LIST',
        ['x', 'x a b c y', 'y'],

        ['x', 'x $CCFLAGS y', 'y'],
        'LIST',
        ['x', 'x $CCFLAGS y', 'y'],

        ['x', 'x $RECURSE y', 'y'],
        'LIST',
        ['x', 'x $RECURSE y', 'y'],
    ]

    def test_subst_once(self):
        """Test the scons_subst_once() function"""
        env = DummyEnv(self.loc)
        cases = self.basic_cases[:]

        failed = 0
        while cases:
            input, key, expect = cases[:3]
            result = scons_subst_once(input, env, key)
            if result != expect:
                if failed == 0: print()
                print("    input %s (%s) => %s did not match %s" % (repr(input), repr(key), repr(result), repr(expect)))
                failed = failed + 1
            del cases[:3]
        assert failed == 0, "%d subst() cases failed" % failed

class quote_spaces_TestCase(unittest.TestCase):
    def test_quote_spaces(self):
        """Test the quote_spaces() method..."""
        q = quote_spaces('x')
        assert q == 'x', q

        q = quote_spaces('x x')
        assert q == '"x x"', q

        q = quote_spaces('x\tx')
        assert q == '"x\tx"', q

    class Node(object):
        def __init__(self, name, children=[]):
            self.children = children
            self.name = name
        def __str__(self):
            return self.name
        def exists(self):
            return 1
        def rexists(self):
            return 1
        def has_builder(self):
            return 1
        def has_explicit_builder(self):
            return 1
        def side_effect(self):
            return 1
        def precious(self):
            return 1
        def always_build(self):
            return 1
        def current(self):
            return 1

class LiteralTestCase(unittest.TestCase):
    def test_Literal(self):
        """Test the Literal() function."""
        input_list = [ '$FOO', Literal('$BAR') ]
        gvars = { 'FOO' : 'BAZ', 'BAR' : 'BLAT' }

        def escape_func(cmd):
            return '**' + cmd + '**'

        cmd_list = scons_subst_list(input_list, None, gvars=gvars)
        cmd_list = escape_list(cmd_list[0], escape_func)
        assert cmd_list == ['BAZ', '**$BAR**'], cmd_list

    def test_LiteralEqualsTest(self):
        """Test that Literals compare for equality properly"""
        assert Literal('a literal') == Literal('a literal')
        assert Literal('a literal') != Literal('b literal')

class SpecialAttrWrapperTestCase(unittest.TestCase):
    def test_SpecialAttrWrapper(self):
        """Test the SpecialAttrWrapper() function."""
        input_list = [ '$FOO', SpecialAttrWrapper('$BAR', 'BLEH') ]
        gvars = { 'FOO' : 'BAZ', 'BAR' : 'BLAT' }

        def escape_func(cmd):
            return '**' + cmd + '**'

        cmd_list = scons_subst_list(input_list, None, gvars=gvars)
        cmd_list = escape_list(cmd_list[0], escape_func)
        assert cmd_list == ['BAZ', '**$BAR**'], cmd_list

        cmd_list = scons_subst_list(input_list, None, mode=SUBST_SIG, gvars=gvars)
        cmd_list = escape_list(cmd_list[0], escape_func)
        assert cmd_list == ['BAZ', '**BLEH**'], cmd_list

class subst_dict_TestCase(unittest.TestCase):
    def test_subst_dict(self):
        """Test substituting dictionary values in an Action
        """
        t = DummyNode('t')
        s = DummyNode('s')
        d = subst_dict(target=t, source=s)
        assert str(d['TARGETS'][0]) == 't', d['TARGETS']
        assert str(d['TARGET']) == 't', d['TARGET']
        assert str(d['SOURCES'][0]) == 's', d['SOURCES']
        assert str(d['SOURCE']) == 's', d['SOURCE']

        t1 = DummyNode('t1')
        t2 = DummyNode('t2')
        s1 = DummyNode('s1')
        s2 = DummyNode('s2')
        d = subst_dict(target=[t1, t2], source=[s1, s2])
        TARGETS = sorted([str(x) for x in d['TARGETS']])
        assert TARGETS == ['t1', 't2'], d['TARGETS']
        assert str(d['TARGET']) == 't1', d['TARGET']
        SOURCES = sorted([str(x) for x in d['SOURCES']])
        assert SOURCES == ['s1', 's2'], d['SOURCES']
        assert str(d['SOURCE']) == 's1', d['SOURCE']

        class V(object):
            # Fake Value node with no rfile() method.
            def __init__(self, name):
                self.name = name
            def __str__(self):
                return 'v-'+self.name
            def get_subst_proxy(self):
                return self

        class N(V):
            def rfile(self):
                return self.__class__('rstr-' + self.name)

        t3 = N('t3')
        t4 = DummyNode('t4')
        t5 = V('t5')
        s3 = DummyNode('s3')
        s4 = N('s4')
        s5 = V('s5')
        d = subst_dict(target=[t3, t4, t5], source=[s3, s4, s5])
        TARGETS = sorted([str(x) for x in d['TARGETS']])
        assert TARGETS == ['t4', 'v-t3', 'v-t5'], TARGETS
        SOURCES = sorted([str(x) for x in d['SOURCES']])
        assert SOURCES == ['s3', 'v-rstr-s4', 'v-s5'], SOURCES

if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
