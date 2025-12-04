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

r"""
Check that incremental builds work in interactive mode.

On Windows, there was a code path where cleaning, then rebuilding
would lead the the source file not being supplied to the build:

  scons: Building targets
  cl /Fosrc\myunit.obj /c /TP /nologo /EHsc /Iinclude
  cl : Command line error D8003 : missing source filename

This is described in detail in GH issue 3039.

This is a live test - depends on running a real compiler.
It could actually skip if not on Windows as the problem has not
been observed there.
"""

import os

import TestSCons

test = TestSCons.TestSCons()
lib = f'{TestSCons.lib_}mylib{TestSCons._lib}'
test.dir_fixture('fixture/issue3029')
# file: fixture/issue3029/SConstruct
test.run(arguments='-Q mylib', stdout=None)
test.must_exist(lib)

scons = test.start(arguments='-Q --interactive')
scons.send("clean mylib\n")
scons.send("build 1\n")
test.wait_for(test.workpath('1'), popen=scons)
test.must_not_exist(test.workpath(lib))
scons.send("build mylib\n")
scons.send("build 2\n")
test.wait_for(test.workpath('2'), popen=scons)
test.must_exist(test.workpath(lib))

test.pass_test()
