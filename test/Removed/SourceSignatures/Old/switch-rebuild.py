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
Test that switching SourceSignature() types no longer causes rebuilds.
"""

import re

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

expect = TestSCons.re_escape("""
scons: warning: The env.SourceSignatures() method is deprecated;
\tconvert your build to use the env.Decider() method instead.
""") + TestSCons.file_expr


base_sconstruct_contents = """\
SetOption('warn', 'deprecated-source-signatures')
SourceSignatures('%s')

def build(env, target, source):
    with open(str(target[0]), 'wt') as ofp, open(str(source[0]), 'rt') as ifp:
        ofp.write(ifp.read())
B = Builder(action = build)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'switch.out', source = 'switch.in')
"""

def write_SConstruct(test, sig_type):
    contents = base_sconstruct_contents % sig_type
    test.write('SConstruct', contents)


write_SConstruct(test, 'MD5')

test.write('switch.in', "switch.in\n")

switch_out_switch_in = re.escape(test.wrap_stdout('build(["switch.out"], ["switch.in"])\n'))

test.run(arguments = 'switch.out',
         stdout = switch_out_switch_in,
         stderr = expect)

test.up_to_date(arguments = 'switch.out', stderr = None)


write_SConstruct(test, 'timestamp')

test.up_to_date(arguments = 'switch.out', stderr = None)


write_SConstruct(test, 'MD5')

test.not_up_to_date(arguments = 'switch.out', stderr = None)


test.write('switch.in', "switch.in 2\n")

test.run(arguments = 'switch.out',
         stdout = switch_out_switch_in,
         stderr = expect)


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
