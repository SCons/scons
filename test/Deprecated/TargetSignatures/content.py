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
Verify use of the TargetSignatures('content') setting to override
SourceSignatures('timestamp') settings.
"""

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

expect = TestSCons.re_escape("""
scons: warning: The env.SourceSignatures() method is deprecated;
\tconvert your build to use the env.Decider() method instead.
""") + TestSCons.file_expr + TestSCons.re_escape("""
scons: warning: The env.TargetSignatures() method is deprecated;
\tconvert your build to use the env.Decider() method instead.
""") + TestSCons.file_expr


test.write('SConstruct', """\
SetOption('warn', 'deprecated-source-signatures')
SetOption('warn', 'deprecated-target-signatures')
env = Environment()

def copy(env, source, target):
    with open(str(target[0]), 'wb') as ofp:
        for s in source:
           with open(str(s), 'rb') as ifp:
               ofp.write(ifp.read())

copyAction = Action(copy, "Copying $TARGET")

SourceSignatures('timestamp')

env['BUILDERS']['Copy'] = Builder(action=copyAction)

env.Copy('foo.out', 'foo.in')

env2 = env.Clone()
env2.TargetSignatures('content')
env2.Copy('bar.out', 'bar.in')
AlwaysBuild('bar.out')

env.Copy('final', ['foo.out', 'bar.out', 'extra.in'])
env.Ignore('final', 'extra.in')
""")

test.write('foo.in', "foo.in\n")
test.write('bar.in', "bar.in\n")
test.write('extra.in', "extra.in 1\n")

test.run(stderr = expect)

test.must_match('final', "foo.in\nbar.in\nextra.in 1\n")

test.sleep()
test.write('extra.in', "extra.in 2\n")

test.run(stderr = expect)

test.must_match('final', "foo.in\nbar.in\nextra.in 1\n")


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
