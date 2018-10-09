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

"""
Verify that Configure calls in SConscript files work when used
with VariantDir.
"""

import os.path

import TestSCons

_obj = TestSCons._obj

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

test.subdir( 'sub', ['sub', 'local'] )

NCR = test.NCR  # non-cached rebuild
CR  = test.CR   # cached rebuild (up to date)
NCF = test.NCF  # non-cached build failure
CF  = test.CF   # cached build failure

test.write('SConstruct', """\
opts = Variables()
opts.Add('chdir')
env = Environment(options=opts)
if env['chdir'] == 'yes':
  SConscriptChdir(1)
else:
  SConscriptChdir(0)
VariantDir( 'build', '.' )
SConscript( 'build/SConscript' )
""")

test.write(['sub', 'local', 'local_header.h'], "/* Hello World */" )

test.write('SConscript', """\
SConscript( 'sub/SConscript' )
""")

test.write(['sub', 'SConscript'], """\
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

test.write(['sub', 'TestProgram.h'], """\
/* Just a test header */
""")

test.write(['sub', 'TestProgram.c'], """\
#include "TestProgram.h"
#include <stdio.h>

int main(void) {
  printf( "Hello\\n" );
}
""")

# first with SConscriptChdir(0)
test.run(arguments='chdir=no')
test.checkLogAndStdout( ["Checking for C header file math.h... ",
                        "Checking for C header file no_std_c_header.h... ",
                        "Executing Custom Test ... "],
                        ["yes", "no", "yes"],
                        [[((".c", NCR), (_obj, NCR))],
                         [((".c", NCR), (_obj, NCF))],
                         [((".c", NCR), (_obj, NCR))]],
                        "config.log",
                        ".sconf_temp",
                        os.path.join("build", "sub", "SConscript"))

test.run(arguments='chdir=no')
test.checkLogAndStdout( ["Checking for C header file math.h... ",
                        "Checking for C header file no_std_c_header.h... ",
                        "Executing Custom Test ... "],
                        ["yes", "no", "yes"],
                        [[((".c", CR), (_obj, CR))],
                         [((".c", CR), (_obj, CF))],
                         [((".c", CR), (_obj, CR))]],
                        "config.log",
                        ".sconf_temp",
                        os.path.join("build", "sub", "SConscript"))

import shutil
shutil.rmtree(test.workpath(".sconf_temp"))
test.unlink(".sconsign.dblite")

# now with SConscriptChdir(1)
test.run(arguments='chdir=yes')
test.checkLogAndStdout( ["Checking for C header file math.h... ",
                        "Checking for C header file no_std_c_header.h... ",
                        "Executing Custom Test ... "],
                        ["yes", "no", "yes"],
                        [[((".c", NCR), (_obj, NCR))],
                         [((".c", NCR), (_obj, NCF))],
                         [((".c", NCR), (_obj, NCR))]],
                        "config.log",
                        ".sconf_temp",
                        os.path.join("build", "sub", "SConscript"))

test.run(arguments='chdir=yes')
test.checkLogAndStdout( ["Checking for C header file math.h... ",
                        "Checking for C header file no_std_c_header.h... ",
                        "Executing Custom Test ... "],
                        ["yes", "no", "yes"],
                        [[((".c", CR), (_obj, CR))],
                         [((".c", CR), (_obj, CF))],
                         [((".c", CR), (_obj, CR))]],
                        "config.log",
                        ".sconf_temp",
                        os.path.join("build", "sub", "SConscript"))


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
