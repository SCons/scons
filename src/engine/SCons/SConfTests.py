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

import io
import os
import re
import sys
from types import *
import unittest

import TestCmd

sys.stdout = io.StringIO()

if sys.platform == 'win32':
    existing_lib = "msvcrt"
else:
    existing_lib = "m"

class SConfTestCase(unittest.TestCase):

    def setUp(self):
        # we always want to start with a clean directory
        self.save_cwd = os.getcwd()
        self.test = TestCmd.TestCmd(workdir = '')
        os.chdir(self.test.workpath(''))

    def tearDown(self):
        self.test.cleanup()
        import SCons.SConsign
        SCons.SConsign.Reset()
        os.chdir(self.save_cwd)

    def _resetSConfState(self):
        # Ok, this is tricky, and i do not know, if everything is sane.
        # We try to reset scons' state (including all global variables)
        import SCons.SConsign
        SCons.SConsign.write() # simulate normal scons-finish
        for n in list(sys.modules.keys()):
            if n.split('.')[0] == 'SCons' and n[:12] != 'SCons.compat':
                m = sys.modules[n]
                if isinstance(m, ModuleType):
                    # if this is really a scons module, clear its namespace
                    del sys.modules[n]
                    m.__dict__.clear()
        # we only use SCons.Environment and SCons.SConf for these tests.
        import SCons.Environment
        import SCons.SConf
        self.Environment = SCons.Environment
        self.SConf = SCons.SConf
        # and we need a new environment, cause references may point to
        # old modules (well, at least this is safe ...)
        self.scons_env = self.Environment.Environment()
        self.scons_env.AppendENVPath('PATH', os.environ['PATH'])

        # we want to do some autodetection here
        # this stuff works with
        #    - cygwin on Windows (using cmd.exe, not bash)
        #    - posix
        #    - msvc on Windows (hopefully)
        if (not self.scons_env.Detect( self.scons_env.subst('$CXX') ) or
            not self.scons_env.Detect( self.scons_env.subst('$CC') ) or
            not self.scons_env.Detect( self.scons_env.subst('$LINK') )):
            raise Exception("This test needs an installed compiler!")
        if self.scons_env['CXX'] == 'g++':
            global existing_lib
            existing_lib = 'm'

        if sys.platform in ['cygwin', 'win32']:
             # On Windows, SCons.Platform.win32 redefines the builtin
             # file() and open() functions to close the file handles.
             # This interferes with the unittest.py infrastructure in
             # some way.  Just sidestep the issue by restoring the
             # original builtin functions whenever we have to reset
             # all of our global state.

             import SCons.Platform.win32

             try:
                file = SCons.Platform.win32._builtin_file
                open = SCons.Platform.win32._builtin_open
             except AttributeError:
                 pass

    def _baseTryXXX(self, TryFunc):
        # TryCompile and TryLink are much the same, so we can test them
        # in one method, we pass the function as a string ('TryCompile',
        # 'TryLink'), so we are aware of reloading modules.

        def checks(self, sconf, TryFuncString):
            TryFunc = self.SConf.SConfBase.__dict__[TryFuncString]
            res1 = TryFunc( sconf, "int main(void) { return 0; }\n", ".c" )
            res2 = TryFunc( sconf,
                            '#include "no_std_header.h"\nint main(void) {return 0; }\n',
                            '.c' )
            return (res1,res2)

        # 1. test initial behaviour (check ok / failed)
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        try:
            res = checks( self, sconf, TryFunc )
            assert res[0] and not res[1], res
        finally:
            sconf.Finish()

        # 2.1 test the error caching mechanism (no dependencies have changed)
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        try:
            res = checks( self, sconf, TryFunc )
            assert res[0] and not res[1], res
        finally:
            sconf.Finish()
        # we should have exactly one one error cached
        log = str(self.test.read( self.test.workpath('config.log') ))
        expr = re.compile( ".*failed in a previous run and all", re.DOTALL )
        firstOcc = expr.match( log )
        assert firstOcc is not None, log
        secondOcc = expr.match( log, firstOcc.end(0) )
        assert secondOcc is None, log

        # 2.2 test the error caching mechanism (dependencies have changed)
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        no_std_header_h = self.test.workpath('config.tests', 'no_std_header.h')
        test_h = self.test.write( no_std_header_h,
                                  "/* we are changing a dependency now */\n" );
        try:
            res = checks( self, sconf, TryFunc )
            log = self.test.read( self.test.workpath('config.log') )
            assert res[0] and res[1], res
        finally:
            sconf.Finish()

    def test_TryBuild(self):
        """Test SConf.TryBuild
        """
        # 1 test that we can try a builder that returns a list of nodes
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        import SCons.Builder
        import SCons.Node
        class MyBuilder(SCons.Builder.BuilderBase):
            def __init__(self):
                self.prefix = ''
                self.suffix = ''
            def __call__(self, env, target, source):
                class MyNode(object):
                    def __init__(self, name):
                        self.name = name
                        self.state = SCons.Node.no_state
                        self.waiting_parents = set()
                        self.side_effects = []
                        self.builder = None
                        self.prerequisites = None
                    def disambiguate(self):
                        return self
                    def has_builder(self):
                        return 1
                    def add_pre_action(self, *actions):
                        pass
                    def add_post_action(self, *actions):
                        pass
                    def children(self):
                        return []
                    def get_state(self):
                        return self.state
                    def set_state(self, state):
                        self.state = state
                    def alter_targets(self):
                        return [], None
                    def depends_on(self, nodes):
                        return None
                    def postprocess(self):
                        pass
                    def clear(self):
                        pass
                    def is_up_to_date(self):
                        return None
                    def prepare(self):
                        pass
                    def push_to_cache(self):
                        pass
                    def retrieve_from_cache(self):
                        return 0
                    def build(self, **kw):
                        return
                    def built(self):
                        pass
                    def get_stored_info(self):
                        pass
                    def get_executor(self):
                        class Executor(object):
                            def __init__(self, targets):
                                self.targets = targets
                            def get_all_targets(self):
                                return self.targets
                        return Executor([self])
                return [MyNode('n1'), MyNode('n2')]
        try:
            self.scons_env.Append(BUILDERS = {'SConfActionBuilder' : MyBuilder()})
            sconf.TryBuild(self.scons_env.SConfActionBuilder)
        finally:
            sconf.Finish()

    def test_TryCompile(self):
        """Test SConf.TryCompile
        """
        self._baseTryXXX( "TryCompile" ) #self.SConf.SConf.TryCompile )

    def test_TryLink(self):
        """Test SConf.TryLink
        """
        self._baseTryXXX( "TryLink" ) #self.SConf.SConf.TryLink )

    def test_TryRun(self):
        """Test SConf.TryRun
        """
        def checks(sconf):
            prog = """
#include <stdio.h>
int main(void) {
  printf( "Hello" );
  return 0;
}
"""
            res1 = sconf.TryRun( prog, ".c" )
            res2 = sconf.TryRun( "not a c program\n", ".c" )
            return (res1, res2)

        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        try:
            res = checks(sconf)
            assert res[0][0] and res[0][1] == "Hello", res
            assert not res[1][0] and res[1][1] == "", res
        finally:
            sconf.Finish()
        log = self.test.read( self.test.workpath('config.log') )

        # test the caching mechanism
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        try:
            res = checks(sconf)
            assert res[0][0] and res[0][1] == "Hello", res
            assert not res[1][0] and res[1][1] == "", res
        finally:
            sconf.Finish()
        # we should have exactly one error cached
        # creating string here because it's bytes by default on py3
        log = str(self.test.read( self.test.workpath('config.log') ))
        expr = re.compile( ".*failed in a previous run and all", re.DOTALL )
        firstOcc = expr.match( log )
        assert firstOcc is not None, log
        secondOcc = expr.match( log, firstOcc.end(0) )
        assert secondOcc is None, log


    def test_TryAction(self):
        """Test SConf.TryAction
        """
        def actionOK(target, source, env):
            open(str(target[0]), "w").write("RUN OK\n")
            return None
        def actionFAIL(target, source, env):
            return 1
        def actionUnicode(target, source, env):
            open(str(target[0]), "wb").write('2\302\242\n')
            return None


        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                  conf_dir=self.test.workpath('config.tests'),
                                  log_file=self.test.workpath('config.log'))
        try:
            (ret, output) = sconf.TryAction(action=actionOK)
            assert ret and output.encode('utf-8') == bytearray("RUN OK"+os.linesep,'utf-8'), (ret, output)
            (ret, output) = sconf.TryAction(action=actionFAIL)
            assert not ret and output == "", (ret, output)

            if not TestCmd.IS_PY3:
                # GH Issue #3141 - unicode text and py2.7 crashes.
                (ret, output) = sconf.TryAction(action=actionUnicode)
                assert ret and output == u'2\xa2\n', (ret, output)

        finally:
            sconf.Finish()

    def _test_check_compilers(self, comp, func, name):
        """This is the implementation for CheckCC and CheckCXX tests."""
        from copy import deepcopy

        # Check that Check* works
        r = func()
        assert r, "could not find %s ?" % comp

        # Check that Check* does fail if comp is not available in env
        oldcomp = deepcopy(self.scons_env[comp])
        del self.scons_env[comp]
        r = func()
        assert not r, "%s worked wo comp ?" % name

        # Check that Check* does fail if comp is set but empty
        self.scons_env[comp] = ''
        r = func()
        assert not r, "%s worked with comp = '' ?" % name

        # Check that Check* does fail if comp is set to buggy executable
        self.scons_env[comp] = 'thiscccompilerdoesnotexist'
        r = func()
        assert not r, "%s worked with comp = thiscompilerdoesnotexist ?" % name

        # Check that Check* does fail if CFLAGS is buggy
        self.scons_env[comp] = oldcomp
        self.scons_env['%sFLAGS' % comp] = '/WX qwertyuiop.c'
        r = func()
        assert not r, "%s worked with %sFLAGS = qwertyuiop ?" % (name, comp)

    def test_CheckCC(self):
        """Test SConf.CheckCC()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        try:
            try:
                self._test_check_compilers('CC', sconf.CheckCC, 'CheckCC')
            except AssertionError:
                sys.stderr.write(self.test.read('config.log', mode='r'))
                raise
        finally:
            sconf.Finish()

    def test_CheckSHCC(self):
        """Test SConf.CheckSHCC()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        try:
            try:
                self._test_check_compilers('SHCC', sconf.CheckSHCC, 'CheckSHCC')
            except AssertionError:
                sys.stderr.write(self.test.read('config.log', mode='r'))
                raise
        finally:
            sconf.Finish()

    def test_CheckCXX(self):
        """Test SConf.CheckCXX()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        try:
            try:
                self._test_check_compilers('CXX', sconf.CheckCXX, 'CheckCXX')
            except AssertionError:
                sys.stderr.write(self.test.read('config.log', mode='r'))
                raise
        finally:
            sconf.Finish()

    def test_CheckSHCXX(self):
        """Test SConf.CheckSHCXX()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        try:
            try:
                self._test_check_compilers('SHCXX', sconf.CheckSHCXX, 'CheckSHCXX')
            except AssertionError:
                sys.stderr.write(self.test.read('config.log', mode='r'))
                raise
        finally:
            sconf.Finish()


    def test_CheckHeader(self):
        """Test SConf.CheckHeader()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        try:
            # CheckHeader()
            r = sconf.CheckHeader( "stdio.h", include_quotes="<>", language="C" )
            assert r, "did not find stdio.h"
            r = sconf.CheckHeader( "HopefullyNoHeader.noh", language="C" )
            assert not r, "unexpectedly found HopefullyNoHeader.noh"
            r = sconf.CheckHeader( "vector", include_quotes="<>", language="C++" )
            assert r, "did not find vector"
            r = sconf.CheckHeader( "HopefullyNoHeader.noh", language="C++" )
            assert not r, "unexpectedly found HopefullyNoHeader.noh"

        finally:
            sconf.Finish()

    def test_CheckCHeader(self):
        """Test SConf.CheckCHeader()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))

        try:
            # CheckCHeader()
            r = sconf.CheckCHeader( "stdio.h", include_quotes="<>" )
            assert r, "did not find stdio.h"
            r = sconf.CheckCHeader( ["math.h", "stdio.h"], include_quotes="<>" )
            assert r, "did not find stdio.h, #include math.h first"
            r = sconf.CheckCHeader( "HopefullyNoCHeader.noh" )
            assert not r, "unexpectedly found HopefullyNoCHeader.noh"

        finally:
            sconf.Finish()

    def test_CheckCXXHeader(self):
        """Test SConf.CheckCXXHeader()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))

        try:
            # CheckCXXHeader()
            r = sconf.CheckCXXHeader( "vector", include_quotes="<>" )
            assert r, "did not find vector"
            r = sconf.CheckCXXHeader( ["stdio.h", "vector"], include_quotes="<>" )
            assert r, "did not find vector, #include stdio.h first"
            r = sconf.CheckCXXHeader( "HopefullyNoCXXHeader.noh" )
            assert not r, "unexpectedly found HopefullyNoCXXHeader.noh"

        finally:
            sconf.Finish()

    def test_CheckLib(self):
        """Test SConf.CheckLib()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))

        try:
            # CheckLib()
            r = sconf.CheckLib( existing_lib, "main", autoadd=0 )
            assert r, "did not find %s" % existing_lib
            r = sconf.CheckLib( "hopefullynolib", "main", autoadd=0 )
            assert not r, "unexpectedly found hopefullynolib"

            # CheckLib() with list of libs
            r = sconf.CheckLib( [existing_lib], "main", autoadd=0 )
            assert r, "did not find %s" % existing_lib
            r = sconf.CheckLib( ["hopefullynolib"], "main", autoadd=0 )
            assert not r, "unexpectedly found hopefullynolib"
            # This is a check that a null list doesn't find functions
            # that are in libraries that must be explicitly named.
            # This works on POSIX systems where you have to -lm to
            # get the math functions, but it fails on Visual Studio
            # where you apparently get all those functions for free.
            # Comment out this check until someone who understands
            # Visual Studio better can come up with a corresponding
            # test (if that ever really becomes necessary).
            #r = sconf.CheckLib( [], "sin", autoadd=0 )
            #assert not r, "unexpectedly found nonexistent library"
            r = sconf.CheckLib( [existing_lib,"hopefullynolib"], "main", autoadd=0 )
            assert r, "did not find %s,%s " % (existing_lib,r)
            r = sconf.CheckLib( ["hopefullynolib",existing_lib], "main", autoadd=0 )
            assert r, "did not find %s " % existing_lib

            # CheckLib() with autoadd
            def libs(env):
                return env.get('LIBS', [])

            env = sconf.env.Clone()

            try:
                r = sconf.CheckLib( existing_lib, "main", autoadd=1 )
                assert r, "did not find main in %s" % existing_lib
                expect = libs(env) + [existing_lib]
                got = libs(sconf.env)
                assert got == expect, "LIBS: expected %s, got %s" % (expect, got)

                sconf.env = env.Clone()
                r = sconf.CheckLib( existing_lib, "main", autoadd=0 )
                assert r, "did not find main in %s" % existing_lib
                expect = libs(env)
                got = libs(sconf.env)
                assert got == expect, "before and after LIBS were not the same"
            finally:
                sconf.env = env
        finally:
            sconf.Finish()

    def test_CheckLibWithHeader(self):
        """Test SConf.CheckLibWithHeader()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))

        try:
            # CheckLibWithHeader()
            r = sconf.CheckLibWithHeader( existing_lib, "math.h", "C", autoadd=0 )
            assert r, "did not find %s" % existing_lib
            r = sconf.CheckLibWithHeader( existing_lib, ["stdio.h", "math.h"], "C", autoadd=0 )
            assert r, "did not find %s, #include stdio.h first" % existing_lib
            r = sconf.CheckLibWithHeader( "hopefullynolib", "math.h", "C", autoadd=0 )
            assert not r, "unexpectedly found hopefullynolib"

            # CheckLibWithHeader() with lists of libs
            r = sconf.CheckLibWithHeader( [existing_lib], "math.h", "C", autoadd=0 )
            assert r, "did not find %s" % existing_lib
            r = sconf.CheckLibWithHeader( [existing_lib], ["stdio.h", "math.h"], "C", autoadd=0 )
            assert r, "did not find %s, #include stdio.h first" % existing_lib
            # This is a check that a null list doesn't find functions
            # that are in libraries that must be explicitly named.
            # This works on POSIX systems where you have to -lm to
            # get the math functions, but it fails on Visual Studio
            # where you apparently get all those functions for free.
            # Comment out this check until someone who understands
            # Visual Studio better can come up with a corresponding
            # test (if that ever really becomes necessary).
            #r = sconf.CheckLibWithHeader( [], "math.h", "C", call="sin(3);", autoadd=0 )
            #assert not r, "unexpectedly found non-existent library"
            r = sconf.CheckLibWithHeader( ["hopefullynolib"], "math.h", "C", autoadd=0 )
            assert not r, "unexpectedly found hopefullynolib"
            r = sconf.CheckLibWithHeader( ["hopefullynolib",existing_lib], ["stdio.h", "math.h"], "C", autoadd=0 )
            assert r, "did not find %s, #include stdio.h first" % existing_lib
            r = sconf.CheckLibWithHeader( [existing_lib,"hopefullynolib"], ["stdio.h", "math.h"], "C", autoadd=0 )
            assert r, "did not find %s, #include stdio.h first" % existing_lib

            # CheckLibWithHeader with autoadd
            def libs(env):
                return env.get('LIBS', [])

            env = sconf.env.Clone()

            try:
                r = sconf.CheckLibWithHeader( existing_lib, "math.h", "C", autoadd=1 )
                assert r, "did not find math.h with %s" % existing_lib
                expect = libs(env) + [existing_lib]
                got = libs(sconf.env)
                assert got == expect, "LIBS: expected %s, got %s" % (expect, got)

                sconf.env = env.Clone()
                r = sconf.CheckLibWithHeader( existing_lib, "math.h", "C", autoadd=0 )
                assert r, "did not find math.h with %s" % existing_lib
                expect = libs(env)
                got = libs(sconf.env)
                assert got == expect, "before and after LIBS were not the same"
            finally:
                sconf.env = env

        finally:
            sconf.Finish()

    def test_CheckFunc(self):
        """Test SConf.CheckFunc()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))

        try:
            # CheckFunc()
            r = sconf.CheckFunc('strcpy')
            assert r, "did not find strcpy"
            r = sconf.CheckFunc('strcpy', '/* header */ char strcpy();')
            assert r, "did not find strcpy"
            r = sconf.CheckFunc('hopefullynofunction')
            assert not r, "unexpectedly found hopefullynofunction"

        finally:
            sconf.Finish()

    def test_CheckProg(self):
        """Test SConf.CheckProg()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))

        try:
            if os.name != 'nt':
                r = sconf.CheckProg('sh')
                assert r, "/bin/sh"
            else:
                r = sconf.CheckProg('cmd.exe')
                self.assertIn('cmd.exe',r)


            r = sconf.CheckProg('hopefully-not-a-program')
            assert r is None

        finally:
            sconf.Finish()


    def test_Define(self):
        """Test SConf.Define()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'),
                                 config_h = self.test.workpath('config.h'))
        try:
            # XXX: we test the generated config.h string. This is not so good,
            # ideally, we would like to test if the generated file included in
            # a test program does what we want.

            # Test defining one symbol wo value
            sconf.config_h_text = ''
            sconf.Define('YOP')
            assert sconf.config_h_text == '#define YOP\n'

            # Test defining one symbol with integer value
            sconf.config_h_text = ''
            sconf.Define('YOP', 1)
            assert sconf.config_h_text == '#define YOP 1\n'

            # Test defining one symbol with string value
            sconf.config_h_text = ''
            sconf.Define('YOP', '"YIP"')
            assert sconf.config_h_text == '#define YOP "YIP"\n'

            # Test defining one symbol with string value
            sconf.config_h_text = ''
            sconf.Define('YOP', "YIP")
            assert sconf.config_h_text == '#define YOP YIP\n'

        finally:
            sconf.Finish()

    def test_CheckTypeSize(self):
        """Test SConf.CheckTypeSize()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        try:
            # CheckTypeSize()

            # In ANSI C, sizeof(char) == 1.
            r = sconf.CheckTypeSize('char', expect = 1)
            assert r == 1, "sizeof(char) != 1 ??"
            r = sconf.CheckTypeSize('char', expect = 0)
            assert r == 0, "sizeof(char) == 0 ??"
            r = sconf.CheckTypeSize('char', expect = 2)
            assert r == 0, "sizeof(char) == 2 ??"
            r = sconf.CheckTypeSize('char')
            assert r == 1, "sizeof(char) != 1 ??"
            r = sconf.CheckTypeSize('const unsigned char')
            assert r == 1, "sizeof(const unsigned char) != 1 ??"

            # Checking C++
            r = sconf.CheckTypeSize('const unsigned char', language = 'C++')
            assert r == 1, "sizeof(const unsigned char) != 1 ??"

            # Checking Non-existing type
            r = sconf.CheckTypeSize('thistypedefhasnotchancetosexist_scons')
            assert r == 0, \
                   "Checking size of thistypedefhasnotchancetosexist_scons succeeded ?"

        finally:
            sconf.Finish()

    def test_CheckDeclaration(self):
        """Test SConf.CheckDeclaration()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        try:
            # In ANSI C, malloc should be available in stdlib
            r = sconf.CheckDeclaration('malloc', includes = "#include <stdlib.h>")
            assert r, "malloc not declared ??"
            # For C++, __cplusplus should be declared
            r = sconf.CheckDeclaration('__cplusplus', language = 'C++')
            assert r, "__cplusplus not declared in C++ ??"
            r = sconf.CheckDeclaration('__cplusplus', language = 'C')
            assert not r, "__cplusplus declared  in C ??"
            r = sconf.CheckDeclaration('unknown', language = 'Unknown')
            assert not r, "unknown language was supported ??"
        finally:
            sconf.Finish()

    def test_(self):
        """Test SConf.CheckType()
        """
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        try:
            # CheckType()
            r = sconf.CheckType('off_t', '#include <sys/types.h>\n')
            assert r, "did not find off_t"
            r = sconf.CheckType('hopefullynotypedef_not')
            assert not r, "unexpectedly found hopefullynotypedef_not"

        finally:
            sconf.Finish()

    def test_CustomChecks(self):
        """Test Custom Checks
        """
        def CheckCustom(test):
            test.Message( "Checking UserTest ... " )
            prog = """
#include <stdio.h>

int main(void) {
  printf( "Hello" );
  return 0;
}
"""
            (ret, output) = test.TryRun( prog, ".c" )
            test.Result( ret )
            assert ret and output == "Hello", (ret, output)
            return ret


        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 custom_tests={'CheckCustom': CheckCustom},
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        try:
            ret = sconf.CheckCustom()
            assert ret, ret
        finally:
            sconf.Finish()


if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
