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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import re

_python_ = TestSCons._python_

def setup_fixtures():
    test.file_fixture('../fixture/test_main.c', 'main.c')
    test.file_fixture('../fixture/SConstruct_test_main.py', 'SConstruct')

def test_help_function():
    # Before anything else, make sure we get valid --debug=action-timestamps results
    # when just running the help option.
    test.run(arguments = "-h --debug=action-timestamps")
    
def build():
    # Execute build
    test.run(arguments='--debug=action-timestamps')
    build_output = test.stdout()
    return build_output

def get_matches_from_output(build_output):
    return [re.findall(pattern, build_output) for pattern in debug_time_patterns]

def test_presence_of_debug_time_strings(build_output):
    # Check presence of duration and timestamps
    if None in get_matches_from_output(build_output):
        print("One or more of the time debug strings were not found in the build output")
        test.fail_test(1)

def test_equal_number_of_debug_time_strings(build_output):
    matches = get_matches_from_output(build_output)
    num_of_matches = [len(match) for match in matches]

    # Check that the number of matches for each pattern is the same
    if num_of_matches.count(num_of_matches[0]) != len(num_of_matches):
        print("Debug time strings differs in quantity")
        test.fail_test(2)

def test_correctness_of_timestamps(build_output):
    # Check if difference between timestamps is equal to duration
    matches = get_matches_from_output(build_output)

    def match_to_float(m): 
        return float(m[1][1])

    execution_time = match_to_float(matches[0])
    start_time = match_to_float(matches[1])
    stop_time = match_to_float(matches[2])
    delta_time = stop_time - start_time

    def within_tolerance(expected, actual, tolerance):
        return abs((expected-actual)/actual) <= tolerance

    if not within_tolerance(execution_time, delta_time, 0.001):
        print("Difference of timestamps differ from action duration")
        print("Execution time = {}. Start time = {}. Stop time = {}. Delta time = {}".format(execution_time, start_time, stop_time, delta_time))
        test.fail_test(3)

debug_time_patterns = [
    r'Command execution time: (.*): (\d+\.\d+) seconds',
    r'Command execution start timestamp: (.*): (\d+\.\d+)',
    r'Command execution end timestamp: (.*): (\d+\.\d+)'
]

test = TestSCons.TestSCons()
setup_fixtures()

test_help_function()

build_output = build()
test_presence_of_debug_time_strings(build_output)
test_equal_number_of_debug_time_strings(build_output)
test_correctness_of_timestamps(build_output)

test.pass_test()
