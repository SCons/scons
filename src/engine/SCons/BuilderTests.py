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

import sys
import unittest

import TestCmd
import SCons.Builder

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

show_string = None
instanced = None
env_scanner = None

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
	builder = SCons.Builder.Builder(action = "foo")
	n1 = Node("n1");
	n2 = Node("n2");
	builder(env, target = n1, source = n2)
	assert n1.env == env
	assert n1.builder == builder
	assert n1.sources == [n2]
        assert n2.env == env

    def test_action(self):
	"""Test Builder creation

	Verify that we can retrieve the supplied action attribute.
	"""
	builder = SCons.Builder.Builder(action = "foo")
	assert builder.action.command == "foo"

    def test_cmp(self):
	"""Test simple comparisons of Builder objects
	"""
	b1 = SCons.Builder.Builder(src_suffix = '.o')
	b2 = SCons.Builder.Builder(src_suffix = '.o')
	assert b1 == b2
	b3 = SCons.Builder.Builder(src_suffix = '.x')
	assert b1 != b3
	assert b2 != b3

    def test_execute(self):
	"""Test execution of simple Builder objects
	
	One Builder is a string that executes an external command,
	one is an internal Python function, one is a list
	containing one of each.
	"""

	python = sys.executable

	cmd1 = r'%s %s %s xyzzy' % (python, act_py, outfile)

	builder = SCons.Builder.Builder(action = cmd1)
	r = builder.execute()
	assert r == 0
	c = test.read(outfile, 'r')
        assert c == "act.py: 'xyzzy'\n", c

	cmd2 = r'%s %s %s $TARGET' % (python, act_py, outfile)

	builder = SCons.Builder.Builder(action = cmd2)
	r = builder.execute(target = 'foo')
	assert r == 0
	c = test.read(outfile, 'r')
        assert c == "act.py: 'foo'\n", c

	cmd3 = r'%s %s %s ${TARGETS}' % (python, act_py, outfile)

	builder = SCons.Builder.Builder(action = cmd3)
	r = builder.execute(target = ['aaa', 'bbb'])
	assert r == 0
	c = test.read(outfile, 'r')
        assert c == "act.py: 'aaa' 'bbb'\n", c

	cmd4 = r'%s %s %s $SOURCES' % (python, act_py, outfile)

	builder = SCons.Builder.Builder(action = cmd4)
	r = builder.execute(source = ['one', 'two'])
	assert r == 0
	c = test.read(outfile, 'r')
        assert c == "act.py: 'one' 'two'\n", c

	cmd4 = r'%s %s %s ${SOURCES[:2]}' % (python, act_py, outfile)

	builder = SCons.Builder.Builder(action = cmd4)
	r = builder.execute(source = ['three', 'four', 'five'])
	assert r == 0
	c = test.read(outfile, 'r')
        assert c == "act.py: 'three' 'four'\n", c

	cmd5 = r'%s %s %s $TARGET XYZZY' % (python, act_py, outfile)

	builder = SCons.Builder.Builder(action = cmd5)
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

        builder = SCons.Builder.Builder(action = cmd6)
        r = builder.execute(target = [Obj('111'), Obj('222')],
                            source = [Obj('333'), Obj('444'), Obj('555')])
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: '222' '111' '333' '444'\n", c

        cmd7 = '%s %s %s one\n\n%s %s %s two' % (python, act_py, outfile,
                                                 python, act_py, outfile)
        expect7 = '%s %s %s one\n%s %s %s two\n' % (python, act_py, outfile,
                                                    python, act_py, outfile)

        builder = SCons.Builder.Builder(action = cmd7)

        global show_string
        show_string = ""
        def my_show(string):
            global show_string
            show_string = show_string + string + "\n"
        builder.action.show = my_show

        r = builder.execute()
        assert r == 0
        assert show_string == expect7, show_string

	def function1(**kw):
	    open(kw['target'], 'w').write("function1\n")
	    return 1

	builder = SCons.Builder.Builder(action = function1)
	r = builder.execute(target = outfile)
	assert r == 1
	c = test.read(outfile, 'r')
	assert c == "function1\n", c

	class class1a:
	    def __init__(self, **kw):
		open(kw['out'], 'w').write("class1a\n")

	builder = SCons.Builder.Builder(action = class1a)
	r = builder.execute(out = outfile)
	assert r.__class__ == class1a
	c = test.read(outfile, 'r')
	assert c == "class1a\n", c

	class class1b:
	    def __call__(self, **kw):
		open(kw['out'], 'w').write("class1b\n")
		return 2

	builder = SCons.Builder.Builder(action = class1b())
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

	builder = SCons.Builder.Builder(action = [cmd2, function2, class2a(), class2b])
	r = builder.execute(out = outfile)
	assert r.__class__ == class2b
	c = test.read(outfile, 'r')
        assert c == "act.py: 'syzygy'\nfunction2\nclass2a\nclass2b\n", c

    def test_get_contents(self):
        """Test returning the signature contents of a Builder
        """

        b1 = SCons.Builder.Builder(action = "foo")
        contents = b1.get_contents()
        assert contents == "foo", contents

        b2 = SCons.Builder.Builder(action = Func)
        contents = b2.get_contents()
        assert contents == "\177\036\000\177\037\000d\000\000S", repr(contents)

        b3 = SCons.Builder.Builder(action = ["foo", Func, "bar"])
        contents = b3.get_contents()
        assert contents == "foo\177\036\000\177\037\000d\000\000Sbar", repr(contents)

        b4 = SCons.Builder.Builder(action = "$_LIBFLAGS $_LIBDIRFLAGS $_INCFLAGS")
        kw = {'LIBS'          : ['l1', 'l2'],
              'LIBLINKPREFIX' : '-l',
              'LIBLINKSUFFIX' : '',
              'LIBPATH'       : ['lib'],
              'LIBDIRPREFIX'  : '-L',
              'LIBDIRSUFFIX'  : '/',
              'CPPPATH'       : ['c', 'p'],
              'INCPREFIX'     : '-I',
              'INCSUFFIX'     : ''}

        contents = apply(b4.get_contents, (), kw)
        assert contents == "-ll1 -ll2 -Llib/ -Ic -Ip", contents

        # SCons.Node.FS has been imported by our import of
        # SCons.Node.Builder.  It's kind of bogus that we don't
        # import this ourselves before using it this way, but it's
        # maybe a little cleaner than tying these tests directly
        # to the other module via a direct import.
        kw['dir'] = SCons.Node.FS.default_fs.Dir('d')
        contents = apply(b4.get_contents, (), kw)
        assert contents == "-ld/l1 -ld/l2 -Ld/lib/ -Id/c -Id/p", contents

    def test_name(self):
	"""Test Builder creation with a specified name
	"""
	builder = SCons.Builder.Builder(name = 'foo')
	assert builder.name == 'foo'

    def test_node_factory(self):
	"""Test a Builder that creates nodes of a specified class
	"""
	class Foo:
	    pass
	def FooFactory(target):
            global Foo
	    return Foo(target)
	builder = SCons.Builder.Builder(node_factory = FooFactory)
	assert builder.node_factory is FooFactory

    def test_prefix(self):
	"""Test Builder creation with a specified target prefix

	Make sure that there is no '.' separator appended.
	"""
	builder = SCons.Builder.Builder(prefix = 'lib.')
	assert builder.prefix == 'lib.'
	builder = SCons.Builder.Builder(prefix = 'lib')
	assert builder.prefix == 'lib'
	tgt = builder(env, target = 'tgt1', source = 'src1')
	assert tgt.path == 'libtgt1', \
	        "Target has unexpected name: %s" % tgt.path

    def test_src_suffix(self):
	"""Test Builder creation with a specified source file suffix
	
	Make sure that the '.' separator is appended to the
	beginning if it isn't already present.
	"""
	builder = SCons.Builder.Builder(src_suffix = '.c')
	assert builder.src_suffix == '.c'
	builder = SCons.Builder.Builder(src_suffix = 'c')
	assert builder.src_suffix == '.c'
	tgt = builder(env, target = 'tgt2', source = 'src2')
	assert tgt.sources[0].path == 'src2.c', \
	        "Source has unexpected name: %s" % tgt.sources[0].path

    def test_suffix(self):
	"""Test Builder creation with a specified target suffix

	Make sure that the '.' separator is appended to the
	beginning if it isn't already present.
	"""
	builder = SCons.Builder.Builder(suffix = '.o')
	assert builder.suffix == '.o'
	builder = SCons.Builder.Builder(suffix = 'o')
	assert builder.suffix == '.o'
	tgt = builder(env, target = 'tgt3', source = 'src3')
	assert tgt.path == 'tgt3.o', \
	        "Target has unexpected name: %s" % tgt[0].path

    def test_MultiStepBuilder(self):
        """Testing MultiStepBuilder class."""
        builder1 = SCons.Builder.Builder(action='foo',
                                        src_suffix='.bar',
                                        suffix='.foo')
        builder2 = SCons.Builder.MultiStepBuilder(action='foo',
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
        builder = SCons.Builder.Builder(action={ '.foo' : 'foo',
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

    def test_build_scanner(self):
        """Testing ability to set a target scanner through a builder."""
        global instanced
        class TestScanner:
            def instance(self, env):
                global instanced
                instanced = 1
                return self
        scn = TestScanner()
        builder=SCons.Builder.Builder(scanner=scn)
        tgt = builder(env, target='foo', source='bar')
        assert tgt.scanner == scn, tgt.scanner
        assert instanced

        instanced = None
        builder1 = SCons.Builder.Builder(action='foo',
                                         src_suffix='.bar',
                                         suffix='.foo')
        builder2 = SCons.Builder.Builder(action='foo',
                                         src_builder = builder1,
                                         scanner = scn)
        tgt = builder2(env, target='baz', source='test.bar test2.foo test3.txt')
        assert tgt.scanner == scn, tgt.scanner
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
        builder = SCons.Builder.Builder(action='action')
        tgt = builder(env, target='foo', source='bar')
        assert not tgt.scanner == env_scanner
        assert tgt.sources[0].scanner == env_scanner

if __name__ == "__main__":
    suite = unittest.makeSuite(BuilderTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
