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
Verify the behavior of the "version" subcommand.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import TestSCons

test = TestSCons.TestSCons(match = TestCmd.match_re)

test.write('SConstruct', "")



# Standard copyright marker is mangled so it doesn't get replaced
# by the packaging build.
copyright_line = """\
(_{2}COPYRIGHT__|Copyright \\(c\\) 2001[-\\d, ]+ The SCons Foundation)
"""

expect1 = """\
scons>>> 
scons>>> 
"""

expect2 = """\
scons>>> 
scons>>> 
"""

test.run(arguments='-Q --interactive',
         stdin="version\nexit\n")

expect2 = r"""scons>>> SCons by Steven Knight et al\.:
\tSCons: v\S+, [^,]*, by \S+ on \S+
\tSCons path: \[.*\]
%(copyright_line)sscons>>> 
""" % locals()

stdout = test.stdout() + '\n'
if not test.match_re(stdout, expect2):
    print(repr(stdout))
    test.fail_test()



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
