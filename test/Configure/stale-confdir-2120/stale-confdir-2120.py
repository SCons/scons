#!/usr/bin/env python

# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""
Verify that Configure checks still work after the configure directory
has been removed but the sconsign file has not (issue #2120).
"""

import shutil

import TestSCons

_obj = TestSCons._obj

test = TestSCons.TestSCons()

NCR = test.NCR  # non-cached rebuild
CR = test.CR  # cached rebuild

test.file_fixture(["fixture", "SConstruct"])

test.run()
test.checkLogAndStdout(
    ["Checking for C header file stdio.h... "],
    ["yes"],
    [[((".c", NCR), (_obj, NCR))]],
    "config.log",
    ".sconf_temp",
    "SConstruct",
)

# Remove the configure directory but keep the sconsign file. The stale
# sconsign entries must not make the check appear up to date.
shutil.rmtree(test.workpath('.sconf_temp'))

test.run()
test.checkLogAndStdout(
    ["Checking for C header file stdio.h... "],
    ["yes"],
    [[((".c", NCR), (_obj, NCR))]],
    "config.log",
    ".sconf_temp",
    "SConstruct",
)

# Forced cache mode deliberately reuses stored results even when the
# configure directory is missing.
shutil.rmtree(test.workpath('.sconf_temp'))

test.run(arguments='--config=cache')
test.checkLogAndStdout(
    ["Checking for C header file stdio.h... "],
    ["yes"],
    [[((".c", CR), (_obj, CR))]],
    "config.log",
    ".sconf_temp",
    "SConstruct",
)

test.pass_test()
