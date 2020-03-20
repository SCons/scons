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
Verify the ConfigureDryRunError.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os

import TestSCons

_obj = TestSCons._obj

test = TestSCons.TestSCons()

lib = test.Configure_lib

NCR = test.NCR  # non-cached rebuild
CR  = test.CR   # cached rebuild (up to date)
NCF = test.NCF  # non-cached build failure
CF  = test.CF   # cached build failure

SConstruct_path = test.workpath('SConstruct')

test.write(SConstruct_path, """
env = Environment()
import os
env.AppendENVPath('PATH', os.environ['PATH'])
conf = Configure(env)
r1 = conf.CheckLib('%s') # will pass
r2 = conf.CheckLib('hopefullynolib') # will fail
env = conf.Finish()
if not (r1 and not r2):
 Exit(1)
""" % lib)

expect = """
scons: *** Cannot create configure directory ".sconf_temp" within a dry-run.
""" + test.python_file_line(SConstruct_path, 5)

test.run(arguments='-n', status=2, stderr=expect)

test.must_not_exist('config.log')
test.subdir('.sconf_temp')

conftest_0_c = os.path.join(".sconf_temp", "conftest_df286a1d2f67e69d030b4eff75ca7e12_0.c")
SConstruct_file_line = test.python_file_line(SConstruct_path, 6)[:-1]

expect = """
scons: *** Cannot update configure test "%(conftest_0_c)s" within a dry-run.
%(SConstruct_file_line)s
""" % locals()

test.run(arguments='-n', status=2, stderr=expect)

test.run()
test.checkLogAndStdout(["Checking for C library %s... " % lib,
                        "Checking for C library hopefullynolib... "],
                       ["yes", "no"],
                       [[((".c", NCR), (_obj, NCR))],
                        [((".c", NCR), (_obj, NCF))]],
                       "config.log", ".sconf_temp", "SConstruct")

oldLog = test.read(test.workpath('config.log'), mode='r')

test.run(arguments='-n')
test.checkLogAndStdout(["Checking for C library %s... " % lib,
                        "Checking for C library hopefullynolib... "],
                       ["yes", "no"],
                       [[((".c", CR), (_obj, CR))],
                        [((".c", CR), (_obj, CF))]],
                       "config.log", ".sconf_temp", "SConstruct",
                       doCheckLog=False)

newLog = test.read(test.workpath('config.log'), mode='r')
if newLog != oldLog:
    print("Unexpected update of log file within a dry run")
    test.fail_test()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
