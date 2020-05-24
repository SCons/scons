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

import SCons.compat

# Define a null function for use as a builder action.
# Where this is defined in the file seems to affect its
# byte-code contents, so try to minimize changes by
# defining it here, before we even import anything.
def Func():
    pass

from collections import UserList
import io
import os.path
import re
import sys
import unittest

import TestCmd
import TestUnit

import SCons.Action
import SCons.Builder
import SCons.Environment
import SCons.Errors
import SCons.Subst
import SCons.Util

sys.stdout = io.StringIO()

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

infile = test.workpath('infile')
test.write(infile, "infile\n")

show_string = None

scons_env = SCons.Environment.Environment()

env_arg2nodes_called = None

class Environment:
    def __init__(self, **kw):
        self.d = {}
        self.d['SHELL'] = scons_env['SHELL']
        self.d['SPAWN'] = scons_env['SPAWN']
        self.d['ESCAPE'] = scons_env['ESCAPE']
        for k, v in kw.items():
            self.d[k] = v
        global env_arg2nodes_called
        env_arg2nodes_called = None
        self.scanner = None
        self.fs = SCons.Node.FS.FS()
    def subst(self, s):
        if not SCons.Util.is_String(s):
            return s
        def substitute(m, d=self.d):
            return d.get(m.group(1), '')
        return re.sub(r'\$(\w+)', substitute, s)
    def subst_target_source(self, string, raw=0, target=None,
                            source=None, dict=None, conv=None):
        return SCons.Subst.scons_subst(string, self, raw, target,
                                       source, dict, conv)
    def subst_list(self, string, raw=0, target=None, source=None, conv=None):
        return SCons.Subst.scons_subst_list(string, self, raw, target,
                                            source, {}, {}, conv)
    def arg2nodes(self, args, factory, **kw):
        global env_arg2nodes_called
        env_arg2nodes_called = 1
        if not SCons.Util.is_List(args):
            args = [args]
        list = []
        for a in args:
            if SCons.Util.is_String(a):
                a = factory(self.subst(a))
            list.append(a)
        return list
    def get_factory(self, factory):
        return factory or self.fs.File
    def get_scanner(self, ext):
        return self.scanner
    def Dictionary(self):
        return {}
    def autogenerate(self, dir=''):
        return {}
    def __setitem__(self, item, var):
        self.d[item] = var
    def __getitem__(self, item):
        return self.d[item]
    def __contains__(self, item):
        return self.d.__contains__(item)
    def has_key(self, item):
        return item in self.d
    def keys(self):
        return list(self.d.keys())
    def get(self, key, value=None):
        return self.d.get(key, value)
    def Override(self, overrides):
        env = Environment(**self.d)
        env.d.update(overrides)
        env.scanner = self.scanner
        return env
    def _update(self, dict):
        self.d.update(dict)
    def items(self):
        return list(self.d.items())
    def sig_dict(self):
        d = {}
        for k,v in self.items(): d[k] = v
        d['TARGETS'] = ['__t1__', '__t2__', '__t3__', '__t4__', '__t5__', '__t6__']
        d['TARGET'] = d['TARGETS'][0]
        d['SOURCES'] = ['__s1__', '__s2__', '__s3__', '__s4__', '__s5__', '__s6__']
        d['SOURCE'] = d['SOURCES'][0]
        return d
    def __eq__(self, other):
        return self.scanner == other.scanner or self.d == other.d

class MyAction:
    def __init__(self, action):
        self.action = action
    def __call__(self, *args, **kw):
        pass
    def get_executor(self, env, overrides, tlist, slist, executor_kw):
        return ['executor'] + [self.action]

class MyNode_without_target_from_source:
    def __init__(self, name):
        self.name = name
        self.sources = []
        self.builder = None
        self.is_explicit = None
        self.side_effect = 0
    def get_suffix(self):
        return os.path.splitext(self.name)[1]
    def disambiguate(self):
        return self
    def __str__(self):
        return self.name
    def builder_set(self, builder):
        self.builder = builder
    def has_builder(self):
        return self.builder is not None
    def set_explicit(self, is_explicit):
        self.is_explicit = is_explicit
    def has_explicit_builder(self):
        return self.is_explicit
    def env_set(self, env, safe=0):
        self.env = env
    def add_source(self, source):
        self.sources.extend(source)
    def scanner_key(self):
        return self.name
    def is_derived(self):
        return self.has_builder()
    def generate_build_env(self, env):
        return env
    def get_build_env(self):
        return self.executor.get_build_env()
    def set_executor(self, executor):
        self.executor = executor
    def get_executor(self, create=1):
        return self.executor

class MyNode(MyNode_without_target_from_source):
    def target_from_source(self, prefix, suffix, stripext):
        return MyNode(prefix + stripext(str(self))[0] + suffix)

class BuilderTestCase(unittest.TestCase):

    def test__init__(self):
        """Test simple Builder creation
        """
        builder = SCons.Builder.Builder(action="foo")
        assert builder is not None, builder
        builder = SCons.Builder.Builder(action="foo", OVERRIDE='x')
        x = builder.overrides['OVERRIDE']
        assert x == 'x', x

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
        env = Environment()
        builder = SCons.Builder.Builder(action="foo",
                                        target_factory=MyNode,
                                        source_factory=MyNode)

        tgt = builder(env, source=[])
        assert tgt == [], tgt

        n1 = MyNode("n1")
        n2 = MyNode("n2")
        builder(env, target = n1, source = n2)
        assert env_arg2nodes_called
        assert n1.env == env, n1.env
        assert n1.builder == builder, n1.builder
        assert n1.sources == [n2], n1.sources
        assert n1.executor, "no executor found"
        assert not hasattr(n2, 'env')

        l = [1]
        ul = UserList([2])
        try:
            l.extend(ul)
        except TypeError:
            def mystr(l):
                return str(list(map(str, l)))
        else:
            mystr = str

        nnn1 = MyNode("nnn1")
        nnn2 = MyNode("nnn2")
        tlist = builder(env, target = [nnn1, nnn2], source = [])
        s = mystr(tlist)
        assert s == "['nnn1', 'nnn2']", s
        l = list(map(str, tlist))
        assert l == ['nnn1', 'nnn2'], l

        tlist = builder(env, target = 'n3', source = 'n4')
        s = mystr(tlist)
        assert s == "['n3']", s
        target = tlist[0]
        l = list(map(str, tlist))
        assert l == ['n3'], l
        assert target.name == 'n3'
        assert target.sources[0].name == 'n4'

        tlist = builder(env, target = 'n4 n5', source = ['n6 n7'])
        s = mystr(tlist)
        assert s == "['n4 n5']", s
        l = list(map(str, tlist))
        assert l == ['n4 n5'], l
        target = tlist[0]
        assert target.name == 'n4 n5'
        assert target.sources[0].name == 'n6 n7'

        tlist = builder(env, target = ['n8 n9'], source = 'n10 n11')
        s = mystr(tlist)
        assert s == "['n8 n9']", s
        l = list(map(str, tlist))
        assert l == ['n8 n9'], l
        target = tlist[0]
        assert target.name == 'n8 n9'
        assert target.sources[0].name == 'n10 n11'

        # A test to be uncommented when we freeze the environment
        # as part of calling the builder.
        #env1 = Environment(VAR='foo')
        #target = builder(env1, target = 'n12', source = 'n13')
        #env1['VAR'] = 'bar'
        #be = target.get_build_env()
        #assert be['VAR'] == 'foo', be['VAR']

        n20 = MyNode_without_target_from_source('n20')
        flag = 0
        try:
            target = builder(env, None, source=n20)
        except SCons.Errors.UserError as e:
            flag = 1
        assert flag, "UserError should be thrown if a source node can't create a target."

        builder = SCons.Builder.Builder(action="foo",
                                        target_factory=MyNode,
                                        source_factory=MyNode,
                                        prefix='p-',
                                        suffix='.s')
        target = builder(env, None, source='n21')[0]
        assert target.name == 'p-n21.s', target

        builder = SCons.Builder.Builder(misspelled_action="foo",
                                        suffix = '.s')
        try:
            builder(env, target = 'n22', source = 'n22')
        except SCons.Errors.UserError as e:
            pass
        else:
            raise Exception("Did not catch expected UserError.")

        builder = SCons.Builder.Builder(action="foo")
        target = builder(env, None, source='n22', srcdir='src_dir')[0]
        p = target.sources[0].get_internal_path()
        assert p == os.path.join('src_dir', 'n22'), p

    def test_mistaken_variables(self):
        """Test keyword arguments that are often mistakes
        """
        import SCons.Warnings
        env = Environment()
        builder = SCons.Builder.Builder(action="foo")

        save_warn = SCons.Warnings.warn
        warned = []
        def my_warn(exception, warning, warned=warned):
            warned.append(warning)
        SCons.Warnings.warn = my_warn

        try:
            target = builder(env, 'mistaken1', sources='mistaken1.c')
            assert warned == ["Did you mean to use `source' instead of `sources'?"], warned
            del warned[:]

            target = builder(env, 'mistaken2', targets='mistaken2.c')
            assert warned == ["Did you mean to use `target' instead of `targets'?"], warned
            del warned[:]

            target = builder(env, 'mistaken3', targets='mistaken3', sources='mistaken3.c')
            assert "Did you mean to use `source' instead of `sources'?" in warned, warned
            assert "Did you mean to use `target' instead of `targets'?" in warned, warned
            del warned[:]
        finally:
            SCons.Warnings.warn = save_warn

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
        assert builder.source_factory is not FooFactory

    def test_source_factory(self):
        """Test a Builder that creates source nodes of a specified class
        """
        class Foo:
            pass
        def FooFactory(source):
            global Foo
            return Foo(source)
        builder = SCons.Builder.Builder(source_factory = FooFactory)
        assert builder.target_factory is not FooFactory
        assert builder.source_factory is FooFactory

    def test_splitext(self):
        """Test the splitext() method attached to a Builder."""
        b = SCons.Builder.Builder()
        assert b.splitext('foo') == ('foo','')
        assert b.splitext('foo.bar') == ('foo','.bar')
        assert b.splitext(os.path.join('foo.bar', 'blat')) == (os.path.join('foo.bar', 'blat'),'')

        class MyBuilder(SCons.Builder.BuilderBase):
            def splitext(self, path):
                return "called splitext()"

        b = MyBuilder()
        ret = b.splitext('xyz.c')
        assert ret == "called splitext()", ret

    def test_adjust_suffix(self):
        """Test how a Builder adjusts file suffixes
        """
        b = SCons.Builder.Builder()
        assert b.adjust_suffix('.foo') == '.foo'
        assert b.adjust_suffix('foo') == '.foo'
        assert b.adjust_suffix('$foo') == '$foo'

        class MyBuilder(SCons.Builder.BuilderBase):
            def adjust_suffix(self, suff):
                return "called adjust_suffix()"

        b = MyBuilder()
        ret = b.adjust_suffix('.foo')
        assert ret == "called adjust_suffix()", ret

    def test_prefix(self):
        """Test Builder creation with a specified target prefix

        Make sure that there is no '.' separator appended.
        """
        env = Environment()
        builder = SCons.Builder.Builder(prefix = 'lib.')
        assert builder.get_prefix(env) == 'lib.'
        builder = SCons.Builder.Builder(prefix = 'lib', action='')
        assert builder.get_prefix(env) == 'lib'
        tgt = builder(env, target = 'tgt1', source = 'src1')[0]
        assert tgt.get_internal_path() == 'libtgt1', \
                "Target has unexpected name: %s" % tgt.get_internal_path()
        tgt = builder(env, target = 'tgt2a tgt2b', source = 'src2')[0]
        assert tgt.get_internal_path() == 'libtgt2a tgt2b', \
                "Target has unexpected name: %s" % tgt.get_internal_path()
        tgt = builder(env, target = None, source = 'src3')[0]
        assert tgt.get_internal_path() == 'libsrc3', \
                "Target has unexpected name: %s" % tgt.get_internal_path()
        tgt = builder(env, target = None, source = 'lib/src4')[0]
        assert tgt.get_internal_path() == os.path.join('lib', 'libsrc4'), \
                "Target has unexpected name: %s" % tgt.get_internal_path()
        tgt = builder(env, target = 'lib/tgt5', source = 'lib/src5')[0]
        assert tgt.get_internal_path() == os.path.join('lib', 'libtgt5'), \
                "Target has unexpected name: %s" % tgt.get_internal_path()

        def gen_prefix(env, sources):
            return "gen_prefix() says " + env['FOO']
        my_env = Environment(FOO = 'xyzzy')
        builder = SCons.Builder.Builder(prefix = gen_prefix)
        assert builder.get_prefix(my_env) == "gen_prefix() says xyzzy"
        my_env['FOO'] = 'abracadabra'
        assert builder.get_prefix(my_env) == "gen_prefix() says abracadabra"

        def my_emit(env, sources):
            return env.subst('$EMIT')
        my_env = Environment(FOO = '.foo', EMIT = 'emit-')
        builder = SCons.Builder.Builder(prefix = {None   : 'default-',
                                                  '.in'  : 'out-',
                                                  '.x'   : 'y-',
                                                  '$FOO' : 'foo-',
                                                  '.zzz' : my_emit},
                                        action = '')
        tgt = builder(my_env, target = None, source = 'f1')[0]
        assert tgt.get_internal_path() == 'default-f1', tgt.get_internal_path()
        tgt = builder(my_env, target = None, source = 'f2.c')[0]
        assert tgt.get_internal_path() == 'default-f2', tgt.get_internal_path()
        tgt = builder(my_env, target = None, source = 'f3.in')[0]
        assert tgt.get_internal_path() == 'out-f3', tgt.get_internal_path()
        tgt = builder(my_env, target = None, source = 'f4.x')[0]
        assert tgt.get_internal_path() == 'y-f4', tgt.get_internal_path()
        tgt = builder(my_env, target = None, source = 'f5.foo')[0]
        assert tgt.get_internal_path() == 'foo-f5', tgt.get_internal_path()
        tgt = builder(my_env, target = None, source = 'f6.zzz')[0]
        assert tgt.get_internal_path() == 'emit-f6', tgt.get_internal_path()

    def test_set_suffix(self):
        """Test the set_suffix() method"""
        b = SCons.Builder.Builder(action='')
        env = Environment(XSUFFIX = '.x')

        s = b.get_suffix(env)
        assert s == '', s

        b.set_suffix('.foo')
        s = b.get_suffix(env)
        assert s == '.foo', s

        b.set_suffix('$XSUFFIX')
        s = b.get_suffix(env)
        assert s == '.x', s

    def test_src_suffix(self):
        """Test Builder creation with a specified source file suffix

        Make sure that the '.' separator is appended to the
        beginning if it isn't already present.
        """
        env = Environment(XSUFFIX = '.x', YSUFFIX = '.y')

        b1 = SCons.Builder.Builder(src_suffix = '.c', action='')
        assert b1.src_suffixes(env) == ['.c'], b1.src_suffixes(env)

        tgt = b1(env, target = 'tgt2', source = 'src2')[0]
        assert tgt.sources[0].get_internal_path() == 'src2.c', \
                "Source has unexpected name: %s" % tgt.sources[0].get_internal_path()

        tgt = b1(env, target = 'tgt3', source = 'src3a src3b')[0]
        assert len(tgt.sources) == 1
        assert tgt.sources[0].get_internal_path() == 'src3a src3b.c', \
                "Unexpected tgt.sources[0] name: %s" % tgt.sources[0].get_internal_path()

        b2 = SCons.Builder.Builder(src_suffix = '.2', src_builder = b1)
        r = sorted(b2.src_suffixes(env))
        assert r == ['.2', '.c'], r

        b3 = SCons.Builder.Builder(action = {'.3a' : '', '.3b' : ''})
        s = sorted(b3.src_suffixes(env))
        assert s == ['.3a', '.3b'], s

        b4 = SCons.Builder.Builder(src_suffix = '$XSUFFIX')
        assert b4.src_suffixes(env) == ['.x'], b4.src_suffixes(env)

        b5 = SCons.Builder.Builder(action = { '.y' : ''})
        assert b5.src_suffixes(env) == ['.y'], b5.src_suffixes(env)

    def test_srcsuffix_nonext(self):
        """Test target generation from non-extension source suffixes"""
        env = Environment()
        b6 = SCons.Builder.Builder(action = '',
                                   src_suffix='_src.a',
                                   suffix='.b')
        tgt = b6(env, target=None, source='foo_src.a')
        assert str(tgt[0]) == 'foo.b', str(tgt[0])

        b7 = SCons.Builder.Builder(action = '',
                                   src_suffix='_source.a',
                                   suffix='_obj.b')
        b8 = SCons.Builder.Builder(action = '',
                                   src_builder=b7,
                                   suffix='.c')
        tgt = b8(env, target=None, source='foo_source.a')
        assert str(tgt[0]) == 'foo_obj.c', str(tgt[0])
        src = env.fs.File('foo_source.a')
        tgt = b8(env, target=None, source=src)
        assert str(tgt[0]) == 'foo_obj.c', str(tgt[0])

        b9 = SCons.Builder.Builder(action={'_src.a' : 'srcaction'},
                                   suffix='.c')
        b9.add_action('_altsrc.b', 'altaction')
        tgt = b9(env, target=None, source='foo_altsrc.b')
        assert str(tgt[0]) == 'foo.c', str(tgt[0])

    def test_src_suffix_expansion(self):
        """Test handling source suffixes when an expansion is involved"""
        env = Environment(OBJSUFFIX = '.obj')

        b1 = SCons.Builder.Builder(action = '',
                                   src_suffix='.c',
                                   suffix='.obj')
        b2 = SCons.Builder.Builder(action = '',
                                   src_builder=b1,
                                   src_suffix='.obj',
                                   suffix='.exe')
        tgt = b2(env, target=None, source=['foo$OBJSUFFIX'])
        s = list(map(str, tgt[0].sources))
        assert s == ['foo.obj'], s

    def test_suffix(self):
        """Test Builder creation with a specified target suffix

        Make sure that the '.' separator is appended to the
        beginning if it isn't already present.
        """
        env = Environment()
        builder = SCons.Builder.Builder(suffix = '.o')
        assert builder.get_suffix(env) == '.o', builder.get_suffix(env)
        builder = SCons.Builder.Builder(suffix = 'o', action='')
        assert builder.get_suffix(env) == '.o', builder.get_suffix(env)
        tgt = builder(env, target = 'tgt3', source = 'src3')[0]
        assert tgt.get_internal_path() == 'tgt3.o', \
                "Target has unexpected name: %s" % tgt.get_internal_path()
        tgt = builder(env, target = 'tgt4a tgt4b', source = 'src4')[0]
        assert tgt.get_internal_path() == 'tgt4a tgt4b.o', \
                "Target has unexpected name: %s" % tgt.get_internal_path()
        tgt = builder(env, target = None, source = 'src5')[0]
        assert tgt.get_internal_path() == 'src5.o', \
                "Target has unexpected name: %s" % tgt.get_internal_path()

        def gen_suffix(env, sources):
            return "gen_suffix() says " + env['BAR']
        my_env = Environment(BAR = 'hocus pocus')
        builder = SCons.Builder.Builder(suffix = gen_suffix)
        assert builder.get_suffix(my_env) == "gen_suffix() says hocus pocus", builder.get_suffix(my_env)
        my_env['BAR'] = 'presto chango'
        assert builder.get_suffix(my_env) == "gen_suffix() says presto chango"

        def my_emit(env, sources):
            return env.subst('$EMIT')
        my_env = Environment(BAR = '.bar', EMIT = '.emit')
        builder = SCons.Builder.Builder(suffix = {None   : '.default',
                                                  '.in'  : '.out',
                                                  '.x'   : '.y',
                                                  '$BAR' : '.new',
                                                  '.zzz' : my_emit},
                                        action='')
        tgt = builder(my_env, target = None, source = 'f1')[0]
        assert tgt.get_internal_path() == 'f1.default', tgt.get_internal_path()
        tgt = builder(my_env, target = None, source = 'f2.c')[0]
        assert tgt.get_internal_path() == 'f2.default', tgt.get_internal_path()
        tgt = builder(my_env, target = None, source = 'f3.in')[0]
        assert tgt.get_internal_path() == 'f3.out', tgt.get_internal_path()
        tgt = builder(my_env, target = None, source = 'f4.x')[0]
        assert tgt.get_internal_path() == 'f4.y', tgt.get_internal_path()
        tgt = builder(my_env, target = None, source = 'f5.bar')[0]
        assert tgt.get_internal_path() == 'f5.new', tgt.get_internal_path()
        tgt = builder(my_env, target = None, source = 'f6.zzz')[0]
        assert tgt.get_internal_path() == 'f6.emit', tgt.get_internal_path()

    def test_single_source(self):
        """Test Builder with single_source flag set"""
        def func(target, source, env):
            """create the file"""
            with open(str(target[0]), "w"):
                pass
            if len(source) == 1 and len(target) == 1:
                env['CNT'][0] = env['CNT'][0] + 1

        env = Environment()
        infiles = []
        outfiles = []
        for i in range(10):
            infiles.append(test.workpath('%d.in' % i))
            outfiles.append(test.workpath('%d.out' % i))
            test.write(infiles[-1], "\n")
        builder = SCons.Builder.Builder(action=SCons.Action.Action(func,None),
                                        single_source = 1, suffix='.out')
        env['CNT'] = [0]
        tgt = builder(env, target=outfiles[0], source=infiles[0])[0]
        s = str(tgt)
        t = os.path.normcase(test.workpath('0.out'))
        assert os.path.normcase(s) == t, s
        tgt.prepare()
        tgt.build()
        assert env['CNT'][0] == 1, env['CNT'][0]
        tgt = builder(env, outfiles[1], infiles[1])[0]
        s = str(tgt)
        t = os.path.normcase(test.workpath('1.out'))
        assert os.path.normcase(s) == t, s
        tgt.prepare()
        tgt.build()
        assert env['CNT'][0] == 2
        tgts = builder(env, None, infiles[2:4])
        s = list(map(str, tgts))
        expect = [test.workpath('2.out'), test.workpath('3.out')]
        expect = list(map(os.path.normcase, expect))
        assert list(map(os.path.normcase, s)) == expect, s
        for t in tgts: t.prepare()
        tgts[0].build()
        tgts[1].build()
        assert env['CNT'][0] == 4
        try:
            tgt = builder(env, outfiles[4], infiles[4:6])
        except SCons.Errors.UserError:
            pass
        else:
            assert 0
        try:
            # The builder may output more than one target per input file.
            tgt = builder(env, outfiles[4:6], infiles[4:6])
        except SCons.Errors.UserError:
            pass
        else:
            assert 0


    def test_lists(self):
        """Testing handling lists of targets and source"""
        def function2(target, source, env, tlist = [outfile, outfile2], **kw):
            for t in target:
                with open(str(t), 'w') as f:
                    f.write("function2\n")
            for t in tlist:
                if t not in list(map(str, target)):
                    with open(t, 'w') as f:
                        f.write("function2\n")
            return 1

        env = Environment()
        builder = SCons.Builder.Builder(action = function2)

        tgts = builder(env, source=[])
        assert tgts == [], tgts

        tgts = builder(env, target = [outfile, outfile2], source = infile)
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
                with open(str(t), 'w') as f:
                    f.write("function3\n")
            for t in tlist:
                if t not in list(map(str, target)):
                    with open(t, 'w') as f:
                        f.write("function3\n")
            return 1

        builder = SCons.Builder.Builder(action = function3)
        tgts = builder(env, target = [sub1_out, sub2_out], source = infile)
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

    def test_src_builder(self):
        """Testing Builders with src_builder"""
        # These used to be MultiStepBuilder objects until we
        # eliminated it as a separate class
        env = Environment()
        builder1 = SCons.Builder.Builder(action='foo',
                                         src_suffix='.bar',
                                         suffix='.foo')
        builder2 = SCons.Builder.Builder(action=MyAction('act'),
                                         src_builder = builder1,
                                         src_suffix = '.foo')

        tgt = builder2(env, source=[])
        assert tgt == [], tgt

        sources = ['test.bar', 'test2.foo', 'test3.txt', 'test4']
        tgt = builder2(env, target='baz', source=sources)[0]
        s = str(tgt)
        assert s == 'baz', s
        s = list(map(str, tgt.sources))
        assert s == ['test.foo', 'test2.foo', 'test3.txt', 'test4.foo'], s
        s = list(map(str, tgt.sources[0].sources))
        assert s == ['test.bar'], s

        tgt = builder2(env, None, 'aaa.bar')[0]
        s = str(tgt)
        assert s == 'aaa', s
        s = list(map(str, tgt.sources))
        assert s == ['aaa.foo'], s
        s = list(map(str, tgt.sources[0].sources))
        assert s == ['aaa.bar'], s

        builder3 = SCons.Builder.Builder(action='bld3')
        assert builder3.src_builder is not builder1.src_builder

        builder4 = SCons.Builder.Builder(action='bld4',
                                         src_suffix='.i',
                                         suffix='_wrap.c')
        builder5 = SCons.Builder.Builder(action=MyAction('act'),
                                         src_builder=builder4,
                                         suffix='.obj',
                                         src_suffix='.c')
        builder6 = SCons.Builder.Builder(action=MyAction('act'),
                                         src_builder=builder5,
                                         suffix='.exe',
                                         src_suffix='.obj')
        tgt = builder6(env, 'test', 'test.i')[0]
        s = str(tgt)
        assert s == 'test.exe', s
        s = list(map(str, tgt.sources))
        assert s == ['test_wrap.obj'], s
        s = list(map(str, tgt.sources[0].sources))
        assert s == ['test_wrap.c'], s
        s = list(map(str, tgt.sources[0].sources[0].sources))
        assert s == ['test.i'], s

    def test_target_scanner(self):
        """Testing ability to set target and source scanners through a builder."""
        global instanced
        class TestScanner:
            pass
        tscan = TestScanner()
        sscan = TestScanner()
        env = Environment()
        builder = SCons.Builder.Builder(target_scanner=tscan,
                                        source_scanner=sscan,
                                        action='')
        tgt = builder(env, target='foo2', source='bar')[0]
        assert tgt.builder.target_scanner == tscan, tgt.builder.target_scanner
        assert tgt.builder.source_scanner == sscan, tgt.builder.source_scanner

        builder1 = SCons.Builder.Builder(action='foo',
                                         src_suffix='.bar',
                                         suffix='.foo')
        builder2 = SCons.Builder.Builder(action='foo',
                                         src_builder = builder1,
                                         target_scanner = tscan,
                                         source_scanner = tscan)
        tgt = builder2(env, target='baz2', source='test.bar test2.foo test3.txt')[0]
        assert tgt.builder.target_scanner == tscan, tgt.builder.target_scanner
        assert tgt.builder.source_scanner == tscan, tgt.builder.source_scanner

    def test_actual_scanner(self):
        """Test usage of actual Scanner objects."""

        import SCons.Scanner

        def func(self):
            pass

        scanner = SCons.Scanner.Base(func, name='fooscan')

        b1 = SCons.Builder.Builder(action='bld', target_scanner=scanner)
        b2 = SCons.Builder.Builder(action='bld', target_scanner=scanner)
        b3 = SCons.Builder.Builder(action='bld')

        assert b1 == b2
        assert b1 != b3

    def test_src_scanner(self):
        """Testing ability to set a source file scanner through a builder."""
        class TestScanner:
            def key(self, env):
                 return 'TestScannerkey'
            def instance(self, env):
                 return self
            def select(self, node):
                 return self
            name = 'TestScanner'
            def __str__(self):
                return self.name

        scanner = TestScanner()
        builder = SCons.Builder.Builder(action='action')

        # With no scanner specified, source_scanner and
        # backup_source_scanner are None.
        bar_y = MyNode('bar.y')
        env1 = Environment()
        tgt = builder(env1, target='foo1.x', source='bar.y')[0]
        src = tgt.sources[0]
        assert tgt.builder.target_scanner != scanner, tgt.builder.target_scanner
        assert tgt.builder.source_scanner is None, tgt.builder.source_scanner
        assert tgt.get_source_scanner(bar_y) is None, tgt.get_source_scanner(bar_y)
        assert not src.has_builder(), src.has_builder()
        s = src.get_source_scanner(bar_y)
        assert isinstance(s, SCons.Util.Null), repr(s)

        # An Environment that has suffix-specified SCANNERS should
        # provide a source scanner to the target.
        class EnvTestScanner:
            def key(self, env):
                 return '.y'
            def instance(self, env):
                 return self
            name = 'EnvTestScanner'
            def __str__(self):
                return self.name
            def select(self, node):
                return self
            def path(self, env, dir=None):
                return ()
            def __call__(self, node, env, path):
                return []
        env3 = Environment(SCANNERS = [EnvTestScanner()])
        env3.scanner = EnvTestScanner() # test env's version of SCANNERS
        tgt = builder(env3, target='foo2.x', source='bar.y')[0]
        src = tgt.sources[0]
        assert tgt.builder.target_scanner != scanner, tgt.builder.target_scanner
        assert not tgt.builder.source_scanner, tgt.builder.source_scanner
        assert tgt.get_source_scanner(bar_y), tgt.get_source_scanner(bar_y)
        assert str(tgt.get_source_scanner(bar_y)) == 'EnvTestScanner', tgt.get_source_scanner(bar_y)
        assert not src.has_builder(), src.has_builder()
        s = src.get_source_scanner(bar_y)
        assert isinstance(s, SCons.Util.Null), repr(s)

        # Can't simply specify the scanner as a builder argument; it's
        # global to all invocations of this builder.
        tgt = builder(env3, target='foo3.x', source='bar.y', source_scanner = scanner)[0]
        src = tgt.sources[0]
        assert tgt.builder.target_scanner != scanner, tgt.builder.target_scanner
        assert not tgt.builder.source_scanner, tgt.builder.source_scanner
        assert tgt.get_source_scanner(bar_y), tgt.get_source_scanner(bar_y)
        assert str(tgt.get_source_scanner(bar_y)) == 'EnvTestScanner', tgt.get_source_scanner(bar_y)
        assert not src.has_builder(), src.has_builder()
        s = src.get_source_scanner(bar_y)
        assert isinstance(s, SCons.Util.Null), s

        # Now use a builder that actually has scanners and ensure that
        # the target is set accordingly (using the specified scanner
        # instead of the Environment's scanner)
        builder = SCons.Builder.Builder(action='action',
                                        source_scanner=scanner,
                                        target_scanner=scanner)
        tgt = builder(env3, target='foo4.x', source='bar.y')[0]
        src = tgt.sources[0]
        assert tgt.builder.target_scanner == scanner, tgt.builder.target_scanner
        assert tgt.builder.source_scanner, tgt.builder.source_scanner
        assert tgt.builder.source_scanner == scanner, tgt.builder.source_scanner
        assert str(tgt.builder.source_scanner) == 'TestScanner', str(tgt.builder.source_scanner)
        assert tgt.get_source_scanner(bar_y), tgt.get_source_scanner(bar_y)
        assert tgt.get_source_scanner(bar_y) == scanner, tgt.get_source_scanner(bar_y)
        assert str(tgt.get_source_scanner(bar_y)) == 'TestScanner', tgt.get_source_scanner(bar_y)
        assert not src.has_builder(), src.has_builder()
        s = src.get_source_scanner(bar_y)
        assert isinstance(s, SCons.Util.Null), s



    def test_Builder_API(self):
        """Test Builder interface.

        Some of this is tested elsewhere in this file, but this is a
        quick collection of common operations on builders with various
        forms of component specifications."""

        builder = SCons.Builder.Builder()
        env = Environment(BUILDERS={'Bld':builder})

        r = builder.get_name(env)
        assert r == 'Bld', r
        r = builder.get_prefix(env)
        assert r == '', r
        r = builder.get_suffix(env)
        assert r == '', r
        r = builder.get_src_suffix(env)
        assert r == '', r
        r = builder.src_suffixes(env)
        assert r == [], r

        # src_suffix can be a single string or a list of strings
        # src_suffixes() caches its return value, so we use a new
        # Builder each time we do any of these tests

        bld = SCons.Builder.Builder()
        env = Environment(BUILDERS={'Bld':bld})

        bld.set_src_suffix('.foo')
        r = bld.get_src_suffix(env)
        assert r == '.foo', r
        r = bld.src_suffixes(env)
        assert r == ['.foo'], r

        bld = SCons.Builder.Builder()
        env = Environment(BUILDERS={'Bld':bld})

        bld.set_src_suffix(['.foo', '.bar'])
        r = bld.get_src_suffix(env)
        assert r == '.foo', r
        r = bld.src_suffixes(env)
        assert r == ['.foo', '.bar'], r

        bld = SCons.Builder.Builder()
        env = Environment(BUILDERS={'Bld':bld})

        bld.set_src_suffix(['.bar', '.foo'])
        r = bld.get_src_suffix(env)
        assert r == '.bar', r
        r = sorted(bld.src_suffixes(env))
        assert r == ['.bar', '.foo'], r

        # adjust_suffix normalizes the suffix, adding a `.' if needed

        r = builder.adjust_suffix('.foo')
        assert r == '.foo', r
        r = builder.adjust_suffix('_foo')
        assert r == '_foo', r
        r = builder.adjust_suffix('$foo')
        assert r == '$foo', r
        r = builder.adjust_suffix('foo')
        assert r == '.foo', r
        r = builder.adjust_suffix('f._$oo')
        assert r == '.f._$oo', r

        # prefix and suffix can be one of:
        #   1. a string (adjusted and env variables substituted),
        #   2. a function (passed (env,sources), returns suffix string)
        #   3. a dict of src_suffix:suffix settings, key==None is
        #      default suffix (special case of #2, so adjust_suffix
        #      not applied)

        builder = SCons.Builder.Builder(prefix='lib', suffix='foo')

        env = Environment(BUILDERS={'Bld':builder})
        r = builder.get_name(env)
        assert r == 'Bld', r
        r = builder.get_prefix(env)
        assert r == 'lib', r
        r = builder.get_suffix(env)
        assert r == '.foo', r

        mkpref = lambda env,sources: 'Lib'
        mksuff = lambda env,sources: '.Foo'
        builder = SCons.Builder.Builder(prefix=mkpref, suffix=mksuff)

        env = Environment(BUILDERS={'Bld':builder})
        r = builder.get_name(env)
        assert r == 'Bld', r
        r = builder.get_prefix(env)
        assert r == 'Lib', r
        r = builder.get_suffix(env)
        assert r == '.Foo', r

        builder = SCons.Builder.Builder(prefix='$PREF', suffix='$SUFF')

        env = Environment(BUILDERS={'Bld':builder},PREF="LIB",SUFF=".FOO")
        r = builder.get_name(env)
        assert r == 'Bld', r
        r = builder.get_prefix(env)
        assert r == 'LIB', r
        r = builder.get_suffix(env)
        assert r == '.FOO', r

        builder = SCons.Builder.Builder(prefix={None:'A_',
                                                '.C':'E_'},
                                        suffix={None:'.B',
                                                '.C':'.D'})

        env = Environment(BUILDERS={'Bld':builder})
        r = builder.get_name(env)
        assert r == 'Bld', r
        r = builder.get_prefix(env)
        assert r == 'A_', r
        r = builder.get_suffix(env)
        assert r == '.B', r
        r = builder.get_prefix(env, [MyNode('X.C')])
        assert r == 'E_', r
        r = builder.get_suffix(env, [MyNode('X.C')])
        assert r == '.D', r

        builder = SCons.Builder.Builder(prefix='A_', suffix={}, action={})
        env = Environment(BUILDERS={'Bld':builder})

        r = builder.get_name(env)
        assert r == 'Bld', r
        r = builder.get_prefix(env)
        assert r == 'A_', r
        r = builder.get_suffix(env)
        assert r is None, r
        r = builder.get_src_suffix(env)
        assert r == '', r
        r = builder.src_suffixes(env)
        assert r == [], r

        # Builder actions can be a string, a list, or a dictionary
        # whose keys are the source suffix.  The add_action()
        # specifies a new source suffix/action binding.

        builder = SCons.Builder.Builder(prefix='A_', suffix={}, action={})
        env = Environment(BUILDERS={'Bld':builder})
        builder.add_action('.src_sfx1', 'FOO')

        r = builder.get_name(env)
        assert r == 'Bld', r
        r = builder.get_prefix(env)
        assert r == 'A_', r
        r = builder.get_suffix(env)
        assert r is None, r
        r = builder.get_suffix(env, [MyNode('X.src_sfx1')])
        assert r is None, r
        r = builder.get_src_suffix(env)
        assert r == '.src_sfx1', r
        r = builder.src_suffixes(env)
        assert r == ['.src_sfx1'], r

        builder = SCons.Builder.Builder(prefix='A_', suffix={}, action={})
        env = Environment(BUILDERS={'Bld':builder})
        builder.add_action('.src_sfx1', 'FOO')
        builder.add_action('.src_sfx2', 'BAR')

        r = builder.get_name(env)
        assert r == 'Bld', r
        r = builder.get_prefix(env)
        assert r == 'A_', r
        r = builder.get_suffix(env)
        assert r is None, r
        r = builder.get_src_suffix(env)
        assert r == '.src_sfx1', r
        r = sorted(builder.src_suffixes(env))
        assert r == ['.src_sfx1', '.src_sfx2'], r


    def test_Builder_Args(self):
        """Testing passing extra args to a builder."""
        def buildFunc(target, source, env, s=self):
            s.foo=env['foo']
            s.bar=env['bar']
            assert env['CC'] == 'mycc'

        env=Environment(CC='cc')

        builder = SCons.Builder.Builder(action=buildFunc)
        tgt = builder(env, target='foo', source='bar', foo=1, bar=2, CC='mycc')[0]
        tgt.build()
        assert self.foo == 1, self.foo
        assert self.bar == 2, self.bar

    def test_emitter(self):
        """Test emitter functions."""
        def emit(target, source, env):
            foo = env.get('foo', 0)
            bar = env.get('bar', 0)
            for t in target:
                assert isinstance(t, MyNode)
                assert t.has_builder()
            for s in source:
                assert isinstance(s, MyNode)
            if foo:
                target.append("bar%d"%foo)
            if bar:
                source.append("baz")
            return ( target, source )

        env = Environment()
        builder = SCons.Builder.Builder(action='foo',
                                        emitter=emit,
                                        target_factory=MyNode,
                                        source_factory=MyNode)
        tgt = builder(env, target='foo2', source='bar')[0]
        assert str(tgt) == 'foo2', str(tgt)
        assert str(tgt.sources[0]) == 'bar', str(tgt.sources[0])

        tgt = builder(env, target='foo3', source='bar', foo=1)
        assert len(tgt) == 2, len(tgt)
        assert 'foo3' in list(map(str, tgt)), list(map(str, tgt))
        assert 'bar1' in list(map(str, tgt)), list(map(str, tgt))

        tgt = builder(env, target='foo4', source='bar', bar=1)[0]
        assert str(tgt) == 'foo4', str(tgt)
        assert len(tgt.sources) == 2, len(tgt.sources)
        assert 'baz' in list(map(str, tgt.sources)), list(map(str, tgt.sources))
        assert 'bar' in list(map(str, tgt.sources)), list(map(str, tgt.sources))

        env2=Environment(FOO=emit)
        builder2=SCons.Builder.Builder(action='foo',
                                       emitter="$FOO",
                                       target_factory=MyNode,
                                       source_factory=MyNode)

        builder2a=SCons.Builder.Builder(action='foo',
                                        emitter="$FOO",
                                        target_factory=MyNode,
                                        source_factory=MyNode)

        assert builder2 == builder2a, repr(builder2.__dict__) + "\n" + repr(builder2a.__dict__)

        tgt = builder2(env2, target='foo5', source='bar')[0]
        assert str(tgt) == 'foo5', str(tgt)
        assert str(tgt.sources[0]) == 'bar', str(tgt.sources[0])

        tgt = builder2(env2, target='foo6', source='bar', foo=2)
        assert len(tgt) == 2, len(tgt)
        assert 'foo6' in list(map(str, tgt)), list(map(str, tgt))
        assert 'bar2' in list(map(str, tgt)), list(map(str, tgt))

        tgt = builder2(env2, target='foo7', source='bar', bar=1)[0]
        assert str(tgt) == 'foo7', str(tgt)
        assert len(tgt.sources) == 2, len(tgt.sources)
        assert 'baz' in list(map(str, tgt.sources)), list(map(str, tgt.sources))
        assert 'bar' in list(map(str, tgt.sources)), list(map(str, tgt.sources))

    def test_emitter_preserve_builder(self):
        """Test an emitter not overwriting a newly-set builder"""
        env = Environment()

        new_builder = SCons.Builder.Builder(action='new')
        node = MyNode('foo8')
        new_node = MyNode('foo8.new')

        def emit(target, source, env, nb=new_builder, nn=new_node):
            for t in target:
                t.builder = nb
            return [nn], source

        builder=SCons.Builder.Builder(action='foo',
                                      emitter=emit,
                                      target_factory=MyNode,
                                      source_factory=MyNode)
        tgt = builder(env, target=node, source='bar')[0]
        assert tgt is new_node, tgt
        assert tgt.builder is builder, tgt.builder
        assert node.builder is new_builder, node.builder

    def test_emitter_suffix_map(self):
        """Test mapping file suffixes to emitter functions"""
        env = Environment()

        def emit4a(target, source, env):
            source = list(map(str, source))
            target = ['emit4a-' + x[:-3] for x in source]
            return (target, source)
        def emit4b(target, source, env):
            source = list(map(str, source))
            target = ['emit4b-' + x[:-3] for x in source]
            return (target, source)

        builder = SCons.Builder.Builder(action='foo',
                                        emitter={'.4a':emit4a,
                                                 '.4b':emit4b},
                                        target_factory=MyNode,
                                        source_factory=MyNode)
        tgt = builder(env, None, source='aaa.4a')[0]
        assert str(tgt) == 'emit4a-aaa', str(tgt)
        tgt = builder(env, None, source='bbb.4b')[0]
        assert str(tgt) == 'emit4b-bbb', str(tgt)
        tgt = builder(env, None, source='ccc.4c')[0]
        assert str(tgt) == 'ccc', str(tgt)

        def emit4c(target, source, env):
            source = list(map(str, source))
            target = ['emit4c-' + x[:-3] for x in source]
            return (target, source)

        builder.add_emitter('.4c', emit4c)
        tgt = builder(env, None, source='ccc.4c')[0]
        assert str(tgt) == 'emit4c-ccc', str(tgt)

    def test_emitter_function_list(self):
        """Test lists of emitter functions"""
        env = Environment()

        def emit1a(target, source, env):
            source = list(map(str, source))
            target = target + ['emit1a-' + x[:-2] for x in source]
            return (target, source)
        def emit1b(target, source, env):
            source = list(map(str, source))
            target = target + ['emit1b-' + x[:-2] for x in source]
            return (target, source)
        builder1 = SCons.Builder.Builder(action='foo',
                                         emitter=[emit1a, emit1b],
                                         node_factory=MyNode)

        tgts = builder1(env, target='target-1', source='aaa.1')
        tgts = list(map(str, tgts))
        assert tgts == ['target-1', 'emit1a-aaa', 'emit1b-aaa'], tgts

        # Test a list of emitter functions through the environment.
        def emit2a(target, source, env):
            source = list(map(str, source))
            target = target + ['emit2a-' + x[:-2] for x in source]
            return (target, source)
        def emit2b(target, source, env):
            source = list(map(str, source))
            target = target + ['emit2b-' + x[:-2] for x in source]
            return (target, source)
        builder2 = SCons.Builder.Builder(action='foo',
                                         emitter='$EMITTERLIST',
                                         node_factory=MyNode)

        env = Environment(EMITTERLIST = [emit2a, emit2b])

        tgts = builder2(env, target='target-2', source='aaa.2')
        tgts = list(map(str, tgts))
        assert tgts == ['target-2', 'emit2a-aaa', 'emit2b-aaa'], tgts

    def test_emitter_TARGET_SOURCE(self):
        """Test use of $TARGET and $SOURCE in emitter results"""

        env = SCons.Environment.Environment()

        def emit(target, source, env):
            return (target + ['${SOURCE}.s1', '${TARGET}.t1'],
                    source + ['${TARGET}.t2', '${SOURCE}.s2'])

        builder = SCons.Builder.Builder(action='foo',
                                        emitter = emit,
                                        node_factory = MyNode)

        targets = builder(env, target = 'TTT', source ='SSS')
        sources = targets[0].sources
        targets = list(map(str, targets))
        sources = list(map(str, sources))
        assert targets == ['TTT', 'SSS.s1', 'TTT.t1'], targets
        assert sources == ['SSS', 'TTT.t2', 'SSS.s2'], targets

    def test_no_target(self):
        """Test deducing the target from the source."""

        env = Environment()
        b = SCons.Builder.Builder(action='foo', suffix='.o')

        tgt = b(env, None, 'aaa')[0]
        assert str(tgt) == 'aaa.o', str(tgt)
        assert len(tgt.sources) == 1, list(map(str, tgt.sources))
        assert str(tgt.sources[0]) == 'aaa', list(map(str, tgt.sources))

        tgt = b(env, None, 'bbb.c')[0]
        assert str(tgt) == 'bbb.o', str(tgt)
        assert len(tgt.sources) == 1, list(map(str, tgt.sources))
        assert str(tgt.sources[0]) == 'bbb.c', list(map(str, tgt.sources))

        tgt = b(env, None, 'ccc.x.c')[0]
        assert str(tgt) == 'ccc.x.o', str(tgt)
        assert len(tgt.sources) == 1, list(map(str, tgt.sources))
        assert str(tgt.sources[0]) == 'ccc.x.c', list(map(str, tgt.sources))

        tgt = b(env, None, ['d0.c', 'd1.c'])[0]
        assert str(tgt) == 'd0.o', str(tgt)
        assert len(tgt.sources) == 2,  list(map(str, tgt.sources))
        assert str(tgt.sources[0]) == 'd0.c', list(map(str, tgt.sources))
        assert str(tgt.sources[1]) == 'd1.c', list(map(str, tgt.sources))

        tgt = b(env, target = None, source='eee')[0]
        assert str(tgt) == 'eee.o', str(tgt)
        assert len(tgt.sources) == 1, list(map(str, tgt.sources))
        assert str(tgt.sources[0]) == 'eee', list(map(str, tgt.sources))

        tgt = b(env, target = None, source='fff.c')[0]
        assert str(tgt) == 'fff.o', str(tgt)
        assert len(tgt.sources) == 1, list(map(str, tgt.sources))
        assert str(tgt.sources[0]) == 'fff.c', list(map(str, tgt.sources))

        tgt = b(env, target = None, source='ggg.x.c')[0]
        assert str(tgt) == 'ggg.x.o', str(tgt)
        assert len(tgt.sources) == 1, list(map(str, tgt.sources))
        assert str(tgt.sources[0]) == 'ggg.x.c', list(map(str, tgt.sources))

        tgt = b(env, target = None, source=['h0.c', 'h1.c'])[0]
        assert str(tgt) == 'h0.o', str(tgt)
        assert len(tgt.sources) == 2,  list(map(str, tgt.sources))
        assert str(tgt.sources[0]) == 'h0.c', list(map(str, tgt.sources))
        assert str(tgt.sources[1]) == 'h1.c', list(map(str, tgt.sources))

        w = b(env, target='i0.w', source=['i0.x'])[0]
        y = b(env, target='i1.y', source=['i1.z'])[0]
        tgt = b(env, None, source=[w, y])[0]
        assert str(tgt) == 'i0.o', str(tgt)
        assert len(tgt.sources) == 2, list(map(str, tgt.sources))
        assert str(tgt.sources[0]) == 'i0.w', list(map(str, tgt.sources))
        assert str(tgt.sources[1]) == 'i1.y', list(map(str, tgt.sources))

    def test_get_name(self):
        """Test getting name of builder.

        Each type of builder should return its environment-specific
        name when queried appropriately.  """

        b1 = SCons.Builder.Builder(action='foo', suffix='.o')
        b2 = SCons.Builder.Builder(action='foo', suffix='.c')
        b3 = SCons.Builder.Builder(action='bar', src_suffix = '.foo',
                                                 src_builder = b1)
        b4 = SCons.Builder.Builder(action={})
        b5 = SCons.Builder.Builder(action='foo', name='builder5')
        b6 = SCons.Builder.Builder(action='foo')
        assert isinstance(b4, SCons.Builder.CompositeBuilder)
        assert isinstance(b4.action, SCons.Action.CommandGeneratorAction)

        env = Environment(BUILDERS={'bldr1': b1,
                                    'bldr2': b2,
                                    'bldr3': b3,
                                    'bldr4': b4})
        env2 = Environment(BUILDERS={'B1': b1,
                                     'B2': b2,
                                     'B3': b3,
                                     'B4': b4})
        # With no name, get_name will return the class.  Allow
        # for caching...
        b6_names = [
            'SCons.Builder.BuilderBase',
            "<class 'SCons.Builder.BuilderBase'>",
            'SCons.Memoize.BuilderBase',
            "<class 'SCons.Memoize.BuilderBase'>",
        ]

        assert b1.get_name(env) == 'bldr1', b1.get_name(env)
        assert b2.get_name(env) == 'bldr2', b2.get_name(env)
        assert b3.get_name(env) == 'bldr3', b3.get_name(env)
        assert b4.get_name(env) == 'bldr4', b4.get_name(env)
        assert b5.get_name(env) == 'builder5', b5.get_name(env)
        assert b6.get_name(env) in b6_names, b6.get_name(env)

        assert b1.get_name(env2) == 'B1', b1.get_name(env2)
        assert b2.get_name(env2) == 'B2', b2.get_name(env2)
        assert b3.get_name(env2) == 'B3', b3.get_name(env2)
        assert b4.get_name(env2) == 'B4', b4.get_name(env2)
        assert b5.get_name(env2) == 'builder5', b5.get_name(env2)
        assert b6.get_name(env2) in b6_names, b6.get_name(env2)

        assert b5.get_name(None) == 'builder5', b5.get_name(None)
        assert b6.get_name(None) in b6_names, b6.get_name(None)

        # This test worked before adding batch builders, but we must now
        # be able to disambiguate a CompositeAction into a more specific
        # action based on file suffix at call time.  Leave this commented
        # out (for now) in case this reflects a real-world use case that
        # we must accomodate and we want to resurrect this test.
        #tgt = b4(env, target = 'moo', source='cow')
        #assert tgt[0].builder.get_name(env) == 'bldr4'

class CompositeBuilderTestCase(unittest.TestCase):

    def setUp(self):
        def func_action(target, source, env):
            return 0

        builder = SCons.Builder.Builder(action={ '.foo' : func_action,
                                                 '.bar' : func_action})

        self.func_action = func_action
        self.builder = builder

    def test___init__(self):
        """Test CompositeBuilder creation"""
        env = Environment()
        builder = SCons.Builder.Builder(action={})

        tgt = builder(env, source=[])
        assert tgt == [], tgt

        assert isinstance(builder, SCons.Builder.CompositeBuilder)
        assert isinstance(builder.action, SCons.Action.CommandGeneratorAction)

    def test_target_action(self):
        """Test CompositeBuilder setting of target builder actions"""
        env = Environment()
        builder = self.builder

        tgt = builder(env, target='test1', source='test1.foo')[0]
        assert isinstance(tgt.builder, SCons.Builder.BuilderBase)
        assert tgt.builder.action is builder.action

        tgt = builder(env, target='test2', source='test1.bar')[0]
        assert isinstance(tgt.builder, SCons.Builder.BuilderBase)
        assert tgt.builder.action is builder.action

    def test_multiple_suffix_error(self):
        """Test the CompositeBuilder multiple-source-suffix error"""
        env = Environment()
        builder = self.builder

        flag = 0
        try:
            builder(env, target='test3', source=['test2.bar', 'test1.foo'])[0]
        except SCons.Errors.UserError as e:
            flag = 1
            err = e
        assert flag, "UserError should be thrown when we call a builder with files of different suffixes."
        expect = "While building `['test3']' from `test1.foo': Cannot build multiple sources with different extensions: .bar, .foo"
        assert str(err) == expect, err

    def test_source_ext_match(self):
        """Test the CompositeBuilder source_ext_match argument"""
        env = Environment()
        func_action = self.func_action
        builder = SCons.Builder.Builder(action={ '.foo' : func_action,
                                                 '.bar' : func_action},
                                        source_ext_match = None)

        tgt = builder(env, target='test3', source=['test2.bar', 'test1.foo'])[0]
        tgt.build()

    def test_suffix_variable(self):
        """Test CompositeBuilder defining action suffixes through a variable"""
        env = Environment(BAR_SUFFIX = '.BAR2', FOO_SUFFIX = '.FOO2')
        func_action = self.func_action
        builder = SCons.Builder.Builder(action={ '.foo' : func_action,
                                                 '.bar' : func_action,
                                                 '$BAR_SUFFIX' : func_action,
                                                 '$FOO_SUFFIX' : func_action })

        tgt = builder(env, target='test4', source=['test4.BAR2'])[0]
        assert isinstance(tgt.builder, SCons.Builder.BuilderBase)
        try:
            tgt.build()
            flag = 1
        except SCons.Errors.UserError as e:
            print(e)
            flag = 0
        assert flag, "It should be possible to define actions in composite builders using variables."
        env['FOO_SUFFIX'] = '.BAR2'
        builder.add_action('$NEW_SUFFIX', func_action)
        flag = 0
        try:
            builder(env, target='test5', source=['test5.BAR2'])[0]
        except SCons.Errors.UserError:
            flag = 1
        assert flag, "UserError should be thrown when we call a builder with ambigous suffixes."

    def test_src_builder(self):
        """Test CompositeBuilder's use of a src_builder"""
        env = Environment()

        foo_bld = SCons.Builder.Builder(action = 'a-foo',
                                        src_suffix = '.ina',
                                        suffix = '.foo')
        assert isinstance(foo_bld, SCons.Builder.BuilderBase)
        builder = SCons.Builder.Builder(action = { '.foo' : 'foo',
                                                   '.bar' : 'bar' },
                                        src_builder = foo_bld)
        assert isinstance(builder, SCons.Builder.CompositeBuilder)
        assert isinstance(builder.action, SCons.Action.CommandGeneratorAction)

        tgt = builder(env, target='t1', source='t1a.ina t1b.ina')[0]
        assert isinstance(tgt.builder, SCons.Builder.BuilderBase)

        tgt = builder(env, target='t2', source='t2a.foo t2b.ina')[0]
        assert isinstance(tgt.builder, SCons.Builder.BuilderBase), tgt.builder.__dict__

        bar_bld = SCons.Builder.Builder(action = 'a-bar',
                                        src_suffix = '.inb',
                                        suffix = '.bar')
        assert isinstance(bar_bld, SCons.Builder.BuilderBase)
        builder = SCons.Builder.Builder(action = { '.foo' : 'foo'},
                                        src_builder = [foo_bld, bar_bld])
        assert isinstance(builder, SCons.Builder.CompositeBuilder)
        assert isinstance(builder.action, SCons.Action.CommandGeneratorAction)

        builder.add_action('.bar', 'bar')

        tgt = builder(env, target='t3-foo', source='t3a.foo t3b.ina')[0]
        assert isinstance(tgt.builder, SCons.Builder.BuilderBase)

        tgt = builder(env, target='t3-bar', source='t3a.bar t3b.inb')[0]
        assert isinstance(tgt.builder, SCons.Builder.BuilderBase)

        flag = 0
        try:
            builder(env, target='t5', source=['test5a.foo', 'test5b.inb'])[0]
        except SCons.Errors.UserError as e:
            flag = 1
            err = e
        assert flag, "UserError should be thrown when we call a builder with files of different suffixes."
        expect = "While building `['t5']' from `test5b.bar': Cannot build multiple sources with different extensions: .foo, .bar"
        assert str(err) == expect, err

        flag = 0
        try:
            builder(env, target='t6', source=['test6a.bar', 'test6b.ina'])[0]
        except SCons.Errors.UserError as e:
            flag = 1
            err = e
        assert flag, "UserError should be thrown when we call a builder with files of different suffixes."
        expect = "While building `['t6']' from `test6b.foo': Cannot build multiple sources with different extensions: .bar, .foo"
        assert str(err) == expect, err

        flag = 0
        try:
            builder(env, target='t4', source=['test4a.ina', 'test4b.inb'])[0]
        except SCons.Errors.UserError as e:
            flag = 1
            err = e
        assert flag, "UserError should be thrown when we call a builder with files of different suffixes."
        expect = "While building `['t4']' from `test4b.bar': Cannot build multiple sources with different extensions: .foo, .bar"
        assert str(err) == expect, err

        flag = 0
        try:
            builder(env, target='t7', source=[env.fs.File('test7')])[0]
        except SCons.Errors.UserError as e:
            flag = 1
            err = e
        assert flag, "UserError should be thrown when we call a builder with files of different suffixes."
        expect = "While building `['t7']': Cannot deduce file extension from source files: ['test7']"
        assert str(err) == expect, err

        flag = 0
        try:
            builder(env, target='t8', source=['test8.unknown'])[0]
        except SCons.Errors.UserError as e:
            flag = 1
            err = e
        assert flag, "UserError should be thrown when we call a builder target with an unknown suffix."
        expect = "While building `['t8']' from `['test8.unknown']': Don't know how to build from a source file with suffix `.unknown'.  Expected a suffix in this list: ['.foo', '.bar']."
        assert str(err) == expect, err

if __name__ == "__main__":
    suite = unittest.TestSuite()
    tclasses = [
        BuilderTestCase,
        CompositeBuilderTestCase
    ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(list(map(tclass, names)))

    TestUnit.run(suite)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
