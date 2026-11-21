#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""
Verify that Configure checks in a variant directory still work after
the variant directory has been removed but the sconsign file has not
(issue #2430).
"""

import os
import shutil

import TestSCons

_obj = TestSCons._obj

test = TestSCons.TestSCons(match=TestSCons.match_re_dotall)

NCR = test.NCR  # non-cached rebuild
NCF = test.NCF  # non-cached build failure

test.dir_fixture('fixture')

expected_checks = [
    "Checking for C header file math.h... ",
    "Checking for C header file no_std_c_header.h... ",
]
expected_results = ["yes", "no"]
config_log = os.path.join("build", "config.log")
conf_dir = os.path.join("build", "config.tests")

test.run()
test.checkLogAndStdout(
    expected_checks,
    expected_results,
    [
        [((".c", NCR), (_obj, NCR))],
        [((".c", NCR), (_obj, NCF))],
    ],
    config_log,
    conf_dir,
    "SConstruct",
)

# Remove the variant directory (including the configure dir) but keep the
# sconsign file. The stale sconsign entries must not be treated as if the
# configure tests were still up to date.
shutil.rmtree(test.workpath('build'))

test.run()
test.checkLogAndStdout(
    expected_checks,
    expected_results,
    [
        [((".c", NCR), (_obj, NCR))],
        [((".c", NCR), (_obj, NCF))],
    ],
    config_log,
    conf_dir,
    "SConstruct",
)

test.pass_test()
