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

import os
import os.path
import string
import sys
import types
import unittest
from SCons.Util import *
import TestCmd

import SCons.Errors

class OutBuffer:
    def __init__(self):
        self.buffer = ""

    def write(self, str):
        self.buffer = self.buffer + str

class DummyNode:
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

class DummyEnv:
    def __init__(self, dict={}):
        self.dict = dict

    def Dictionary(self, key = None):
        if not key:
            return self.dict
        return self.dict[key]

    def __getitem__(self, key):
        return self.dict[key]

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

class CmdGen2:
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
        return string.replace(str, '/', os.sep)

class UtilTestCase(unittest.TestCase):
    def test_subst(self):
        """Test the subst() function"""
        class MyNode(DummyNode):
            """Simple node work-alike with some extra stuff for testing."""
            def __init__(self, name):
                DummyNode.__init__(self, name)
                class Attribute:
                    pass
                self.attribute = Attribute()
                self.attribute.attr1 = 'attr$1-' + os.path.basename(name)
                self.attribute.attr2 = 'attr$2-' + os.path.basename(name)
            def get_stuff(self, extra):
                return self.name + extra
            foo = 1

        class TestLiteral:
            def __init__(self, literal):
                self.literal = literal
            def __str__(self):
                return self.literal
            def is_literal(self):
                return 1

        def function_foo(arg):
            pass

        target = [ MyNode("./foo/bar.exe"),
                   MyNode("/bar/baz.obj"),
                   MyNode("../foo/baz.obj") ]
        source = [ MyNode("./foo/blah.cpp"),
                   MyNode("/bar/ack.cpp"),
                   MyNode("../foo/ack.c") ]

        loc = {
            'xxx'       : None,
            'null'      : '',
            'zero'      : 0,
            'one'       : 1,
            'BAR'       : 'baz',
            'ONE'       : '$TWO',
            'TWO'       : '$THREE',
            'THREE'     : 'four',

            'AAA'       : 'a',
            'BBB'       : 'b',
            'CCC'       : 'c',

            # $XXX$HHH should expand to GGGIII, not BADNEWS.
            'XXX'       : '$FFF',
            'FFF'       : 'GGG',
            'HHH'       : 'III',
            'FFFIII'    : 'BADNEWS',

            'LITERAL'   : TestLiteral("$XXX"),

            # Test that we can expand to and return a function.
            #'FUNCTION'  : function_foo,

            'CMDGEN1'   : CmdGen1,
            'CMDGEN2'   : CmdGen2,

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
            'CS'        : cs,
            'CL'        : cl,

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
        }

        env = DummyEnv(loc)

        # Basic tests of substitution functionality.
        cases = [
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
            "test foo/bar.exe /bar/baz.obj ../foo/baz.obj foo/blah.cpp /bar/ack.cpp ../foo/ack.c",

            "test ${TARGETS[:]} ${SOURCES[0]}",
            "test foo/bar.exe /bar/baz.obj ../foo/baz.obj foo/blah.cpp",

            "test ${TARGETS[1:]}v",
            "test /bar/baz.obj ../foo/baz.objv",

            "test $TARGET",
            "test foo/bar.exe",

            "test $TARGET$FOO[0]",
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
            "test foo/blah.cppblah /bar/ack.cppblah ../foo/ack.cblah",

            "test ${SOURCES[0:2].get_stuff('blah')}",
            "test foo/blah.cppblah /bar/ack.cppblah",

            "test ${SOURCES[0:2].get_stuff('blah')}",
            "test foo/blah.cppblah /bar/ack.cppblah",

            "test ${SOURCES.attribute.attr1}",
            "test attr$1-blah.cpp attr$1-ack.cpp attr$1-ack.c",

            "test ${SOURCES.attribute.attr2}",
            "test attr$2-blah.cpp attr$2-ack.cpp attr$2-ack.c",

            # Test adjacent expansions.
            "foo$BAR",
            "foobaz",

            "foo${BAR}",
            "foobaz",

            # Test that adjacent expansions don't get re-interpreted
            # together.  The correct disambiguated expansion should be:
            #   $XXX$HHH => ${FFF}III => GGGIII
            # not:
            #   $XXX$HHH => ${FFFIII} => BADNEWS
            "$XXX$HHH",             "GGGIII",

            # Test double-dollar-sign behavior.
            "$$FFF$HHH",            "$FFFIII",

            # Test that a Literal will stop dollar-sign substitution.
            "$XXX $LITERAL $FFF",   "GGG $XXX GGG",

            # Test that we don't blow up even if they subscript
            # something in ways they "can't."
            "${FFF[0]}",            "G",
            "${FFF[7]}",            "",
            "${NOTHING[1]}",        "",
            "${NONE[2]}",           "",

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
            '$S z',                 'x y z',
            '$LS z',                'x y z',
            '$L z',                 'x y z',
            #cs,                     'cs',
            #cl,                     'cl',
            '$CS',                  'cs',
            '$CL',                  'cl',

            # Test function calls within ${}.
            '$FUNCCALL',            'a xc b',

            # Bug reported by Christoph Wiedemann.
            cvt('$xxx/bin'),        '/bin',
        ]

        kwargs = {'target' : target, 'source' : source}

        failed = 0
        while cases:
            input, expect = cases[:2]
            expect = cvt(expect)
            result = apply(scons_subst, (input, env), kwargs)
            if result != expect:
                if failed == 0: print
                print "    input %s => %s did not match %s" % (repr(input), repr(result), repr(expect))
                failed = failed + 1
            del cases[:2]
        assert failed == 0, "%d subst() cases failed" % failed

        # Tests of the various SUBST_* modes of substitution.
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
                "| $( a | b $) | c 1",
                "| a | b | c 1",
                "| | c 1",
        ]

        failed = 0
        while subst_cases:
            input, eraw, ecmd, esig = subst_cases[:4]
            result = scons_subst(input, env, mode=SUBST_RAW)
            if result != eraw:
                if failed == 0: print
                print "    input %s => RAW %s did not match %s" % (repr(input), repr(result), repr(eraw))
                failed = failed + 1
            result = scons_subst(input, env, mode=SUBST_CMD)
            if result != ecmd:
                if failed == 0: print
                print "    input %s => CMD %s did not match %s" % (repr(input), repr(result), repr(ecmd))
                failed = failed + 1
            result = scons_subst(input, env, mode=SUBST_SIG)
            if result != esig:
                if failed == 0: print
                print "    input %s => SIG %s did not match %s" % (repr(input), repr(result), repr(esig))
                failed = failed + 1
            del subst_cases[:4]
        assert failed == 0, "%d subst() mode cases failed" % failed

        t1 = MyNode('t1')
        t2 = MyNode('t2')
        s1 = MyNode('s1')
        s2 = MyNode('s2')
        result = scons_subst("$TARGET $SOURCES", env,
                                  target=[t1, t2],
                                  source=[s1, s2])
        assert result == "t1 s1 s2", result
        result = scons_subst("$TARGET $SOURCES", env,
                                  target=[t1, t2],
                                  source=[s1, s2],
                                  dict={})
        assert result == " ", result

        result = scons_subst("$TARGET $SOURCES", env, target=[], source=[])
        assert result == " ", result
        result = scons_subst("$TARGETS $SOURCE", env, target=[], source=[])
        assert result == " ", result

        # Test interpolating a callable.
        newcom = scons_subst("test $CMDGEN1 $SOURCES $TARGETS",
                             env, target=MyNode('t'), source=MyNode('s'))
        assert newcom == "test foo baz s t", newcom

        # Test that we handle syntax errors during expansion as expected.
        try:
            scons_subst('$foo.bar.3.0', env)
        except SCons.Errors.UserError, e:
            expect1 = "Syntax error `invalid syntax' trying to evaluate `$foo.bar.3.0'"
            expect2 = "Syntax error `invalid syntax (line 1)' trying to evaluate `$foo.bar.3.0'"
            assert str(e) in [expect1, expect2], e
        else:
            raise AssertionError, "did not catch expected UserError"

        # Test how we handle overriding the internal conversion routines.
        def s(obj):
            return obj

        n1 = MyNode('n1')
        env = DummyEnv({'NODE' : n1})
        node = scons_subst("$NODE", env, mode=SUBST_RAW, conv=s)
        assert node == [n1], node
        node = scons_subst("$NODE", env, mode=SUBST_CMD, conv=s)
        assert node == [n1], node
        node = scons_subst("$NODE", env, mode=SUBST_SIG, conv=s)
        assert node == [n1], node

        # Test returning a function.
        #env = DummyEnv({'FUNCTION' : foo})
        #func = scons_subst("$FUNCTION", env, mode=SUBST_RAW, call=None)
        #assert func is function_foo, func
        #func = scons_subst("$FUNCTION", env, mode=SUBST_CMD, call=None)
        #assert func is function_foo, func
        #func = scons_subst("$FUNCTION", env, mode=SUBST_SIG, call=None)
        #assert func is function_foo, func

        # Test supplying an overriding gvars dictionary.
        env = DummyEnv({'XXX' : 'xxx'})
        result = scons_subst('$XXX', env)
        assert result == 'xxx', result
        result = scons_subst('$XXX', env, gvars={'XXX' : 'yyy'})
        assert result == 'yyy', result

    def test_subst_list(self):
        """Testing the scons_subst_list() method..."""
        class MyNode(DummyNode):
            """Simple node work-alike with some extra stuff for testing."""
            def __init__(self, name):
                DummyNode.__init__(self, name)
                class Attribute:
                    pass
                self.attribute = Attribute()
                self.attribute.attr1 = 'attr$1-' + os.path.basename(name)
                self.attribute.attr2 = 'attr$2-' + os.path.basename(name)

        target = [ MyNode("./foo/bar.exe"),
                   MyNode("/bar/baz with spaces.obj"),
                   MyNode("../foo/baz.obj") ]
        source = [ MyNode("./foo/blah with spaces.cpp"),
                   MyNode("/bar/ack.cpp"),
                   MyNode("../foo/ack.c") ]

        loc = {
            'xxx'       : None,
            'NEWLINE'   : 'before\nafter',

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

            'CMDGEN1'   : CmdGen1,
            'CMDGEN2'   : CmdGen2,

            'LITERALS'  : [ Literal('foo\nwith\nnewlines'),
                            Literal('bar\nwith\nnewlines') ],

            # Test various combinations of strings, lists and functions.
            'N'         : None,
            'X'         : 'x',
            'Y'         : '$X',
            'R'         : '$R',
            'S'         : 'x y',
            'LS'        : ['x y'],
            'L'         : ['x', 'y'],
            'CS'        : cs,
            'CL'        : cl,

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
        }

        env = DummyEnv(loc)

        cases = [
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

            # Test function calls within ${}.
            '$FUNCCALL',            [['a', 'xc', 'b']],

            # Test handling of newlines in white space.
            'foo\nbar',             [['foo'], ['bar']],
            'foo\n\nbar',           [['foo'], ['bar']],
            'foo \n \n bar',        [['foo'], ['bar']],
            'foo \nmiddle\n bar',   [['foo'], ['middle'], ['bar']],

            # Bug reported by Christoph Wiedemann.
            cvt('$xxx/bin'),        [['/bin']],
        ]

        kwargs = {'target' : target, 'source' : source}

        failed = 0
        while cases:
            input, expect = cases[:2]
            expect = map(lambda l: map(cvt, l), expect)
            result = apply(scons_subst_list, (input, env), kwargs)
            if result != expect:
                if failed == 0: print
                print "    input %s => %s did not match %s" % (repr(input), result, repr(expect))
                failed = failed + 1
            del cases[:2]
        assert failed == 0, "%d subst_list() cases failed" % failed

        t1 = MyNode('t1')
        t2 = MyNode('t2')
        s1 = MyNode('s1')
        s2 = MyNode('s2')
        result = scons_subst_list("$TARGET $SOURCES", env,
                                  target=[t1, t2],
                                  source=[s1, s2])
        assert result == [['t1', 's1', 's2']], result
        result = scons_subst_list("$TARGET $SOURCES", env,
                                  target=[t1, t2],
                                  source=[s1, s2],
                                  dict={})
        assert result == [[]], result

        # Test interpolating a callable.
        _t = DummyNode('t')
        _s = DummyNode('s')
        cmd_list = scons_subst_list("testing $CMDGEN1 $TARGETS $SOURCES",
                                    env, target=_t, source=_s)
        assert cmd_list == [['testing', 'foo', 'bar with spaces.out', 't', 's']], cmd_list

        # Test escape functionality.
        def escape_func(foo):
            return '**' + foo + '**'
        cmd_list = scons_subst_list("abc $LITERALS xyz", env)
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

        # Tests of the various SUBST_* modes of substitution.
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

        r = scons_subst_list("$TARGET $SOURCES", env, mode=SUBST_RAW)
        assert r == [[]], r

        failed = 0
        while subst_list_cases:
            input, eraw, ecmd, esig = subst_list_cases[:4]
            result = scons_subst_list(input, env, mode=SUBST_RAW)
            if result != eraw:
                if failed == 0: print
                print "    input %s => RAW %s did not match %s" % (repr(input), repr(result), repr(eraw))
                failed = failed + 1
            result = scons_subst_list(input, env, mode=SUBST_CMD)
            if result != ecmd:
                if failed == 0: print
                print "    input %s => CMD %s did not match %s" % (repr(input), repr(result), repr(ecmd))
                failed = failed + 1
            result = scons_subst_list(input, env, mode=SUBST_SIG)
            if result != esig:
                if failed == 0: print
                print "    input %s => SIG %s did not match %s" % (repr(input), repr(result), repr(esig))
                failed = failed + 1
            del subst_list_cases[:4]
        assert failed == 0, "%d subst() mode cases failed" % failed

        # Test that we handle syntax errors during expansion as expected.
        try:
            scons_subst_list('$foo.bar.3.0', env)
        except SCons.Errors.UserError, e:
            expect1 = "Syntax error `invalid syntax' trying to evaluate `$foo.bar.3.0'"
            expect2 = "Syntax error `invalid syntax (line 1)' trying to evaluate `$foo.bar.3.0'"
            assert str(e) in [expect1, expect2], e
        else:
            raise AssertionError, "did not catch expected SyntaxError"

        # Test we handle overriding the internal conversion routines.
        def s(obj):
            return obj

        n1 = MyNode('n1')
        env = DummyEnv({'NODE' : n1})
        node = scons_subst_list("$NODE", env, mode=SUBST_RAW, conv=s)
        assert node == [[n1]], node
        node = scons_subst_list("$NODE", env, mode=SUBST_CMD, conv=s)
        assert node == [[n1]], node
        node = scons_subst_list("$NODE", env, mode=SUBST_SIG, conv=s)
        assert node == [[n1]], node

        # Test supplying an overriding gvars dictionary.
        env = DummyEnv({'XXX' : 'xxx'})
        result = scons_subst_list('$XXX', env)
        assert result == [['xxx']], result
        result = scons_subst_list('$XXX', env, gvars={'XXX' : 'yyy'})
        assert result == [['yyy']], result

    def test_subst_once(self):
        """Testing the scons_subst_once() method"""

        loc = {
            'CCFLAGS'           : '-DFOO',
            'ONE'               : 1,
            'RECURSE'           : 'r $RECURSE r',
            'LIST'              : ['a', 'b', 'c'],
        }

        env = DummyEnv(loc)

        cases = [
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

        failed = 0
        while cases:
            input, key, expect = cases[:3]
            result = scons_subst_once(input, env, key)
            if result != expect:
                if failed == 0: print
                print "    input %s (%s) => %s did not match %s" % (repr(input), repr(key), repr(result), repr(expect))
                failed = failed + 1
            del cases[:3]
        assert failed == 0, "%d subst() cases failed" % failed

    def test_splitext(self):
        assert splitext('foo') == ('foo','')
        assert splitext('foo.bar') == ('foo','.bar')
        assert splitext(os.path.join('foo.bar', 'blat')) == (os.path.join('foo.bar', 'blat'),'')

    def test_quote_spaces(self):
        """Testing the quote_spaces() method..."""
        q = quote_spaces('x')
        assert q == 'x', q

        q = quote_spaces('x x')
        assert q == '"x x"', q

        q = quote_spaces('x\tx')
        assert q == '"x\tx"', q

    def test_render_tree(self):
        class Node:
            def __init__(self, name, children=[]):
                self.children = children
                self.name = name
            def __str__(self):
                return self.name

        def get_children(node):
            return node.children

        windows_h = Node("windows.h")
        stdlib_h = Node("stdlib.h")
        stdio_h = Node("stdio.h")
        bar_c = Node("bar.c", [stdlib_h, windows_h])
        bar_o = Node("bar.o", [bar_c])
        foo_c = Node("foo.c", [stdio_h])
        foo_o = Node("foo.o", [foo_c])
        foo = Node("foo", [foo_o, bar_o])

        expect = """\
+-foo
  +-foo.o
  | +-foo.c
  |   +-stdio.h
  +-bar.o
    +-bar.c
      +-stdlib.h
      +-windows.h
"""

        actual = render_tree(foo, get_children)
        assert expect == actual, (expect, actual)

        bar_h = Node('bar.h', [stdlib_h])
        blat_h = Node('blat.h', [stdlib_h])
        blat_c = Node('blat.c', [blat_h, bar_h])
        blat_o = Node('blat.o', [blat_c])

        expect = """\
+-blat.o
  +-blat.c
    +-blat.h
    | +-stdlib.h
    +-bar.h
"""

        actual = render_tree(blat_o, get_children, 1)
        assert expect == actual, (expect, actual)

    def test_is_Dict(self):
        assert is_Dict({})
        import UserDict
        assert is_Dict(UserDict.UserDict())
        assert not is_Dict([])
        assert not is_Dict("")
        if hasattr(types, 'UnicodeType'):
            exec "assert not is_Dict(u'')"

    def test_is_List(self):
        assert is_List([])
        import UserList
        assert is_List(UserList.UserList())
        assert not is_List({})
        assert not is_List("")
        if hasattr(types, 'UnicodeType'):
            exec "assert not is_List(u'')"

    def test_is_String(self):
        assert is_String("")
        if hasattr(types, 'UnicodeType'):
            exec "assert is_String(u'')"
        try:
            import UserString
        except:
            pass
        else:
            assert is_String(UserString.UserString(''))
        assert not is_String({})
        assert not is_String([])

    def test_to_String(self):
        """Test the to_String() method."""
        assert to_String(1) == "1", to_String(1)
        assert to_String([ 1, 2, 3]) == str([1, 2, 3]), to_String([1,2,3])
        assert to_String("foo") == "foo", to_String("foo")

        try:
            import UserString

            s1=UserString.UserString('blah')
            assert to_String(s1) == s1, s1
            assert to_String(s1) == 'blah', s1

            class Derived(UserString.UserString):
                pass
            s2 = Derived('foo')
            assert to_String(s2) == s2, s2
            assert to_String(s2) == 'foo', s2

            if hasattr(types, 'UnicodeType'):
                s3=UserString.UserString(unicode('bar'))
                assert to_String(s3) == s3, s3
                assert to_String(s3) == unicode('bar'), s3
                assert type(to_String(s3)) is types.UnicodeType, \
                       type(to_String(s3))
        except ImportError:
            pass

        if hasattr(types, 'UnicodeType'):
            s4 = unicode('baz')
            assert to_String(s4) == unicode('baz'), to_String(s4)
            assert type(to_String(s4)) is types.UnicodeType, \
                   type(to_String(s4))

    def test_WhereIs(self):
        test = TestCmd.TestCmd(workdir = '')

        sub1_xxx_exe = test.workpath('sub1', 'xxx.exe')
        sub2_xxx_exe = test.workpath('sub2', 'xxx.exe')
        sub3_xxx_exe = test.workpath('sub3', 'xxx.exe')
        sub4_xxx_exe = test.workpath('sub4', 'xxx.exe')

        test.subdir('subdir', 'sub1', 'sub2', 'sub3', 'sub4')

        if sys.platform != 'win32':
            test.write(sub1_xxx_exe, "\n")

        os.mkdir(sub2_xxx_exe)

        test.write(sub3_xxx_exe, "\n")
        os.chmod(sub3_xxx_exe, 0777)

        test.write(sub4_xxx_exe, "\n")
        os.chmod(sub4_xxx_exe, 0777)

        env_path = os.environ['PATH']

        pathdirs_1234 = [ test.workpath('sub1'),
                          test.workpath('sub2'),
                          test.workpath('sub3'),
                          test.workpath('sub4'),
                        ] + string.split(env_path, os.pathsep)

        pathdirs_1243 = [ test.workpath('sub1'),
                          test.workpath('sub2'),
                          test.workpath('sub4'),
                          test.workpath('sub3'),
                        ] + string.split(env_path, os.pathsep)

        os.environ['PATH'] = string.join(pathdirs_1234, os.pathsep)
        wi = WhereIs('xxx.exe')
        assert wi == test.workpath(sub3_xxx_exe), wi
        wi = WhereIs('xxx.exe', pathdirs_1243)
        assert wi == test.workpath(sub4_xxx_exe), wi
        wi = WhereIs('xxx.exe', string.join(pathdirs_1243, os.pathsep))
        assert wi == test.workpath(sub4_xxx_exe), wi

        wi = WhereIs('xxx.exe',reject = sub3_xxx_exe)
        assert wi == test.workpath(sub4_xxx_exe), wi
        wi = WhereIs('xxx.exe', pathdirs_1243, reject = sub3_xxx_exe)
        assert wi == test.workpath(sub4_xxx_exe), wi

        os.environ['PATH'] = string.join(pathdirs_1243, os.pathsep)
        wi = WhereIs('xxx.exe')
        assert wi == test.workpath(sub4_xxx_exe), wi
        wi = WhereIs('xxx.exe', pathdirs_1234)
        assert wi == test.workpath(sub3_xxx_exe), wi
        wi = WhereIs('xxx.exe', string.join(pathdirs_1234, os.pathsep))
        assert wi == test.workpath(sub3_xxx_exe), wi

        if sys.platform == 'win32':
            wi = WhereIs('xxx', pathext = '')
            assert wi is None, wi

            wi = WhereIs('xxx', pathext = '.exe')
            assert wi == test.workpath(sub4_xxx_exe), wi

            wi = WhereIs('xxx', path = pathdirs_1234, pathext = '.BAT;.EXE')
            assert string.lower(wi) == string.lower(test.workpath(sub3_xxx_exe)), wi

            # Test that we return a normalized path even when
            # the path contains forward slashes.
            forward_slash = test.workpath('') + '/sub3'
            wi = WhereIs('xxx', path = forward_slash, pathext = '.EXE')
            assert string.lower(wi) == string.lower(test.workpath(sub3_xxx_exe)), wi

    def test_is_valid_construction_var(self):
        """Testing is_valid_construction_var()"""
        r = is_valid_construction_var("_a")
        assert not r is None, r
        r = is_valid_construction_var("z_")
        assert not r is None, r
        r = is_valid_construction_var("X_")
        assert not r is None, r
        r = is_valid_construction_var("2a")
        assert r is None, r
        r = is_valid_construction_var("a2_")
        assert not r is None, r
        r = is_valid_construction_var("/")
        assert r is None, r
        r = is_valid_construction_var("_/")
        assert r is None, r
        r = is_valid_construction_var("a/")
        assert r is None, r
        r = is_valid_construction_var(".b")
        assert r is None, r
        r = is_valid_construction_var("_.b")
        assert r is None, r
        r = is_valid_construction_var("b1._")
        assert r is None, r
        r = is_valid_construction_var("-b")
        assert r is None, r
        r = is_valid_construction_var("_-b")
        assert r is None, r
        r = is_valid_construction_var("b1-_")
        assert r is None, r

    def test_get_env_var(self):
        """Testing get_environment_var()."""
        assert get_environment_var("$FOO") == "FOO", get_environment_var("$FOO")
        assert get_environment_var("${BAR}") == "BAR", get_environment_var("${BAR}")
        assert get_environment_var("$FOO_BAR1234") == "FOO_BAR1234", get_environment_var("$FOO_BAR1234")
        assert get_environment_var("${BAR_FOO1234}") == "BAR_FOO1234", get_environment_var("${BAR_FOO1234}")
        assert get_environment_var("${BAR}FOO") == None, get_environment_var("${BAR}FOO")
        assert get_environment_var("$BAR ") == None, get_environment_var("$BAR ")
        assert get_environment_var("FOO$BAR") == None, get_environment_var("FOO$BAR")
        assert get_environment_var("$FOO[0]") == None, get_environment_var("$FOO[0]")
        assert get_environment_var("${some('complex expression')}") == None, get_environment_var("${some('complex expression')}")

    def test_Proxy(self):
        """Test generic Proxy class."""
        class Subject:
            def foo(self):
                return 1
            def bar(self):
                return 2

        s=Subject()
        s.baz = 3

        class ProxyTest(Proxy):
            def bar(self):
                return 4

        p=ProxyTest(s)

        assert p.foo() == 1, p.foo()
        assert p.bar() == 4, p.bar()
        assert p.baz == 3, p.baz

        p.baz = 5
        s.baz = 6

        assert p.baz == 5, p.baz
        assert p.get() == s, p.get()

    def test_Literal(self):
        """Test the Literal() function."""
        input_list = [ '$FOO', Literal('$BAR') ]
        dummy_env = DummyEnv({ 'FOO' : 'BAZ', 'BAR' : 'BLAT' })

        def escape_func(cmd):
            return '**' + cmd + '**'

        cmd_list = scons_subst_list(input_list, dummy_env)
        cmd_list = SCons.Util.escape_list(cmd_list[0], escape_func)
        assert cmd_list == ['BAZ', '**$BAR**'], cmd_list

    def test_SpecialAttrWrapper(self):
        """Test the SpecialAttrWrapper() function."""
        input_list = [ '$FOO', SpecialAttrWrapper('$BAR', 'BLEH') ]
        dummy_env = DummyEnv({ 'FOO' : 'BAZ', 'BAR' : 'BLAT' })

        def escape_func(cmd):
            return '**' + cmd + '**'

        cmd_list = scons_subst_list(input_list, dummy_env)
        cmd_list = SCons.Util.escape_list(cmd_list[0], escape_func)
        assert cmd_list == ['BAZ', '**$BAR**'], cmd_list

        cmd_list = scons_subst_list(input_list, dummy_env, mode=SUBST_SIG)
        cmd_list = SCons.Util.escape_list(cmd_list[0], escape_func)
        assert cmd_list == ['BAZ', '**BLEH**'], cmd_list

    def test_display(self):
        old_stdout = sys.stdout
        sys.stdout = OutBuffer()
        display("line1")
        display.set_mode(0)
        display("line2")
        display.set_mode(1)
        display("line3")

        assert sys.stdout.buffer == "line1\nline3\n"
        sys.stdout = old_stdout

    def test_fs_delete(self):
        test = TestCmd.TestCmd(workdir = '')
        base = test.workpath('')
        xxx = test.workpath('xxx.xxx')
        ZZZ = test.workpath('ZZZ.ZZZ')
        sub1_yyy = test.workpath('sub1', 'yyy.yyy')

        test.subdir('sub1')
        test.write(xxx, "\n")
        test.write(ZZZ, "\n")
        test.write(sub1_yyy, "\n")

        old_stdout = sys.stdout
        sys.stdout = OutBuffer()

        exp = "Removed " + os.path.join(base, ZZZ) + "\n" + \
              "Removed " + os.path.join(base, sub1_yyy) + '\n' + \
              "Removed directory " + os.path.join(base, 'sub1') + '\n' + \
              "Removed " + os.path.join(base, xxx) + '\n' + \
              "Removed directory " + base + '\n'

        fs_delete(base, remove=0)
        assert sys.stdout.buffer == exp, sys.stdout.buffer
        assert os.path.exists(sub1_yyy)

        sys.stdout.buffer = ""
        fs_delete(base, remove=1)
        assert sys.stdout.buffer == exp
        assert not os.path.exists(base)

        test._dirlist = None
        sys.stdout = old_stdout

    def test_get_native_path(self):
        """Test the get_native_path() function."""
        import tempfile
        filename = tempfile.mktemp()
        str = '1234567890 ' + filename
        open(filename, 'w').write(str)
        assert open(get_native_path(filename)).read() == str

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
        TARGETS = map(lambda x: str(x), d['TARGETS'])
        TARGETS.sort()
        assert TARGETS == ['t1', 't2'], d['TARGETS']
        assert str(d['TARGET']) == 't1', d['TARGET']
        SOURCES = map(lambda x: str(x), d['SOURCES'])
        SOURCES.sort()
        assert SOURCES == ['s1', 's2'], d['SOURCES']
        assert str(d['SOURCE']) == 's1', d['SOURCE']

        class N:
            def __init__(self, name):
                self.name = name
            def __str__(self):
                return self.name
            def rfile(self):
                return self.__class__('rstr-' + self.name)
            def get_subst_proxy(self):
                return self

        t3 = N('t3')
        t4 = DummyNode('t4')
        s3 = DummyNode('s3')
        s4 = N('s4')
        d = subst_dict(target=[t3, t4], source=[s3, s4])
        TARGETS = map(lambda x: str(x), d['TARGETS'])
        TARGETS.sort()
        assert TARGETS == ['t3', 't4'], d['TARGETS']
        SOURCES = map(lambda x: str(x), d['SOURCES'])
        SOURCES.sort()
        assert SOURCES == ['rstr-s4', 's3'], d['SOURCES']

    def test_PrependPath(self):
        """Test prepending to a path"""
        p1 = r'C:\dir\num\one;C:\dir\num\two'
        p2 = r'C:\mydir\num\one;C:\mydir\num\two'
        # have to include the pathsep here so that the test will work on UNIX too.
        p1 = PrependPath(p1,r'C:\dir\num\two',sep = ';')
        p1 = PrependPath(p1,r'C:\dir\num\three',sep = ';')
        p2 = PrependPath(p2,r'C:\mydir\num\three',sep = ';')
        p2 = PrependPath(p2,r'C:\mydir\num\one',sep = ';')
        assert(p1 == r'C:\dir\num\three;C:\dir\num\two;C:\dir\num\one')
        assert(p2 == r'C:\mydir\num\one;C:\mydir\num\three;C:\mydir\num\two')

    def test_AppendPath(self):
        """Test appending to a path."""
        p1 = r'C:\dir\num\one;C:\dir\num\two'
        p2 = r'C:\mydir\num\one;C:\mydir\num\two'
        # have to include the pathsep here so that the test will work on UNIX too.
        p1 = AppendPath(p1,r'C:\dir\num\two',sep = ';')
        p1 = AppendPath(p1,r'C:\dir\num\three',sep = ';')
        p2 = AppendPath(p2,r'C:\mydir\num\three',sep = ';')
        p2 = AppendPath(p2,r'C:\mydir\num\one',sep = ';')
        assert(p1 == r'C:\dir\num\one;C:\dir\num\two;C:\dir\num\three')
        assert(p2 == r'C:\mydir\num\two;C:\mydir\num\three;C:\mydir\num\one')

    def test_NodeList(self):
        """Test NodeList class"""
        class TestClass:
            def __init__(self, name, child=None):
                self.child = child
                self.bar = name
            def foo(self):
                return self.bar + "foo"
            def getself(self):
                return self

        t1 = TestClass('t1', TestClass('t1child'))
        t2 = TestClass('t2', TestClass('t2child'))
        t3 = TestClass('t3')

        nl = NodeList([t1, t2, t3])
        assert nl.foo() == [ 't1foo', 't2foo', 't3foo' ], nl.foo()
        assert nl.bar == [ 't1', 't2', 't3' ], nl.bar
        assert nl.getself().bar == [ 't1', 't2', 't3' ], nl.getself().bar
        assert nl[0:2].child.foo() == [ 't1childfoo', 't2childfoo' ], \
               nl[0:2].child.foo()
        assert nl[0:2].child.bar == [ 't1child', 't2child' ], \
               nl[0:2].child.bar

    def test_CLVar(self):
        """Test the command-line construction variable class"""
        f = SCons.Util.CLVar('a b')

        r = f + 'c d'
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + ' c d'
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + ['c d']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c d'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + [' c d']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', ' c d'], r.data
        assert str(r) == 'a b  c d', str(r)

        r = f + ['c', 'd']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + [' c', 'd']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', ' c', 'd'], r.data
        assert str(r) == 'a b  c d', str(r)

        f = SCons.Util.CLVar(['a b'])

        r = f + 'c d'
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + ' c d'
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + ['c d']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a b', 'c d'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + [' c d']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a b', ' c d'], r.data
        assert str(r) == 'a b  c d', str(r)

        r = f + ['c', 'd']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + [' c', 'd']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a b', ' c', 'd'], r.data
        assert str(r) == 'a b  c d', str(r)

        f = SCons.Util.CLVar(['a', 'b'])

        r = f + 'c d'
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + ' c d'
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + ['c d']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c d'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + [' c d']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', ' c d'], r.data
        assert str(r) == 'a b  c d', str(r)

        r = f + ['c', 'd']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', 'c', 'd'], r.data
        assert str(r) == 'a b c d', str(r)

        r = f + [' c', 'd']
        assert isinstance(r, SCons.Util.CLVar), type(r)
        assert r.data == ['a', 'b', ' c', 'd'], r.data
        assert str(r) == 'a b  c d', str(r)

        loc = {}
        loc['FOO'] = 'foo'
        loc['BAR'] = SCons.Util.CLVar('bar')
        loc['CALL'] = lambda target, source, env, for_signature: 'call'
        env = DummyEnv(loc)

        cmd = SCons.Util.CLVar("test $FOO $BAR $CALL test")

        newcmd = scons_subst(cmd, env)
        assert newcmd == 'test foo bar call test', newcmd

        cmd_list = scons_subst_list(cmd, env)
        assert len(cmd_list) == 1, cmd_list
        assert cmd_list[0][0] == "test", cmd_list[0][0]
        assert cmd_list[0][1] == "foo", cmd_list[0][1]
        assert cmd_list[0][2] == "bar", cmd_list[0][2]
        assert cmd_list[0][3] == "call", cmd_list[0][3]
        assert cmd_list[0][4] == "test", cmd_list[0][4]

    def test_Selector(self):
        """Test the Selector class"""

        s = Selector({'a' : 'AAA', 'b' : 'BBB'})
        assert s['a'] == 'AAA', s['a']
        assert s['b'] == 'BBB', s['b']
        exc_caught = None
        try:
            x = s['c']
        except KeyError:
            exc_caught = 1
        assert exc_caught, "should have caught a KeyError"
        s['c'] = 'CCC'
        assert s['c'] == 'CCC', s['c']

        class DummyEnv(UserDict.UserDict):
            def subst(self, key):
                if key[0] == '$':
                    return self[key[1:]]
                return key

        env = DummyEnv()

        s = Selector({'.d' : 'DDD', '.e' : 'EEE'})
        ret = s(env, ['foo.d'])
        assert ret == 'DDD', ret
        ret = s(env, ['bar.e'])
        assert ret == 'EEE', ret
        ret = s(env, ['bar.x'])
        assert ret == None, ret
        s[None] = 'XXX'
        ret = s(env, ['bar.x'])
        assert ret == 'XXX', ret

        env = DummyEnv({'FSUFF' : '.f', 'GSUFF' : '.g'})

        s = Selector({'$FSUFF' : 'FFF', '$GSUFF' : 'GGG'})
        ret = s(env, ['foo.f'])
        assert ret == 'FFF', ret
        ret = s(env, ['bar.g'])
        assert ret == 'GGG', ret

    def test_adjustixes(self):
        """Test the adjustixes() function"""
        r = adjustixes('file', 'pre-', '-suf')
        assert r == 'pre-file-suf', r
        r = adjustixes('pre-file', 'pre-', '-suf')
        assert r == 'pre-file-suf', r
        r = adjustixes('file-suf', 'pre-', '-suf')
        assert r == 'pre-file-suf', r
        r = adjustixes('pre-file-suf', 'pre-', '-suf')
        assert r == 'pre-file-suf', r
        r = adjustixes('pre-file.xxx', 'pre-', '-suf')
        assert r == 'pre-file.xxx', r
        r = adjustixes('dir/file', 'pre-', '-suf')
        assert r == os.path.join('dir', 'pre-file-suf'), r

if __name__ == "__main__":
    suite = unittest.makeSuite(UtilTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
