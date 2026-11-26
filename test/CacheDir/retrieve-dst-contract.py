#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""
A custom CACHEDIR_CLASS overrides copy_from_cache(). The destination it is
given must not exist yet and must keep the target's basename, as it did before
cache retrieval started staging through a temporary directory.
"""

import glob

import TestSCons

test = TestSCons.TestSCons()

test.file_fixture(["retrieve-dst-contract-fixture", "SConstruct"])
test.write('in', 'in\n')

test.run()
test.must_match('out', 'in\n', mode='r')

test.unlink('out')
test.run()
test.must_match('out', 'in\n', mode='r')
test.must_contain_all_lines(test.stdout(), ["Retrieved `out' from cache"])
test.must_not_contain_any_line(test.stdout(), ["build out"])
test.fail_test(
    bool(glob.glob(test.workpath('.scons-cache-*'))),
    message="temporary directory from the cache retrieve was left behind",
)

test.pass_test()
