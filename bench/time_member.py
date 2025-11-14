#!/usr/bin/python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation
#

"""
Benchmark for the switch from "foo.find('key') == -1" and similar
to using the membership operators "in" and "not in".
This is currently a standalone test, not integrated into the bench/
mechanism for running such tests.

The operators are quite a bit faster, around 4x.
"""

import timeit

# Sample string and substring to test
sample_string = "This is a sample string for testing."
substring = "sample"
missingstring = "badger"

def test_in_operator() -> bool:
    return substring in sample_string

def test_not_in_operator() -> bool:
    return missingstring not in sample_string

def test_find_method() -> bool:
    return sample_string.find(substring) != -1

def test_no_find_method() -> bool:
    return sample_string.find(missingstring) == -1

# Time the "in" membership test
time_in = timeit.timeit(test_in_operator, number=10000000)
time_not_in = timeit.timeit(test_not_in_operator, number=10000000)

# Time the "find" method membership test
time_find = timeit.timeit(test_find_method, number=10000000)
time_no_find = timeit.timeit(test_no_find_method, number=10000000)

# Print the results
print(f'"in" operator time: {time_in:.6f} seconds')
print(f'.find() method time: {time_find:.6f} seconds')
print(f'"not in" operator time: {time_not_in:.6f} seconds')
print(f'.find() method time: {time_no_find:.6f} seconds')

