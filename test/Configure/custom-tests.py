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

"""
Verify execution of custom test cases.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

_exe = TestSCons._exe
_obj = TestSCons._obj
_python_ = TestSCons._python_

test = TestSCons.TestSCons()

NCR = test.NCR  # non-cached rebuild
CR  = test.CR   # cached rebuild (up to date)
NCF = test.NCF  # non-cached build failure
CF  = test.CF   # cached build failure

compileOK = '#include <stdio.h>\\nint main(void) {printf("Hello");return 0;}'
compileFAIL = "syntax error"
linkOK = compileOK
linkFAIL = "void myFunc(); int main(void) { myFunc(); }"
runOK = compileOK
runFAIL = "int main(void) { return 1; }"

test.write('pyAct.py', """\
import sys
print(sys.argv[1])
sys.exit(int(sys.argv[1]))
""")

test.write('SConstruct', """\
def CheckCustom(test):
    test.Message( 'Executing MyTest ... ' )
    retCompileOK                = test.TryCompile( '%(compileOK)s', '.c' )
    retCompileFAIL              = test.TryCompile( '%(compileFAIL)s', '.c' )
    retLinkOK                   = test.TryLink( '%(linkOK)s', '.c' )
    retLinkFAIL                 = test.TryLink( '%(linkFAIL)s', '.c' )
    (retRunOK, outputRunOK)     = test.TryRun( '%(runOK)s', '.c' )
    (retRunFAIL, outputRunFAIL) = test.TryRun( '%(runFAIL)s', '.c' )
    (retActOK, outputActOK) = test.TryAction( r'%(_python_)s pyAct.py 0 > $TARGET' )
    (retActFAIL, outputActFAIL) = test.TryAction( r'%(_python_)s pyAct.py 1 > $TARGET' )
    resOK = retCompileOK and retLinkOK and retRunOK and outputRunOK=="Hello"
    resOK = resOK and retActOK and int(outputActOK)==0
    resFAIL = retCompileFAIL or retLinkFAIL or retRunFAIL or outputRunFAIL!=""
    resFAIL = resFAIL or retActFAIL or outputActFAIL!=""
    test.Result( resOK and not resFAIL )
    return resOK and not resFAIL

env = Environment()
import os
env.AppendENVPath('PATH', os.environ['PATH'])
conf = Configure( env, custom_tests={'CheckCustom'    : CheckCustom} )
conf.CheckCustom()
env = conf.Finish()
""" % locals())

test.run()

test.checkLogAndStdout(["Executing MyTest ... "],
                       ["yes"],
                      [[(('.c', NCR), (_obj, NCR)),
                        (('.c', NCR), (_obj, NCF)),
                        (('.c', NCR), (_obj, NCR), (_exe, NCR)),
                        (('.c', NCR), (_obj, NCR), (_exe, NCF)),
                        (('.c', NCR), (_obj, NCR), (_exe, NCR), (_exe + '.out', NCR)),
                        (('.c', NCR), (_obj, NCR), (_exe, NCR), (_exe + '.out', NCF)),
                        (('', NCR),),
                        (('', NCF),)]],
                       "config.log", ".sconf_temp", "SConstruct")

test.run()

# Try again to check caching
test.checkLogAndStdout(["Executing MyTest ... "],
                      ["yes"],
                      [[(('.c', CR), (_obj, CR)),
                        (('.c', CR), (_obj, CF)),
                        (('.c', CR), (_obj, CR), (_exe, CR)),
                        (('.c', CR), (_obj, CR), (_exe, CF)),
                        (('.c', CR), (_obj, CR), (_exe, CR), (_exe + '.out', CR)),
                        (('.c', CR), (_obj, CR), (_exe, CR), (_exe + '.out', CF)),
                        (('', CR),),
                        (('', CF),)]],
                       "config.log", ".sconf_temp", "SConstruct")

# Test other customs:
test.write('SConstruct', """\
def CheckList(test):
    test.Message( 'Display of list ...' )
    res = [1, 2, 3, 4]
    test.Result( res )
    return res

def CheckEmptyList(test):
    test.Message( 'Display of empty list ...' )
    res = list()
    test.Result( res )
    return res

def CheckRandomStr(test):
    test.Message( 'Display of random string ...' )
    res = "a random string"
    test.Result( res )
    return res

def CheckEmptyStr(test):
    test.Message( 'Display of empty string ...' )
    res = ""
    test.Result( res )
    return res

def CheckDict(test):
    test.Message( 'Display of dictionary ...' )
    res = {"key1" : 1, "key2" : "text"}
    test.Result( res )
    return res

def CheckEmptyDict(test):
    test.Message( 'Display of empty dictionary ...' )
    res = dict
    test.Result( res )
    return res

env = Environment()
import os
env.AppendENVPath('PATH', os.environ['PATH'])
conf = Configure( env, custom_tests={'CheckList'      : CheckList,
                                     'CheckEmptyList' : CheckEmptyList,
                                     'CheckRandomStr' : CheckRandomStr,
                                     'CheckEmptyStr'  : CheckEmptyStr,
                                     'CheckDict'      : CheckDict,
                                     'CheckEmptyDict' : CheckEmptyDict} )
conf.CheckList()
conf.CheckEmptyList()
conf.CheckRandomStr()
conf.CheckEmptyStr()
conf.CheckDict()
conf.CheckEmptyDict()
env = conf.Finish()
""" % locals())

test.run()

test.must_match('config.log',
r""".*
.*
scons: Configure: Display of list ...
scons: Configure: \(cached\) yes

scons: Configure: Display of empty list ...
scons: Configure: \(cached\) no

scons: Configure: Display of random string ...
scons: Configure: \(cached\) a random string

scons: Configure: Display of empty string ...
scons: Configure: \(cached\) *

scons: Configure: Display of dictionary ...
scons: Configure: \(cached\) yes

scons: Configure: Display of empty dictionary ...
scons: Configure: \(cached\) yes


""",
match=TestSCons.match_re)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
