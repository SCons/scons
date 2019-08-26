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
Test the simultaneous use of implicit_cache and
SourceSignatures('timestamp')
"""

import re

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

test.write('SConstruct', """\
SetOption('warn', 'deprecated-source-signatures')
SetOption('implicit_cache', 1)
SourceSignatures('timestamp')

def build(env, target, source):
    with open(str(target[0]), 'wt') as ofp, open(str(source[0]), 'rt') as ifp:
        ofp.write(ifp.read())
B = Builder(action = build)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'both.out', source = 'both.in')
""")


expect = TestSCons.re_escape("""
scons: warning: The env.SourceSignatures() method is deprecated;
\tconvert your build to use the env.Decider() method instead.
""") + TestSCons.file_expr


both_out_both_in = re.escape(test.wrap_stdout('build(["both.out"], ["both.in"])\n'))

test.write('both.in', "both.in 1\n")

test.run(arguments = 'both.out',
         stdout = both_out_both_in,
         stderr = expect)


test.sleep(2)

test.write('both.in', "both.in 2\n")

test.run(arguments = 'both.out',
         stdout = both_out_both_in,
         stderr = expect)


test.sleep(2)

test.write('both.in', "both.in 3\n")

test.run(arguments = 'both.out',
         stdout = both_out_both_in,
         stderr = expect)


test.sleep(2)

test.write('both.in', "both.in 4\n")

test.run(arguments = 'both.out',
         stdout = both_out_both_in,
         stderr = expect)


test.sleep(2)

test.up_to_date(arguments = 'both.out', stderr = None)


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
