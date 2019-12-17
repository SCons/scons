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
Verify basic use of batch_key to write a batch builder that handles
arbitrary pairs of target + source files.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
def batch_build(target, source, env):
    for t, s in zip(target, source):
        with open(str(t), 'wb') as f, open(str(s), 'rb') as infp:
            f.write(infp.read())
env = Environment()
bb = Action(batch_build, batch_key=True)
env['BUILDERS']['Batch'] = Builder(action=bb)
env1 = env.Clone()
env1.Batch('f1a.out', 'f1a.in')
env1.Batch('f1b.out', 'f1b.in')
env2 = env.Clone()
env2.Batch('f2a.out', 'f2a.in')
env3 = env.Clone()
env3.Batch('f3a.out', 'f3a.in')
env3.Batch('f3b.out', 'f3b.in')
""")

test.write('f1a.in', "f1a.in\n")
test.write('f1b.in', "f1b.in\n")
test.write('f2a.in', "f2a.in\n")
test.write('f3a.in', "f3a.in\n")
test.write('f3b.in', "f3b.in\n")

expect = test.wrap_stdout("""\
batch_build(["f1a.out", "f1b.out"], ["f1a.in", "f1b.in"])
batch_build(["f2a.out"], ["f2a.in"])
batch_build(["f3a.out", "f3b.out"], ["f3a.in", "f3b.in"])
""")

test.run(stdout = expect)

test.must_match('f1a.out', "f1a.in\n")
test.must_match('f1b.out', "f1b.in\n")
test.must_match('f2a.out', "f2a.in\n")
test.must_match('f3a.out', "f3a.in\n")
test.must_match('f3b.out', "f3b.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
