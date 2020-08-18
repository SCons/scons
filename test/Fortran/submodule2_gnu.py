#!/usr/bin/env python
#
# __COPYRIGHT__
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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import TestSCons
import subprocess
import re

_python_ = TestSCons._python_

test = TestSCons.TestSCons()
_exe = TestSCons._exe


gfortran = test.detect_tool('gfortran',ENV=os.environ)
if not gfortran:
    test.skip_test("could not find gnu fortran compiler, skipping test . . .\n")
version=subprocess.run(['gfortran','-v'], stderr=subprocess.PIPE).stderr.decode('utf-8')
v=(re.findall("gcc version (\d)\.(\d)\.(\d)",version))[0]
if (int(v[0])<8):
    test.skip_test("current gfortran version ({}.{}.{}) less than required gfortran release level (\"8\"), skipping test . . .\n".format(v[0],v[1],v[2]))

# proceed

test.file_fixture(os.path.join('SubmoduleFiles','ATestSubmod2.F90'))
test.file_fixture(os.path.join('SubmoduleFiles','BTestSubmod.F90'))
test.file_fixture(os.path.join('SubmoduleFiles','TestMod.F90'))
test.file_fixture(os.path.join('SubmoduleFiles','submod_driver.F90'))
test.file_fixture(os.path.join('SubmoduleFiles','SConstruct_intel'),'SConstruct')

test.run(arguments = _exe, stderr = None)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
