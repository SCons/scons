#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""
Verify Configure paths with a duplicate=False VariantDir.

Regression test for issue #2096.  Configure() is called from a SConscript
being read through a duplicate=False VariantDir.  The configure directory
and log file must be created in the variant directory, not next to the
SConscript in the source tree.

Before the fix, SConf used str() on the confdir and logfile nodes.
With duplicate=False, str() can return a source-relative path, while the
operating system's working directory may still be the source directory
because the variant directory has not been materialized yet.  The result
was a source-tree confdir and config.log.
"""

import TestSCons

test = TestSCons.TestSCons()

test.file_fixture(['fixture', 'SConstruct-2096'], 'SConstruct')
test.file_fixture(['fixture', 'SConscript-2096'], 'SConscript')

test.run()

# The configuration directory, log, and header belong in the variant dir.
test.must_exist(test.workpath('build', 'sconf'))
test.must_exist(test.workpath('build', 'config.log'))
test.must_exist(test.workpath('build', 'config.h'))

# Nothing should have leaked into the source directory.
test.must_not_exist(test.workpath('sconf'))
test.must_not_exist(test.workpath('config.log'))
test.must_not_exist(test.workpath('config.h'))

test.pass_test()
