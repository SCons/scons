#
# Copyright (c) 2001 Steven Knight
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
import unittest

import TestCmd
import SCons.Builder
import SCons.Errors

# Initial setup of the common environment for all tests,
# a temporary working directory containing a
# script for writing arguments to an output file.
#
# We don't do this as a setUp() method because it's
# unnecessary to create a separate directory and script
# for each test, they can just use the one.
test = TestCmd.TestCmd(workdir = '')

test.write('act.py', """import os, string, sys
f = open(sys.argv[1], 'w')
f.write("act.py: '" + string.join(sys.argv[2:], "' '") + "'\\n")
try:
    if sys.argv[3]:
        f.write("act.py: '" + os.environ[sys.argv[3]] + "'\\n")
except:
    pass
f.close()
sys.exit(0)
""")

act_py = test.workpath('act.py')
outfile = test.workpath('outfile')
outfile2 = test.workpath('outfile')

show_string = None
instanced = None
env_scanner = None
count = 0

class Environment:
    def subst(self, s):
        return s
    def get_scanner(self, ext):
        return env_scanner
env = Environment()

class BuilderTestCase(unittest.TestCase):

    def test__call__(self):
	"""Test calling a builder to establish source dependencies
	"""
	class Node:
	    def __init__(self, name):
		self.name = name
		self.sources = []
		self.builder = None
	    def __str__(self):
	        return self.name
	    def builder_set(self, builder):
		self.builder = builder
	    def env_set(self, env, safe=0):
		self.env = env
	    def add_source(self, source):
		self.sources.extend(source)
        builder = SCons.Builder.Builder(name="builder", action="foo", node_factory=Node)

	n1 = Node("n1");
	n2 = Node("n2");
	builder(env, target = n1, source = n2)
	assert n1.env == env
	assert n1.builder == builder
	assert n1.sources == [n2]
        assert n2.env == env

        target = builder(env, target = 'n3', source = 'n4')
        assert target.name == 'n3'
        assert target.sources[0].name == 'n4'

        targets = builder(env, target = 'n4 n5', source = ['n6 n7'])
        assert targets[0].name == 'n4'
        assert targets[0].sources[0].name == 'n6 n7'
        assert targets[1].name == 'n5'
        assert targets[1].sources[0].name == 'n6 n7'

        target = builder(env, target = ['n8 n9'], source = 'n10 n11')
        assert target.name == 'n8 n9'
        assert target.sources[0].name == 'n10'
        assert target.sources[1].name == 'n11'

    def test_noname(self):
        """Test error reporting for missing name

        Verify that the Builder constructor gives an error message if the
        name is missing.
        """
        try:
            b = SCons.Builder.Builder()
        except SCons.Errors.UserError:
            pass
        else:
            assert 0

    def test_action(self):
	"""Test Builder creation

	Verify that we can retrieve the supplied action attribute.
	"""
	builder = SCons.Builder.Builder(name="builder", action="foo")
	assert builder.action.command == "foo"

    def test_cmp(self):
	"""Test simple comparisons of Builder objects
	"""
	b1 = SCons.Builder.Builder(name="b1", src_suffix = '.o')
	b2 = SCons.Builder.Builder(name="b1", src_suffix = '.o')
	assert b1 == b2
	b3 = SCons.Builder.Builder(name="b3", src_suffix = '.x')
	assert b1 != b3
	assert b2 != b3

    def test_execute(self):
	"""Test execution of simple Builder objects
	
	One Builder is a string that executes an external command,
	one is an internal Python function, one is a list
	containing one of each.
	"""

        def MyBuilder(**kw):
            builder = apply(SCons.Builder.Builder, (), kw)
            def no_show(str):
                pass
            builder.action.show = no_show
            return builder

	python = sys.executable

	cmd1 = r'%s %s %s xyzzy' % (python, act_py, outfile)

        builder = MyBuilder(action = cmd1, name = "cmd1")
	r = builder.execute()
	assert r == 0
	c = test.read(outfile, 'r')
        assert c == "act.py: 'xyzzy'\n", c

	cmd2 = r'%s %s %s $TARGET' % (python, act_py, outfile)

        builder = MyBuilder(action = cmd2, name = "cmd2")
	r = builder.execute(target = 'foo')
	assert r == 0
	c = test.read(outfile, 'r')
        assert c == "act.py: 'foo'\n", c

	cmd3 = r'%s %s %s ${TARGETS}' % (python, act_py, outfile)

        builder = MyBuilder(action = cmd3, name = "cmd3")
	r = builder.execute(target = ['aaa', 'bbb'])
	assert r == 0
	c = test.read(outfile, 'r')
        assert c == "act.py: 'aaa' 'bbb'\n", c

	cmd4 = r'%s %s %s $SOURCES' % (python, act_py, outfile)

        builder = MyBuilder(action = cmd4, name = "cmd4")
	r = builder.execute(source = ['one', 'two'])
	assert r == 0
	c = test.read(outfile, 'r')
        assert c == "act.py: 'one' 'two'\n", c

	cmd4 = r'%s %s %s ${SOURCES[:2]}' % (python, act_py, outfile)

        builder = MyBuilder(action = cmd4, name = "cmd4")
	r = builder.execute(source = ['three', 'four', 'five'])
	assert r == 0
	c = test.read(outfile, 'r')
        assert c == "act.py: 'three' 'four'\n", c

	cmd5 = r'%s %s %s $TARGET XYZZY' % (python, act_py, outfile)

        builder = MyBuilder(action = cmd5, name = "cmd5")
	r = builder.execute(target = 'out5', env = {'ENV' : {'XYZZY' : 'xyzzy'}})
	assert r == 0
	c = test.read(outfile, 'r')
        assert c == "act.py: 'out5' 'XYZZY'\nact.py: 'xyzzy'\n", c

        class Obj:
            def __init__(self, str):
                self._str = str
            def __str__(self):
                return self._str

        cmd6 = r'%s %s %s ${TARGETS[1]} $TARGET ${SOURCES[:2]}' % (python, act_py, outfile)

        builder = MyBuilder(action = cmd6, name = "cmd6")
        r = builder.execute(target = [Obj('111'), Obj('222')],
                            source = [Obj('333'), Obj('444'), Obj('555')])
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: '222' '111' '333' '444'\n", c

        cmd7 = '%s %s %s one\n\n%s %s %s two' % (python, act_py, outfile,
                                                 python, act_py, outfile)
        expect7 = '%s %s %s one\n%s %s %s two\n' % (python, act_py, outfile,
                                                    python, act_py, outfile)

        builder = MyBuilder(action = cmd7, name = "cmd7")

        global show_string
        show_string = ""
        def my_show(string):
            global show_string
            show_string = show_string + string + "\n"
        builder.action.show = my_show

        r = builder.execute()
        assert r == 0
        assert show_string == expect7, show_string

        global count
        count = 0
	def function1(**kw):
            global count
            count = count + 1
            if not type(kw['target']) is type([]):
                kw['target'] = [ kw['target'] ]
            for t in kw['target']:
	        open(t, 'w').write("function1\n")
	    return 1

	builder = MyBuilder(action = function1, name = "function1")
        r = builder.execute(target = [outfile, outfile2])
        assert r == 1
        assert count == 1
        c = test.read(outfile, 'r')
	assert c == "function1\n", c
        c = test.read(outfile2, 'r')
	assert c == "function1\n", c

	class class1a:
	    def __init__(self, **kw):
		open(kw['out'], 'w').write("class1a\n")

	builder = MyBuilder(action = class1a, name = "class1a")
	r = builder.execute(out = outfile)
	assert r.__class__ == class1a
	c = test.read(outfile, 'r')
	assert c == "class1a\n", c

	class class1b:
	    def __call__(self, **kw):
		open(kw['out'], 'w').write("class1b\n")
		return 2

	builder = MyBuilder(action = class1b(), name = "class1b")
	r = builder.execute(out = outfile)
	assert r == 2
	c = test.read(outfile, 'r')
	assert c == "class1b\n", c

	cmd2 = r'%s %s %s syzygy' % (python, act_py, outfile)

	def function2(**kw):
	    open(kw['out'], 'a').write("function2\n")
	    return 0

	class class2a:
	    def __call__(self, **kw):
		open(kw['out'], 'a').write("class2a\n")
		return 0

	class class2b:
	    def __init__(self, **kw):
		open(kw['out'], 'a').write("class2b\n")

	builder = MyBuilder(action = [cmd2, function2, class2a(), class2b], name = "clist")
	r = builder.execute(out = outfile)
	assert r.__class__ == class2b
	c = test.read(outfile, 'r')
        assert c == "act.py: 'syzygy'\nfunction2\nclass2a\nclass2b\n", c

        if os.name == 'nt':
            # NT treats execs of directories and non-executable files
            # as "file not found" errors
            expect_nonexistent = 1
            expect_nonexecutable = 1
        else:
            expect_nonexistent = 127
            expect_nonexecutable = 126

        # Test that a nonexistent command returns 127
        builder = MyBuilder(action = python + "_XyZzY_", name="badcmd")
        r = builder.execute(out = outfile)
        assert r == expect_nonexistent, "r == %d" % r

        # Test that trying to execute a directory returns 126
        dir, tail = os.path.split(python)
        builder = MyBuilder(action = dir, name = "dir")
        r = builder.execute(out = outfile)
        assert r == expect_nonexecutable, "r == %d" % r

        # Test that trying to execute a non-executable file returns 126
        builder = MyBuilder(action = outfile, name = "badfile")
        r = builder.execute(out = outfile)
        assert r == expect_nonexecutable, "r == %d" % r

    def test_get_contents(self):
        """Test returning the signature contents of a Builder
        """

        b1 = SCons.Builder.Builder(name = "b1", action = "foo")
        contents = b1.get_contents()
        assert contents == "foo", contents

        b2 = SCons.Builder.Builder(name = "b2", action = Func)
        contents = b2.get_contents()
        assert contents == "\177\036\000\177\037\000d\000\000S", repr(contents)

        b3 = SCons.Builder.Builder(name = "b3", action = ["foo", Func, "bar"])
        contents = b3.get_contents()
        assert contents == "foo\177\036\000\177\037\000d\000\000Sbar", repr(contents)

        b4 = SCons.Builder.Builder(name = "b4", action = "$_LIBFLAGS $_LIBDIRFLAGS $_INCFLAGS")
        kw = {'LIBS'          : ['l1', 'l2'],
              'LIBLINKPREFIX' : '-l',
              'LIBLINKSUFFIX' : '',
              'LIBPATH'       : ['lib'],
              'LIBDIRPREFIX'  : '-L',
              'LIBDIRSUFFIX'  : 'X',
              'CPPPATH'       : ['c', 'p'],
              'INCPREFIX'     : '-I',
              'INCSUFFIX'     : ''}

        contents = apply(b4.get_raw_contents, (), kw)
        assert contents == "-ll1 -ll2 $( -LlibX $) $( -Ic -Ip $)", contents

        contents = apply(b4.get_contents, (), kw)
        assert contents == "-ll1 -ll2", "'%s'" % contents

        # SCons.Node.FS has been imported by our import of
        # SCons.Node.Builder.  It's kind of bogus that we don't
        # import this ourselves before using it this way, but it's
        # maybe a little cleaner than tying these tests directly
        # to the other module via a direct import.
        kw['dir'] = SCons.Node.FS.default_fs.Dir('d')

        contents = apply(b4.get_raw_contents, (), kw)
        expect = os.path.normpath("-ll1 -ll2 $( -Ld/libX $) $( -Id/c -Id/p $)")
        assert contents == expect, contents + " != " + expect

        contents = apply(b4.get_contents, (), kw)
        expect = os.path.normpath("-ll1 -ll2")
        assert contents == expect, contents + " != " + expect

    def test_node_factory(self):
	"""Test a Builder that creates nodes of a specified class
	"""
	class Foo:
	    pass
	def FooFactory(target):
            global Foo
	    return Foo(target)
	builder = SCons.Builder.Builder(name = "builder", node_factory = FooFactory)
	assert builder.node_factory is FooFactory

    def test_prefix(self):
	"""Test Builder creation with a specified target prefix

	Make sure that there is no '.' separator appended.
	"""
	builder = SCons.Builder.Builder(name = "builder", prefix = 'lib.')
	assert builder.prefix == 'lib.'
	builder = SCons.Builder.Builder(name = "builder", prefix = 'lib')
	assert builder.prefix == 'lib'
	tgt = builder(env, target = 'tgt1', source = 'src1')
	assert tgt.path == 'libtgt1', \
	        "Target has unexpected name: %s" % tgt.path
        tgts = builder(env, target = 'tgt2a tgt2b', source = 'src2')
        assert tgts[0].path == 'libtgt2a', \
                "Target has unexpected name: %s" % tgts[0].path
        assert tgts[1].path == 'libtgt2b', \
                "Target has unexpected name: %s" % tgts[1].path

    def test_src_suffix(self):
	"""Test Builder creation with a specified source file suffix
	
	Make sure that the '.' separator is appended to the
	beginning if it isn't already present.
	"""
	builder = SCons.Builder.Builder(name = "builder", src_suffix = '.c')
        assert builder.src_suffixes() == ['.c'], builder.src_suffixes()

	tgt = builder(env, target = 'tgt2', source = 'src2')
	assert tgt.sources[0].path == 'src2.c', \
	        "Source has unexpected name: %s" % tgt.sources[0].path

        tgt = builder(env, target = 'tgt3', source = 'src3a src3b')
        assert tgt.sources[0].path == 'src3a.c', \
                "Sources[0] has unexpected name: %s" % tgt.sources[0].path
        assert tgt.sources[1].path == 'src3b.c', \
                "Sources[1] has unexpected name: %s" % tgt.sources[1].path

        b2 = SCons.Builder.Builder(name = "b2", src_suffix = '.2', src_builder = builder)
        assert b2.src_suffixes() == ['.2', '.c'], b2.src_suffixes()

        b3 = SCons.Builder.Builder(name = "b2", action = {'.3a' : '', '.3b' : ''})
        s = b3.src_suffixes()
        s.sort()
        assert s == ['.3a', '.3b'], s

    def test_suffix(self):
	"""Test Builder creation with a specified target suffix

	Make sure that the '.' separator is appended to the
	beginning if it isn't already present.
	"""
	builder = SCons.Builder.Builder(name = "builder", suffix = '.o')
	assert builder.suffix == '.o'
	builder = SCons.Builder.Builder(name = "builder", suffix = 'o')
	assert builder.suffix == '.o'
	tgt = builder(env, target = 'tgt3', source = 'src3')
	assert tgt.path == 'tgt3.o', \
	        "Target has unexpected name: %s" % tgt[0].path
        tgts = builder(env, target = 'tgt4a tgt4b', source = 'src4')
        assert tgts[0].path == 'tgt4a.o', \
                "Target has unexpected name: %s" % tgts[0].path
        tgts = builder(env, target = 'tgt4a tgt4b', source = 'src4')
        assert tgts[1].path == 'tgt4b.o', \
                "Target has unexpected name: %s" % tgts[1].path

    def test_ListBuilder(self):
        """Testing ListBuilder class."""
        global count
        count = 0
        def function2(**kw):
            global count
            count = count + 1
            if not type(kw['target']) is type([]):
                kw['target'] = [ kw['target'] ]
            for t in kw['target']:
                open(t, 'w').write("function2\n")
            return 1

        builder = SCons.Builder.Builder(action = function2, name = "function2")
        tgts = builder(env, target = [outfile, outfile2], source = 'foo')
        r = tgts[0].builder.execute(target = tgts[0])
        assert r == 1, r
        c = test.read(outfile, 'r')
        assert c == "function2\n", c
        c = test.read(outfile2, 'r')
        assert c == "function2\n", c
        r = tgts[1].builder.execute(target = tgts[1])
        assert r == 1, r
        assert count == 1, count

    def test_MultiStepBuilder(self):
        """Testing MultiStepBuilder class."""
        builder1 = SCons.Builder.Builder(name = "builder1",
                                         action='foo',
                                         src_suffix='.bar',
                                         suffix='.foo')
        builder2 = SCons.Builder.MultiStepBuilder(name = "builder2",
                                                  action='foo',
                                                  src_builder = builder1)
        tgt = builder2(env, target='baz', source='test.bar test2.foo test3.txt')
        flag = 0
        for snode in tgt.sources:
            if snode.path == 'test.foo':
                flag = 1
                assert snode.sources[0].path == 'test.bar'
        assert flag

    def test_CompositeBuilder(self):
        """Testing CompositeBuilder class."""
        builder = SCons.Builder.Builder(name = "builder",
                                        action={ '.foo' : 'foo',
                                                 '.bar' : 'bar' })
        
        assert isinstance(builder, SCons.Builder.CompositeBuilder)
        tgt = builder(env, target='test1', source='test1.foo')
        assert isinstance(tgt.builder, SCons.Builder.BuilderBase)
        assert tgt.builder.action.command == 'foo'
        tgt = builder(env, target='test2', source='test2.bar')
        assert tgt.builder.action.command == 'bar'
        flag = 0
        try:
            tgt = builder(env, target='test2', source='test2.bar test1.foo')
        except SCons.Errors.UserError:
            flag = 1
        assert flag, "UserError should be thrown when we build targets with files of different suffixes."

        foo_bld = SCons.Builder.Builder(name = "foo_bld",
                                        action = 'a-foo',
                                        src_suffix = '.ina',
                                        suffix = '.foo')
        assert isinstance(foo_bld, SCons.Builder.BuilderBase)
        builder = SCons.Builder.Builder(name = "builder",
                                        action = { '.foo' : 'foo',
                                                   '.bar' : 'bar' },
                                        src_builder = foo_bld)
        assert isinstance(builder, SCons.Builder.CompositeBuilder)

        tgt = builder(env, target='t1', source='t1a.ina t1b.ina')
        assert isinstance(tgt.builder, SCons.Builder.BuilderBase)

        tgt = builder(env, target='t2', source='t2a.foo t2b.ina')
        assert isinstance(tgt.builder, SCons.Builder.MultiStepBuilder), tgt.builder.__dict__

        bar_bld = SCons.Builder.Builder(name = "bar_bld",
                                        action = 'a-bar',
                                        src_suffix = '.inb',
                                        suffix = '.bar')
        assert isinstance(bar_bld, SCons.Builder.BuilderBase)
        builder = SCons.Builder.Builder(name = "builder",
                                        action = { '.foo' : 'foo',
                                                   '.bar' : 'bar' },
                                        src_builder = [foo_bld, bar_bld])
        assert isinstance(builder, SCons.Builder.CompositeBuilder)

        tgt = builder(env, target='t3-foo', source='t3a.foo t3b.ina')
        assert isinstance(tgt.builder, SCons.Builder.MultiStepBuilder)

        tgt = builder(env, target='t3-bar', source='t3a.bar t3b.inb')
        assert isinstance(tgt.builder, SCons.Builder.MultiStepBuilder)

        flag = 0
        try:
            tgt = builder(env, target='t5', source='test5a.foo test5b.inb')
        except SCons.Errors.UserError:
            flag = 1
        assert flag, "UserError should be thrown when we build targets with files of different suffixes."

        flag = 0
        try:
            tgt = builder(env, target='t6', source='test6a.bar test6b.ina')
        except SCons.Errors.UserError:
            flag = 1
        assert flag, "UserError should be thrown when we build targets with files of different suffixes."

        flag = 0
        try:
            tgt = builder(env, target='t4', source='test4a.ina test4b.inb')
        except SCons.Errors.UserError:
            flag = 1
        assert flag, "UserError should be thrown when we build targets with files of different suffixes."

    def test_build_scanner(self):
        """Testing ability to set a target scanner through a builder."""
        global instanced
        class TestScanner:
            def instance(self, env):
                global instanced
                instanced = 1
                return self
        scn = TestScanner()
        builder=SCons.Builder.Builder(name = "builder", scanner=scn)
        tgt = builder(env, target='foo', source='bar')
        assert scn in tgt.scanners, tgt.scanners
        assert instanced

        instanced = None
        builder1 = SCons.Builder.Builder(name = "builder1",
                                         action='foo',
                                         src_suffix='.bar',
                                         suffix='.foo')
        builder2 = SCons.Builder.Builder(name = "builder2",
                                         action='foo',
                                         src_builder = builder1,
                                         scanner = scn)
        tgt = builder2(env, target='baz', source='test.bar test2.foo test3.txt')
        assert scn in tgt.scanners, tgt.scanners
        assert instanced

    def test_src_scanner(slf):
        """Testing ability to set a source file scanner through a builder."""
        global env_scanner
        class TestScanner:
            def key(self, env):
                 return 'TestScannerkey'
            def instance(self, env):
                 return self
        env_scanner = TestScanner()
        builder = SCons.Builder.Builder(name = "builder", action='action')
        tgt = builder(env, target='foo', source='bar')
        assert not tgt.scanners == [ env_scanner ]
        assert tgt.sources[0].scanners == [ env_scanner ]

if __name__ == "__main__":
    suite = unittest.makeSuite(BuilderTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
