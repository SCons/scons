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
import shutil

import TestCmd
import TestSCons

if sys.platform == 'win32':
    lib = 'msvcrt'
else:
    lib = 'm'

# to use cygwin compilers on cmd.exe -> uncomment following line
#lib = 'm'

oldPwd = os.getcwd()
python = TestSCons.python
test = None

def reset(dot = 1):
    global test, oldPwd
    os.chdir( oldPwd )
    TestSCons.scons = None
    test = TestSCons.TestSCons()
    if dot == 1:
        test.match_func = TestCmd.match_re_dotall
    

def checkFiles(test, files):
    for f in files:
        test.fail_test( not os.path.isfile( test.workpath(f) ) )


def checkLog( test, logfile, numUpToDate, numCache ):
    test.fail_test(not os.path.exists(test.workpath(logfile)))
    log = test.read(test.workpath(logfile))
    try:
        test.fail_test( len( re.findall( "is up to date", log ) ) != numUpToDate )
        test.fail_test( len( re.findall( "\(cached\): Building \S+ failed in a previous run.", log ) ) != numCache )
    except:
        print "contents of log ", test.workpath(logfile), "\n", log
        raise 


try:

    # 1.1 if checks are ok, the cache mechanism should work

    reset(dot=0)
    
    test.write( 'SConstruct', """
env = Environment()
import os
env['ENV']['PATH'] = os.environ['PATH']
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
""" % (lib,lib))

    required_stdout = test.wrap_stdout(build_str="scons: `.' is up to date.\n",
                                       read_str=
    """Checking for main() in C library %s... yes
Checking for main() in C library None... yes
Checking for main() in C library %s... yes
Checking for main() in C library None... yes
Checking for C header file math.h... yes
Checking for C++ header file vector... yes
""" % (lib, lib))


    test.run(stdout = required_stdout)
    checkLog(test,'config.log', 0, 0 )

    test.run(stdout = required_stdout)
    checkLog(test,'config.log',12, 0 )

    # 1.2 if checks are not ok, the cache mechanism should work as well
    #     (via explicit cache)
    reset(dot = 0)              # match exactly, "()" is a regexp thing

    test.write( 'SConstruct', """
env = Environment()
import os
env['ENV']['PATH'] = os.environ['PATH']
conf = env.Configure()
r1 = conf.CheckCHeader( 'no_std_c_header.h' ) # leads to compile error
r2 = conf.CheckLib( 'no_c_library_SAFFDG' )   # leads to link error
env = conf.Finish()
if not (not r1 and not r2):
     print "FAIL: ", r1, r2
     Exit(1)
""")

    required_stdout = test.wrap_stdout(build_str="scons: `.' is up to date.\n",
                                       read_str=
    """Checking for C header file no_std_c_header.h... no
Checking for main() in C library no_c_library_SAFFDG... no
""")


    test.run(stdout = required_stdout)
    checkLog(test, 'config.log', 0, 0 )
    
    test.run(stdout = required_stdout)
    checkLog(test, 'config.log', 2, 2 )


    # 2.1 test that normal builds work together with Sconf
    reset()
    

    test.write( 'SConstruct', """
env = Environment()
import os
env['ENV']['PATH'] = os.environ['PATH']
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
    required_stdout = test.wrap_stdout(build_str='.*',
                                       read_str=
    """Checking for C header file math.h... yes
Checking for C header file no_std_c_header.h... no
""")
    test.run( stdout = required_stdout )
    checkLog( test, 'config.log', 0, 0 )
    
    test.run( stdout = required_stdout )
    checkLog( test, 'config.log', 3, 1 )


    # 2.2 test that BuildDir builds work together with Sconf
    reset()
    

    test.write( 'SConstruct', """
env = Environment(LOGFILE='build/config.log')
import os
env['ENV']['PATH'] = os.environ['PATH']
BuildDir( 'build', '.' )
conf = env.Configure(conf_dir='build/config.tests', log_file='$LOGFILE')
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
    """Checking for C header file math.h... yes
Checking for C header file no_std_c_header.h... no
""")
    test.run( stdout = required_stdout )
    checkLog( test, 'build/config.log', 0, 0 )
    
    test.run( stdout = required_stdout )
    checkLog( test, 'build/config.log', 3, 1 )
    
    # 2.3 test that Configure calls in SConscript files work
    #     even if BuildDir is set
    reset()

    test.subdir( 'sub', ['sub', 'local'] )
    test.write( 'SConstruct', """
opts = Options()
opts.Add('chdir')
env = Environment(options=opts)
if env['chdir'] == 'yes':
  SConscriptChdir(1)
else:
  SConscriptChdir(0)
BuildDir( 'build', '.' )
SConscript( 'build/SConscript' )
""")
    test.write( 'sub/local/local_header.h', "/* Hello World */" )
    test.write( 'SConscript', """
SConscript( 'sub/SConscript' )
""")
    test.write( 'sub/SConscript', """
def CustomTest(context):
  context.Message('Executing Custom Test ... ')
  ret = context.TryCompile('#include "local_header.h"', '.c')
  context.Result(ret)
  return ret

env = Environment(FOO='fff')
env.Append( CPPPATH='local' )
import os
env['ENV']['PATH'] = os.environ['PATH']
conf = Configure( env, custom_tests = {'CustomTest' : CustomTest,
                                       '$FOO' : CustomTest} )
if hasattr(conf, 'fff'):
  conf.Message('$FOO should not have been expanded!')
  Exit(1)
if not conf.CheckCHeader( 'math.h' ):
  Exit(1)
if conf.CheckCHeader( 'no_std_c_header.h' ):
  Exit(1)
if not conf.CustomTest():
  Exit(1)
env = conf.Finish()
env.Program( 'TestProgram', 'TestProgram.c' )
""")
    test.write( 'sub/TestProgram.h', """
/* Just a test header */
""")
    test.write( 'sub/TestProgram.c', """
#include "TestProgram.h"
#include <stdio.h>

int main() {
  printf( "Hello\\n" );
}
""")
    required_stdout = test.wrap_stdout(build_str='.*',
                                       read_str=
    """Checking for C header file math.h... yes
Checking for C header file no_std_c_header.h... no
Executing Custom Test ... ok
""")
    # first with SConscriptChdir(0)
    test.run(stdout = required_stdout, arguments='chdir=no')
    checkFiles( test, [".sconf_temp/.cache", "config.log"] )
    checkLog( test, 'config.log', 0, 0 )

    test.run(stdout = required_stdout, arguments='chdir=no')
    checkFiles( test, [".sconf_temp/.cache", "config.log"] )
    checkLog( test, 'config.log', 5, 1 )

    shutil.rmtree(test.workpath(".sconf_temp"))

    # now with SConscriptChdir(1)
    test.run(stdout = required_stdout, arguments='chdir=yes')
    checkFiles( test, [".sconf_temp/.cache", "config.log"] )
    checkLog( test, 'config.log', 0, 0 )

    test.run(stdout = required_stdout, arguments='chdir=yes')
    checkFiles( test, [".sconf_temp/.cache", "config.log"] )
    checkLog( test, 'config.log', 5, 1 )

    # 3.1 test custom tests
    reset()
    
    compileOK = '#include <stdio.h>\\nint main() {printf("Hello");return 0;}'
    compileFAIL = "syntax error" 
    linkOK = compileOK
    linkFAIL = "void myFunc(); int main() { myFunc(); }"
    runOK = compileOK
    runFAIL = "int main() { return 1; }"
    test.write('pyAct.py', 'import sys\nprint sys.argv[1]\nsys.exit(int(sys.argv[1]))\n') 
    test.write('SConstruct', """ 
def CheckCustom(test):
    test.Message( 'Executing MyTest ... ' )
    retCompileOK = test.TryCompile( '%s', '.c' )
    retCompileFAIL = test.TryCompile( '%s', '.c' )
    retLinkOK = test.TryLink( '%s', '.c' )
    retLinkFAIL = test.TryLink( '%s', '.c' )
    (retRunOK, outputRunOK) = test.TryRun( '%s', '.c' )
    (retRunFAIL, outputRunFAIL) = test.TryRun( '%s', '.c' )
    (retActOK, outputActOK) = test.TryAction( '%s pyAct.py 0 > $TARGET' )
    (retActFAIL, outputActFAIL) = test.TryAction( '%s pyAct.py 1 > $TARGET' )
    resOK = retCompileOK and retLinkOK and retRunOK and outputRunOK=="Hello"
    resOK = resOK and retActOK and int(outputActOK)==0
    resFAIL = retCompileFAIL or retLinkFAIL or retRunFAIL or outputRunFAIL!=""
    resFAIL = resFAIL or retActFAIL or outputActFAIL!=""
    test.Result( resOK and not resFAIL )
    return resOK and not resFAIL

env = Environment()
import os
env['ENV']['PATH'] = os.environ['PATH']
conf = Configure( env, custom_tests={'CheckCustom' : CheckCustom} )
conf.CheckCustom()
env = conf.Finish()
""" % (compileOK, compileFAIL, linkOK, linkFAIL, runOK, runFAIL,
       python, python ) )
    required_stdout = test.wrap_stdout(build_str='.*',
                                       read_str="Executing MyTest ... ok\n")
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
