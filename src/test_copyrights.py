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

class Collect:
    expression = re.compile('Copyright.*The SCons Foundation')
    def __init__(self, remove_list):
        self.copyright = []
        self.no_copyright = []
        self.remove_list = remove_list

def visit(collect, dirname, names):
    for r in collect.remove_list:
        try:
            names.remove(r)
        except ValueError:
            pass
    for name in map(lambda n, d=dirname: os.path.join(d, n), names):
        if not os.path.isfile(name):
            continue
        if collect.expression.search(open(name, 'r').read()):
            collect.copyright.append(name)
        else:
            collect.no_copyright.append(name)

remove_list = [
        'build',
        'debian',
        'dist',
        'Optik',
        'dblite.py',
        'Conftest.py',
        'MANIFEST',
        'os_spawnv_fix.diff',
        'setup.cfg',
]

src_remove_list = [
        'bin',
                'cons.pl',
                'design',
                'python10',
                'reference',
        'etc',
        'gentoo',
        'config',
        'MANIFEST.in',
]

# XXX Remove '*-stamp' when we get rid of those.
scons = Collect(remove_list + ['build-stamp', 'configure-stamp'])
# XXX Remove '.sconsign' when we start using SConsignFile() for SCons builds.
local = Collect(remove_list + ['.sconsign'])
src = Collect(remove_list + src_remove_list)

build_scons = os.path.join(cwd, 'build', 'scons')
build_local = os.path.join(cwd, 'build', 'scons-local')
build_src = os.path.join(cwd, 'build', 'scons-src')

no_result = []

if os.path.exists(build_scons):
    os.path.walk(build_scons, visit, scons)
else:
    no_result.append(build_scons)

if os.path.exists(build_local):
    os.path.walk(build_local, visit, local)
else:
    no_result.append(build_local)

if os.path.exists(build_src):
    os.path.walk(build_src, visit, src)
else:
    no_result.append(build_src)

no_copyright = scons.no_copyright + local.no_copyright + src.no_copyright

if no_copyright:
    print "Found the following files with no copyrights:"
    print "\t" + string.join(no_copyright, "\n\t")
    test.fail_test(1)

if no_result:
    print "Cannot check copyrights, the following have apparently not been built:"
    print "\t" + string.join(no_result, "\n\t")
    test.no_result(1)

# All done.
test.pass_test()
