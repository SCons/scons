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
Verify use of the --config=<auto|force|cache> option.
"""

import os.path

from TestSCons import TestSCons, ConfigCheckInfo, _obj
from TestCmd import IS_WINDOWS

test = TestSCons()

test.subdir('include')

NCR = test.NCR  # non-cached rebuild
CR = test.CR  # cached rebuild (up to date)
NCF = test.NCF  # non-cached build failure
CF = test.CF  # cached build failure

SConstruct_path = test.workpath('SConstruct')

test.write(SConstruct_path, """
env = Environment(CPPPATH='#/include')
import os
env.AppendENVPath('PATH', os.environ['PATH'])
conf = Configure(env)
conf.CheckCHeader('non_system_header0.h')
conf.CheckCHeader('non_system_header1.h')
env = conf.Finish()
""")

test.write(['include', 'non_system_header0.h'], """
/* A header */
""")

conftest_0_c_hash = 'cda36b76729ffb03bf36a48d13b2d98d'
conftest_1_c_hash = 'acc476a565a3f6d5d67ddc21f187d062'

if IS_WINDOWS:
  conftest_0_obj_suffix = '_213c72f9eb682c6f27f2eb78ed8bd57a'+_obj
  conftest_1_obj_suffix = '_7c505229a64dccfea6e7cfdffe76bd2a'+_obj
else:
  conftest_0_obj_suffix = '_9b191e4c46e9d6ba17c8cd4d730900cf'+_obj
  conftest_1_obj_suffix = '_b9da1a844a8707269188b28a62c0d83e'+_obj

conftest_0_base = os.path.join(".sconf_temp", "conftest_%s_0%%s"%conftest_0_c_hash)
conftest_0_c = conftest_0_base%'.c'
conftest_1_base = os.path.join(".sconf_temp", "conftest_%s_0%%s"%conftest_1_c_hash)

SConstruct_file_line = test.python_file_line(SConstruct_path, 6)[:-1]

expect = """
scons: *** "%(conftest_0_c)s" is not yet built and cache is forced.
%(SConstruct_file_line)s
""" % locals()

test.run(arguments='--config=cache', status=2, stderr=expect)

test.run(arguments='--config=auto')
test.checkConfigureLogAndStdout(checks=[
    ConfigCheckInfo("Checking for C header file non_system_header0.h... ",
                    'yes', 
                    [((".c", NCR), 
                    (_obj, NCR))],
                    conftest_0_base
                    ),
    ConfigCheckInfo("Checking for C header file non_system_header1.h... ",
                    'no', 
                    [((".c", NCR), 
                    (_obj, NCF))],
                    conftest_1_base)]
)

test.run(arguments='--config=auto')
test.checkConfigureLogAndStdout(checks=[
    ConfigCheckInfo("Checking for C header file non_system_header0.h... ",
                    'yes',
                    [((".c", CR),
                      (conftest_0_obj_suffix, CR))],
                    conftest_0_base,
                    ),
    ConfigCheckInfo("Checking for C header file non_system_header1.h... ",
                    'no',
                    [((".c", CR),
                      (conftest_1_obj_suffix, CF))],
                    conftest_1_base)]
)


test.run(arguments='--config=force')
test.checkConfigureLogAndStdout(checks=[
    ConfigCheckInfo("Checking for C header file non_system_header0.h... ",
                    'yes',
                    [((".c", NCR),
                      (conftest_0_obj_suffix, NCR))],
                    conftest_0_base,
                    ),
    ConfigCheckInfo("Checking for C header file non_system_header1.h... ",
                    'no',
                    [((".c", NCR),
                      (conftest_1_obj_suffix, NCF))],
                    conftest_1_base)]
)


test.run(arguments='--config=cache')
test.checkConfigureLogAndStdout(checks=[
    ConfigCheckInfo("Checking for C header file non_system_header0.h... ",
                    'yes',
                    [((".c", CR),
                      (conftest_0_obj_suffix, CR))],
                    conftest_0_base,
                    ),
    ConfigCheckInfo("Checking for C header file non_system_header1.h... ",
                    'no',
                    [((".c", CR),
                      (conftest_1_obj_suffix, CF))],
                    conftest_1_base)]
)


test.write(['include', 'non_system_header1.h'], """
/* Another header */
""")
test.unlink(['include', 'non_system_header0.h'])

test.run(arguments='--config=cache')

test.checkConfigureLogAndStdout(checks=[
    ConfigCheckInfo("Checking for C header file non_system_header0.h... ",
                    'yes',
                    [((".c", CR),
                      (conftest_0_obj_suffix, CR))],
                    conftest_0_base,
                    ),
    ConfigCheckInfo("Checking for C header file non_system_header1.h... ",
                    'no',
                    [((".c", CR),
                      (conftest_1_obj_suffix, CF))],
                    conftest_1_base)]
)

test.run(arguments='--config=auto')
test.checkConfigureLogAndStdout(checks=[
    ConfigCheckInfo("Checking for C header file non_system_header0.h... ",
                    'no',
                    [((".c", CR),
                      (conftest_0_obj_suffix, NCF))],
                    conftest_0_base,
                    ),
    ConfigCheckInfo("Checking for C header file non_system_header1.h... ",
                    'yes',
                    [((".c", CR),
                      (conftest_1_obj_suffix, NCR))],
                    conftest_1_base)]
)

test.file_fixture('test_main.c')

# Check the combination of --config=force and Decider('MD5-timestamp')
SConstruct_path = test.workpath('SConstruct')
test.write(SConstruct_path, """
env = Environment()
env.Decider('MD5-timestamp')
conf = Configure(env)
conf.TryLink('int main(){return 0;}','.c')
env = conf.Finish()
env.Program('test_main.c')
""")
test.run(arguments='--config=force')
# On second run the sconsign is loaded and decider doesn't just indicate need to rebuild
test.run(arguments='--config=force')
test.must_not_contain(test.workpath('config.log'), "TypeError: 'NoneType' object is not callable", mode='r')

# Now check to check that test_main.c didn't rebuild on second run above.
# This fixes an issue where --config=force overwrites the Environments decider and is not reset when
# the configure context is done.
# https://github.com/SCons/scons/issues/3303
test.fail_test('test_main.o' in test.stdout())

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
