#!/usr/bin/env python
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
import sys

import TestCmd
import TestSCons

if sys.platform == 'win32':
    lib = 'msvcrt'
else:
    lib = 'm'

test = TestSCons.TestSCons() 
python = TestSCons.python

def checkLog( test, logfile, numUpToDate, numCache ):
    test.fail_test(not os.path.exists(test.workpath('config.log')))
    log = test.read(test.workpath(logfile))
    test.fail_test( len( re.findall( "is up to date", log ) ) != numUpToDate )
    test.fail_test( len( re.findall( "\(cached\): Building \S+ failed in a previous run.", log ) ) != numCache )
    


try:

    # 1.1 if checks are ok, the cache mechanism should work

    test.write( 'SConstruct', """
env = Environment()
conf = Configure(env)
r1 = conf.CheckLibWithHeader( '%s', 'math.h', 'c' )
r2 = conf.CheckLibWithHeader( None, 'math.h', 'c' )
r3 = conf.CheckLib( '%s', autoadd=0 )
r4 = conf.CheckLib( None, autoadd=0 )
r5 = conf.CheckCHeader( 'math.h' )
r6 = conf.CheckCXXHeader( 'vector' )
env = conf.Finish()
if not (r1 and r2 and r3 and r4 and r5 and r6):
     Exit(1)
""" % (lib, lib))

    required_stdout = test.wrap_stdout(build_str='scons: "." is up to date.\n',
                                       read_str=
    """Checking for main(); in library %s (header math.h) ... ok
Checking for main(); in library None (header math.h) ... ok
Checking for main in library %s... ok
Checking for main in library None... ok
Checking for C header math.h... ok
Checking for C header vector... ok
""" % (lib, lib))

    test.run(stdout = required_stdout)
    checkLog(test,'config.log', 0, 0 )

    test.run(stdout = required_stdout)
    checkLog(test,'config.log',12, 0 )

    # 1.2 if checks are not ok, the cache mechanism should work as well
    #     (via explicit cache)

    test.write( 'SConstruct', """
env = Environment()
conf = Configure(env)
r1 = conf.CheckCHeader( 'no_std_c_header.h' ) # leads to compile error
r2 = conf.CheckLib( 'no_c_library_SAFFDG' )   # leads to link error
env = conf.Finish()
if not (not r1 and not r2):
     print "FAIL: ", r1, r2
     Exit(1)
""")

    required_stdout = test.wrap_stdout(build_str='scons: "." is up to date.\n',
                                       read_str=
    """Checking for C header no_std_c_header.h... failed
Checking for main in library no_c_library_SAFFDG... failed
""")

    test.run(stdout = required_stdout)
    checkLog(test, 'config.log', 0, 0 )
    
    test.run(stdout = required_stdout)
    checkLog(test, 'config.log', 2, 2 )


    # 2.1 test that normal builds work together with Sconf
    test.write( 'SConstruct', """
env = Environment()
conf = Configure(env)
r1 = conf.CheckCHeader( 'math.h' )
r2 = conf.CheckCHeader( 'no_std_c_header.h' ) # leads to compile error
env = conf.Finish()
Export( 'env' )
SConscript( 'SConscript' )
""")
    test.write( 'SConscript', """
Import( 'env' )
env.Program( 'TestProgram', 'TestProgram.c' )
""")
    test.write( 'TestProgram.c', """
#include <stdio.h>

int main() {
  printf( "Hello\\n" );
}
""")
    test.match_func = TestCmd.match_re_dotall
    required_stdout = test.wrap_stdout(build_str='.*',
                                       read_str=
    """Checking for C header math.h... ok
Checking for C header no_std_c_header.h... failed
""")
    test.run( stdout = required_stdout )
    checkLog( test, 'config.log', 0, 0 )
    
    test.run( stdout = required_stdout )
    checkLog( test, 'config.log', 3, 1 )


    # 2.2 test that BuildDir builds work together with Sconf
    test.write( 'SConstruct', """
env = Environment()
BuildDir( 'build', '.' )
conf = Configure(env, conf_dir='build/config.tests', log_file='build/config.log')
r1 = conf.CheckCHeader( 'math.h' )
r2 = conf.CheckCHeader( 'no_std_c_header.h' ) # leads to compile error
env = conf.Finish()
Export( 'env' )
# print open( 'build/config.log' ).readlines()
SConscript( 'build/SConscript' )
""")
    test.write( 'SConscript', """
Import( 'env' )
env.Program( 'TestProgram', 'TestProgram.c' )
""")
    test.write( 'TestProgram.c', """
#include <stdio.h>

int main() {
  printf( "Hello\\n" );
}
""")
    required_stdout = test.wrap_stdout(build_str='.*',
                                       read_str=
    """Checking for C header math.h... ok
Checking for C header no_std_c_header.h... failed
""")
    test.run( stdout = required_stdout )
    checkLog( test, 'build/config.log', 0, 0 )
    
    test.run( stdout = required_stdout )
    checkLog( test, 'build/config.log', 3, 1 )
    

    # 3.1 test custom tests
    compileOK = '#include <stdio.h>\\nint main() {printf("Hello");return 0;}'
    compileFAIL = "syntax error" 
    linkOK = compileOK
    linkFAIL = "void myFunc(); int main() { myFunc(); }"
    runOK = compileOK
    runFAIL = "int main() { return 1; }"
    test.write( 'pyAct.py', 'import sys\nopen(sys.argv[1], "w").write(sys.argv[2] + "\\n"),\nsys.exit(int(sys.argv[2]))\n' ) 
    test.write( 'SConstruct', """ 
def CheckCustom(test):
    test.Message( 'Executing MyTest...' )
    retCompileOK = test.TryCompile( '%s', '.c' )
    retCompileFAIL = test.TryCompile( '%s', '.c' )
    retLinkOK = test.TryLink( '%s', '.c' )
    retLinkFAIL = test.TryLink( '%s', '.c' )
    (retRunOK, outputRunOK) = test.TryRun( '%s', '.c' )
    (retRunFAIL, outputRunFAIL) = test.TryRun( '%s', '.c' )
    (retActOK, outputActOK) = test.TryAction( '%s pyAct.py $TARGET 0' )
    (retActFAIL, outputActFAIL) = test.TryAction( '%s pyAct.py $TARGET 1' )
    resOK = retCompileOK and retLinkOK and retRunOK and outputRunOK=="Hello"
    resOK = resOK and retActOK and int(outputActOK)==0
    resFAIL = retCompileFAIL or retLinkFAIL or retRunFAIL or outputRunFAIL!=""
    resFAIL = resFAIL or retActFAIL or outputActFAIL!=""
    test.Result( resOK and not resFAIL )
    return resOK and not resFAIL

env = Environment()
conf = Configure( env, custom_tests={'CheckCustom' : CheckCustom} )
conf.CheckCustom()
env = conf.Finish()
""" % (compileOK, compileFAIL, linkOK, linkFAIL, runOK, runFAIL,
       python, python ) )
    required_stdout = test.wrap_stdout(build_str='.*',
                                       read_str="Executing MyTest...ok\n")
    test.run(stdout = required_stdout)
    checkLog( test, 'config.log', 0, 0 )

    test.run(stdout = required_stdout)
    checkLog( test, 'config.log', 12, 4 )

    test.pass_test()
    
finally:
    pass
    #os.system( 'find . -type f -exec ls -l {} \;' )
    #print "-------------config.log------------------"
    #print test.read( test.workpath('config.log' ))
    #print "-------------build/config.log------------"    
    #print test.read( test.workpath('build/config.log' ))
