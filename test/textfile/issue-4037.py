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
Test for GH Issue 4037

The fix for #4031 created a code path where the subst function
used by textfile was called with SUBST_RAW, which, if the items to
subst was a callable, caused it to be called with for_signature=True.
This did not happen previously as the test was "!= SUBST_CMD",
and the mode coming in was indeed SUBST_CMD.
"""

import TestSCons

test = TestSCons.TestSCons()

match_mode = 'r'

test.file_fixture('fixture/SConstruct.issue-4037', 'SConstruct')

test.run(arguments='.')

test.must_match(
    'target.txt',
    "val",
    mode=match_mode,
)

test.pass_test()
