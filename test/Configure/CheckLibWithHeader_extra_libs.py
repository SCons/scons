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
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

"""
Verify that a program which depends on library which in turn depends
on another library can be built correctly using CheckLibWithHeader

This is a "live" test - requires a configured C compiler/toolchain to run.
"""

from TestSCons import TestSCons, dll_, _dll

test = TestSCons(match=TestSCons.match_re_dotall)
test.dir_fixture(['fixture', 'checklib_extra'])

libA = f"libA/{dll_}A{_dll}"
libB = f"libB/{dll_}B{_dll}"

test.run(arguments='-C libA')
test.must_exist(libA)
test.run(arguments='-C libB')
test.must_exist(libB)

test.run()

test.pass_test()
