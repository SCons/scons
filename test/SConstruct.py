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

import TestCmd
import TestSCons

test = TestSCons.TestSCons(match = TestCmd.match_re)

test.run(arguments = ".",
         status = 2,
         stdout = "",
         stderr = r"""
scons: \*\*\* No SConstruct file found.
""" + TestSCons.file_expr)

test.match_func = TestCmd.match_exact

wpath = test.workpath()

test.write('sconstruct', """
import os
print "sconstruct", os.getcwd()
""")

test.run(arguments = ".",
         stdout = test.wrap_stdout(read_str = 'sconstruct %s\n' % wpath,
                                   build_str = "scons: `.' is up to date.\n"))


test.write('Sconstruct', """
import os
print "Sconstruct", os.getcwd()
""")

test.run(arguments = ".",
         stdout = test.wrap_stdout(read_str = 'Sconstruct %s\n' % wpath,
                                   build_str = "scons: `.' is up to date.\n"))

test.write('SConstruct', """
import os
print "SConstruct", os.getcwd()
""")

test.run(arguments = ".",
         stdout = test.wrap_stdout(read_str = 'SConstruct %s\n' % wpath,
                                   build_str = "scons: `.' is up to date.\n"))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
