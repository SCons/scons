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

import os
from timeit import default_timer as timer

import TestSCons
from TestCmd import IS_WINDOWS

test = TestSCons.TestSCons()

try:
    import ninja
except ImportError:
    test.skip_test("Could not find ninja module in python")

try:
    import psutil
except ImportError:
    test.skip_test("Could not find psutil module in python")


_python_ = TestSCons._python_
_exe = TestSCons._exe

ninja_bin = os.path.abspath(
    os.path.join(ninja.__file__, os.pardir, "data", "bin", "ninja" + _exe)
)

test.dir_fixture("ninja-fixture")

test.file_fixture(
    "ninja_test_sconscripts/sconstruct_force_scons_callback", "SConstruct"
)

test.run(stdout=None)
pid = None
test.must_exist(test.workpath('.ninja/scons_daemon_dirty'))
with open(test.workpath('.ninja/scons_daemon_dirty')) as f:
    pid = int(f.read())
    if pid not in [proc.pid for proc in psutil.process_iter()]:
        test.fail_test(message="daemon not running!")

program = test.workpath("run_ninja_env.bat") if IS_WINDOWS else ninja_bin
test.run(program=program, arguments='shutdown-ninja-scons-daemon', stdout=None)

wait_time = 10
start_time = timer()
while True:
    if wait_time > (timer() - start_time):
        if pid not in [proc.pid for proc in psutil.process_iter()]:
            break
    else:
        test.fail_test(message=f"daemon still not shutdown after {wait_time} seconds.")

test.must_not_exist(test.workpath('.ninja/scons_daemon_dirty'))
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
