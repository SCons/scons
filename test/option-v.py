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
from __future__ import print_function

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import TestSCons

test = TestSCons.TestSCons(match = TestCmd.match_re)

test.write('SConstruct', "")

# Construct the standard copyright marker so it doesn't get replaced
# by the packaging build.
copyright_marker = '__' + 'COPYRIGHT' + '__'

fmt = '(%s|Copyright \\(c\\) %s The SCons Foundation)\n'

copyright_line = fmt % (copyright_marker, TestSCons.copyright_years)

# Windows may or may not print a line for the script version
# depending on whether it's invoked through scons.py or scons.bat.
expect1 = r"""SCons by Steven Knight et al.:
\tengine: v\S+, [^,]*, by \S+ on \S+
\tengine path: \[.*\]
""" + copyright_line

expect2 = r"""SCons by Steven Knight et al.:
\tscript: v\S+, [^,]*, by \S+ on \S+
\tengine: v\S+, [^,]*, by \S+ on \S+
\tengine path: \[.*\]
""" + copyright_line

test.run(arguments = '-v')
stdout = test.stdout()
if not test.match_re(stdout, expect1) and not test.match_re(stdout, expect2):
    print(stdout)
    test.fail_test()

test.run(arguments = '--version')
stdout = test.stdout()
if not test.match_re(stdout, expect1) and not test.match_re(stdout, expect2):
    print(stdout)
    test.fail_test()

test.pass_test()
 

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
