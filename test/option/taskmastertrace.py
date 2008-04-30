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
env = Environment()

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
Taskmaster:      adjusting ref count: <pending    1   '.'>
Taskmaster:      adjusting ref count: <pending    2   '.'>
Taskmaster:      adjusting ref count: <pending    3   '.'>
Taskmaster:      adjusting ref count: <pending    4   '.'>
Taskmaster:     Considering node <no_state   0   'SConstruct'> and its children:
Taskmaster: Evaluating <pending    0   'SConstruct'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   'Tfile.in'> and its children:
Taskmaster: Evaluating <pending    0   'Tfile.in'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   'Tfile.mid'> and its children:
Taskmaster:        <up_to_date 0   'Tfile.in'>
Taskmaster: Evaluating <pending    0   'Tfile.mid'>
Copy("Tfile.mid", "Tfile.in")

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   'Tfile.out'> and its children:
Taskmaster:        <executed   0   'Tfile.mid'>
Taskmaster: Evaluating <pending    0   'Tfile.out'>
Copy("Tfile.out", "Tfile.mid")

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <pending    0   '.'> and its children:
Taskmaster:        <up_to_date 0   'SConstruct'>
Taskmaster:        <up_to_date 0   'Tfile.in'>
Taskmaster:        <executed   0   'Tfile.mid'>
Taskmaster:        <executed   0   'Tfile.out'>
Taskmaster: Evaluating <pending    0   '.'>

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
Taskmaster:      adjusting ref count: <pending    1   '.'>
Taskmaster:      adjusting ref count: <pending    2   '.'>
Taskmaster:      adjusting ref count: <pending    3   '.'>
Taskmaster:      adjusting ref count: <pending    4   '.'>
Taskmaster:     Considering node <no_state   0   'SConstruct'> and its children:
Taskmaster: Evaluating <pending    0   'SConstruct'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   'Tfile.in'> and its children:
Taskmaster: Evaluating <pending    0   'Tfile.in'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   'Tfile.mid'> and its children:
Taskmaster:        <up_to_date 0   'Tfile.in'>
Taskmaster: Evaluating <pending    0   'Tfile.mid'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <no_state   0   'Tfile.out'> and its children:
Taskmaster:        <executed   0   'Tfile.mid'>
Taskmaster: Evaluating <pending    0   'Tfile.out'>

Taskmaster: Looking for a node to evaluate
Taskmaster:     Considering node <pending    0   '.'> and its children:
Taskmaster:        <up_to_date 0   'SConstruct'>
Taskmaster:        <up_to_date 0   'Tfile.in'>
Taskmaster:        <executed   0   'Tfile.mid'>
Taskmaster:        <executed   0   'Tfile.out'>
Taskmaster: Evaluating <pending    0   '.'>

Taskmaster: Looking for a node to evaluate
Taskmaster: No candidate anymore.

"""

test.must_match('trace.out', expect_trace)

test.pass_test()
