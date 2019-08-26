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
Verify passing in a batch_key callable for more control over how
batch builders behave.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

test.subdir('sub1', 'sub2')

test.write('SConstruct', """
def batch_build(target, source, env):
    for t, s in zip(target, source):
        with open(str(t), 'wb') as f, open(str(s), 'rb') as infp:
            f.write(infp.read())
if ARGUMENTS.get('BATCH_CALLABLE'):
    def batch_key(action, env, target, source):
        return (id(action), id(env), target[0].dir)
else:
    batch_key=True
env = Environment()
bb = Action(batch_build, batch_key=batch_key)
env['BUILDERS']['Batch'] = Builder(action=bb)
env1 = env.Clone()
env1.Batch('sub1/f1a.out', 'f1a.in')
env1.Batch('sub2/f1b.out', 'f1b.in')
env2 = env.Clone()
env2.Batch('sub1/f2a.out', 'f2a.in')
env2.Batch('sub2/f2b.out', 'f2b.in')
""")

test.write('f1a.in', "f1a.in\n")
test.write('f1b.in', "f1b.in\n")
test.write('f2a.in', "f2a.in\n")
test.write('f2b.in', "f2b.in\n")

sub1_f1a_out = os.path.join('sub1', 'f1a.out')
sub2_f1b_out = os.path.join('sub2', 'f1b.out')
sub1_f2a_out = os.path.join('sub1', 'f2a.out')
sub2_f2b_out = os.path.join('sub2', 'f2b.out')

expect = test.wrap_stdout("""\
batch_build(["%(sub1_f1a_out)s", "%(sub2_f1b_out)s"], ["f1a.in", "f1b.in"])
batch_build(["%(sub1_f2a_out)s", "%(sub2_f2b_out)s"], ["f2a.in", "f2b.in"])
""" % locals())

test.run(stdout = expect)

test.must_match(['sub1', 'f1a.out'], "f1a.in\n")
test.must_match(['sub2', 'f1b.out'], "f1b.in\n")
test.must_match(['sub1', 'f2a.out'], "f2a.in\n")
test.must_match(['sub2', 'f2b.out'], "f2b.in\n")

test.run(arguments = '-c')

test.must_not_exist(['sub1', 'f1a.out'])
test.must_not_exist(['sub2', 'f1b.out'])
test.must_not_exist(['sub1', 'f2a.out'])
test.must_not_exist(['sub2', 'f2b.out'])

expect = test.wrap_stdout("""\
batch_build(["%(sub1_f1a_out)s"], ["f1a.in"])
batch_build(["%(sub1_f2a_out)s"], ["f2a.in"])
batch_build(["%(sub2_f1b_out)s"], ["f1b.in"])
batch_build(["%(sub2_f2b_out)s"], ["f2b.in"])
""" % locals())

test.run(arguments = 'BATCH_CALLABLE=1', stdout = expect)

test.must_match(['sub1', 'f1a.out'], "f1a.in\n")
test.must_match(['sub2', 'f1b.out'], "f1b.in\n")
test.must_match(['sub1', 'f2a.out'], "f2a.in\n")
test.must_match(['sub2', 'f2b.out'], "f2b.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
