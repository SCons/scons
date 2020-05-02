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
Make sure that TargetSignatures() works when overrides are used on a
Builder call.  Previous implementations used methods that would stay
bound to the underlying construction environment and cause weird
behavior like infinite recursion.
"""

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

test.write('SConstruct', """\
SetOption('warn', 'deprecated-target-signatures')
env = Environment()
env.TargetSignatures('content')
env.Command('foo.out', 'foo.mid', Copy('$TARGET', '$SOURCE'), FOO=1)
env.Command('foo.mid', 'foo.in', Copy('$TARGET', '$SOURCE'), FOO=2)
""")

test.write('foo.in', "foo.in\n")

expect = TestSCons.re_escape("""
scons: warning: The env.TargetSignatures() method is deprecated;
\tconvert your build to use the env.Decider() method instead.
""") + TestSCons.file_expr

test.run(arguments = '.', stderr = expect)

test.must_match('foo.mid', "foo.in\n")
test.must_match('foo.out', "foo.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
