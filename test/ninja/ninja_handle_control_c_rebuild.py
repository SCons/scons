#!/usr/bin/env python
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
#
"""
This test ensures if ninja gets a control-c (or other interrupting signal) while
regenerating the build.ninja, it doesn't remove the build.ninja leaving it 
in an unworkable state.
"""
import os

import TestSCons
from TestCmd import IS_WINDOWS

test = TestSCons.TestSCons()

try:
    import ninja
except ImportError:
    test.skip_test("Could not find module in python")

_python_ = TestSCons._python_
_exe = TestSCons._exe

ninja_bin = os.path.abspath(
    os.path.join(ninja.__file__, os.pardir, "data", "bin", "ninja" + _exe)
)

test.dir_fixture("ninja-fixture")

test.file_fixture("ninja_test_sconscripts/sconstruct_generate_and_build", "SConstruct")

# generate simple build
test.run(stdout=None)
test.must_contain_all_lines(test.stdout(), ["Generating: build.ninja"])
test.must_contain_all(test.stdout(), "Executing:")
test.must_contain_all(test.stdout(), "ninja%(_exe)s -f" % locals())
test.run(program=test.workpath("foo" + _exe), stdout="foo.c")

# Change the SConstruct
test.file_fixture("ninja_test_sconscripts/sconstruct_control_c_ninja", "SConstruct")

# run ninja independently
program = test.workpath("run_ninja_env.bat") if IS_WINDOWS else ninja_bin
if IS_WINDOWS:
    test.fail_test(
        condition=(test.status in [1, 2]),
        message="Expected exit status to be 1 or 2 was actually:%d" % test.status,
    )
else:
    test.fail_test(
        condition=(test.status == 1),
        message="Expected exit status to be 1 was actually:%d" % test.status,
    )

test.run(program=program, stdout=None, stderr=None, status=None)

if not IS_WINDOWS:
    error_msg = "ninja: error: rebuilding 'build.ninja': interrupted by user"
    test.must_contain_all(test.stderr(), error_msg)

# Verify that Rebuilding build.ninja and sending control-c to ninja doesn't remove build.ninja
test.must_exist("build.ninja")
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
