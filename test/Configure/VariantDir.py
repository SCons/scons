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
Verify that Configure contexts work with basic use of VariantDir.
"""

import os

import TestSCons

_obj = TestSCons._obj

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

NCR = test.NCR  # non-cached rebuild
CR  = test.CR   # cached rebuild (up to date)
NCF = test.NCF  # non-cached build failure
CF  = test.CF   # cached build failure

test.write('SConstruct', """\
env = Environment(LOGFILE='build/config.log')
import os
env.AppendENVPath('PATH', os.environ['PATH'])
VariantDir('build', '.')
conf = env.Configure(conf_dir='build/config.tests', log_file='$LOGFILE')
r1 = conf.CheckCHeader('math.h')
r2 = conf.CheckCHeader('no_std_c_header.h') # leads to compile error
env = conf.Finish()
Export('env')
# with open('build/config.log') as f:
#     print f.readlines()
SConscript('build/SConscript')
""")

test.write('SConscript', """\
Import('env')
env.Program('TestProgram', 'TestProgram.c')
""")

test.write('TestProgram.c', """\
#include <stdio.h>

int main(void) {
  printf("Hello\\n");
}
""")

test.run()
test.checkLogAndStdout(["Checking for C header file math.h... ",
                       "Checking for C header file no_std_c_header.h... "],
                      ["yes", "no"],
                      [[((".c", NCR), (_obj, NCR))],
                       [((".c", NCR), (_obj, NCF))]],
                      os.path.join("build", "config.log"),
                      os.path.join("build", "config.tests"),
                      "SConstruct")
    
test.run()
test.checkLogAndStdout(["Checking for C header file math.h... ",
                       "Checking for C header file no_std_c_header.h... "],
                      ["yes", "no"],
                      [[((".c", CR), (_obj, CR))],
                       [((".c", CR), (_obj, CF))]],
                      os.path.join("build", "config.log"),
                      os.path.join("build", "config.tests"),
                      "SConstruct")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
