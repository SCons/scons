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
Verify that we have proper Copyright notices on all the right files
in our distributions.

Note that this is a packaging test, not a functional test, so the
name of this script doesn't end in *Tests.py.
"""

import os
import os.path
import re
import string

import TestSCons

test = TestSCons.TestSCons()

try:
    cwd = os.environ['SCONS_CWD']
except KeyError:
    cwd = os.getcwd()

build_scons = os.path.join(cwd, 'build', 'scons')
build_local = os.path.join(cwd, 'build', 'scons-local', 'scons-local-0.96.92')
build_src = os.path.join(cwd, 'build', 'scons-src')

class Collect:
    expression = re.compile('Copyright.*The SCons Foundation')
    def __init__(self, directory, remove_list):
        self.copyright = []
        self.no_copyright = []
        self.remove = {}
        for r in remove_list:
            self.remove[os.path.join(directory, r)] = 1

def visit(collect, dirname, names):
    make_path_tuple = lambda n, d=dirname: (n, os.path.join(d, n))
    for name, path in map(make_path_tuple, names):
        if collect.remove.get(path):
            names.remove(name)
        elif os.path.isfile(path):
            if collect.expression.search(open(path, 'r').read()):
                collect.copyright.append(path)
            else:
                collect.no_copyright.append(path)

# Map each directory to search (dictionary keys) to a list of its
# subsidiary files and directories to exclude from copyright checks.
check = {
    build_scons : [
        'build',
        'dist',
        'engine/SCons/Conftest.py',
        'engine/SCons/dblite.py',
        'engine/SCons/Optik',
        'MANIFEST',
        'os_spawnv_fix.diff',
        'setup.cfg',
    ],
    build_local : [
        'SCons/Conftest.py',
        'SCons/dblite.py',
        'SCons/Optik',
    ],
    build_src : [
        'bin',
        'config',
        'debian',
        'doc/design',
        'doc/MANIFEST',
        'doc/python10',
        'doc/reference',
        'doc/man/MANIFEST',
        'doc/user/cons.pl',
        'doc/user/MANIFEST',
        'doc/user/SCons-win32-install-1.jpg',
        'doc/user/SCons-win32-install-2.jpg',
        'doc/user/SCons-win32-install-3.jpg',
        'doc/user/SCons-win32-install-4.jpg',
        'gentoo',
        'QMTest/classes.qmc',
        'QMTest/configuration',
        'QMTest/TestCmd.py',
        'QMTest/TestCommon.py',
        'QMTest/unittest.py',
        'src/os_spawnv_fix.diff',
        'src/MANIFEST.in',
        'src/setup.cfg',
        'src/engine/MANIFEST.in',
        'src/engine/MANIFEST-xml.in',
        'src/engine/setup.cfg',
        'src/engine/SCons/Conftest.py',
        'src/engine/SCons/dblite.py',
        'src/engine/SCons/Optik',
        'src/script/MANIFEST.in',
        'src/script/setup.cfg',
    ],
}

no_copyright = []
no_result = []

for directory, remove_list in check.items():
    if os.path.exists(directory):
        c = Collect(directory, remove_list)
        os.path.walk(directory, visit, c)
        no_copyright.extend(c.no_copyright)
    else:
        no_result.append(directory)

if no_copyright:
    print "Found the following files with no copyrights:"
    print "\t" + string.join(no_copyright, "\n\t")
    test.fail_test(1)

if no_result:
    print "Cannot check copyrights, the following have apparently not been built:"
    print "\t" + string.join(no_result, "\n\t")
    test.no_result(1)

test.pass_test()
