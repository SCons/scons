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
Verify that the cache mechanism works when checks are ok.
"""

import TestSCons

_exe = TestSCons._exe
_obj = TestSCons._obj

test = TestSCons.TestSCons(match = TestSCons.match_re)

lib = test.Configure_lib

NCR = test.NCR  # non-cached rebuild
CR  = test.CR   # cached rebuild (up to date)
NCF = test.NCF  # non-cached build failure
CF  = test.CF   # cached build failure

test.write('SConstruct', """\
if not int(ARGUMENTS.get('target_signatures_content', 0)):
    Decider('timestamp-newer')
env = Environment()
import os
env.AppendENVPath('PATH', os.environ['PATH'])
conf = Configure(env)
r1 = conf.CheckLibWithHeader( '%(lib)s', 'math.h', 'c' )
r2 = conf.CheckLibWithHeader( None, 'math.h', 'c' )
r3 = conf.CheckLib( '%(lib)s', autoadd=0 )
r4 = conf.CheckLib( None, autoadd=0 )
r5 = conf.CheckCHeader( 'math.h' )
r6 = conf.CheckCXXHeader( 'vector' )
env = conf.Finish()
if not (r1 and r2 and r3 and r4 and r5 and r6):
     Exit(1)
""" % locals())

# Verify correct behavior when we call Decider('timestamp-newer')

test.run()
test.checkLogAndStdout(["Checking for C library %s... " % lib,
                       "Checking for C library None... ",
                       "Checking for C library %s... " % lib,
                       "Checking for C library None... ",
                       "Checking for C header file math.h... ",
                       "Checking for C++ header file vector... "],
                      ["yes"]*6,
                      [[((".c", NCR), (_obj, NCR), (_exe, NCR))]]*4 +
                        [[((".c", NCR), (_obj, NCR))]] +
                        [[((".cpp", NCR), (_obj, NCR))]],
                      "config.log", ".sconf_temp", "SConstruct")    
    

test.run()
test.checkLogAndStdout(["Checking for C library %s... " % lib,
                       "Checking for C library None... ",
                       "Checking for C library %s... " % lib,
                       "Checking for C library None... ",
                       "Checking for C header file math.h... ",
                       "Checking for C++ header file vector... "],
                      ["yes"]*6,
                      [[((".c", CR), (_obj, CR), (_exe, CR))]]*4 +
                       [[((".c", CR), (_obj, CR))]] +
                       [[((".cpp", CR), (_obj, CR))]],
                      "config.log", ".sconf_temp", "SConstruct")

# same should be true for the default behavior of Decider('content')

test.run(arguments='target_signatures_content=1 --config=force')
test.checkLogAndStdout(["Checking for C library %s... " % lib,
                       "Checking for C library None... ",
                       "Checking for C library %s... " % lib,
                       "Checking for C library None... ",
                       "Checking for C header file math.h... ",
                       "Checking for C++ header file vector... "],
                      ["yes"]*6,
                      [[((".c", NCR), (_obj, NCR), (_exe, NCR))]]*4 +
                        [[((".c", NCR), (_obj, NCR))]] +
                        [[((".cpp", NCR), (_obj, NCR))]],
                      "config.log", ".sconf_temp", "SConstruct")    

test.run(arguments='target_signatures_content=1')
test.checkLogAndStdout(["Checking for C library %s... " % lib,
                       "Checking for C library None... ",
                       "Checking for C library %s... " % lib,
                       "Checking for C library None... ",
                       "Checking for C header file math.h... ",
                       "Checking for C++ header file vector... "],
                      ["yes"]*6,
                      [[((".c", CR), (_obj, CR), (_exe, CR))]]*4 +
                       [[((".c", CR), (_obj, CR))]] +
                       [[((".cpp", CR), (_obj, CR))]],
                      "config.log", ".sconf_temp", "SConstruct")    

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
