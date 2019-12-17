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
Verify that two different environments can be used for the same target,
so long as the actions have the same signature; a warning is generated.
"""

import TestSCons

test = TestSCons.TestSCons(match=TestSCons.match_re)

test.write('SConstruct', """\
DefaultEnvironment(tools=[])

def build(env, target, source):
    with open(str(target[0]), 'wb') as f:
        for s in source:
            with open(str(s), 'rb') as infp:
                f.write(infp.read())

B = Builder(action=build, multi=1)
env = Environment(tools=[], BUILDERS = { 'B' : B })
env2 = env.Clone(DIFFERENT_VARIABLE = 'true')
env.B(target = 'file5.out', source = 'file5a.in')
env2.B(target = 'file5.out', source = 'file5b.in')
""")

test.write('file5a.in', 'file5a.in\n')
test.write('file5b.in', 'file5b.in\n')

expect = TestSCons.re_escape("""
scons: warning: Two different environments were specified for target file5.out,
\tbut they appear to have the same action: build(target, source, env)
""") + TestSCons.file_expr

test.run(arguments='file5.out', stderr=expect)

test.must_match('file5.out', "file5a.in\nfile5b.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
