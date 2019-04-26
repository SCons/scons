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
Verify that "build" command of --interactive mode can take a -j
option to build things in parallel.
"""

import TestSCons

test = TestSCons.TestSCons(combine=1)

test.write('SConstruct', """\
import os
import time
from SCons.Script import *
def cat(target, source, env):
    t = str(target[0])
    os.mkdir(t + '.started')
    with open(t, 'wb') as ofp:
        for s in source:
            with open(str(s), 'rb') as ifp:
                ofp.write(ifp.read())
    os.mkdir(t + '.finished')

def must_be_finished(target, source, env, dir):
    if not os.path.exists(dir):
        msg = 'build failed, %s does not exist\\n' % dir
        sys.stderr.write(msg)
        return 1
    return cat(target, source, env)

def f1_a_out_must_be_finished(target, source, env):
    return must_be_finished(target, source, env, 'f1-a.out.finished')
def f3_a_out_must_be_finished(target, source, env):
    return must_be_finished(target, source, env, 'f3-a.out.finished')

def must_wait_for_f2_b_out(target, source, env):
    t = str(target[0])
    os.mkdir(t + '.started')
    f2_b_started = 'f2-b.out.started'
    while not os.path.exists(f2_b_started):
        time.sleep(1)
    with open(t, 'wb') as ofp:
        for s in source:
            with open(str(s), 'rb') as ifp:
                ofp.write(ifp.read())
    os.mkdir(t + '.finished')

def _f2_a_out_must_not_be_finished(target, source, env):
    f2_a_started = 'f2-a.out.started'
    f2_a_finished = 'f2-a.out.finished'
    while not os.path.exists(f2_a_started):
        time.sleep(1)
    msg = 'f2_a_out_must_not_be_finished(["%s"], ["%s"])\\n' % (target[0], source[0])
    sys.stdout.write(msg)
    if os.path.exists(f2_a_finished):
        msg = 'build failed, %s exists\\n' % f2_a_finished
        sys.stderr.write(msg)
        return 1
    return cat(target, source, env)

f2_a_out_must_not_be_finished = Action(_f2_a_out_must_not_be_finished,
                                       strfunction = None)

Cat = Action(cat)
f1_a = Command('f1-a.out', 'f1-a.in', cat)
f1_b = Command('f1-b.out', 'f1-b.in', f1_a_out_must_be_finished)
f2_a = Command('f2-a.out', 'f2-a.in', must_wait_for_f2_b_out)
f2_b = Command('f2-b.out', 'f2-b.in', f2_a_out_must_not_be_finished)
f3_a = Command('f3-a.out', 'f3-a.in', cat)
f3_b = Command('f3-b.out', 'f3-b.in', f3_a_out_must_be_finished)
Command('f1.out', f1_a + f1_b, cat)
Command('f2.out', f2_a + f2_b, cat)
Command('f3.out', f3_a + f3_b, cat)
Command('1', [], Touch('$TARGET'))
Command('2', [], Touch('$TARGET'))
Command('3', [], Touch('$TARGET'))
""")

test.write('f1-a.in', "f1-a.in\n")
test.write('f1-b.in', "f1-b.in\n")
test.write('f2-a.in', "f2-a.in\n")
test.write('f2-b.in', "f2-b.in\n")
test.write('f3-a.in', "f3-a.in\n")
test.write('f3-b.in', "f3-b.in\n")



scons = test.start(arguments = '-Q --interactive')

scons.send("build f1.out\n")

scons.send("build 1\n")

test.wait_for(test.workpath('1'), popen=scons)

test.must_match(test.workpath('f1.out'), "f1-a.in\nf1-b.in\n")



scons.send("build -j2 f2.out\n")

scons.send("build 2\n")

test.wait_for(test.workpath('2'), popen=scons)

test.must_match(test.workpath('f2.out'), "f2-a.in\nf2-b.in\n")



scons.send("build f3.out\n")

scons.send("build 3\n")

test.wait_for(test.workpath('3'))

test.must_match(test.workpath('f3.out'), "f3-a.in\nf3-b.in\n")



expect_stdout = """\
scons>>> cat(["f1-a.out"], ["f1-a.in"])
f1_a_out_must_be_finished(["f1-b.out"], ["f1-b.in"])
cat(["f1.out"], ["f1-a.out", "f1-b.out"])
scons>>> Touch("1")
scons>>> must_wait_for_f2_b_out(["f2-a.out"], ["f2-a.in"])
f2_a_out_must_not_be_finished(["f2-b.out"], ["f2-b.in"])
cat(["f2.out"], ["f2-a.out", "f2-b.out"])
scons>>> Touch("2")
scons>>> cat(["f3-a.out"], ["f3-a.in"])
f3_a_out_must_be_finished(["f3-b.out"], ["f3-b.in"])
cat(["f3.out"], ["f3-a.out", "f3-b.out"])
scons>>> Touch("3")
scons>>> 
"""

test.finish(scons, stdout = expect_stdout)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
