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
Test that SharedLibrary() updates when a different lib is linked,
even if it has the same md5.
This is https://github.com/SCons/scons/issues/2903
"""

import sys
import sysconfig

import TestSCons

test = TestSCons.TestSCons()

test.dir_fixture( "bug2903" )

# Build the sub-libs (don't care about details of this)
test.run(arguments='-f SConstruct-libs')

# This should build the main lib, using libfoo.so
test.run(arguments='libname=foo')
# This should rebuild the main lib, using libbar.so;
# it should NOT say it's already up to date.
test.run(arguments='libname=bar')
test.must_not_contain_any_line(test.stdout(), ["is up to date"])
# Try it again, in reverse, to make sure:
test.run(arguments='libname=foo')
test.must_not_contain_any_line(test.stdout(), ["is up to date"])

# Now try changing the link command line (in an innocuous way); should rebuild.
if sys.platform == 'win32' and not sysconfig.get_platform() in ("mingw",):
    extraflags='shlinkflags=/DEBUG'
else:
    extraflags='shlinkflags=-g'

test.run(arguments=['libname=foo', extraflags])
test.must_not_contain_any_line(test.stdout(), ["is up to date"])
test.run(arguments=['libname=foo', extraflags, '--debug=explain'])
test.must_contain_all_lines(test.stdout(), ["is up to date"])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
