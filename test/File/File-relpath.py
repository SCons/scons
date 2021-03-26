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
Test that .relpath works on file nodes.
Specifically ${TARGET.relpath}, ${SOURCE.relpath} match expected path
"""

import os

import TestSCons
from TestCmd import IS_WINDOWS

test = TestSCons.TestSCons()

test.subdir("src", ["src", "dir"])

test.dir_fixture("fixture/relpath")

expected = [
    # expanding variable, expected string
    ("${TARGETS.relpath}", "../foo/dir build/file1"),
    (
        "${TARGETS.abspath}",
        "%s %s"
        % (os.path.abspath("base/../foo/dir"), os.path.abspath("base/build/file1")),
    ),
    ("${SOURCES.relpath}", "src/file"),
    ("${SOURCES.abspath}", os.path.abspath("base/src/file")),
    ("${SOURCE.relpath}", "src/file"),
    ("${SOURCE.abspath}", os.path.abspath("base/src/file")),
]

expected_stdout = "\n".join(["%s=%s" % (s, o) for s, o in expected])
expected_stdout += "\nscons: `.' is up to date."

if IS_WINDOWS:
    expected_stdout = expected_stdout.replace("/", os.sep)

test.run("-Q", chdir="base", status=0, stdout=expected_stdout + "\n")
