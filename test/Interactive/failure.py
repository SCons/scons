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
Verify that when a build fails, later builds correctly report
that their builds succeeded, and that we don't get "stuck" on
reporting the earlier build failure.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
def fail(target, source, env):
    return 1
Command('f1.out', 'f1.in', Action(fail))
Command('f2.out', 'f2.in', Copy('$TARGET', '$SOURCE'))
Command('1', [], Touch('$TARGET'))
Command('2', [], Touch('$TARGET'))
Command('3', [], Touch('$TARGET'))
Command('4', [], Touch('$TARGET'))
""")

test.write('f1.in', "f1.in 1\n")
test.write('f2.in', "f2.in 1\n")



scons = test.start(arguments = '--interactive')

scons.send("build f1.out\n")

scons.send("build 1\n")

test.wait_for(test.workpath('1'))

test.must_not_exist(test.workpath('f1.out'))



scons.send("build f2.out\n")

scons.send("build 2\n")

test.wait_for(test.workpath('2'))

test.must_match(test.workpath('f2.out'), "f2.in 1\n")



scons.send("build f1.out\n")

scons.send("build 3\n")

test.wait_for(test.workpath('3'))

test.must_not_exist(test.workpath('f1.out'))



test.write('f2.in', "f2.in 2\n")

scons.send("build f2.out\n")

scons.send("build 4\n")

test.wait_for(test.workpath('4'))

test.must_match(test.workpath('f2.out'), "f2.in 2\n")



expect_stdout = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons>>> scons: Building targets ...
fail(["f1.out"], ["f1.in"])
scons: building terminated because of errors.
scons: Clearing cached node information ...
scons: done clearing node information.
scons>>> scons: Building targets ...
Touch("1")
scons: done building targets.
scons: Clearing cached node information ...
scons: done clearing node information.
scons>>> scons: Building targets ...
Copy("f2.out", "f2.in")
scons: done building targets.
scons: Clearing cached node information ...
scons: done clearing node information.
scons>>> scons: Building targets ...
Touch("2")
scons: done building targets.
scons: Clearing cached node information ...
scons: done clearing node information.
scons>>> scons: Building targets ...
fail(["f1.out"], ["f1.in"])
scons: building terminated because of errors.
scons: Clearing cached node information ...
scons: done clearing node information.
scons>>> scons: Building targets ...
Touch("3")
scons: done building targets.
scons: Clearing cached node information ...
scons: done clearing node information.
scons>>> scons: Building targets ...
Copy("f2.out", "f2.in")
scons: done building targets.
scons: Clearing cached node information ...
scons: done clearing node information.
scons>>> scons: Building targets ...
Touch("4")
scons: done building targets.
scons: Clearing cached node information ...
scons: done clearing node information.
scons>>> 
"""

expect_stderr = """\
scons: *** [f1.out] Error 1
scons: *** [f1.out] Error 1
"""

test.finish(scons, stdout = expect_stdout, stderr = expect_stderr)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
