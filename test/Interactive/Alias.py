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
Verify the ability to build an Alias in --interactive mode.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
foo = Command('foo.out', 'foo.in', Copy('$TARGET', '$SOURCE'))
Alias('foo-alias', foo)
Command('1', [], Touch('$TARGET'))
Command('2', [], Touch('$TARGET'))
""")

test.write('foo.in', "foo.in 1\n")



scons = test.start(arguments='-Q --interactive')

scons.send("build foo-alias\n")

scons.send("build 1\n")

test.wait_for(test.workpath('1'), popen=scons)

test.must_match(test.workpath('foo.out'), "foo.in 1\n")



test.write('foo.in', "foo.in 2\n")

# Verify that "scons" can be used as a synonmyn for the "build" command.
scons.send("scons foo-alias\n")

scons.send("scons 2\n")

test.wait_for(test.workpath('2'), popen=scons)

test.must_match(test.workpath('foo.out'), "foo.in 2\n")



scons.send("build foo-alias\n")

expect_stdout = """\
scons>>> Copy("foo.out", "foo.in")
scons>>> Touch("1")
scons>>> Copy("foo.out", "foo.in")
scons>>> Touch("2")
scons>>> scons: `foo-alias' is up to date.
scons>>> 
"""

test.finish(scons, stdout = expect_stdout)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
