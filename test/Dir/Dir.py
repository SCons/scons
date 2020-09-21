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
Verify that the Dir() global function and environment method work
correctly, and that the former does not try to expand construction
variables.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(tools=[], FOO='fff', BAR='bbb')
print(Dir('ddd'))
print(Dir('$FOO'))
print(Dir('${BAR}_$BAR'))
rv = Dir(['mmm', 'nnn'])
rv_msg = [node.path for node in rv]
print(rv_msg)
print(env.Dir('eee'))
print(env.Dir('$FOO'))
print(env.Dir('${BAR}_$BAR'))
rv = env.Dir(['ooo', 'ppp'])
rv_msg = [node.path for node in rv]
print(rv_msg)
""")

test.run(stdout=test.wrap_stdout(read_str="""\
ddd
$FOO
${BAR}_$BAR
['mmm', 'nnn']
eee
fff
bbb_bbb
['ooo', 'ppp']
""", build_str="""\
scons: `.' is up to date.
"""))

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
import os
def my_mkdir(target=None, source=None, env=None):
    os.mkdir(str(target[0]))

MDBuilder = Builder(action=my_mkdir, target_factory=Dir)
env = Environment(tools=[])
env.Append(BUILDERS={'MD': MDBuilder})
env.MD(target='sub1', source=['SConstruct'])
env.MD(target='sub2', source=['SConstruct'], OVERRIDE='foo')
""")

test.run()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
