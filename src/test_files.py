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

"""
Verify that we have certain important files in our distribution
packages.

Note that this is a packaging test, not a functional test, so the
name of this script doesn't end in *Tests.py.
"""

import os
import os.path
import re

import TestSCons

test = TestSCons.TestSCons()

try:
    cwd = os.environ['SCONS_CWD']
except KeyError:
    cwd = os.getcwd()

def build_path(*args):
    return os.path.join(cwd, 'build', *args)

build_scons_tar_gz  = build_path('unpack-tar-gz', 'scons-'+test.scons_version)
build_scons_zip     = build_path('unpack-zip', 'scons-'+test.scons_version)
build_local_tar_gz  = build_path('test-local-tar-gz')
build_local_zip     = build_path('test-local-zip')

scons_files = [
    'CHANGES.txt',
    'LICENSE.txt',
    'README.txt',
    'RELEASE.txt',
]

local_files = [
    'scons-LICENSE',
    'scons-README',
]

# Map each directory to search (dictionary keys) to a list of its
# subsidiary files and directories to exclude from copyright checks.
check = {
    build_scons_tar_gz  : scons_files,
    build_scons_zip     : scons_files,
    build_local_tar_gz  : local_files,
    build_local_zip     : local_files,
}

missing = []
no_result = []

for directory, check_list in check.items():
    if os.path.exists(directory):
        for c in check_list:
            f = os.path.join(directory, c)
            if not os.path.isfile(f):
                missing.append(f)
    else:
        no_result.append(directory)

if missing:
    print("Missing the following files:\n")
    print("\t" + "\n\t".join(missing))
    test.fail_test(1)

if no_result:
    print("Cannot check files, the following have apparently not been built:")
    print("\t" + "\n\t".join(no_result))
    test.no_result(1)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
