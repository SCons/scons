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

# Define a null function for use as a builder action.
# Where this is defined in the file seems to affect its
# byte-code contents, so try to minimize changes by
# defining it here, before we even import anything.
def Func():
    pass

import os.path
import sys
import types
import unittest

import TestCmd

import SCons.Action
import SCons.Builder
import SCons.Errors
import SCons.Node.FS
import SCons.Warnings
import SCons.Environment

# Initial setup of the common environment for all tests,
# a temporary working directory containing a
# script for writing arguments to an output file.
#
# We don't do this as a setUp() method because it's
# unnecessary to create a separate directory and script
# for each test, they can just use the one.
test = TestCmd.TestCmd(workdir = '')

outfile = test.workpath('outfile')
outfile2 = test.workpath('outfile2')

show_string = None
env_scanner = None

scons_env = SCons.Environment.Environment()

class Environment:
    def __init__(self, **kw):
        self.d = {}
        self.d['SHELL'] = scons_env['SHELL']
        self.d['SPAWN'] = scons_env['SPAWN']
        self.d['ESCAPE'] = scons_env['ESCAPE']
        for k, v in kw.items():
            self.d[k] = v
    def subst(self, s):
        if not SCons.Util.is_String(s):
            return s
        try:
            if s[0] == '$':
                return self.d.get(s[1:], '')
        except IndexError:
            pass
        return self.d.get(s, s)
    def get_scanner(self, ext):
        return env_scanner
    def Dictionary(self):
        return {}
    def autogenerate(self, dir=''):
        return {}
    def __getitem__(self, item):
        return self.d[item]
    def has_key(self, item):
        return self.d.has_key(item)
    def keys(self):
        return self.d.keys()
    def get(self, key, value):
        return self.d.get(key, value)
    def Override(self, overrides):
        env = apply(Environment, (), self.d)
        env.d.update(overrides)
        return env
    def items(self):
        return self.d.items()
    def sig_dict(self):
        d = {}
        for k,v in self.items(): d[k] = v
        d['TARGETS'] = ['__t1__', '__t2__', '__t3__', '__t4__', '__t5__', '__t6__']
        d['TARGET'] = d['TARGETS'][0]
        d['SOURCES'] = ['__s1__', '__s2__', '__s3__', '__s4__', '__s5__', '__s6__']
        d['SOURCE'] = d['SOURCES'][0]
        return d
    
env = Environment()

class BuilderTestCase(unittest.TestCase):

    def test__nonzero__(self):
        """Test a builder raising an exception when __nonzero__ is called
        """
        builder = SCons.Builder.Builder(action="foo")
        exc_caught = None
        try:
            builder.__nonzero__()
        except SCons.Errors.InternalError:
            exc_caught = 1
        assert exc_caught, "did not catch expected InternalError exception"

        class Node:
             pass

        n = Node()
        n.builder = builder
        exc_caught = None
        try:
            if n.builder:
                pass
        except SCons.Errors.InternalError:
            exc_caught = 1
        assert exc_caught, "did not catch expected InternalError exception"

    def test__call__(self):
        """Test calling a builder to establish source dependencies
        """
        class Node:
            def __init__(self, name):
                self.name = name
                self.sources = []
                self.builder = None
                self.side_effect = 0
            def __str__(self):
                return self.name
            def builder_set(self, builder):
                self.builder = builder
            def has_builder(self, fetch=1):
                return not self.builder is None
            def env_set(self, env, safe=0):
                self.env = env
            def add_source(self, source):
                self.sources.extend(source)
            def scanner_key(self):
                return self.name
        builder = SCons.Builder.Builder(action="foo", node_factory=Node)

        n1 = Node("n1");
        n2 = Node("n2");
        builder(env, target = n1, source = n2)
        assert n1.env == env
        assert n1.builder == builder
        assert n1.sources == [n2]
        assert not hasattr(n2, 'env')

        target = builder(env, target = 'n3', source = 'n4')
        assert target.name == 'n3'
        assert target.sources[0].name == 'n4'

        target = builder(env, target = 'n4 n5', source = ['n6 n7'])
        assert target.name == 'n4 n5'
        assert target.sources[0].name == 'n6 n7'

        target = builder(env, target = ['n8 n9'], source = 'n10 n11')
        assert target.name == 'n8 n9'
        assert target.sources[0].name == 'n10 n11'

        if not hasattr(types, 'UnicodeType'):
            uni = str
        else:
            uni = unicode

        target = builder(env, target = uni('n12 n13'),
                          source = [uni('n14 n15')])
        assert target.name == uni('n12 n13')
        assert target.sources[0].name == uni('n14 n15')

        target = builder(env, target = [uni('n16 n17')],
                         source = uni('n18 n19'))
        assert target.name == uni('n16 n17')
        assert target.sources[0].name == uni('n18 n19')

    def test_action(self):
        """Test Builder creation

        Verify that we can retrieve the supplied action attribute.
        """
        builder = SCons.Builder.Builder(action="foo")
        assert builder.action.cmd_list == "foo"

        def func():
            pass
        builder = SCons.Builder.Builder(action=func)
        assert isinstance(builder.action, SCons.Action.FunctionAction)
        # Preserve the following so that the baseline test will fail.
        # Remove it in favor of the previous test at some convenient
        # point in the future.
        assert builder.action.execfunction == func

    def test_generator(self):
        """Test Builder creation given a generator function."""

        def generator():
            pass

        builder = SCons.Builder.Builder(generator=generator)
        assert builder.action.generator == generator

    def test_cmp(self):
        """Test simple comparisons of Builder objects
        """
        b1 = SCons.Builder.Builder(src_suffix = '.o')
        b2 = SCons.Builder.Builder(src_suffix = '.o')
        assert b1 == b2
        b3 = SCons.Builder.Builder(src_suffix = '.x')
        assert b1 != b3
        assert b2 != b3

    def test_get_actions(self):
        """Test fetching the Builder's Action list
        """
        def func():
            pass
        builder = SCons.Builder.Builder(action=SCons.Action.ListAction(["x",
                                                                        func,
                                                                        "z"]))
        a = builder.get_actions()
        assert len(a) == 3, a
        assert isinstance(a[0], SCons.Action.CommandAction), a[0]
        assert isinstance(a[1], SCons.Action.FunctionAction), a[1]
        assert isinstance(a[2], SCons.Action.CommandAction), a[2]

    def test_get_contents(self):
        """Test returning the signature contents of a Builder
        """

        b1 = SCons.Builder.Builder(action = "foo ${TARGETS[5]}")
        contents = b1.get_contents([],[],Environment())
        assert contents == "foo __t6__", contents

        b1 = SCons.Builder.Builder(action = "bar ${SOURCES[3:5]}")
        contents = b1.get_contents([],[],Environment())
        assert contents == "bar __s4__ __s5__", contents

        b2 = SCons.Builder.Builder(action = Func)
        contents = b2.get_contents([],[],Environment())
        assert contents == "\177\036\000\177\037\000d\000\000S", repr(contents)

        b3 = SCons.Builder.Builder(action = SCons.Action.ListAction(["foo", Func, "bar"]))
        contents = b3.get_contents([],[],Environment())
        assert contents == "foo\177\036\000\177\037\000d\000\000Sbar", repr(contents)

    def test_node_factory(self):
        """Test a Builder that creates nodes of a specified class
        """
        class Foo:
            pass
        def FooFactory(target):
            global Foo
            return Foo(target)
        builder = SCons.Builder.Builder(node_factory = FooFactory)
        assert builder.target_factory is FooFactory
        assert builder.source_factory is FooFactory

    def test_target_factory(self):
        """Test a Builder that creates target nodes of a specified class
        """
        class Foo:
            pass
        def FooFactory(target):
            global Foo
            return Foo(target)
        builder = SCons.Builder.Builder(target_factory = FooFactory)
        assert builder.target_factory is FooFactory
        assert not builder.source_factory is FooFactory

    def test_source_factory(self):
        """Test a Builder that creates source nodes of a specified class
        """
        class Foo:
            pass
        def FooFactory(source):
            global Foo
            return Foo(source)
        builder = SCons.Builder.Builder(source_factory = FooFactory)
        assert not builder.target_factory is FooFactory
        assert builder.source_factory is FooFactory

    def test_prefix(self):
        """Test Builder creation with a specified target prefix

        Make sure that there is no '.' separator appended.
        """
        builder = SCons.Builder.Builder(prefix = 'lib.')
        assert builder.get_prefix(env) == 'lib.'
        builder = SCons.Builder.Builder(prefix = 'lib')
        assert builder.get_prefix(env) == 'lib'
        tgt = builder(env, target = 'tgt1', source = 'src1')
        assert tgt.path == 'libtgt1', \
                "Target has unexpected name: %s" % tgt.path
        tgt = builder(env, target = 'tgt2a tgt2b', source = 'src2')
        assert tgt.path == 'libtgt2a tgt2b', \
                "Target has unexpected name: %s" % tgt.path
        tgt = builder(env, source = 'src3')
        assert tgt.path == 'libsrc3', \
                "Target has unexpected name: %s" % tgt.path

    def test_src_suffix(self):
        """Test Builder creation with a specified source file suffix
        
        Make sure that the '.' separator is appended to the
        beginning if it isn't already present.
        """
        env = Environment(XSUFFIX = '.x', YSUFFIX = '.y')

        b1 = SCons.Builder.Builder(src_suffix = '.c')
        assert b1.src_suffixes(env) == ['.c'], b1.src_suffixes(env)

        tgt = b1(env, target = 'tgt2', source = 'src2')
        assert tgt.sources[0].path == 'src2.c', \
                "Source has unexpected name: %s" % tgt.sources[0].path

        tgt = b1(env, target = 'tgt3', source = 'src3a src3b')
        assert len(tgt.sources) == 1
        assert tgt.sources[0].path == 'src3a src3b.c', \
                "Unexpected tgt.sources[0] name: %s" % tgt.sources[0].path

        b2 = SCons.Builder.Builder(src_suffix = '.2', src_builder = b1)
        assert b2.src_suffixes(env) == ['.2', '.c'], b2.src_suffixes(env)

        b3 = SCons.Builder.Builder(action = {'.3a' : '', '.3b' : ''})
        s = b3.src_suffixes(env)
        s.sort()
        assert s == ['.3a', '.3b'], s

        b4 = SCons.Builder.Builder(src_suffix = '$XSUFFIX')
        assert b4.src_suffixes(env) == ['.x'], b4.src_suffixes(env)

        b5 = SCons.Builder.Builder(action = { '.y' : ''})
        assert b5.src_suffixes(env) == ['.y'], b5.src_suffixes(env)

    def test_suffix(self):
        """Test Builder creation with a specified target suffix

        Make sure that the '.' separator is appended to the
        beginning if it isn't already present.
        """
        builder = SCons.Builder.Builder(suffix = '.o')
        assert builder.get_suffix(env) == '.o', builder.get_suffix(env)
        builder = SCons.Builder.Builder(suffix = 'o')
        assert builder.get_suffix(env) == '.o', builder.get_suffix(env)
        tgt = builder(env, target = 'tgt3', source = 'src3')
        assert tgt.path == 'tgt3.o', \
                "Target has unexpected name: %s" % tgt.path
        tgt = builder(env, target = 'tgt4a tgt4b', source = 'src4')
        assert tgt.path == 'tgt4a tgt4b.o', \
                "Target has unexpected name: %s" % tgt.path
        tgt = builder(env, source = 'src5')
        assert tgt.path == 'src5.o', \
                "Target has unexpected name: %s" % tgt.path

    def test_ListBuilder(self):
        """Testing ListBuilder class."""
        def function2(target, source, env, tlist = [outfile, outfile2], **kw):
            for t in target:
                open(str(t), 'w').write("function2\n")
            for t in tlist:
                if not t in map(str, target):
                    open(t, 'w').write("function2\n")
            return 1

        builder = SCons.Builder.Builder(action = function2)
        tgts = builder(env, target = [outfile, outfile2], source = 'foo')
        for t in tgts:
            t.prepare()
        try:
            tgts[0].build()
        except SCons.Errors.BuildError:
            pass
        c = test.read(outfile, 'r')
        assert c == "function2\n", c
        c = test.read(outfile2, 'r')
        assert c == "function2\n", c

        sub1_out = test.workpath('sub1', 'out')
        sub2_out = test.workpath('sub2', 'out')

        def function3(target, source, env, tlist = [sub1_out, sub2_out]):
            for t in target:
                open(str(t), 'w').write("function3\n")
            for t in tlist:
                if not t in map(str, target):
                    open(t, 'w').write("function3\n")
            return 1

        builder = SCons.Builder.Builder(action = function3)
        tgts = builder(env, target = [sub1_out, sub2_out], source = 'foo')
        for t in tgts:
            t.prepare()
        try:
            tgts[0].build()
        except SCons.Errors.BuildError:
            pass
        c = test.read(sub1_out, 'r')
        assert c == "function3\n", c
        c = test.read(sub2_out, 'r')
        assert c == "function3\n", c
        assert os.path.exists(test.workpath('sub1'))
        assert os.path.exists(test.workpath('sub2'))

    def test_MultiStepBuilder(self):
        """Testing MultiStepBuilder class."""
        builder1 = SCons.Builder.Builder(action='foo',
                                         src_suffix='.bar',
                                         suffix='.foo')
        builder2 = SCons.Builder.MultiStepBuilder(action='bar',
                                                  src_builder = builder1,
                                                  src_suffix = '.foo')
        tgt = builder2(env, target='baz', source=['test.bar', 'test2.foo', 'test3.txt'])
        assert str(tgt.sources[0]) == 'test.foo', str(tgt.sources[0])
        assert str(tgt.sources[0].sources[0]) == 'test.bar', \
               str(tgt.sources[0].sources[0])
        assert str(tgt.sources[1]) == 'test2.foo', str(tgt.sources[1])
        assert str(tgt.sources[2]) == 'test3.txt', str(tgt.sources[2])

        tgt = builder2(env, 'aaa.bar')
        assert str(tgt) == 'aaa', str(tgt)
        assert str(tgt.sources[0]) == 'aaa.foo', str(tgt.sources[0])
        assert str(tgt.sources[0].sources[0]) == 'aaa.bar', \
               str(tgt.sources[0].sources[0])

        builder3 = SCons.Builder.MultiStepBuilder(action = 'foo',
                                                  src_builder = 'xyzzy',
                                                  src_suffix = '.xyzzy')
        assert builder3.get_src_builders(Environment()) == []
        
    def test_CompositeBuilder(self):
        """Testing CompositeBuilder class."""
        def func_action(target, source, env):
            return 0
        
        builder = SCons.Builder.Builder(action={ '.foo' : func_action,
                                                 '.bar' : func_action })
        
        assert isinstance(builder, SCons.Builder.CompositeBuilder)
        assert isinstance(builder.action, SCons.Action.CommandGeneratorAction)
        tgt = builder(env, target='test1', source='test1.foo')
        assert isinstance(tgt.builder, SCons.Builder.BuilderBase)
        assert tgt.builder.action is builder.action
        tgt = builder(env, target='test2', source='test1.bar')
        assert isinstance(tgt.builder, SCons.Builder.BuilderBase)
        assert tgt.builder.action is builder.action
        flag = 0
        tgt = builder(env, target='test3', source=['test2.bar', 'test1.foo'])
        try:
            tgt.build()
        except SCons.Errors.UserError:
            flag = 1
        assert flag, "UserError should be thrown when we build targets with files of different suffixes."

        foo_bld = SCons.Builder.Builder(action = 'a-foo',
                                        src_suffix = '.ina',
                                        suffix = '.foo')
        assert isinstance(foo_bld, SCons.Builder.BuilderBase)
        builder = SCons.Builder.Builder(action = { '.foo' : 'foo',
                                                   '.bar' : 'bar' },
                                        src_builder = foo_bld)
        assert isinstance(builder, SCons.Builder.CompositeBuilder)
        assert isinstance(builder.action, SCons.Action.CommandGeneratorAction)

        tgt = builder(env, target='t1', source='t1a.ina t1b.ina')
        assert isinstance(tgt.builder, SCons.Builder.BuilderBase)

        tgt = builder(env, target='t2', source='t2a.foo t2b.ina')
        assert isinstance(tgt.builder, SCons.Builder.MultiStepBuilder), tgt.builder.__dict__

        bar_bld = SCons.Builder.Builder(action = 'a-bar',
                                        src_suffix = '.inb',
                                        suffix = '.bar')
        assert isinstance(bar_bld, SCons.Builder.BuilderBase)
        builder = SCons.Builder.Builder(action = { '.foo' : 'foo'},
                                        src_builder = [foo_bld, bar_bld])
        assert isinstance(builder, SCons.Builder.CompositeBuilder)
        assert isinstance(builder.action, SCons.Action.CommandGeneratorAction)

        builder.add_action('.bar', 'bar')

        tgt = builder(env, target='t3-foo', source='t3a.foo t3b.ina')
        assert isinstance(tgt.builder, SCons.Builder.MultiStepBuilder)

        tgt = builder(env, target='t3-bar', source='t3a.bar t3b.inb')
        assert isinstance(tgt.builder, SCons.Builder.MultiStepBuilder)

        flag = 0
        tgt = builder(env, target='t5', source='test5a.foo test5b.inb')
        try:
            tgt.build()
        except SCons.Errors.UserError:
            flag = 1
        assert flag, "UserError should be thrown when we build targets with files of different suffixes."

        flag = 0
        tgt = builder(env, target='t6', source='test6a.bar test6b.ina')
        try:
            tgt.build()
        except SCons.Errors.UserError:
            flag = 1
        assert flag, "UserError should be thrown when we build targets with files of different suffixes."

        flag = 0
        tgt = builder(env, target='t4', source='test4a.ina test4b.inb')
        try:
            tgt.build()
        except SCons.Errors.UserError:
            flag = 1
        assert flag, "UserError should be thrown when we build targets with files of different suffixes."

    def test_build_scanner(self):
        """Testing ability to set a target scanner through a builder."""
        global instanced
        class TestScanner:
            pass
        scn = TestScanner()
        builder = SCons.Builder.Builder(scanner=scn)
        tgt = builder(env, target='foo2', source='bar')
        assert tgt.target_scanner == scn, tgt.target_scanner

        builder1 = SCons.Builder.Builder(action='foo',
                                         src_suffix='.bar',
                                         suffix='.foo')
        builder2 = SCons.Builder.Builder(action='foo',
                                         src_builder = builder1,
                                         scanner = scn)
        tgt = builder2(env, target='baz2', source='test.bar test2.foo test3.txt')
        assert tgt.target_scanner == scn, tgt.target_scanner

    def test_src_scanner(slf):
        """Testing ability to set a source file scanner through a builder."""
        global env_scanner
        class TestScanner:
            def key(self, env):
                 return 'TestScannerkey'
            def instance(self, env):
                 return self
        env_scanner = TestScanner()
        builder = SCons.Builder.Builder(action='action')
        tgt = builder(env, target='foo.x', source='bar')
        src = tgt.sources[0]
        assert tgt.target_scanner != env_scanner, tgt.target_scanner
        assert src.source_scanner == env_scanner

    def test_Builder_Args(self):
        """Testing passing extra args to a builder."""
        def buildFunc(target, source, env, s=self):
            s.foo=env['foo']
            s.bar=env['bar']
            assert env['CC'] == 'mycc'

        env=Environment(CC='cc')

        builder = SCons.Builder.Builder(action=buildFunc)
        tgt = builder(env, target='foo', source='bar', foo=1, bar=2, CC='mycc')
        tgt.build()
        assert self.foo == 1, self.foo
        assert self.bar == 2, self.bar

    def test_emitter(self):
        """Test emitter functions."""
        def emit(target, source, env):
            foo = env.get('foo', 0)
            bar = env.get('bar', 0)
            if foo:
                target.append("bar%d"%foo)
            if bar:
                source.append("baz")
            return ( target, source )

        builder = SCons.Builder.Builder(action='foo',
                                        emitter=emit)
        tgt = builder(env, target='foo2', source='bar')
        assert str(tgt) == 'foo2', str(tgt)
        assert str(tgt.sources[0]) == 'bar', str(tgt.sources[0])

        tgt = builder(env, target='foo3', source='bar', foo=1)
        assert len(tgt) == 2, len(tgt)
        assert 'foo3' in map(str, tgt), map(str, tgt)
        assert 'bar1' in map(str, tgt), map(str, tgt)

        tgt = builder(env, target='foo4', source='bar', bar=1)
        assert str(tgt) == 'foo4', str(tgt)
        assert len(tgt.sources) == 2, len(tgt.sources)
        assert 'baz' in map(str, tgt.sources), map(str, tgt.sources)
        assert 'bar' in map(str, tgt.sources), map(str, tgt.sources)

        env2=Environment(FOO=emit)
        builder2=SCons.Builder.Builder(action='foo',
                                       emitter="$FOO")

        tgt = builder2(env2, target='foo5', source='bar')
        assert str(tgt) == 'foo5', str(tgt)
        assert str(tgt.sources[0]) == 'bar', str(tgt.sources[0])

        tgt = builder2(env2, target='foo6', source='bar', foo=2)
        assert len(tgt) == 2, len(tgt)
        assert 'foo6' in map(str, tgt), map(str, tgt)
        assert 'bar2' in map(str, tgt), map(str, tgt)

        tgt = builder2(env2, target='foo7', source='bar', bar=1)
        assert str(tgt) == 'foo7', str(tgt)
        assert len(tgt.sources) == 2, len(tgt.sources)
        assert 'baz' in map(str, tgt.sources), map(str, tgt.sources)
        assert 'bar' in map(str, tgt.sources), map(str, tgt.sources)

        builder2a=SCons.Builder.Builder(action='foo',
                                        emitter="$FOO")
        assert builder2 == builder2a, repr(builder2.__dict__) + "\n" + repr(builder2a.__dict__)

    def test_no_target(self):
        """Test deducing the target from the source."""

        b = SCons.Builder.Builder(action='foo', suffix='.o')

        tgt = b(env, 'aaa')
        assert str(tgt) == 'aaa.o', str(tgt)
        assert len(tgt.sources) == 1, map(str, tgt.sources)
        assert str(tgt.sources[0]) == 'aaa', map(str, tgt.sources)

        tgt = b(env, 'bbb.c')
        assert str(tgt) == 'bbb.o', str(tgt)
        assert len(tgt.sources) == 1, map(str, tgt.sources)
        assert str(tgt.sources[0]) == 'bbb.c', map(str, tgt.sources)

        tgt = b(env, 'ccc.x.c')
        assert str(tgt) == 'ccc.x.o', str(tgt)
        assert len(tgt.sources) == 1, map(str, tgt.sources)
        assert str(tgt.sources[0]) == 'ccc.x.c', map(str, tgt.sources)

        tgt = b(env, ['d0.c', 'd1.c'])
        assert str(tgt) == 'd0.o', str(tgt)
        assert len(tgt.sources) == 2,  map(str, tgt.sources)
        assert str(tgt.sources[0]) == 'd0.c', map(str, tgt.sources)
        assert str(tgt.sources[1]) == 'd1.c', map(str, tgt.sources)

        tgt = b(env, source='eee')
        assert str(tgt) == 'eee.o', str(tgt)
        assert len(tgt.sources) == 1, map(str, tgt.sources)
        assert str(tgt.sources[0]) == 'eee', map(str, tgt.sources)

        tgt = b(env, source='fff.c')
        assert str(tgt) == 'fff.o', str(tgt)
        assert len(tgt.sources) == 1, map(str, tgt.sources)
        assert str(tgt.sources[0]) == 'fff.c', map(str, tgt.sources)

        tgt = b(env, source='ggg.x.c')
        assert str(tgt) == 'ggg.x.o', str(tgt)
        assert len(tgt.sources) == 1, map(str, tgt.sources)
        assert str(tgt.sources[0]) == 'ggg.x.c', map(str, tgt.sources)

        tgt = b(env, source=['h0.c', 'h1.c'])
        assert str(tgt) == 'h0.o', str(tgt)
        assert len(tgt.sources) == 2,  map(str, tgt.sources)
        assert str(tgt.sources[0]) == 'h0.c', map(str, tgt.sources)
        assert str(tgt.sources[1]) == 'h1.c', map(str, tgt.sources)

        w = b(env, target='i0.w', source=['i0.x'])
        y = b(env, target='i1.y', source=['i1.z'])
        tgt = b(env, source=[w, y])
        assert str(tgt) == 'i0.o', str(tgt)
        assert len(tgt.sources) == 2, map(str, tgt.sources)
        assert str(tgt.sources[0]) == 'i0.w', map(str, tgt.sources)
        assert str(tgt.sources[1]) == 'i1.y', map(str, tgt.sources)


if __name__ == "__main__":
    suite = unittest.makeSuite(BuilderTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
