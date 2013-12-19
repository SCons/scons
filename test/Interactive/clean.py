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
Verifies operation of the --interactive command line option
"clean" subcommand.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
Command('f1.out', 'f1.in', Copy('$TARGET', '$SOURCE'))
Command('f2.out', 'f2.in', Copy('$TARGET', '$SOURCE'))
Command('f3.out', 'f3.in', Copy('$TARGET', '$SOURCE'))
Command('1', [], Touch('$TARGET'))
Command('2', [], Touch('$TARGET'))
Command('3', [], Touch('$TARGET'))
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")



scons = test.start(arguments = '-Q --interactive')

scons.send("build f1.out f2.out f3.out\n")

scons.send("build 1\n")

test.wait_for(test.workpath('1'))

test.must_match(test.workpath('f1.out'), "f1.in\n")
test.must_match(test.workpath('f2.out'), "f2.in\n")
test.must_match(test.workpath('f3.out'), "f3.in\n")



scons.send("clean f1.out\n")

scons.send("build 2\n")

test.wait_for(test.workpath('2'), popen=scons)

test.must_not_exist('f1.out')
test.must_exist('f2.out')
test.must_exist('f3.out')



scons.send("build -c\n")

scons.send("build 3\n")

test.wait_for(test.workpath('3'))

test.must_not_exist('f1.out')
test.must_not_exist('f2.out')
test.must_not_exist('f3.out')

expect_stdout = """\
scons>>> Copy("f1.out", "f1.in")
Copy("f2.out", "f2.in")
Copy("f3.out", "f3.in")
scons>>> Touch("1")
scons>>> Removed f1.out
scons>>> Touch("2")
scons>>> Removed 1
Removed 2
Removed f2.out
Removed f3.out
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
