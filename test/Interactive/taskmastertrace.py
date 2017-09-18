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
Verify use of the --taskmastertrace= option to the "build" command
of --interactive mode.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
Command('foo.out', 'foo.in', Copy('$TARGET', '$SOURCE'))
Command('1', [], Touch('$TARGET'))
Command('2', [], Touch('$TARGET'))
""")

test.write('foo.in', "foo.in 1\n")



scons = test.start(arguments = '-Q --interactive')

scons.send("build foo.out 1\n")

test.wait_for(test.workpath('1'))

test.must_match(test.workpath('foo.out'), "foo.in 1\n")



test.write('foo.in', "foo.in 2\n")

scons.send("build --taskmastertrace=- foo.out\n")

test.wait_for(test.workpath('foo.out'))

scons.send("build 2\n")

test.wait_for(test.workpath('2'))

test.must_match(test.workpath('foo.out'), "foo.in 2\n")



scons.send("build foo.out\n")

expect_stdout = """\
scons>>> Copy("foo.out", "foo.in")
Touch("1")
scons>>> 
Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   'foo.out'> and its children:
Taskmaster:        <no_state   0   'foo.in'>
Taskmaster:      adjusted ref count: <pending    1   'foo.out'>, child 'foo.in'
Taskmaster:     Considering node <no_state   0   'foo.in'> and its children:
Taskmaster: Evaluating <pending    0   'foo.in'>

Task.make_ready_current(): node <pending    0   'foo.in'>
Task.prepare():      node <up_to_date 0   'foo.in'>
Task.executed_with_callbacks(): node <up_to_date 0   'foo.in'>
Task.postprocess():  node <up_to_date 0   'foo.in'>
Task.postprocess():  removing <up_to_date 0   'foo.in'>
Task.postprocess():  adjusted parent ref count <pending    0   'foo.out'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <pending    0   'foo.out'> and its children:
Taskmaster:        <up_to_date 0   'foo.in'>
Taskmaster: Evaluating <pending    0   'foo.out'>

Task.make_ready_current(): node <pending    0   'foo.out'>
Task.prepare():      node <executing  0   'foo.out'>
Task.execute():      node <executing  0   'foo.out'>
Copy("foo.out", "foo.in")
Task.executed_with_callbacks(): node <executing  0   'foo.out'>
Task.postprocess():  node <executed   0   'foo.out'>

Taskmaster: Looking for a node to evaluate
Taskmaster: No candidate anymore.

scons>>> Touch("2")
scons>>> scons: `foo.out' is up to date.
scons>>> 
"""

test.finish(scons, stdout = expect_stdout)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
