#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""
A failure while copying a file out of the cache must not leave a truncated
target behind.  The retrieve is treated as a miss and the target is built.
"""

import glob

import TestSCons

test = TestSCons.TestSCons()

test.file_fixture(["retrieve-error-fixture", "SConstruct"])
test.write('in', 'in\n')

# Prime the cache with a good copy of the target.
test.run()
test.must_match('out', 'initial=\n', mode='r')

# Make the next read from the cache fail after writing a partial file.
test.write('fail_next', '')
test.unlink('out')
test.run()
# The action must not have seen the partial file left by the failed copy.
test.must_match('out', 'initial=\n', mode='r')
test.fail_test(
    bool(glob.glob(test.workpath('.scons-cache-*'))),
    message="a temporary file from the failed cache retrieve was left behind",
)

# The cache entry itself is still usable: a later build retrieves normally.
test.unlink('fail_next')
test.unlink('out')
test.run()
test.must_match('out', 'initial=\n', mode='r')
test.must_contain_all_lines(test.stdout(), ["Retrieved `out' from cache"])

# A KeyboardInterrupt during the copy must abort the build but must not
# leave the partial copy behind in the build directory.
test.write('interrupt_next', '')
test.unlink('out')
test.run(status=2)
test.must_not_exist('out')
test.fail_test(
    bool(glob.glob(test.workpath('.scons-cache-*'))),
    message="a temporary file from the interrupted cache retrieve was left behind",
)

# The cache entry survives the abort and is still usable.
test.unlink('interrupt_next')
test.run()
test.must_match('out', 'initial=\n', mode='r')

test.pass_test()
