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
import shutil
import string
import sys

import __builtin__
try:
    __builtin__.zip
except AttributeError:
    def zip(*lists):
        result = []
        for i in xrange(len(lists[0])):
            result.append(tuple(map(lambda l, i=i: l[i], lists)))
        return result
    __builtin__.zip = zip

import TestCmd
import TestSCons

if sys.platform == 'win32':
    lib = 'msvcrt'
else:
    lib = 'm'

# to use cygwin compilers on cmd.exe -> uncomment following line
#lib = 'm'

work_cnt = 0
work_dir = None
python = TestSCons.python
test = TestSCons.TestSCons()
_obj = TestSCons._obj
_exe = TestSCons._exe

RE = 0
RE_DOTALL = 1
EXACT = 2
def reset(match):
    global test, work_dir, work_cnt
    work_cnt = work_cnt + 1
    work_dir='test%d' % work_cnt
    test.subdir(work_dir)
    if match == RE:
        test.match_func = TestCmd.match_re
    elif match == RE_DOTALL:
        test.match_func = TestCmd.match_re_dotall
    elif match == EXACT:
        test.match_func = TestCmd.match_exact

def checkFiles(test, files):
    global work_dir
    for f in files:
        test.fail_test( not os.path.isfile( test.workpath(work_dir,f) ) )

def checklib(lang, name, up_to_date):
    if lang == 'C':
        return (".c", _obj, _exe)
    elif lang == 'C++':
        return (".cc", _obj, _exe)

class NoMatch:
    def __init__(self, p):
        self.pos = p

NCR = 0 # non-cached rebuild
CR  = 1 # cached rebuild (up to date)
NCF = 2 # non-cached build failure
CF  = 3 # cached build failure

def checkLogAndStdout(checks, results, cached,
                      test, logfile, sconf_dir, sconstruct,
                      doCheckLog=1, doCheckStdout=1):
    def matchPart(log, logfile, lastEnd):
        m = re.match(log, logfile[lastEnd:])
        if not m:
            raise NoMatch, lastEnd
        return m.end() + lastEnd
    try:
        #print len(os.linesep)
        ls = os.linesep
        nols = "("
        for i in range(len(ls)):
            nols = nols + "("
            for j in range(i):
                nols = nols + ls[j]
            nols = nols + "[^" + ls[i] + "])"
            if i < len(ls)-1:
                nols = nols + "|"
        nols = nols + ")"
        lastEnd = 0
        logfile = test.read(test.workpath(work_dir, logfile))
        if (doCheckLog and
            string.find( logfile, "scons: warning: The stored build "
                         "information has an unexpected class." ) >= 0):
            test.fail_test()
        sconf_dir = sconf_dir
        sconstruct = sconstruct

        log = re.escape("file " + sconstruct + ",line ") + r"\d+:" + ls
        if doCheckLog: lastEnd = matchPart(log, logfile, lastEnd)
        log = "\t" + re.escape("Configure(confdir = %s)" % sconf_dir) + ls
        if doCheckLog: lastEnd = matchPart(log, logfile, lastEnd)
        rdstr = ""
        cnt = 0
        for check,result,cache_desc in zip(checks, results, cached):
            log   = re.escape("scons: Configure: " + check) + ls
            if doCheckLog: lastEnd = matchPart(log, logfile, lastEnd)
            log = ""
            result_cached = 1
            for bld_desc in cache_desc: # each TryXXX
                for ext, flag in bld_desc: # each file in TryBuild
                    file = os.path.join(sconf_dir,"conftest_%d%s" % (cnt, ext))
                    if flag == NCR:
                        # rebuild will pass
                        if ext in ['.c', '.cpp']:
                            log=log + re.escape(file + " <-") + ls
                            log=log + r"(  \|" + nols + "*" + ls + ")+?"
                        else:
                            log=log + "(" + nols + "*" + ls +")*?"
                        result_cached = 0
                    if flag == CR:
                        # up to date
                        log=log + \
                             re.escape("scons: Configure: \"%s\" is up to date." 
                                       % file) + ls
                        log=log+re.escape("scons: Configure: The original builder "
                                          "output was:") + ls
                        log=log+r"(  \|.*"+ls+")+"
                    if flag == NCF:
                        # non-cached rebuild failure
                        log=log + "(" + nols + "*" + ls + ")*?"
                        result_cached = 0
                    if flag == CF:
                        # cached rebuild failure
                        log=log + \
                             re.escape("scons: Configure: Building \"%s\" failed "
                                       "in a previous run and all its sources are"
                                       " up to date." % file) + ls
                        log=log+re.escape("scons: Configure: The original builder "
                                          "output was:") + ls
                        log=log+r"(  \|.*"+ls+")+"
                cnt = cnt + 1
            if result_cached:
                result = "(cached) " + result
            rdstr = rdstr + re.escape(check) + re.escape(result) + "\n"
            log=log + re.escape("scons: Configure: " + result) + ls + ls
            if doCheckLog: lastEnd = matchPart(log, logfile, lastEnd)
            log = ""
        if doCheckLog: lastEnd = matchPart(ls, logfile, lastEnd)
        if doCheckLog and lastEnd != len(logfile):
            raise NoMatch, lastEnd
        
    except NoMatch, m:
        print "Cannot match log file against log regexp."
        print "log file: "
        print "------------------------------------------------------"
        print logfile[m.pos:]
        print "------------------------------------------------------"
        print "log regexp: "
        print "------------------------------------------------------"
        print log
        print "------------------------------------------------------"
        test.fail_test()

    if doCheckStdout:
        exp_stdout = test.wrap_stdout(".*", rdstr)
        if not test.match_re_dotall(test.stdout(), exp_stdout):
            print "Unexpected stdout: "
            print "-----------------------------------------------------"
            print repr(test.stdout())
            print "-----------------------------------------------------"
            print repr(exp_stdout)
            print "-----------------------------------------------------"
            test.fail_test()
        
try:
    # 1.1 if checks are ok, the cache mechanism should work

    reset(RE)

    test.write([work_dir,  'SConstruct'], """
if int(ARGUMENTS.get('target_signatures_content', 0)):
    TargetSignatures('content')
env = Environment()
import os
env.AppendENVPath('PATH', os.environ['PATH'])
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

    test.run(chdir=work_dir)
    checkLogAndStdout(["Checking for main() in C library %s... " % lib,
                       "Checking for main() in C library None... ",
                       "Checking for main() in C library %s... " % lib,
                       "Checking for main() in C library None... ",
                       "Checking for C header file math.h... ",
                       "Checking for C++ header file vector... "],
                      ["yes"]*6,
                      [[((".c", NCR), (_obj, NCR), (_exe, NCR))]]*4 +
                        [[((".c", NCR), (_obj, NCR))]] +
                        [[((".cpp", NCR), (_obj, NCR))]],
                      test, "config.log", ".sconf_temp", "SConstruct")    
    

    test.run(chdir=work_dir)
    checkLogAndStdout(["Checking for main() in C library %s... " % lib,
                       "Checking for main() in C library None... ",
                       "Checking for main() in C library %s... " % lib,
                       "Checking for main() in C library None... ",
                       "Checking for C header file math.h... ",
                       "Checking for C++ header file vector... "],
                      ["yes"]*6,
                      [[((".c", CR), (_obj, CR), (_exe, CR))]]*4 +
                       [[((".c", CR), (_obj, CR))]] +
                       [[((".cpp", CR), (_obj, CR))]],
                      test, "config.log", ".sconf_temp", "SConstruct")

    # same should be true for TargetSignatures('content')

    test.run(chdir=work_dir, arguments='target_signatures_content=1 --config=force')
    checkLogAndStdout(["Checking for main() in C library %s... " % lib,
                       "Checking for main() in C library None... ",
                       "Checking for main() in C library %s... " % lib,
                       "Checking for main() in C library None... ",
                       "Checking for C header file math.h... ",
                       "Checking for C++ header file vector... "],
                      ["yes"]*6,
                      [[((".c", NCR), (_obj, NCR), (_exe, NCR))]]*4 +
                        [[((".c", NCR), (_obj, NCR))]] +
                        [[((".cpp", NCR), (_obj, NCR))]],
                      test, "config.log", ".sconf_temp", "SConstruct")    

    test.run(chdir=work_dir, arguments='target_signatures_content=1')
    checkLogAndStdout(["Checking for main() in C library %s... " % lib,
                       "Checking for main() in C library None... ",
                       "Checking for main() in C library %s... " % lib,
                       "Checking for main() in C library None... ",
                       "Checking for C header file math.h... ",
                       "Checking for C++ header file vector... "],
                      ["yes"]*6,
                      [[((".c", CR), (_obj, CR), (_exe, CR))]]*4 +
                       [[((".c", CR), (_obj, CR))]] +
                       [[((".cpp", CR), (_obj, CR))]],
                      test, "config.log", ".sconf_temp", "SConstruct")    

    # 1.2 if checks are not ok, the cache mechanism should work as well
    #     (via explicit cache)
    reset(EXACT)              # match exactly, "()" is a regexp thing

    test.write([work_dir,  'SConstruct'], """
if int(ARGUMENTS.get('target_signatures_content', 0)):
    TargetSignatures('content')
env = Environment()
import os
env.AppendENVPath('PATH', os.environ['PATH'])
conf = env.Configure()
r1 = conf.CheckCHeader( 'no_std_c_header.h' ) # leads to compile error
r2 = conf.CheckLib( 'no_c_library_SAFFDG' )   # leads to link error
env = conf.Finish()
if not (not r1 and not r2):
     print "FAIL: ", r1, r2
     Exit(1)
""")

    test.run(chdir=work_dir)
    checkLogAndStdout(["Checking for C header file no_std_c_header.h... ",
                       "Checking for main() in C library no_c_library_SAFFDG... "],
                      ["no"]*2,
                      [[((".c", NCR), (_obj, NCF))],
                       [((".c", NCR), (_obj, NCR), (_exe, NCF))]],
                      test, "config.log", ".sconf_temp", "SConstruct")

    test.run(chdir=work_dir)
    checkLogAndStdout(["Checking for C header file no_std_c_header.h... ",
                       "Checking for main() in C library no_c_library_SAFFDG... "],
                      ["no"]*2,
                      [[((".c", CR), (_obj, CF))],
                       [((".c", CR), (_obj, CR), (_exe, CF))]],
                      test, "config.log", ".sconf_temp", "SConstruct")

    # 1.3 same should be true for TargetSignatures('content')
    test.run(chdir=work_dir, arguments='--config=force target_signatures_content=1')
    checkLogAndStdout(["Checking for C header file no_std_c_header.h... ",
                       "Checking for main() in C library no_c_library_SAFFDG... "],
                      ["no"]*2,
                      [[((".c", NCR), (_obj, NCF))],
                       [((".c", NCR), (_obj, NCR), (_exe, NCF))]],
                      test, "config.log", ".sconf_temp", "SConstruct")

    test.run(chdir=work_dir, arguments='target_signatures_content=1')
    checkLogAndStdout(["Checking for C header file no_std_c_header.h... ",
                       "Checking for main() in C library no_c_library_SAFFDG... "],
                      ["no"]*2,
                      [[((".c", CR), (_obj, CF))],
                       [((".c", CR), (_obj, CR), (_exe, CF))]],
                      test, "config.log", ".sconf_temp", "SConstruct")

    

    # 2.1 test that normal builds work together with Sconf
    reset(RE_DOTALL)


    test.write([work_dir,  'SConstruct'], """
env = Environment()
import os
env.AppendENVPath('PATH', os.environ['PATH'])
conf = Configure(env)
r1 = conf.CheckCHeader( 'math.h' )
r2 = conf.CheckCHeader( 'no_std_c_header.h' ) # leads to compile error
env = conf.Finish()
Export( 'env' )
SConscript( 'SConscript' )
""")
    test.write([work_dir,  'SConscript'], """
Import( 'env' )
env.Program( 'TestProgram', 'TestProgram.c' )
""")
    test.write([work_dir,  'TestProgram.c'], """
#include <stdio.h>

int main() {
  printf( "Hello\\n" );
}
""")
    test.run(chdir=work_dir)
    checkLogAndStdout(["Checking for C header file math.h... ",
                       "Checking for C header file no_std_c_header.h... "],
                      ["yes", "no"],
                      [[((".c", NCR), (_obj, NCR))],
                       [((".c", NCR), (_obj, NCF))]],
                      test, "config.log", ".sconf_temp", "SConstruct")

    test.run(chdir=work_dir)
    checkLogAndStdout(["Checking for C header file math.h... ",
                       "Checking for C header file no_std_c_header.h... "],
                      ["yes", "no"],
                      [[((".c", CR), (_obj, CR))],
                       [((".c", CR), (_obj, CF))]],
                      test, "config.log", ".sconf_temp", "SConstruct")

    # 2.2 test that BuildDir builds work together with Sconf
    reset(RE_DOTALL)


    test.write([work_dir,  'SConstruct'], """
env = Environment(LOGFILE='build/config.log')
import os
env.AppendENVPath('PATH', os.environ['PATH'])
BuildDir( 'build', '.' )
conf = env.Configure(conf_dir='build/config.tests', log_file='$LOGFILE')
r1 = conf.CheckCHeader( 'math.h' )
r2 = conf.CheckCHeader( 'no_std_c_header.h' ) # leads to compile error
env = conf.Finish()
Export( 'env' )
# print open( 'build/config.log' ).readlines()
SConscript( 'build/SConscript' )
""")
    test.write([work_dir,  'SConscript'], """
Import( 'env' )
env.Program( 'TestProgram', 'TestProgram.c' )
""")
    test.write([work_dir,  'TestProgram.c'], """
#include <stdio.h>

int main() {
  printf( "Hello\\n" );
}
""")

    test.run(chdir=work_dir)
    checkLogAndStdout(["Checking for C header file math.h... ",
                       "Checking for C header file no_std_c_header.h... "],
                      ["yes", "no"],
                      [[((".c", NCR), (_obj, NCR))],
                       [((".c", NCR), (_obj, NCF))]],
                      test,
                      os.path.join("build", "config.log"),
                      os.path.join("build", "config.tests"),
                      "SConstruct")
    
    test.run(chdir=work_dir)
    checkLogAndStdout(["Checking for C header file math.h... ",
                       "Checking for C header file no_std_c_header.h... "],
                      ["yes", "no"],
                      [[((".c", CR), (_obj, CR))],
                       [((".c", CR), (_obj, CF))]],
                      test,
                      os.path.join("build", "config.log"),
                      os.path.join("build", "config.tests"),
                      "SConstruct")

    # 2.3 test that Configure calls in SConscript files work
    #     even if BuildDir is set
    reset(RE_DOTALL)

    test.subdir( [work_dir, 'sub'], [work_dir, 'sub', 'local'] )
    test.write([work_dir,  'SConstruct'], """
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
    test.write([work_dir,  'sub', 'local', 'local_header.h'],
               "/* Hello World */" )
    test.write([work_dir,  'SConscript'], """
SConscript( 'sub/SConscript' )
""")
    test.write([work_dir,  'sub', 'SConscript'], """
def CustomTest(context):
  context.Message('Executing Custom Test ... ')
  ret = context.TryCompile('#include "local_header.h"', '.c')
  context.Result(ret)
  return ret

env = Environment(FOO='fff')
env.Append( CPPPATH='local' )
import os
env.AppendENVPath('PATH', os.environ['PATH'])
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
    test.write([work_dir, 'sub', 'TestProgram.h'], """
/* Just a test header */
""")
    test.write([work_dir, 'sub', 'TestProgram.c'], """
#include "TestProgram.h"
#include <stdio.h>

int main() {
  printf( "Hello\\n" );
}
""")

    # first with SConscriptChdir(0)
    test.run(chdir=work_dir, arguments='chdir=no')
    checkLogAndStdout( ["Checking for C header file math.h... ",
                        "Checking for C header file no_std_c_header.h... ",
                        "Executing Custom Test ... "],
                        ["yes", "no", "yes"],
                        [[((".c", NCR), (_obj, NCR))],
                         [((".c", NCR), (_obj, NCF))],
                         [((".c", NCR), (_obj, NCR))]],
                        test, "config.log",
                        ".sconf_temp",
                        os.path.join("build", "sub", "SConscript"))

    test.run(chdir=work_dir, arguments='chdir=no')
    checkLogAndStdout( ["Checking for C header file math.h... ",
                        "Checking for C header file no_std_c_header.h... ",
                        "Executing Custom Test ... "],
                        ["yes", "no", "yes"],
                        [[((".c", CR), (_obj, CR))],
                         [((".c", CR), (_obj, CF))],
                         [((".c", CR), (_obj, CR))]],
                        test, "config.log",
                        ".sconf_temp",
                        os.path.join("build", "sub", "SConscript"))

    shutil.rmtree(test.workpath(work_dir, ".sconf_temp"))
    os.unlink(test.workpath(work_dir, ".sconsign.dblite"))

    # now with SConscriptChdir(1)
    test.run(chdir=work_dir, arguments='chdir=yes')
    checkLogAndStdout( ["Checking for C header file math.h... ",
                        "Checking for C header file no_std_c_header.h... ",
                        "Executing Custom Test ... "],
                        ["yes", "no", "yes"],
                        [[((".c", NCR), (_obj, NCR))],
                         [((".c", NCR), (_obj, NCF))],
                         [((".c", NCR), (_obj, NCR))]],
                        test, "config.log",
                        ".sconf_temp",
                        os.path.join("build", "sub", "SConscript"))

    test.run(chdir=work_dir, arguments='chdir=yes')
    checkLogAndStdout( ["Checking for C header file math.h... ",
                        "Checking for C header file no_std_c_header.h... ",
                        "Executing Custom Test ... "],
                        ["yes", "no", "yes"],
                        [[((".c", CR), (_obj, CR))],
                         [((".c", CR), (_obj, CF))],
                         [((".c", CR), (_obj, CR))]],
                        test, "config.log",
                        ".sconf_temp",
                        os.path.join("build", "sub", "SConscript"))

    # 3.1 test custom tests
    reset(RE_DOTALL)

    compileOK = '#include <stdio.h>\\nint main() {printf("Hello");return 0;}'
    compileFAIL = "syntax error"
    linkOK = compileOK
    linkFAIL = "void myFunc(); int main() { myFunc(); }"
    runOK = compileOK
    runFAIL = "int main() { return 1; }"
    test.write([work_dir, 'pyAct.py'], 'import sys\nprint sys.argv[1]\nsys.exit(int(sys.argv[1]))\n')
    test.write([work_dir, 'SConstruct'], """
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
    test.Result( int(resOK and not resFAIL) )
    return resOK and not resFAIL

env = Environment()
import os
env.AppendENVPath('PATH', os.environ['PATH'])
conf = Configure( env, custom_tests={'CheckCustom' : CheckCustom} )
conf.CheckCustom()
env = conf.Finish()
""" % (compileOK, compileFAIL, linkOK, linkFAIL, runOK, runFAIL,
       python, python ) )
    test.run(chdir=work_dir)
    checkLogAndStdout(["Executing MyTest ... "],
                      ["yes"],
                      [[(('.c', NCR), (_obj, NCR)),
                        (('.c', NCR), (_obj, NCF)),
                        (('.c', NCR), (_obj, NCR), (_exe, NCR)),
                        (('.c', NCR), (_obj, NCR), (_exe, NCF)),
                        (('.c', NCR), (_obj, NCR), (_exe, NCR), (_exe + '.out', NCR)),
                        (('.c', NCR), (_obj, NCR), (_exe, NCR), (_exe + '.out', NCF)),
                        (('', NCR),),
                        (('', NCF),)]],
                       test, "config.log", ".sconf_temp", "SConstruct")

    test.run(chdir=work_dir)
    checkLogAndStdout(["Executing MyTest ... "],
                      ["yes"],
                      [[(('.c', CR), (_obj, CR)),
                        (('.c', CR), (_obj, CF)),
                        (('.c', CR), (_obj, CR), (_exe, CR)),
                        (('.c', CR), (_obj, CR), (_exe, CF)),
                        (('.c', CR), (_obj, CR), (_exe, CR), (_exe + '.out', CR)),
                        (('.c', CR), (_obj, CR), (_exe, CR), (_exe + '.out', CF)),
                        (('', CR),),
                        (('', CF),)]],
                       test, "config.log", ".sconf_temp", "SConstruct")

    # 4.1 test that calling normal builders from an actual configuring
    # environment works
    reset(RE_DOTALL)

    test.write([work_dir, 'cmd.py'], r"""
import sys
sys.stderr.write( 'Hello World on stderr\n' )
sys.stdout.write( 'Hello World on stdout\n' )
open(sys.argv[1], 'w').write( 'Hello World\n' )
""")

    test.write([work_dir, 'SConstruct'], """
env = Environment()
def CustomTest(*args):
    return 0
conf = env.Configure(custom_tests = {'MyTest' : CustomTest})
if not conf.MyTest():
    env.Command("hello", [], "%s cmd.py $TARGET")
env = conf.Finish()
""" % python)
    test.run(chdir=work_dir, stderr="Hello World on stderr\n")

    # 4.2 test that calling Configure from a builder results in a
    # readable Error
    reset(EXACT)

    test.write([work_dir, 'SConstruct'], """
def ConfigureAction(target, source, env):
    env.Configure()
    return 0
env = Environment(BUILDERS = {'MyAction' :
                              Builder(action=Action(ConfigureAction))})
env.MyAction('target', [])
""")
    test.run(chdir=work_dir, status=2,
             stderr="scons: *** Calling Configure from Builders is not supported.\n")

    # 4.3 test the calling Configure from multiple subsidiary,
    # nested SConscript files does *not* result in an error.

    test.subdir([work_dir, 'dir1'],
                [work_dir, 'dir2'],
                [work_dir, 'dir2', 'sub1'],
                [work_dir, 'dir2', 'sub1', 'sub2'])
    test.write([work_dir, 'SConstruct'], """
env = Environment()
SConscript(dirs=['dir1', 'dir2'], exports="env")
""")
    test.write([work_dir, 'dir1', 'SConscript'], """
Import("env")
conf = env.Configure()
conf.Finish()
""")
    test.write([work_dir, 'dir2', 'SConscript'], """
Import("env")
conf = env.Configure()
conf.Finish()
SConscript(dirs=['sub1'], exports="env")
""")
    test.write([work_dir, 'dir2', 'sub1', 'SConscript'], """
Import("env")
conf = env.Configure()
conf.Finish()
SConscript(dirs=['sub2'], exports="env")
""")
    test.write([work_dir, 'dir2', 'sub1', 'sub2', 'SConscript'], """
Import("env")
conf = env.Configure()
conf.Finish()
""")
    test.run(chdir=work_dir)

    # 5.1 test the ConfigureDryRunError
    
    reset(EXACT) # exact match
    test.write([work_dir,  'SConstruct'], """
env = Environment()
import os
env.AppendENVPath('PATH', os.environ['PATH'])
conf = Configure(env)
r1 = conf.CheckLib('%s') # will pass
r2 = conf.CheckLib('hopefullynolib') # will fail
env = conf.Finish()
if not (r1 and not r2):
     Exit(1)
""" % (lib))

    test.run(chdir=work_dir, arguments='-n', status=2, stderr="""
scons: *** Cannot create configure directory ".sconf_temp" within a dry-run.
File "SConstruct", line 5, in ?
""")
    test.must_not_exist([work_dir, 'config.log'])
    test.subdir([work_dir, '.sconf_temp'])
    
    test.run(chdir=work_dir, arguments='-n', status=2, stderr="""
scons: *** Cannot update configure test "%s" within a dry-run.
File "SConstruct", line 6, in ?
""" % os.path.join(".sconf_temp", "conftest_0.c"))

    test.run(chdir=work_dir)
    checkLogAndStdout( ["Checking for main() in C library %s... " % lib,
                        "Checking for main() in C library hopefullynolib... "],
                        ["yes", "no"],
                        [[((".c", NCR), (_obj, NCR))],
                         [((".c", NCR), (_obj, NCF))]],
                        test, "config.log", ".sconf_temp", "SConstruct")
    oldLog = test.read(test.workpath(work_dir, 'config.log'))

    test.run(chdir=work_dir, arguments='-n')
    checkLogAndStdout( ["Checking for main() in C library %s... " % lib,
                        "Checking for main() in C library hopefullynolib... "],
                        ["yes", "no"],
                        [[((".c", CR), (_obj, CR))],
                         [((".c", CR), (_obj, CF))]],
                        test, "config.log", ".sconf_temp", "SConstruct",
                        doCheckLog=0)
    newLog = test.read(test.workpath(work_dir, 'config.log'))
    if newLog != oldLog:
        print "Unexpected update of log file within a dry run"
        test.fail_test()

    # 5.2 test the --config=<auto|force|cache> option
    reset(EXACT) # exact match

    test.write([work_dir,  'SConstruct'], """
env = Environment(CPPPATH='#/include')
import os
env.AppendENVPath('PATH', os.environ['PATH'])
conf = Configure(env)
r1 = conf.CheckCHeader('non_system_header1.h')
r2 = conf.CheckCHeader('non_system_header2.h')
env = conf.Finish()
""")
    test.subdir([work_dir, 'include'])
    test.write([work_dir, 'include', 'non_system_header1.h'], """
/* A header */
""")

    test.run(chdir=work_dir, arguments='--config=cache', status=2, stderr="""
scons: *** "%s" is not yet built and cache is forced.
File "SConstruct", line 6, in ?
""" % os.path.join(".sconf_temp", "conftest_0.c"))

    test.run(chdir=work_dir, arguments='--config=auto')
    checkLogAndStdout( ["Checking for C header file non_system_header1.h... ",
                        "Checking for C header file non_system_header2.h... "],
                        ["yes", "no"],
                        [[((".c", NCR), (_obj, NCR))],
                         [((".c", NCR), (_obj, NCF))]],
                        test, "config.log", ".sconf_temp", "SConstruct")
    test.run(chdir=work_dir, arguments='--config=auto')
    checkLogAndStdout( ["Checking for C header file non_system_header1.h... ",
                        "Checking for C header file non_system_header2.h... "],
                        ["yes", "no"],
                        [[((".c", CR), (_obj, CR))],
                         [((".c", CR), (_obj, CF))]],
                        test, "config.log", ".sconf_temp", "SConstruct")
    
    test.run(chdir=work_dir, arguments='--config=force')
    checkLogAndStdout( ["Checking for C header file non_system_header1.h... ",
                        "Checking for C header file non_system_header2.h... "],
                        ["yes", "no"],
                        [[((".c", NCR), (_obj, NCR))],
                         [((".c", NCR), (_obj, NCF))]],
                        test, "config.log", ".sconf_temp", "SConstruct")

    test.run(chdir=work_dir, arguments='--config=cache')
    checkLogAndStdout( ["Checking for C header file non_system_header1.h... ",
                        "Checking for C header file non_system_header2.h... "],
                        ["yes", "no"],
                        [[((".c", CR), (_obj, CR))],
                         [((".c", CR), (_obj, CF))]],
                        test, "config.log", ".sconf_temp", "SConstruct")

    test.write([work_dir, 'include', 'non_system_header2.h'], """
/* Another header */
""")
    test.unlink([work_dir, 'include', 'non_system_header1.h'])
    test.run(chdir=work_dir, arguments='--config=cache')
    checkLogAndStdout( ["Checking for C header file non_system_header1.h... ",
                        "Checking for C header file non_system_header2.h... "],
                        ["yes", "no"],
                        [[((".c", CR), (_obj, CR))],
                         [((".c", CR), (_obj, CF))]],
                        test, "config.log", ".sconf_temp", "SConstruct")
    
    test.run(chdir=work_dir, arguments='--config=auto')
    checkLogAndStdout( ["Checking for C header file non_system_header1.h... ",
                        "Checking for C header file non_system_header2.h... "],
                        ["no", "yes"],
                        [[((".c", CR), (_obj, NCF))],
                         [((".c", CR), (_obj, NCR))]],
                        test, "config.log", ".sconf_temp", "SConstruct")

    # 5.3 test -Q option
    reset(EXACT)
    test.write([work_dir,  'SConstruct'], """
env = Environment()
import os
env.AppendENVPath('PATH', os.environ['PATH'])
conf = Configure(env)
r1 = conf.CheckCHeader('stdio.h')
env = conf.Finish()
""")
    test.run(chdir=work_dir, arguments='-Q',
             stdout="scons: `.' is up to date.\n", stderr="")


    # 6. check config.h support
    reset(EXACT)
    test.write([work_dir, 'SConstruct'], """
env = Environment()
import os
env.AppendENVPath('PATH', os.environ['PATH'])
conf = Configure(env, config_h = 'config.h')
r1 = conf.CheckFunc('printf')
r2 = conf.CheckFunc('noFunctionCall')
r3 = conf.CheckType('int')
r4 = conf.CheckType('noType')
r5 = conf.CheckCHeader('stdio.h', '<>')
r6 = conf.CheckCHeader('hopefullynoc-header.h')
r7 = conf.CheckCXXHeader('vector', '<>')
r8 = conf.CheckCXXHeader('hopefullynocxx-header.h')
env = conf.Finish()
conf = Configure(env, config_h = 'config.h')
r9 = conf.CheckLib('%s', 'sin')
r10 = conf.CheckLib('hopefullynolib', 'sin')
r11 = conf.CheckLibWithHeader('%s', 'math.h', 'c')
r12 = conf.CheckLibWithHeader('%s', 'hopefullynoheader2.h', 'c')
r13 = conf.CheckLibWithHeader('hopefullynolib2', 'math.h', 'c')
env = conf.Finish()
""" % (lib, lib, lib))

    expected_read_str = """\
Checking for C function printf()... yes
Checking for C function noFunctionCall()... no
Checking for C type int... yes
Checking for C type noType... no
Checking for C header file stdio.h... yes
Checking for C header file hopefullynoc-header.h... no
Checking for C++ header file vector... yes
Checking for C++ header file hopefullynocxx-header.h... no
Checking for sin() in C library %(lib)s... yes
Checking for sin() in C library hopefullynolib... no
Checking for main() in C library %(lib)s... yes
Checking for main() in C library %(lib)s... no
Checking for main() in C library hopefullynolib2... no
""" % {'lib' : lib}

    expected_build_str = """\
scons: Configure: creating config.h
"""
    
    expected_stdout = test.wrap_stdout(build_str=expected_build_str,
                                       read_str=expected_read_str)

    expected_config_h = string.replace("""#ifndef CONFIG_H_SEEN
#define CONFIG_H_SEEN

#define HAVE_PRINTF
/* #undef HAVE_NOFUNCTIONCALL */
#define HAVE_INT
/* #undef HAVE_NOTYPE */
#define HAVE_STDIO_H
/* #undef HAVE_HOPEFULLYNOC_HEADER_H */
#define HAVE_VECTOR
/* #undef HAVE_HOPEFULLYNOCXX_HEADER_H */
#define HAVE_%(LIB)s
/* #undef HAVE_LIBHOPEFULLYNOLIB */
#define HAVE_%(LIB)s
/* #undef HAVE_%(LIB)s */
/* #undef HAVE_LIBHOPEFULLYNOLIB2 */

#endif /* CONFIG_H_SEEN */
""" % {'LIB' : "LIB" + string.upper(lib) }, "\n", os.linesep)

    test.run(chdir=work_dir, stdout=expected_stdout)
    config_h = test.read(test.workpath(work_dir, 'config.h'))
    if expected_config_h != config_h:
        print "Unexpected config.h"
        print "Expected: "
        print "---------------------------------------------------------"
        print repr(expected_config_h)
        print "---------------------------------------------------------"
        print "Found: "
        print "---------------------------------------------------------"
        print repr(config_h)
        print "---------------------------------------------------------"
        print "Stdio: "
        print "---------------------------------------------------------"
        print test.stdout()
        print "---------------------------------------------------------"
        test.fail_test()

    expected_read_str = re.sub(r'\b((yes)|(no))\b',
                               r'(cached) \1',
                               expected_read_str)
    expected_build_str = "scons: `.' is up to date.\n"
    expected_stdout = test.wrap_stdout(build_str=expected_build_str,
                                       read_str=expected_read_str)
    #expected_stdout = string.replace(expected_stdout, "\n", os.linesep)
    test.run(chdir=work_dir, stdout=expected_stdout)    
    config_h = test.read(test.workpath(work_dir, 'config.h'))    
    if expected_config_h != config_h:
        print "Unexpected config.h"
        print "Expected: "
        print "---------------------------------------------------------"
        print repr(expected_config_h)
        print "---------------------------------------------------------"
        print "Found: "
        print "---------------------------------------------------------"
        print repr(config_h)
        print "---------------------------------------------------------"
        print "Stdio: "
        print "---------------------------------------------------------"
        print test.stdout()
        print "---------------------------------------------------------"
        test.fail_test()

finally:
    pass
    #os.system( 'find . -type f -exec ls -l {} \;' )
    #print "-------------config.log------------------"
    #print test.read( test.workpath(work_dir, 'config.log'))
    #print "-------------build/config.log------------"
    #print test.read( test.workpath('build/config.log' ))


test.pass_test()
