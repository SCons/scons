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
Verify operation of the -q (--question) option in conjunction
with Configure tests.

(This was originally mostly copied and pasted from test/option-n.py.)
"""

import os.path
import re

import TestCmd
import TestSCons

test = TestSCons.TestSCons(match = TestCmd.match_re_dotall)

test.write('aaa.in', 'Hello world\n')

test.write('SConstruct', """\
def userAction(target,source,env):
    import shutil
    shutil.copyfile( str(source[0]), str(target[0]))

def strAction(target,source,env):
    return "cp " + str(source[0]) + " " + str(target[0])

def CustomTest(context):
    context.Message("Executing Custom Test ... " )
    (ok, msg) = context.TryAction(Action(userAction,strAction),
                                  "Hello World", ".in")
    context.Result(ok)
    return ok

env = Environment(BUILDERS={'B' : Builder(action=Action(userAction,strAction))})

conf = Configure( env,
                  custom_tests={'CustomTest':CustomTest},
                  conf_dir="config.test",
                  log_file="config.log")
if not conf.CustomTest():
    Exit(1)
else:
    env = conf.Finish()

env.B(target='aaa.out', source='aaa.in')
""")

# test that conf_dir isn't created and an error is raised
stderr=r"""
scons: \*\*\* Cannot create configure directory "config\.test" within a dry-run\.
File \S+, line \S+, in \S+
"""
test.run(arguments="-q aaa.out",stderr=stderr,status=2)

test.must_not_exist(test.workpath("config.test"))
test.must_not_exist(test.workpath("config.log"))

# test that targets are not built, if conf_dir exists.
# verify that .cache and config.log are not created.
# an error should be raised
stderr=r"""
scons: \*\*\* Cannot update configure test "%s" within a dry-run\.
File \S+, line \S+, in \S+
""" % re.escape(os.path.join("config.test", "conftest_b10a8db164e0754105b7a99be72e3fe5_0.in"))

test.subdir('config.test')

test.run(arguments="-q aaa.out",stderr=stderr,status=2)

test.must_not_exist(test.workpath("config.test", ".cache"))
test.must_not_exist(test.workpath("config.test", "conftest_0"))
test.must_not_exist(test.workpath("config.test", "conftest_b10a8db164e0754105b7a99be72e3fe5_0.in"))
test.must_not_exist(test.workpath("config.log"))

# test that no error is raised, if all targets are up-to-date. In this
# case .cache and config.log shouldn't be created
stdout=test.wrap_stdout(build_str='cp aaa.in aaa.out\n',
                        read_str="""Executing Custom Test ... yes
""")

test.run(stdout=stdout,arguments="aaa.out",status=0)

log1_mtime = os.path.getmtime(test.workpath("config.log"))

test.run(arguments="-q aaa.out",status=0)
log2_mtime = os.path.getmtime(test.workpath("config.log"))
test.fail_test( log1_mtime != log2_mtime )

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
