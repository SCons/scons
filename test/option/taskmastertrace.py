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
test.file_fixture('fixture/taskmaster_expected_new_parallel.txt', 'taskmaster_expected_new_parallel.txt')

test.write('Tfile.in', "Tfile.in\n")

expect_stdout = test.wrap_stdout(test.read('taskmaster_expected_stdout_1.txt', mode='r'))

test.run(arguments='--taskmastertrace=- .', stdout=expect_stdout)

test.run(arguments='-c .')

expect_stdout = test.wrap_stdout("""\
Copy("Tfile.mid", "Tfile.in")
Copy("Tfile.out", "Tfile.mid")
""")

test.run(arguments='--taskmastertrace=trace.out .', stdout=expect_stdout)
test.must_match_file('trace.out', 'taskmaster_expected_file_1.txt', mode='r')

# Test NewParallel Job implementation
test.run(arguments='-j 2 --experimental=tm_v2 --taskmastertrace=new_parallel_trace.out .')

new_trace = test.read('new_parallel_trace.out', mode='r')
thread_id = re.compile(r'\[Thread:\d+\]')
new_trace=thread_id.sub('[Thread:XXXXX]', new_trace)
test.must_match('taskmaster_expected_new_parallel.txt', new_trace,  mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
