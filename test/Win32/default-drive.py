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

"""
This test verifies (on Windows systems) that specifying an
absolute path name without a drive letter uses the SConstruct
file's drive as the default.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import sys

import TestSCons

test = TestSCons.TestSCons()

if sys.platform != 'win32':
    msg = "Skipping drive-letter test on non-Windows platform '%s'\n" % sys.platform
    test.skip_test(msg)

test.subdir('src')

test.write(['src', 'SConstruct'], """
def cat(env, source, target):
    target = str(target[0])
    with open(target, "wb") as ofp:
        for src in source:
            with open(str(src), "rb") as ifp:
                ofp.write(ifp.read())

env = Environment(BUILDERS={'Build':Builder(action=cat)})
env.Build('../build/file.out', 'file.in')
""")

test.write(['src', 'file.in'], "src/file.in\n")

build_file_out = test.workpath('build', 'file.out')

print(os.path.splitdrive(build_file_out)[1])
test.run(chdir = 'src',
         arguments = os.path.splitdrive(build_file_out)[1])

test.must_match(['build', 'file.out'], "src/file.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
