#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

"""
Simple tests of the --taskmastertrace= option.
"""
import os
import re

import TestSCons

test = TestSCons.TestSCons()

test.file_fixture('fixture/SConstruct__taskmastertrace', 'SConstruct')
test.file_fixture('fixture/taskmaster_expected_stdout_1.txt', 'taskmaster_expected_stdout_1.txt')
test.file_fixture('fixture/taskmaster_expected_file_1.txt', 'taskmaster_expected_file_1.txt')
test.file_fixture('fixture/taskmaster_expected_parallel.txt', 'taskmaster_expected_parallel.txt')

test.write('Tfile.in', "Tfile.in\n")

thread_id = re.compile(r'\[Thread:\d+\]')

def without_thread_ids(text):
    return thread_id.sub('[Thread:XXXXX]', text)

expect_stdout = test.wrap_stdout(test.read('taskmaster_expected_stdout_1.txt', mode='r'))

test.run(arguments='--taskmastertrace=- .', stdout=expect_stdout,
         match=lambda actual, expected: test.match(without_thread_ids(actual), expected))

test.run(arguments='-c .')

expect_stdout = test.wrap_stdout("""\
Copy("Tfile.mid", "Tfile.in")
Copy("Tfile.out", "Tfile.mid")
""")

# Test Serial Job implementation
test.run(arguments='--taskmastertrace=trace.out .', stdout=expect_stdout)
trace = without_thread_ids(test.read('trace.out', mode='r'))
test.must_match('taskmaster_expected_file_1.txt', trace, mode='r')

# Test Parallel Job implementation
test.run(arguments='-j 2 --taskmastertrace=parallel_trace.out .')
trace = without_thread_ids(test.read('parallel_trace.out', mode='r'))
test.must_match('taskmaster_expected_parallel.txt', trace, mode='r')

test.pass_test()
