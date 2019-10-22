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
Make sure that SourceSignatures() works when overrides are used on a
Builder call.  (Previous implementations used methods that would stay
bound to the underlying construction environment, which in this case
meant ignoring the 'timestamp' setting and still using the underlying
content signature.)
"""

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

expect = TestSCons.re_escape("""
scons: warning: The env.SourceSignatures() method is deprecated;
\tconvert your build to use the env.Decider() method instead.
""") + TestSCons.file_expr

test.write('SConstruct', """\
SetOption('warn', 'deprecated-source-signatures')
DefaultEnvironment().SourceSignatures('MD5')
env = Environment()
env.SourceSignatures('timestamp')
env.Command('foo.out', 'foo.in', Copy('$TARGET', '$SOURCE'), FOO=1)
""")

test.write('foo.in', "foo.in 1\n")

test.run(arguments = 'foo.out', stderr = expect)

test.sleep()

test.write('foo.in', "foo.in 1\n")

test.not_up_to_date(arguments = 'foo.out', stderr = expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
