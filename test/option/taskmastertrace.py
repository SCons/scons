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
Simple tests of the --taskmastertrace= option.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(tools=[])

# We name the files 'Tfile' so that they will sort after the SConstruct
# file regardless of whether the test is being run on a case-sensitive
# or case-insensitive system.

env.Command('Tfile.out', 'Tfile.mid', Copy('$TARGET', '$SOURCE'))
env.Command('Tfile.mid', 'Tfile.in', Copy('$TARGET', '$SOURCE'))
""")

test.write('Tfile.in', "Tfile.in\n")

expect_stdout = test.wrap_stdout("""\

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   '.'> and its children:
Taskmaster:        <no_state   0   'SConstruct'>
Taskmaster:        <no_state   0   'Tfile.in'>
Taskmaster:        <no_state   0   'Tfile.mid'>
Taskmaster:        <no_state   0   'Tfile.out'>
Taskmaster:      adjusted ref count: <pending    1   '.'>, child 'SConstruct'
Taskmaster:      adjusted ref count: <pending    2   '.'>, child 'Tfile.in'
Taskmaster:      adjusted ref count: <pending    3   '.'>, child 'Tfile.mid'
Taskmaster:      adjusted ref count: <pending    4   '.'>, child 'Tfile.out'
Taskmaster:     Considering node <no_state   0   'SConstruct'> and its children:
Taskmaster: Evaluating <pending    0   'SConstruct'>

Task.make_ready_current(): node <pending    0   'SConstruct'>
Task.prepare():      node <up_to_date 0   'SConstruct'>
Task.executed_with_callbacks(): node <up_to_date 0   'SConstruct'>
Task.postprocess():  node <up_to_date 0   'SConstruct'>
Task.postprocess():  removing <up_to_date 0   'SConstruct'>
Task.postprocess():  adjusted parent ref count <pending    3   '.'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   'Tfile.in'> and its children:
Taskmaster: Evaluating <pending    0   'Tfile.in'>

Task.make_ready_current(): node <pending    0   'Tfile.in'>
Task.prepare():      node <up_to_date 0   'Tfile.in'>
Task.executed_with_callbacks(): node <up_to_date 0   'Tfile.in'>
Task.postprocess():  node <up_to_date 0   'Tfile.in'>
Task.postprocess():  removing <up_to_date 0   'Tfile.in'>
Task.postprocess():  adjusted parent ref count <pending    2   '.'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   'Tfile.mid'> and its children:
Taskmaster:        <up_to_date 0   'Tfile.in'>
Taskmaster: Evaluating <pending    0   'Tfile.mid'>

Task.make_ready_current(): node <pending    0   'Tfile.mid'>
Task.prepare():      node <executing  0   'Tfile.mid'>
Task.execute():      node <executing  0   'Tfile.mid'>
Copy("Tfile.mid", "Tfile.in")
Task.executed_with_callbacks(): node <executing  0   'Tfile.mid'>
Task.postprocess():  node <executed   0   'Tfile.mid'>
Task.postprocess():  removing <executed   0   'Tfile.mid'>
Task.postprocess():  adjusted parent ref count <pending    1   '.'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   'Tfile.out'> and its children:
Taskmaster:        <executed   0   'Tfile.mid'>
Taskmaster: Evaluating <pending    0   'Tfile.out'>

Task.make_ready_current(): node <pending    0   'Tfile.out'>
Task.prepare():      node <executing  0   'Tfile.out'>
Task.execute():      node <executing  0   'Tfile.out'>
Copy("Tfile.out", "Tfile.mid")
Task.executed_with_callbacks(): node <executing  0   'Tfile.out'>
Task.postprocess():  node <executed   0   'Tfile.out'>
Task.postprocess():  removing <executed   0   'Tfile.out'>
Task.postprocess():  adjusted parent ref count <pending    0   '.'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <pending    0   '.'> and its children:
Taskmaster:        <up_to_date 0   'SConstruct'>
Taskmaster:        <up_to_date 0   'Tfile.in'>
Taskmaster:        <executed   0   'Tfile.mid'>
Taskmaster:        <executed   0   'Tfile.out'>
Taskmaster: Evaluating <pending    0   '.'>

Task.make_ready_current(): node <pending    0   '.'>
Task.prepare():      node <executing  0   '.'>
Task.execute():      node <executing  0   '.'>
Task.executed_with_callbacks(): node <executing  0   '.'>
Task.postprocess():  node <executed   0   '.'>

Taskmaster: Looking for a node to evaluate
Taskmaster: No candidate anymore.

""")

test.run(arguments='--taskmastertrace=- .', stdout=expect_stdout)

test.run(arguments='-c .')

expect_stdout = test.wrap_stdout("""\
Copy("Tfile.mid", "Tfile.in")
Copy("Tfile.out", "Tfile.mid")
""")

test.run(arguments='--taskmastertrace=trace.out .', stdout=expect_stdout)

expect_trace = """\

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   '.'> and its children:
Taskmaster:        <no_state   0   'SConstruct'>
Taskmaster:        <no_state   0   'Tfile.in'>
Taskmaster:        <no_state   0   'Tfile.mid'>
Taskmaster:        <no_state   0   'Tfile.out'>
Taskmaster:      adjusted ref count: <pending    1   '.'>, child 'SConstruct'
Taskmaster:      adjusted ref count: <pending    2   '.'>, child 'Tfile.in'
Taskmaster:      adjusted ref count: <pending    3   '.'>, child 'Tfile.mid'
Taskmaster:      adjusted ref count: <pending    4   '.'>, child 'Tfile.out'
Taskmaster:     Considering node <no_state   0   'SConstruct'> and its children:
Taskmaster: Evaluating <pending    0   'SConstruct'>

Task.make_ready_current(): node <pending    0   'SConstruct'>
Task.prepare():      node <up_to_date 0   'SConstruct'>
Task.executed_with_callbacks(): node <up_to_date 0   'SConstruct'>
Task.postprocess():  node <up_to_date 0   'SConstruct'>
Task.postprocess():  removing <up_to_date 0   'SConstruct'>
Task.postprocess():  adjusted parent ref count <pending    3   '.'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   'Tfile.in'> and its children:
Taskmaster: Evaluating <pending    0   'Tfile.in'>

Task.make_ready_current(): node <pending    0   'Tfile.in'>
Task.prepare():      node <up_to_date 0   'Tfile.in'>
Task.executed_with_callbacks(): node <up_to_date 0   'Tfile.in'>
Task.postprocess():  node <up_to_date 0   'Tfile.in'>
Task.postprocess():  removing <up_to_date 0   'Tfile.in'>
Task.postprocess():  adjusted parent ref count <pending    2   '.'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   'Tfile.mid'> and its children:
Taskmaster:        <up_to_date 0   'Tfile.in'>
Taskmaster: Evaluating <pending    0   'Tfile.mid'>

Task.make_ready_current(): node <pending    0   'Tfile.mid'>
Task.prepare():      node <executing  0   'Tfile.mid'>
Task.execute():      node <executing  0   'Tfile.mid'>
Task.executed_with_callbacks(): node <executing  0   'Tfile.mid'>
Task.postprocess():  node <executed   0   'Tfile.mid'>
Task.postprocess():  removing <executed   0   'Tfile.mid'>
Task.postprocess():  adjusted parent ref count <pending    1   '.'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   'Tfile.out'> and its children:
Taskmaster:        <executed   0   'Tfile.mid'>
Taskmaster: Evaluating <pending    0   'Tfile.out'>

Task.make_ready_current(): node <pending    0   'Tfile.out'>
Task.prepare():      node <executing  0   'Tfile.out'>
Task.execute():      node <executing  0   'Tfile.out'>
Task.executed_with_callbacks(): node <executing  0   'Tfile.out'>
Task.postprocess():  node <executed   0   'Tfile.out'>
Task.postprocess():  removing <executed   0   'Tfile.out'>
Task.postprocess():  adjusted parent ref count <pending    0   '.'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <pending    0   '.'> and its children:
Taskmaster:        <up_to_date 0   'SConstruct'>
Taskmaster:        <up_to_date 0   'Tfile.in'>
Taskmaster:        <executed   0   'Tfile.mid'>
Taskmaster:        <executed   0   'Tfile.out'>
Taskmaster: Evaluating <pending    0   '.'>

Task.make_ready_current(): node <pending    0   '.'>
Task.prepare():      node <executing  0   '.'>
Task.execute():      node <executing  0   '.'>
Task.executed_with_callbacks(): node <executing  0   '.'>
Task.postprocess():  node <executed   0   '.'>

Taskmaster: Looking for a node to evaluate
Taskmaster: No candidate anymore.

"""

test.must_match('trace.out', expect_trace, mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
