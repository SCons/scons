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
Verify that changing the order and/or number of config tests does not reuse 
incorrect temporary test files on successive runs.
This addresses Issue 3469: 
https://github.com/SCons/scons/issues/3469
"""

import TestSCons

_exe = TestSCons._exe
_obj = TestSCons._obj
_python_ = TestSCons._python_

test = TestSCons.TestSCons()

NCR = test.NCR  # non-cached rebuild
CR  = test.CR   # cached rebuild (up to date)
NCF = test.NCF  # non-cached build failure
CF  = test.CF   # cached build failure

test.file_fixture('./fixture/SConstruct')

test.run()

# First run all tests should build
test.checkLogAndStdout(["Checking for C header file math.h... ",
                        "Checking for C header file stdlib.h... ",
                        "Checking for C header file stdio.h... "],
                       ["yes", "yes", "yes"],
                      [[(('.c', NCR), (_obj, NCR))],
                        [(('.c', NCR), (_obj, NCR))],
                        [(('.c', NCR), (_obj, NCR))]],
                       "config.log", ".sconf_temp", "SConstruct")


# Second run, this will skip middle check.  First and third (now second) checks should
# reuse cached
test.run('SKIP=1')
test.checkLogAndStdout(["Checking for C header file math.h... ",
                        # "Checking for C header file stdlib.h... ",
                        "Checking for C header file stdio.h... "],
                       ["yes", "yes", "yes"],
                      [[(('.c', CR), (_obj, CR))],
                        # [(('.c', CR), (_obj, CR))],
                        [(('.c', CR), (_obj, CR))]],
                       "config.log", ".sconf_temp", "SConstruct")

# Third run. We're re-adding the middle test, all tests should reuse cached.
test.run('SKIP=0')
test.checkLogAndStdout(["Checking for C header file math.h... ",
                        "Checking for C header file stdlib.h... ",
                        "Checking for C header file stdio.h... "],
                       ["yes", "yes", "yes"],
                      [[(('.c', CR), (_obj, CR))],
                        [(('.c', CR), (_obj, CR))],
                        [(('.c', CR), (_obj, CR))]],
                       "config.log", ".sconf_temp", "SConstruct")



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
