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
import re
import string
import StringIO
import sys
from types import *
import unittest

import TestCmd

sys.stdout = StringIO.StringIO()

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
        for n in sys.modules.keys():
            if string.split(n, '.')[0] == 'SCons':
                m = sys.modules[n]
                if type(m) is ModuleType:
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
            raise Exception, "This test needs an installed compiler!"
        if self.scons_env['CXX'] == 'g++':
            global existing_lib
            existing_lib = 'm'
        
    def _baseTryXXX(self, TryFunc):
        # TryCompile and TryLink are much the same, so we can test them
        # in one method, we pass the function as a string ('TryCompile',
        # 'TryLink'), so we are aware of reloading modules.
        
        def checks(self, sconf, TryFuncString):
            TryFunc = self.SConf.SConf.__dict__[TryFuncString]
            res1 = TryFunc( sconf, "int main() { return 0; }", ".c" )
            res2 = TryFunc( sconf,
                            '#include "no_std_header.h"\nint main() {return 0; }',
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
        log = self.test.read( self.test.workpath('config.log') )
        expr = re.compile( ".*failed in a previous run and all", re.DOTALL ) 
        firstOcc = expr.match( log )
        assert firstOcc != None, log
        secondOcc = expr.match( log, firstOcc.end(0) )
        assert secondOcc == None, log

        # 2.2 test the error caching mechanism (dependencies have changed)
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                 conf_dir=self.test.workpath('config.tests'),
                                 log_file=self.test.workpath('config.log'))
        test_h = self.test.write( self.test.workpath('config.tests', 'no_std_header.h'),
                                  "/* we are changing a dependency now */" );
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
        class MyBuilder:
            def __init__(self):
                self.prefix = ''
                self.suffix = ''
            def __call__(self, env, target, source):
                class MyNode:
                    def __init__(self, name):
                        self.name = name
                        self.state = None
                        self.side_effects = []
                        self.builder = None
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
                    def current(self, calc=None):
                        return None
                    def prepare(self):
                        pass
                    def retrieve_from_cache(self):
                        return 0
                    def build(self, **kw):
                        return
                    def built(self):
                        pass
                    def get_stored_info(self):
                        pass
                    def calc_signature(self, calc):
                        pass
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
int main() {
  printf( "Hello" );
  return 0;
}
"""
            res1 = sconf.TryRun( prog, ".c" ) 
            res2 = sconf.TryRun( "not a c program", ".c" )
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
        log = self.test.read( self.test.workpath('config.log') )
        expr = re.compile( ".*failed in a previous run and all", re.DOTALL )
        firstOcc = expr.match( log )
        assert firstOcc != None, log
        secondOcc = expr.match( log, firstOcc.end(0) )
        assert secondOcc == None, log


    def test_TryAction(self):
        """Test SConf.TryAction
        """
        def actionOK(target, source, env):
            open(str(target[0]), "w").write( "RUN OK" )
            return None
        def actionFAIL(target, source, env):
            return 1
        self._resetSConfState()
        sconf = self.SConf.SConf(self.scons_env,
                                  conf_dir=self.test.workpath('config.tests'),
                                  log_file=self.test.workpath('config.log'))
        try:
            (ret, output) = sconf.TryAction(action=actionOK)
            assert ret and output == "RUN OK", (ret, output)
            (ret, output) = sconf.TryAction(action=actionFAIL)
            assert not ret and output == "", (ret, output)
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

            env = sconf.env.Copy()

            try:
                r = sconf.CheckLib( existing_lib, "main", autoadd=1 )
                assert r, "did not find main in %s" % existing_lib
                expect = libs(env) + [existing_lib]
                got = libs(sconf.env)
                assert got == expect, "LIBS: expected %s, got %s" % (expect, got)

                sconf.env = env.Copy()
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

            env = sconf.env.Copy()

            try:
                r = sconf.CheckLibWithHeader( existing_lib, "math.h", "C", autoadd=1 )
                assert r, "did not find math.h with %s" % existing_lib
                expect = libs(env) + [existing_lib]
                got = libs(sconf.env)
                assert got == expect, "LIBS: expected %s, got %s" % (expect, got)

                sconf.env = env.Copy()
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

int main() {
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
    suite = unittest.makeSuite(SConfTestCase, 'test_')
    res = unittest.TextTestRunner().run(suite)
    if not res.wasSuccessful():
        sys.exit(1)

