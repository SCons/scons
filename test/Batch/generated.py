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
Verify use of a batch builder when one of the later targets in the
list the list depends on a generated file.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
def batch_build(target, source, env):
    for t, s in zip(target, source):
        with open(str(t), 'wb') as fp:
            if str(t) == 'f3.out':
                with open('f3.include', 'rb') as f:
                    fp.write(f.read())
            with open(str(s), 'rb') as f:
                fp.write(f.read())
env = Environment()
bb = Action(batch_build, batch_key=True)
env['BUILDERS']['Batch'] = Builder(action=bb)
env1 = env.Clone()
env1.Batch('f1.out', 'f1.in')
env1.Batch('f2.out', 'f2.mid')
f3_out = env1.Batch('f3.out', 'f3.in')

env2 = env.Clone()
env2.Batch('f2.mid', 'f2.in')

f3_include = env.Batch('f3.include', 'f3.include.in')
env.Depends(f3_out, f3_include)
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write('f3.include.in', "f3.include.in\n")

expect = test.wrap_stdout("""\
batch_build(["f2.mid"], ["f2.in"])
batch_build(["f3.include"], ["f3.include.in"])
batch_build(["f1.out", "f2.out", "f3.out"], ["f1.in", "f2.mid", "f3.in"])
""")

test.run(stdout = expect)

test.must_match('f1.out', "f1.in\n")
test.must_match('f2.out', "f2.in\n")

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
