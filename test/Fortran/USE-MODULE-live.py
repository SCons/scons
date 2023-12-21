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
Test Fortran module use, organized in such a way that
module files will be "not found" unless dependencies have been forced.
See PR #4452.

This is a "live" test - uses an actual Fortran compiler, as the
mock compiler would need to have a sophisticated regex to catch
the situation. Possibly we could convert later if the mock fortran.py
gets smarter.
"""

import TestSCons

_python_ = TestSCons._python_
_exe = TestSCons._exe

test = TestSCons.TestSCons()
if not test.where_is('gfortran'):
    test.skip_test("Could not find 'gfortran', skipping test.\n")

test.file_fixture(['fixture-mod', 'SConstruct'])
test.file_fixture(['fixture-mod', 'main.f90'], dstfile=['src', 'main.f90'])
test.file_fixture(
    ['fixture-mod', 'module0.f90'],
    dstfile=['src', 'module0.f90'],
)
test.file_fixture(
    ['fixture-mod', 'module1.f90'],
    dstfile=['src', 'module1.f90'],
)
test.file_fixture(
    ['fixture-mod', 'module2.f90'],
    dstfile=['src', 'module2.f90'],
)
test.file_fixture(
    ['fixture-mod', 'util_module.f90'],
    dstfile=['src', 'utils', 'util_module.f90'],
)
test.run(arguments='.', stderr=None)
test.must_exist(["fortran_mods", "module0.mod"])
test.must_exist(["fortran_mods", "module1.mod"])
test.must_exist(["fortran_mods", "module2.mod"])
test.must_exist(["fortran_mods", "util_module.mod"])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
