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
Verify the exit status and error output if variable expansion
throws a SyntaxError.
"""

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)


expect_build = r"""scons: \*\*\*%s SyntaxError `(invalid syntax|Unknown character)( \((<string>, )?line 1\))?' trying to evaluate `%s'
"""

expect_read = "\n" + expect_build + TestSCons.file_expr


# Syntax errors at SConscript read time:
test.write('SConstruct', """\
env = Environment()
env.subst('$foo.bar.3.0')
""")

test.run(status=2, stderr=expect_read % ('', r'\$foo\.bar\.3\.0'))



test.write('SConstruct', """\
env = Environment()
env.subst('${x ! y}')
""")

test.run(status=2, stderr=expect_read % ('', r'\$\{x \! y\}'))



# Syntax errors at build time:
test.write('SConstruct', """\
env = Environment()
env.Command('foo.bar', [], '$foo.bar.3.0')
""")

expect = expect_build % (r' \[foo\.bar\]', r'\$foo\.bar\.3\.0')

test.run(status=2, stderr=expect)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
