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

import TestSCons

_obj = TestSCons._obj

test = TestSCons.TestSCons()

test.subdir('include')

NCR = test.NCR  # non-cached rebuild
CR  = test.CR   # cached rebuild (up to date)
NCF = test.NCF  # non-cached build failure
CF  = test.CF   # cached build failure

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

conftest_0_c = os.path.join(".sconf_temp", "conftest_0.c")
SConstruct_file_line = test.python_file_line(SConstruct_path, 6)[:-1]

expect = """
scons: *** "%(conftest_0_c)s" is not yet built and cache is forced.
%(SConstruct_file_line)s
""" % locals()

test.run(arguments='--config=cache', status=2, stderr=expect)

test.run(arguments='--config=auto')
test.checkLogAndStdout( ["Checking for C header file non_system_header0.h... ",
                    "Checking for C header file non_system_header1.h... "],
                    ["yes", "no"],
                    [[((".c", NCR), (_obj, NCR))],
                     [((".c", NCR), (_obj, NCF))]],
                    "config.log", ".sconf_temp", "SConstruct")

test.run(arguments='--config=auto')
test.checkLogAndStdout( ["Checking for C header file non_system_header0.h... ",
                    "Checking for C header file non_system_header1.h... "],
                    ["yes", "no"],
                    [[((".c", CR), (_obj, CR))],
                     [((".c", CR), (_obj, CF))]],
                    "config.log", ".sconf_temp", "SConstruct")

test.run(arguments='--config=force')
test.checkLogAndStdout( ["Checking for C header file non_system_header0.h... ",
                    "Checking for C header file non_system_header1.h... "],
                    ["yes", "no"],
                    [[((".c", NCR), (_obj, NCR))],
                     [((".c", NCR), (_obj, NCF))]],
                    "config.log", ".sconf_temp", "SConstruct")

test.run(arguments='--config=cache')
test.checkLogAndStdout( ["Checking for C header file non_system_header0.h... ",
                    "Checking for C header file non_system_header1.h... "],
                    ["yes", "no"],
                    [[((".c", CR), (_obj, CR))],
                     [((".c", CR), (_obj, CF))]],
                    "config.log", ".sconf_temp", "SConstruct")

test.write(['include', 'non_system_header1.h'], """
/* Another header */
""")
test.unlink(['include', 'non_system_header0.h'])

test.run(arguments='--config=cache')
test.checkLogAndStdout( ["Checking for C header file non_system_header0.h... ",
                    "Checking for C header file non_system_header1.h... "],
                    ["yes", "no"],
                    [[((".c", CR), (_obj, CR))],
                     [((".c", CR), (_obj, CF))]],
                    "config.log", ".sconf_temp", "SConstruct")

test.run(arguments='--config=auto')
test.checkLogAndStdout( ["Checking for C header file non_system_header0.h... ",
                    "Checking for C header file non_system_header1.h... "],
                    ["no", "yes"],
                    [[((".c", CR), (_obj, NCF))],
                     [((".c", CR), (_obj, NCR))]],
                    "config.log", ".sconf_temp", "SConstruct")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
