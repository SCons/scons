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
Test but which only shows on windows when one generated file depends on another generated file
In this case flex and yacc are an example.
"""

import os
import stat

import TestSCons
from TestCmd import IS_WINDOWS


test = TestSCons.TestSCons()

if IS_WINDOWS:
    yacc = test.where_is('yacc') or test.where_is('bison') or test.where_is('win_bison')
    lex = test.where_is('flex') or test.where_is('lex') or test.where_is('win_flex')
    # print("Lex:%s yacc:%s"%(lex,yacc))
    if not yacc or not lex:
        test.skip_test("On windows but no flex/lex/win_flex and yacc/bison/win_bison required for test\n")
else:
    test.skip_test("Windows only test\n")


test.dir_fixture('MD5-winonly-fixture')
test.run()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
