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
Verify that the -i option, specified on the build command, causes
build errors to be ignored, just for that command.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
def error(target, source, env):
    return 1
e1 = Command('e1.out', 'e1.in', Action(error))
e2 = Command('e2.out', 'e2.in', Action(error))
f1 = Command('f1.out', 'f1.in', Copy('$TARGET', '$SOURCE'))
f2 = Command('f2.out', 'f2.in', Copy('$TARGET', '$SOURCE'))
Depends(f1, e1)
Depends(f2, e2)
Command('1', [], Touch('$TARGET'))
Command('2', [], Touch('$TARGET'))
Command('3', [], Touch('$TARGET'))
""")

test.write('e1.in', "e1.in\n")
test.write('e2.in', "e2.in\n")
test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")



scons = test.start(arguments = '-Q --interactive', combine=1)

scons.send("build f1.out\n")

scons.send("build 1\n")

test.wait_for(test.workpath('1'), popen=scons)

test.must_not_exist(test.workpath('f1.out'))



scons.send("build -i e1.out f1.out\n")

scons.send("build 2\n")

test.wait_for(test.workpath('2'), popen=scons)

test.must_match(test.workpath('f1.out'), "f1.in\n")



scons.send("build f2.out\n")

scons.send("build 3\n")

test.wait_for(test.workpath('3'), popen=scons)

test.must_not_exist(test.workpath('f2.out'))



expect_stdout = """\
scons>>> error(["e1.out"], ["e1.in"])
scons: *** [e1.out] Error 1
scons>>> Touch("1")
scons>>> error(["e1.out"], ["e1.in"])
scons: *** [e1.out] Error 1
Copy("f1.out", "f1.in")
scons>>> Touch("2")
scons>>> error(["e2.out"], ["e2.in"])
scons: *** [e2.out] Error 1
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
