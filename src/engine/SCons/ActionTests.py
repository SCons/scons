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

import os
import re
import StringIO
import string
import sys
import types
import unittest
import UserDict

import SCons.Action
import SCons.Environment
import SCons.Errors

import TestCmd

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
if os.environ.has_key( 'ACTPY_PIPE' ):
    if os.environ.has_key( 'PIPE_STDOUT_FILE' ):
         stdout_msg = open(os.environ['PIPE_STDOUT_FILE'], 'r').read()
    else:
         stdout_msg = "act.py: stdout: executed act.py %s\\n" % string.join(sys.argv[1:])
    sys.stdout.write( stdout_msg )
    if os.environ.has_key( 'PIPE_STDERR_FILE' ):
         stderr_msg = open(os.environ['PIPE_STDERR_FILE'], 'r').read()
    else:
         stderr_msg = "act.py: stderr: executed act.py %s\\n" % string.join(sys.argv[1:])
    sys.stderr.write( stderr_msg )
sys.exit(0)
""")

act_py = test.workpath('act.py')

outfile = test.workpath('outfile')
outfile2 = test.workpath('outfile2')
pipe_file = test.workpath('pipe.out')

scons_env = SCons.Environment.Environment()

# Capture all the stuff the Actions will print,
# so it doesn't clutter the output.
sys.stdout = StringIO.StringIO()

class CmdStringHolder:
    def __init__(self, cmd, literal=None):
        self.data = str(cmd)
        self.literal = literal

    def is_literal(self):
        return self.literal

    def escape(self, escape_func):
        """Escape the string with the supplied function.  The
        function is expected to take an arbitrary string, then
        return it with all special characters escaped and ready
        for passing to the command interpreter.

        After calling this function, the next call to str() will
        return the escaped string.
        """

        if self.is_literal():
            return escape_func(self.data)
        elif ' ' in self.data or '\t' in self.data:
            return '"%s"' % self.data
        else:
            return self.data

class Environment:
    def __init__(self, **kw):
        self.d = {}
        self.d['SHELL'] = scons_env['SHELL']
        self.d['SPAWN'] = scons_env['SPAWN']
        self.d['PSPAWN'] = scons_env['PSPAWN']
        self.d['ESCAPE'] = scons_env['ESCAPE']
        for k, v in kw.items():
            self.d[k] = v
    # Just use the underlying scons_subst*() utility methods.
    def subst(self, strSubst, raw=0, target=[], source=[], dict=None):
        return SCons.Util.scons_subst(strSubst, self, raw, target, source, dict)
    subst_target_source = subst
    def subst_list(self, strSubst, raw=0, target=[], source=[], dict=None):
        return SCons.Util.scons_subst_list(strSubst, self, raw, target, source, dict)
    def __getitem__(self, item):
        return self.d[item]
    def __setitem__(self, item, value):
        self.d[item] = value
    def has_key(self, item):
        return self.d.has_key(item)
    def get(self, key, value):
        return self.d.get(key, value)
    def items(self):
        return self.d.items()
    def Dictionary(self):
        return self.d
    def Copy(self, **kw):
        res = Environment()
        res.d = SCons.Environment.our_deepcopy(self.d)
        for k, v in kw.items():
            res.d[k] = v
        return res
    def sig_dict(self):
        d = {}
        for k,v in self.items(): d[k] = v
        d['TARGETS'] = ['__t1__', '__t2__', '__t3__', '__t4__', '__t5__', '__t6__']
        d['TARGET'] = d['TARGETS'][0]
        d['SOURCES'] = ['__s1__', '__s2__', '__s3__', '__s4__', '__s5__', '__s6__']
        d['SOURCE'] = d['SOURCES'][0]
        return d

class DummyNode:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name
    def rfile(self):
        return self
    def get_subst_proxy(self):
        return self

if os.name == 'java':
    python = os.path.join(sys.prefix, 'jython')
else:
    python = sys.executable

class ActionTestCase(unittest.TestCase):

    def test_factory(self):
        """Test the Action factory
        """
        def foo():
            pass
        def bar():
            pass
        a1 = SCons.Action.Action(foo)
        assert isinstance(a1, SCons.Action.FunctionAction), a1
        assert a1.execfunction == foo, a1.execfunction

        a2 = SCons.Action.Action("string")
        assert isinstance(a2, SCons.Action.CommandAction), a2
        assert a2.cmd_list == "string", a2.cmd_list

        if hasattr(types, 'UnicodeType'):
            exec "a3 = SCons.Action.Action(u'string')"
            exec "assert isinstance(a3, SCons.Action.CommandAction), a3"

        a4 = SCons.Action.Action(["x", "y", "z", [ "a", "b", "c"]])
        assert isinstance(a4, SCons.Action.ListAction), a4
        assert isinstance(a4.list[0], SCons.Action.CommandAction), a4.list[0]
        assert a4.list[0].cmd_list == "x", a4.list[0].cmd_list
        assert isinstance(a4.list[1], SCons.Action.CommandAction), a4.list[1]
        assert a4.list[1].cmd_list == "y", a4.list[1].cmd_list
        assert isinstance(a4.list[2], SCons.Action.CommandAction), a4.list[2]
        assert a4.list[2].cmd_list == "z", a4.list[2].cmd_list
        assert isinstance(a4.list[3], SCons.Action.CommandAction), a4.list[3]
        assert a4.list[3].cmd_list == [ "a", "b", "c" ], a4.list[3].cmd_list

        a5 = SCons.Action.Action(1)
        assert a5 is None, a5

        a6 = SCons.Action.Action(a1)
        assert a6 is a1, a6

        a7 = SCons.Action.Action([[ "explicit", "command", "line" ]])
        assert isinstance(a7, SCons.Action.CommandAction), a7
        assert a7.cmd_list == [ "explicit", "command", "line" ], a7.cmd_list

        a8 = SCons.Action.Action(["a8"])
        assert isinstance(a8, SCons.Action.CommandAction), a8
        assert a8.cmd_list == "a8", a8.cmd_list

        a9 = SCons.Action.Action("x\ny\nz")
        assert isinstance(a9, SCons.Action.ListAction), a9
        assert isinstance(a9.list[0], SCons.Action.CommandAction), a9.list[0]
        assert a9.list[0].cmd_list == "x", a9.list[0].cmd_list
        assert isinstance(a9.list[1], SCons.Action.CommandAction), a9.list[1]
        assert a9.list[1].cmd_list == "y", a9.list[1].cmd_list
        assert isinstance(a9.list[2], SCons.Action.CommandAction), a9.list[2]
        assert a9.list[2].cmd_list == "z", a9.list[2].cmd_list

        a10 = SCons.Action.Action(["x", foo, "z"])
        assert isinstance(a10, SCons.Action.ListAction), a10
        assert isinstance(a10.list[0], SCons.Action.CommandAction), a10.list[0]
        assert a10.list[0].cmd_list == "x", a10.list[0].cmd_list
        assert isinstance(a10.list[1], SCons.Action.FunctionAction), a10.list[1]
        assert a10.list[1].execfunction == foo, a10.list[1].execfunction
        assert isinstance(a10.list[2], SCons.Action.CommandAction), a10.list[2]
        assert a10.list[2].cmd_list == "z", a10.list[2].cmd_list

        a11 = SCons.Action.Action(foo, strfunction=bar)
        assert isinstance(a11, SCons.Action.FunctionAction), a11
        assert a11.execfunction == foo, a11.execfunction
        assert a11.strfunction == bar, a11.strfunction

class ActionBaseTestCase(unittest.TestCase):

    def test___cmp__(self):
        """Test Action comparison
        """
        a1 = SCons.Action.Action("x")
        a2 = SCons.Action.Action("x")
        assert a1 == a2
        a3 = SCons.Action.Action("y")
        assert a1 != a3
        assert a2 != a3

    def test_show(self):
        """Test the show() method
        """
        save_stdout = sys.stdout

        save_print_actions = SCons.Action.print_actions
        SCons.Action.print_actions = 0

        try:
            a = SCons.Action.Action("x")

            sio = StringIO.StringIO()
            sys.stdout = sio
            a.show("xyzzy")
            s = sio.getvalue()
            assert s == "", s

            SCons.Action.print_actions = 1

            sio = StringIO.StringIO()
            sys.stdout = sio
            a.show("foobar")
            s = sio.getvalue()
            assert s == "foobar\n", s

        finally:
            SCons.Action.print_actions = save_print_actions
            sys.stdout = save_stdout

    def test_presub(self):
        """Test the presub() method
        """
        save_stdout = sys.stdout

        save_print_actions_presub = SCons.Action.print_actions_presub
        SCons.Action.print_actions_presub = 0

        try:
            a = SCons.Action.Action("x")
            env = Environment()

            sio = StringIO.StringIO()
            sys.stdout = sio
            a.presub("xyzzy", env)
            s = sio.getvalue()
            assert s == "", s

            SCons.Action.print_actions_presub = 1

            sio = StringIO.StringIO()
            sys.stdout = sio
            a.presub("foobar", env)
            s = sio.getvalue()
            assert s == "Building foobar with action(s):\n  x\n", s

            a = SCons.Action.Action(["y", "z"])

            sio = StringIO.StringIO()
            sys.stdout = sio
            a.presub("foobar", env)
            s = sio.getvalue()
            assert s == "Building foobar with action(s):\n  y\n  z\n", s

            def func():
                pass
            a = SCons.Action.Action(func)

            sio = StringIO.StringIO()
            sys.stdout = sio
            a.presub("foobar", env)
            s = sio.getvalue()
            assert s == "Building foobar with action(s):\n  func(env, target, source)\n", s

            def gen(target, source, env, for_signature):
                return 'generat' + env.get('GEN', 'or')
            a = SCons.Action.Action(SCons.Action.CommandGenerator(gen))

            sio = StringIO.StringIO()
            sys.stdout = sio
            a.presub("foobar", env)
            s = sio.getvalue()
            assert s == "Building foobar with action(s):\n  generator\n", s

            sio = StringIO.StringIO()
            sys.stdout = sio
            a.presub("foobar", Environment(GEN = 'ed'))
            s = sio.getvalue()
            assert s == "Building foobar with action(s):\n  generated\n", s

            a = SCons.Action.Action("$ACT")

            sio = StringIO.StringIO()
            sys.stdout = sio
            a.presub("foobar", env)
            s = sio.getvalue()
            assert s == "Building foobar with action(s):\n  \n", s

            sio = StringIO.StringIO()
            sys.stdout = sio
            a.presub("foobar", Environment(ACT = 'expanded action'))
            s = sio.getvalue()
            assert s == "Building foobar with action(s):\n  expanded action\n", s

        finally:
            SCons.Action.print_actions_presub = save_print_actions_presub
            sys.stdout = save_stdout

    def test_get_actions(self):
        """Test the get_actions() method
        """
        a = SCons.Action.Action("x")
        l = a.get_actions()
        assert l == [a], l

    def test_add(self):
        """Test adding Actions to stuff."""
        # Adding actions to other Actions or to stuff that can
        # be converted into an Action should produce a ListAction
        # containing all the Actions.
        def bar():
            return None
        baz = SCons.Action.CommandGenerator(bar)
        act1 = SCons.Action.Action('foo bar')
        act2 = SCons.Action.Action([ 'foo', bar ])

        sum = act1 + act2
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 3, len(sum.list)
        assert map(lambda x: isinstance(x, SCons.Action.ActionBase),
                   sum.list) == [ 1, 1, 1 ]

        sum = act1 + act1
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 2, len(sum.list)

        sum = act2 + act2
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 4, len(sum.list)

        # Should also be able to add command generators to each other
        # or to actions
        sum = baz + baz
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 2, len(sum.list)

        sum = baz + act1
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 2, len(sum.list)

        sum = act2 + baz
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 3, len(sum.list)

        # Also should be able to add Actions to anything that can
        # be converted into an action.
        sum = act1 + bar
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 2, len(sum.list)
        assert isinstance(sum.list[1], SCons.Action.FunctionAction)

        sum = 'foo bar' + act2
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 3, len(sum.list)
        assert isinstance(sum.list[0], SCons.Action.CommandAction)

        sum = [ 'foo', 'bar' ] + act1
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 3, sum.list
        assert isinstance(sum.list[0], SCons.Action.CommandAction)
        assert isinstance(sum.list[1], SCons.Action.CommandAction)

        sum = act2 + [ baz, bar ]
        assert isinstance(sum, SCons.Action.ListAction), str(sum)
        assert len(sum.list) == 4, len(sum.list)
        assert isinstance(sum.list[2], SCons.Action.CommandGeneratorAction)
        assert isinstance(sum.list[3], SCons.Action.FunctionAction)

        try:
            sum = act2 + 1
        except TypeError:
            pass
        else:
            assert 0, "Should have thrown a TypeError adding to an int."

        try:
            sum = 1 + act2
        except TypeError:
            pass
        else:
            assert 0, "Should have thrown a TypeError adding to an int."

class CommandActionTestCase(unittest.TestCase):

    def test___init__(self):
        """Test creation of a command Action
        """
        a = SCons.Action.CommandAction(["xyzzy"])
        assert a.cmd_list == [ "xyzzy" ], a.cmd_list

    def test___str__(self):
        """Test fetching the pre-substitution string for command Actions
        """
        env = Environment()
        act = SCons.Action.CommandAction('xyzzy $TARGET $SOURCE')
        s = str(act)
        assert s == 'xyzzy $TARGET $SOURCE', s

        act = SCons.Action.CommandAction(['xyzzy',
                                          '$TARGET', '$SOURCE',
                                          '$TARGETS', '$SOURCES'])
        s = str(act)
        assert s == "['xyzzy', '$TARGET', '$SOURCE', '$TARGETS', '$SOURCES']", s

    def test_strfunction(self):
        """Test fetching the string representation of command Actions
        """

        env = Environment()
        t1 = DummyNode('t1')
        t2 = DummyNode('t2')
        s1 = DummyNode('s1')
        s2 = DummyNode('s2')
        act = SCons.Action.CommandAction('xyzzy $TARGET $SOURCE')
        s = act.strfunction([], [], env)
        assert s == ['xyzzy'], s
        s = act.strfunction([t1], [s1], env)
        assert s == ['xyzzy t1 s1'], s
        s = act.strfunction([t1, t2], [s1, s2], env)
        assert s == ['xyzzy t1 s1'], s

        act = SCons.Action.CommandAction('xyzzy $TARGETS $SOURCES')
        s = act.strfunction([], [], env)
        assert s == ['xyzzy'], s
        s = act.strfunction([t1], [s1], env)
        assert s == ['xyzzy t1 s1'], s
        s = act.strfunction([t1, t2], [s1, s2], env)
        assert s == ['xyzzy t1 t2 s1 s2'], s

        act = SCons.Action.CommandAction(['xyzzy',
                                          '$TARGET', '$SOURCE',
                                          '$TARGETS', '$SOURCES'])
        s = act.strfunction([], [], env)
        assert s == ['xyzzy'], s
        s = act.strfunction([t1], [s1], env)
        assert s == ['xyzzy t1 s1 t1 s1'], s
        s = act.strfunction([t1, t2], [s1, s2], env)
        assert s == ['xyzzy t1 s1 t1 t2 s1 s2'], s

    def test_execute(self):
        """Test execution of command Actions

        """
        try:
            env = self.env
        except AttributeError:
            env = Environment()

        cmd1 = r'%s %s %s xyzzy' % (python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd1)
        r = act([], [], env.Copy())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'xyzzy'\n", c

        cmd2 = r'%s %s %s $TARGET' % (python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd2)
        r = act(DummyNode('foo'), [], env.Copy())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'foo'\n", c

        cmd3 = r'%s %s %s ${TARGETS}' % (python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd3)
        r = act(map(DummyNode, ['aaa', 'bbb']), [], env.Copy())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'aaa' 'bbb'\n", c

        cmd4 = r'%s %s %s $SOURCES' % (python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd4)
        r = act([], [DummyNode('one'), DummyNode('two')], env.Copy())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'one' 'two'\n", c

        cmd4 = r'%s %s %s ${SOURCES[:2]}' % (python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd4)
        sources = [DummyNode('three'), DummyNode('four'), DummyNode('five')]
        env2 = env.Copy()
        r = act([], source = sources, env = env2)
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'three' 'four'\n", c

        cmd5 = r'%s %s %s $TARGET XYZZY' % (python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd5)
        env5 = Environment()
        if scons_env.has_key('ENV'):
            env5['ENV'] = scons_env['ENV']
            PATH = scons_env['ENV'].get('PATH', '')
        else:
            env5['ENV'] = {}
            PATH = ''

        env5['ENV']['XYZZY'] = 'xyzzy'
        r = act(target = DummyNode('out5'), source = [], env = env5)

        act = SCons.Action.CommandAction(cmd5)
        r = act(target = DummyNode('out5'),
                source = [],
                env = env.Copy(ENV = {'XYZZY' : 'xyzzy5',
                                      'PATH' : PATH}))
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: 'out5' 'XYZZY'\nact.py: 'xyzzy5'\n", c

        class Obj:
            def __init__(self, str):
                self._str = str
            def __str__(self):
                return self._str
            def rfile(self):
                return self
            def get_subst_proxy(self):
                return self

        cmd6 = r'%s %s %s ${TARGETS[1]} $TARGET ${SOURCES[:2]}' % (python, act_py, outfile)

        act = SCons.Action.CommandAction(cmd6)
        r = act(target = [Obj('111'), Obj('222')],
                        source = [Obj('333'), Obj('444'), Obj('555')],
                        env = env.Copy())
        assert r == 0
        c = test.read(outfile, 'r')
        assert c == "act.py: '222' '111' '333' '444'\n", c

        if os.name == 'nt':
            # NT treats execs of directories and non-executable files
            # as "file not found" errors
            expect_nonexistent = 1
            expect_nonexecutable = 1
        elif sys.platform == 'cygwin':
            expect_nonexistent = 127
            expect_nonexecutable = 127
        else:
            expect_nonexistent = 127
            expect_nonexecutable = 126

        # Test that a nonexistent command returns 127
        act = SCons.Action.CommandAction(python + "_no_such_command_")
        r = act([], [], env.Copy(out = outfile))
        assert r == expect_nonexistent, "r == %d" % r

        # Test that trying to execute a directory returns 126
        dir, tail = os.path.split(python)
        act = SCons.Action.CommandAction(dir)
        r = act([], [], env.Copy(out = outfile))
        assert r == expect_nonexecutable, "r == %d" % r

        # Test that trying to execute a non-executable file returns 126
        act = SCons.Action.CommandAction(outfile)
        r = act([], [], env.Copy(out = outfile))
        assert r == expect_nonexecutable, "r == %d" % r

    def test_pipe_execute(self):
        """Test capturing piped output from an action
        """
        pipe = open( pipe_file, "w" )
        self.env = Environment(ENV = {'ACTPY_PIPE' : '1'}, PIPE_BUILD = 1,
                               PSTDOUT = pipe, PSTDERR = pipe)
        # everything should also work when piping output
        self.test_execute()
        self.env['PSTDOUT'].close()
        pipe_out = test.read( pipe_file )

        act_out = "act.py: stdout: executed act.py"
        act_err = "act.py: stderr: executed act.py"

        # Since we are now using select(), stdout and stderr can be
        # intermixed, so count the lines separately.
        outlines = re.findall(act_out, pipe_out)
        errlines = re.findall(act_err, pipe_out)
        assert len(outlines) == 6, pipe_out + repr(outlines)
        assert len(errlines) == 6, pipe_out + repr(errlines)

        # test redirection operators
        def test_redirect(self, redir, stdout_msg, stderr_msg):
            cmd = r'%s %s %s xyzzy %s' % (python, act_py, outfile, redir)
            # Write the output and error messages to files because Win32
            # can't handle strings that are too big in its external
            # environment (os.spawnve() returns EINVAL, "Invalid
            # argument").
            stdout_file = test.workpath('stdout_msg')
            stderr_file = test.workpath('stderr_msg')
            open(stdout_file, 'w').write(stdout_msg)
            open(stderr_file, 'w').write(stderr_msg)
            pipe = open( pipe_file, "w" )
            act = SCons.Action.CommandAction(cmd)
            env = Environment( ENV = {'ACTPY_PIPE' : '1',
                                      'PIPE_STDOUT_FILE' : stdout_file,
                                      'PIPE_STDERR_FILE' : stderr_file},
                               PIPE_BUILD = 1,
                               PSTDOUT = pipe, PSTDERR = pipe )
            r = act([], [], env)
            pipe.close()
            assert r == 0
            return (test.read(outfile2, 'r'), test.read(pipe_file, 'r'))

        (redirected, pipe_out) = test_redirect(self,'> %s' % outfile2,
                                               act_out, act_err)
        assert redirected == act_out
        assert pipe_out == act_err

        (redirected, pipe_out) = test_redirect(self,'2> %s' % outfile2,
                                               act_out, act_err)
        assert redirected == act_err
        assert pipe_out == act_out

        (redirected, pipe_out) = test_redirect(self,'> %s 2>&1' % outfile2,
                                               act_out, act_err)
        assert (redirected == act_out + act_err or
                redirected == act_err + act_out)
        assert pipe_out == ""

        act_err = "Long Command Output\n"*3000
        # the size of the string should exceed the system's default block size
        act_out = ""
        (redirected, pipe_out) = test_redirect(self,'> %s' % outfile2,
                                               act_out, act_err)
        assert (redirected == act_out)
        assert (pipe_out == act_err)

    def test_set_handler(self):
        """Test setting the command handler...
        """
        class Test:
            def __init__(self):
                self.executed = 0
        t=Test()
        def func(sh, escape, cmd, args, env, test=t):
            test.executed = args
            test.shell = sh
            return 0
        def escape_func(cmd):
            return '**' + cmd + '**'

        class LiteralStr:
            def __init__(self, x):
                self.data = x
            def __str__(self):
                return self.data
            def escape(self, escape_func):
                return escape_func(self.data)
            def is_literal(self):
                return 1

        a = SCons.Action.CommandAction(["xyzzy"])
        e = Environment(SPAWN = func)
        a([], [], e)
        assert t.executed == [ 'xyzzy' ], t.executed

        a = SCons.Action.CommandAction(["xyzzy"])
        e = Environment(SPAWN = func, SHELL = 'fake shell')
        a([], [], e)
        assert t.executed == [ 'xyzzy' ], t.executed
        assert t.shell == 'fake shell', t.shell

        a = SCons.Action.CommandAction([ LiteralStr("xyzzy") ])
        e = Environment(SPAWN = func, ESCAPE = escape_func)
        a([], [], e)
        assert t.executed == [ '**xyzzy**' ], t.executed

    def test_get_contents(self):
        """Test fetching the contents of a command Action
        """
        def CmdGen(target, source, env, for_signature):
            assert for_signature
            return "%s %s" % \
                   (env["foo"], env["bar"])

        # The number 1 is there to make sure all args get converted to strings.
        a = SCons.Action.CommandAction(["|", "$(", "$foo", "|", "$bar",
                                        "$)", "|", "$baz", 1])
        c = a.get_contents(target=[], source=[],
                           env=Environment(foo = 'FFF', bar = 'BBB',
                                           baz = CmdGen))
        assert c == "| | FFF BBB 1", c

        # Make sure that CommandActions use an Environment's
        # subst_target_source() method for substitution.
        class SpecialEnvironment(Environment):
            def subst_target_source(self, strSubst, raw=0, target=[], source=[], dict=None):
                return 'subst_target_source: ' + strSubst

        c = a.get_contents(target=DummyNode('ttt'), source = DummyNode('sss'),
                           env=SpecialEnvironment(foo = 'GGG', bar = 'CCC',
                                                  baz = 'ZZZ'))
        assert c == 'subst_target_source: | $( $foo | $bar $) | $baz 1', c

        # We've discussed using the real target and source names in a
        # CommandAction's signature contents.  This would have have the
        # advantage of recompiling when a file's name changes (keeping
        # debug info current), but it would currently break repository
        # logic that will change the file name based on whether the
        # files come from a repository or locally.  If we ever move to
        # that scheme, then all of the '__t1__' and '__s6__' file names
        # in the asserts below would change to 't1' and 's6' and the
        # like.
        t = map(DummyNode, ['t1', 't2', 't3', 't4', 't5', 't6'])
        s = map(DummyNode, ['s1', 's2', 's3', 's4', 's5', 's6'])
        env = Environment()

        a = SCons.Action.CommandAction(["$TARGET"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == "t1", c
        c = a.get_contents(target=t, source=s, env=env, dict={})
        assert c == "", c

        a = SCons.Action.CommandAction(["$TARGETS"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == "t1 t2 t3 t4 t5 t6", c
        c = a.get_contents(target=t, source=s, env=env, dict={})
        assert c == "", c

        a = SCons.Action.CommandAction(["${TARGETS[2]}"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == "t3", c

        a = SCons.Action.CommandAction(["${TARGETS[3:5]}"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == "t4 t5", c

        a = SCons.Action.CommandAction(["$SOURCE"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == "s1", c
        c = a.get_contents(target=t, source=s, env=env, dict={})
        assert c == "", c

        a = SCons.Action.CommandAction(["$SOURCES"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == "s1 s2 s3 s4 s5 s6", c
        c = a.get_contents(target=t, source=s, env=env, dict={})
        assert c == "", c

        a = SCons.Action.CommandAction(["${SOURCES[2]}"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == "s3", c

        a = SCons.Action.CommandAction(["${SOURCES[3:5]}"])
        c = a.get_contents(target=t, source=s, env=env)
        assert c == "s4 s5", c

class CommandGeneratorActionTestCase(unittest.TestCase):

    def test___init__(self):
        """Test creation of a command generator Action
        """
        def f(target, source, env):
            pass
        a = SCons.Action.CommandGeneratorAction(f)
        assert a.generator == f

    def test___str__(self):
        """Test the pre-substitution strings for command generator Actions
        """
        def f(target, source, env, for_signature, self=self):
            return "FOO"
        a = SCons.Action.CommandGeneratorAction(f)
        s = str(a)
        assert s == 'FOO', s

    def test_strfunction(self):
        """Test the command generator Action string function
        """
        def f(target, source, env, for_signature, self=self):
            dummy = env['dummy']
            self.dummy = dummy
            return "$FOO"
        a = SCons.Action.CommandGeneratorAction(f)
        self.dummy = 0
        s = a.strfunction([], [], env=Environment(FOO='xyzzy', dummy=1))
        assert self.dummy == 1, self.dummy
        assert s == ['xyzzy'], s

    def test_execute(self):
        """Test executing a command generator Action
        """

        def f(target, source, env, for_signature, self=self):
            dummy = env['dummy']
            self.dummy = dummy
            s = env.subst("$FOO")
            assert s == 'foo baz\nbar ack', s
            return "$FOO"
        def func_action(target, source, env, self=self):
            dummy=env['dummy']
            s = env.subst('$foo')
            assert s == 'bar', s
            self.dummy=dummy
        def f2(target, source, env, for_signature, f=func_action):
            return f
        def ch(sh, escape, cmd, args, env, self=self):
            self.cmd.append(cmd)
            self.args.append(args)

        a = SCons.Action.CommandGeneratorAction(f)
        self.dummy = 0
        self.cmd = []
        self.args = []
        a([], [], env=Environment(FOO = 'foo baz\nbar ack',
                                          dummy = 1,
                                          SPAWN = ch))
        assert self.dummy == 1, self.dummy
        assert self.cmd == ['foo', 'bar'], self.cmd
        assert self.args == [[ 'foo', 'baz' ], [ 'bar', 'ack' ]], self.args

        b = SCons.Action.CommandGeneratorAction(f2)
        self.dummy = 0
        b(target=[], source=[], env=Environment(foo =  'bar',
                                                        dummy =  2 ))
        assert self.dummy==2, self.dummy
        del self.dummy

        class DummyFile:
            def __init__(self, t):
                self.t = t
            def rfile(self):
                self.t.rfile_called = 1
                return self
            def get_subst_proxy(self):
                return self
        def f3(target, source, env, for_signature):
            return ''
        c = SCons.Action.CommandGeneratorAction(f3)
        c(target=[], source=DummyFile(self), env=Environment())
        assert self.rfile_called

    def test_get_contents(self):
        """Test fetching the contents of a command generator Action
        """
        def f(target, source, env, for_signature):
            foo = env['foo']
            bar = env['bar']
            assert for_signature, for_signature
            return [["guux", foo, "$(", "$ignore", "$)", bar,
                     '${test("$( foo $bar $)")}' ]]

        def test(mystr):
            assert mystr == "$( foo $bar $)", mystr
            return "test"

        env = Environment(foo = 'FFF', bar =  'BBB',
                          ignore = 'foo', test=test)
        a = SCons.Action.CommandGeneratorAction(f)
        c = a.get_contents(target=[], source=[], env=env)
        assert c == "guux FFF BBB test", c
        c = a.get_contents(target=[], source=[], env=env, dict={})
        assert c == "guux FFF BBB test", c


class FunctionActionTestCase(unittest.TestCase):

    def test___init__(self):
        """Test creation of a function Action
        """
        def func1():
            pass
        def func2():
            pass
        def func3():
            pass
        def func4():
            pass

        a = SCons.Action.FunctionAction(func1)
        assert a.execfunction == func1, a.execfunction
        assert isinstance(a.strfunction, types.FunctionType)

        a = SCons.Action.FunctionAction(func2, strfunction=func3)
        assert a.execfunction == func2, a.execfunction
        assert a.strfunction == func3, a.strfunction

        a = SCons.Action.FunctionAction(func3, func4)
        assert a.execfunction == func3, a.execfunction
        assert a.strfunction == func4, a.strfunction

        a = SCons.Action.FunctionAction(func4, None)
        assert a.execfunction == func4, a.execfunction
        assert a.strfunction is None, a.strfunction

    def test___str__(self):
        """Test the __str__() method for function Actions
        """
        def func1():
            pass
        a = SCons.Action.FunctionAction(func1)
        s = str(a)
        assert s == "func1(env, target, source)", s

        class class1:
            def __call__(self):
                pass
        a = SCons.Action.FunctionAction(class1())
        s = str(a)
        assert s == "class1(env, target, source)", s

    def test_execute(self):
        """Test executing a function Action
        """
        self.inc = 0
        def f(target, source, env):
            s = env['s']
            s.inc = s.inc + 1
            s.target = target
            s.source=source
            assert env.subst("$BAR") == 'foo bar', env.subst("$BAR")
            return 0
        a = SCons.Action.FunctionAction(f)
        a(target=1, source=2, env=Environment(BAR = 'foo bar',
                                                      s = self))
        assert self.inc == 1, self.inc
        assert self.source == [2], self.source
        assert self.target == [1], self.target

        global count
        count = 0
        def function1(target, source, env):
            global count
            count = count + 1
            for t in target:
                open(t, 'w').write("function1\n")
            return 1

        act = SCons.Action.FunctionAction(function1)
        r = None
        try:
            r = act(target = [outfile, outfile2], source=[], env=Environment())
        except SCons.Errors.BuildError:
            pass
        assert r == 1
        assert count == 1
        c = test.read(outfile, 'r')
        assert c == "function1\n", c
        c = test.read(outfile2, 'r')
        assert c == "function1\n", c

        class class1a:
            def __init__(self, target, source, env):
                open(env['out'], 'w').write("class1a\n")

        act = SCons.Action.FunctionAction(class1a)
        r = act([], [], Environment(out = outfile))
        assert r.__class__ == class1a
        c = test.read(outfile, 'r')
        assert c == "class1a\n", c

        class class1b:
            def __call__(self, target, source, env):
                open(env['out'], 'w').write("class1b\n")
                return 2

        act = SCons.Action.FunctionAction(class1b())
        r = act([], [], Environment(out = outfile))
        assert r == 2
        c = test.read(outfile, 'r')
        assert c == "class1b\n", c

        def build_it(target, source, env, self=self):
            self.build_it = 1
            return 0
        def string_it(target, source, env, self=self):
            self.string_it = 1
            return None
        act = SCons.Action.FunctionAction(build_it, string_it)
        r = act([], [], Environment())
        assert r == 0, r
        assert self.build_it
        assert self.string_it

    def test_get_contents(self):
        """Test fetching the contents of a function Action
        """
        a = SCons.Action.FunctionAction(Func)
        c = a.get_contents(target=[], source=[], env=Environment())
        assert c == "\177\036\000\177\037\000d\000\000S", repr(c)
        c = a.get_contents(target=[], source=[], env=Environment(), dict={})
        assert c == "\177\036\000\177\037\000d\000\000S", repr(c)

        a = SCons.Action.FunctionAction(Func, varlist=['XYZ'])
        c = a.get_contents(target=[], source=[], env=Environment())
        assert c == "\177\036\000\177\037\000d\000\000S", repr(c)
        c = a.get_contents(target=[], source=[], env=Environment(XYZ = 'foo'))
        assert c == "\177\036\000\177\037\000d\000\000Sfoo", repr(c)

class ListActionTestCase(unittest.TestCase):

    def test___init__(self):
        """Test creation of a list of subsidiary Actions
        """
        def func():
            pass
        a = SCons.Action.ListAction(["x", func, ["y", "z"]])
        assert isinstance(a.list[0], SCons.Action.CommandAction)
        assert isinstance(a.list[1], SCons.Action.FunctionAction)
        assert isinstance(a.list[2], SCons.Action.ListAction)
        assert a.list[2].list[0].cmd_list == 'y'

    def test_get_actions(self):
        """Test the get_actions() method for ListActions
        """
        a = SCons.Action.ListAction(["x", "y"])
        l = a.get_actions()
        assert len(l) == 2, l
        assert isinstance(l[0], SCons.Action.CommandAction), l[0]
        g = l[0].get_actions()
        assert g == [l[0]], g
        assert isinstance(l[1], SCons.Action.CommandAction), l[1]
        g = l[1].get_actions()
        assert g == [l[1]], g

    def test___str__(self):
        """Test the __str__() method ffor a list of subsidiary Actions
        """
        def f(target,source,env):
            pass
        def g(target,source,env):
            pass
        a = SCons.Action.ListAction([f, g, "XXX", f])
        s = str(a)
        assert s == "f(env, target, source)\ng(env, target, source)\nXXX\nf(env, target, source)", s

    def test_strfunction(self):
        """Test the string function for a list of subsidiary Actions
        """
        def f(target,source,env):
            pass
        def g(target,source,env):
            pass
        a = SCons.Action.ListAction([f, g, "XXX", f])
        s = a.strfunction([], [], Environment())
        assert s == "f([], [])\ng([], [])\nXXX\nf([], [])", s

    def test_execute(self):
        """Test executing a list of subsidiary Actions
        """
        self.inc = 0
        def f(target,source,env):
            s = env['s']
            s.inc = s.inc + 1
        a = SCons.Action.ListAction([f, f, f])
        a([], [], Environment(s = self))
        assert self.inc == 3, self.inc

        cmd2 = r'%s %s %s syzygy' % (python, act_py, outfile)

        def function2(target, source, env):
            open(env['out'], 'a').write("function2\n")
            return 0

        class class2a:
            def __call__(self, target, source, env):
                open(env['out'], 'a').write("class2a\n")
                return 0

        class class2b:
            def __init__(self, target, source, env):
                open(env['out'], 'a').write("class2b\n")
        act = SCons.Action.ListAction([cmd2, function2, class2a(), class2b])
        r = act([], [], Environment(out = outfile))
        assert r.__class__ == class2b
        c = test.read(outfile, 'r')
        assert c == "act.py: 'syzygy'\nfunction2\nclass2a\nclass2b\n", c

    def test_get_contents(self):
        """Test fetching the contents of a list of subsidiary Actions
        """
        self.foo=0
        def gen(target, source, env, for_signature):
            s = env['s']
            s.foo=1
            return "y"
        a = SCons.Action.ListAction(["x",
                                     SCons.Action.CommandGenerator(gen),
                                     "z"])
        c = a.get_contents(target=[], source=[], env=Environment(s = self))
        assert self.foo==1, self.foo
        assert c == "xyz", c
        c = a.get_contents(target=[], source=[], env=Environment(s = self), dict={})
        assert self.foo==1, self.foo
        assert c == "xyz", c

class LazyActionTestCase(unittest.TestCase):
    def test___init__(self):
        """Test creation of a lazy-evaluation Action
        """
        # Environment variable references should create a special
        # type of CommandGeneratorAction that lazily evaluates the
        # variable.
        a9 = SCons.Action.Action('$FOO')
        assert isinstance(a9, SCons.Action.CommandGeneratorAction), a9
        assert a9.generator.var == 'FOO', a9.generator.var

        a10 = SCons.Action.Action('${FOO}')
        assert isinstance(a9, SCons.Action.CommandGeneratorAction), a10
        assert a10.generator.var == 'FOO', a10.generator.var

    def test_strfunction(self):
        """Test the lazy-evaluation Action string function
        """
        def f(target, source, env):
            pass
        a = SCons.Action.Action('$BAR')
        s = a.strfunction([], [], env=Environment(BAR=f, s=self))
        assert s == "f([], [])", s

    def test_execute(self):
        """Test executing a lazy-evaluation Action
        """
        def f(target, source, env):
            s = env['s']
            s.test=1
            return 0
        a = SCons.Action.Action('$BAR')
        a([], [], env=Environment(BAR = f, s = self))
        assert self.test == 1, self.test

    def test_get_contents(self):
        """Test fetching the contents of a lazy-evaluation Action
        """
        a = SCons.Action.Action("${FOO}")
        env = Environment(FOO = [["This", "is", "a", "test"]])
        c = a.get_contents(target=[], source=[], env=env)
        assert c == "This is a test", c
        c = a.get_contents(target=[], source=[], env=env, dict={})
        assert c == "This is a test", c


if __name__ == "__main__":
    suite = unittest.TestSuite()
    tclasses = [ ActionTestCase,
                 ActionBaseTestCase,
                 CommandActionTestCase,
                 CommandGeneratorActionTestCase,
                 FunctionActionTestCase,
                 ListActionTestCase,
                 LazyActionTestCase ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(map(tclass, names))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
