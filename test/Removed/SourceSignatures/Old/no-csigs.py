
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

import TestSCons
import TestSConsign

test = TestSConsign.TestSConsign(match = TestSConsign.match_re)


test.write('SConstruct', """\
SetOption('warn', 'deprecated-source-signatures')
def build(env, target, source):
    with open(str(target[0]), 'wt') as ofp, open(str(source[0]), 'rt') as ifp:
        ofp.write(ifp.read())
B = Builder(action = build)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'f1.out', source = 'f1.in')
env.B(target = 'f2.out', source = 'f2.in')
SourceSignatures('timestamp')
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")

expect = TestSCons.re_escape("""
scons: warning: The env.SourceSignatures() method is deprecated;
\tconvert your build to use the env.Decider() method instead.
""") + TestSCons.file_expr

test.run(arguments = '.', stderr = expect)


expect = r"""=== .:
SConstruct: None \d+ \d+
f1.in: None \d+ \d+
f1.out: \S+ \d+ \d+
        f1.in: None \d+ \d+
        \S+ \[build\(target, source, env\)\]
f2.in: None \d+ \d+
f2.out: \S+ \d+ \d+
        f2.in: None \d+ \d+
        \S+ \[build\(target, source, env\)\]
"""

test.run_sconsign(arguments = test.workpath(test.get_sconsignname()),
                  stdout = expect)


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
