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

import re
import StringIO
import sys
import unittest

import TestCmd

import SCons.Environment
import SCons.SConf

scons_env = SCons.Environment.Environment()
sys.stdout = StringIO.StringIO()

if sys.platform == 'win32':
    existing_lib = "msvcrt"
else:
    existing_lib = "m"

def clearFileCache(dir):
    # mostly from FS.Dir.__clearRepositoryCache, but set also state
    # of nodes to None
    for node in dir.entries.values():
        if node != dir.dir:
            if node != dir and isinstance(node, SCons.Node.FS.Dir):
                clearFileCache(node)
            else:
                node._srcreps = None
                del node._srcreps
                node._rfile = None
                del node._rfile
                node._rexists = None
                del node._rexists
                node._exists = None
                del node._exists
                node._srcnode = None
                del node._srcnode
                node.set_state(None)

class SConfTestCase(unittest.TestCase):

    def setUp(self):
        self.test = TestCmd.TestCmd(workdir = '')

    def tearDown(self):
        self.test.cleanup()

    def _resetSConfState(self):
                        
        clearFileCache( SCons.Node.FS.default_fs.Dir(self.test.workpath()) )
        SCons.SConf._ac_config_counter = 0
        SCons.SConf._ac_build_counter = 0
            
        
    def _baseTryXXX(self, TryFunc):
        def checks(sconf, TryFunc):
            res1 = TryFunc( sconf, "int main() { return 0; }", ".c" )
            res2 = TryFunc( sconf, "not a c program", ".c" )
            return (res1,res2)
        
        self._resetSConfState()
        sconf = SCons.SConf.SConf(scons_env,
                                  conf_dir=self.test.workpath('config.tests'),
                                  log_file=self.test.workpath('config.log'))
        try:
            res = checks( sconf, TryFunc )
            assert res[0] and not res[1] 
        finally:
            sconf.Finish()

        # test the caching mechanism
        self._resetSConfState()

        sconf = SCons.SConf.SConf(scons_env,
                                  conf_dir=self.test.workpath('config.tests'),
                                  log_file=self.test.workpath('config.log'))
        try:
            res = checks( sconf, TryFunc )
            assert res[0] and not res[1] 
        finally:
            sconf.Finish()

        # we should have exactly one one error cached 
        log = self.test.read( self.test.workpath('config.log') )
        expr = re.compile( ".*(\(cached\))", re.DOTALL ) 
        firstOcc = expr.match( log )
        assert firstOcc != None 
        secondOcc = expr.match( log, firstOcc.end(0) )
        assert secondOcc == None 

    def test_TryCompile(self):
        self._baseTryXXX( SCons.SConf.SConf.TryCompile )
        
    def test_TryLink(self):
        self._baseTryXXX( SCons.SConf.SConf.TryLink )

    def test_TryRun(self):
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
        sconf = SCons.SConf.SConf(scons_env,
                                  conf_dir=self.test.workpath('config.tests'),
                                  log_file=self.test.workpath('config.log'))
        try:
            res = checks(sconf)
            assert res[0][0] and res[0][1] == "Hello" 
            assert not res[1][0] and res[1][1] == ""
        finally:
            sconf.Finish()

        # test the caching mechanism
        self._resetSConfState()

        sconf = SCons.SConf.SConf(scons_env,
                                  conf_dir=self.test.workpath('config.tests'),
                                  log_file=self.test.workpath('config.log'))
        try:
            res = checks(sconf)
            assert res[0][0] and res[0][1] == "Hello" 
            assert not res[1][0] and res[1][1] == ""
        finally:
            sconf.Finish()

        # we should have exactly one one error cached 
        log = self.test.read( self.test.workpath('config.log') )
        expr = re.compile( ".*(\(cached\))", re.DOTALL )
        firstOcc = expr.match( log )
        assert firstOcc != None 
        secondOcc = expr.match( log, firstOcc.end(0) )
        assert secondOcc == None 


    def test_TryAction(self):
        def actionOK(target, source, env):
            open(str(target[0]), "w").write( "RUN OK" )
            return None
        def actionFAIL(target, source, env):
            return 1
        self._resetSConfState()
        sconf = SCons.SConf.SConf(scons_env,
                                  conf_dir=self.test.workpath('config.tests'),
                                  log_file=self.test.workpath('config.log'))
        try:
            (ret, output) = sconf.TryAction(action=actionOK)
            assert ret and output == "RUN OK"
            (ret, output) = sconf.TryAction(action=actionFAIL)
            assert not ret and output == ""
        finally:
            sconf.Finish()
            
        

    def test_StandardTests(self):
        def CHeaderChecks( sconf ):
            res1 = sconf.CheckCHeader( "stdio.h" )
            res2 = sconf.CheckCHeader( "HopefullyNotCHeader.noh" )
            return (res1,res2)

        def CXXHeaderChecks(sconf):
            res1 = sconf.CheckCXXHeader( "vector" )
            res2 = sconf.CheckCXXHeader( "HopefullyNotCXXHeader.noh" )
            return (res1,res2)

        def LibChecks(sconf):
            res1 = sconf.CheckLib( existing_lib, "main", autoadd=0 )
            res2 = sconf.CheckLib( "hopefullynolib", "main", autoadd=0 )
            return (res1, res2)
        
        def LibChecksAutoAdd(sconf):
            def libs(env):
                if env.has_key( "LIBS" ):
                    return env['LIBS']
                else:
                    return []
            env = sconf.env.Copy()
            res1 = sconf.CheckLib( existing_lib, "main", autoadd=1 )
            libs1 = (libs(env), libs(sconf.env) )
            sconf.env = env.Copy()
            res2 = sconf.CheckLib( existing_lib, "main", autoadd=0 )
            libs2 = (libs(env), libs(sconf.env) )
            sconf.env = env.Copy()
            return ((res1, libs1), (res2, libs2))

        def LibWithHeaderChecks(sconf):
            res1 = sconf.CheckLibWithHeader( existing_lib, "math.h", "C", autoadd=0 )
            res2 = sconf.CheckLibWithHeader( "hopefullynolib", "math.h", "C", autoadd=0 )
            return (res1, res2)

        def LibWithHeaderChecksAutoAdd(sconf):
            def libs(env):
                if env.has_key( "LIBS" ):
                    return env['LIBS']
                else:
                    return []
            env = sconf.env.Copy()
            res1 = sconf.CheckLibWithHeader( existing_lib, "math.h", "C", autoadd=1 )
            libs1 = (libs(env), libs(sconf.env) )
            sconf.env = env.Copy()
            res2 = sconf.CheckLibWithHeader( existing_lib, "math.h", "C", autoadd=0 )
            libs2 = (libs(env), libs(sconf.env) )
            sconf.env = env.Copy()
            return ((res1, libs1), (res2, libs2))

        self._resetSConfState()
        sconf = SCons.SConf.SConf(scons_env,
                                  conf_dir=self.test.workpath('config.tests'),
                                  log_file=self.test.workpath('config.log'))
        try:
            (res1, res2) = CHeaderChecks(sconf)
            assert res1 and not res2 
            (res1, res2) = CXXHeaderChecks(sconf)
            assert res1 and not res2 
            (res1, res2) = LibChecks(sconf)
            assert res1 and not res2 
            ((res1, libs1), (res2, libs2)) = LibChecksAutoAdd(sconf)
            assert res1 and res2 
            assert len(libs1[1]) - 1 == len(libs1[0]) and libs1[1][-1] == existing_lib
            assert len(libs2[1]) == len(libs2[0]) 
            (res1, res2) = LibWithHeaderChecks(sconf)
            assert res1 and not res2 
            ((res1, libs1), (res2, libs2)) = LibWithHeaderChecksAutoAdd(sconf)
            assert res1 and res2 
            assert len(libs1[1]) - 1 == len(libs1[0]) and libs1[1][-1] == existing_lib
            assert len(libs2[1]) == len(libs2[0]) 
        finally:
            sconf.Finish()

    def test_CustomChecks(self):

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
            assert ret and output == "Hello" 
            return ret
        

        self._resetSConfState()
        sconf = SCons.SConf.SConf(scons_env,
                                  custom_tests={'CheckCustom': CheckCustom},
                                  conf_dir=self.test.workpath('config.tests'),
                                  log_file=self.test.workpath('config.log'))
        try:
            ret = sconf.CheckCustom()
            assert ret 
        finally:
            sconf.Finish()
            

if __name__ == "__main__":
    suite = unittest.makeSuite(SConfTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful ():
        sys.exit(1)
        
