#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""
Check that interactive mode sees source changes in a duplicate=True VariantDir.

GH issue 2425 reported that after an initial build, a later interactive
build did not pick up changes to a source file when a variant directory
was in use.  The original report suspected a Windows drive letter in the
variant directory path, but the problem is not path-specific: with the
default duplicate=True, the variant copy of the source retains a cached
"linked" marker between interactive builds, so the changed source is
never copied into the variant directory again.

The test also checks that a removed source file is handled cleanly and
that restoring it allows the build to recover.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

out = os.path.join('build', 'out.txt')
dup_in = os.path.join('build', 'in.txt')

test.dir_fixture(['fixture', 'issue2425'])
test.write('in.txt', "first\n")

scons = test.start(arguments='-Q --interactive')

scons.send("build\n")
scons.send("build 1\n")
test.wait_for(test.workpath('1'), popen=scons)
test.must_match(dup_in, "first\n")
test.must_match(out, "first\n")

test.write('in.txt', "second\n")

scons.send("build\n")
scons.send("build 2\n")
test.wait_for(test.workpath('2'), popen=scons)
test.must_match(dup_in, "second\n")
test.must_match(out, "second\n")

test.unlink('in.txt')

scons.send("build\n")
scons.send("build 3\n")
test.wait_for(test.workpath('3'), popen=scons)
test.must_not_exist(dup_in)

test.write('in.txt', "third\n")

scons.send("build\n")
scons.send("build 4\n")
test.wait_for(test.workpath('4'), popen=scons)
test.must_match(dup_in, "third\n")
test.must_match(out, "third\n")

test.finish(scons, stdout=None, stderr=None)
test.pass_test()
