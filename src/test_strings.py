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
Verify that we have proper strings like Copyright notices on all the
right files in our distributions.

Note that this is a source file and packaging test, not a functional test,
so the name of this script doesn't end in *Tests.py.
"""

import fnmatch
import os
import os.path
import re

import TestCmd
import TestSCons

# Use TestCmd, not TestSCons, so we don't chdir to a temporary directory.
test = TestCmd.TestCmd()

scons_version = TestSCons.SConsVersion

def build_path(*args):
    return os.path.join('build', *args)

build_scons     = build_path('scons')
build_local     = build_path('scons-local', 'scons-local-'+scons_version)
build_src       = build_path('scons-src')

class Checker:
    def __init__(self, directory,
                 search_list = [],
                 remove_list = [],
                 remove_patterns = []):
        self.directory = directory
        self.search_list = search_list
        self.remove_dict = {}
        for r in remove_list:
            self.remove_dict[os.path.join(directory, r)] = 1
        self.remove_patterns = remove_patterns

    def directory_exists(self):
        return os.path.exists(self.directory)

    def remove_this(self, name, path):
        if self.remove_dict.get(path):
            return 1
        else:
            for pattern in self.remove_patterns:
                if fnmatch.fnmatch(name, pattern):
                    return 1
        return 0

    def search_this(self, path):
        if self.search_list:
            for pattern in self.search_list:
                if fnmatch.fnmatch(path, pattern):
                    return 1
            return None
        else:
            return os.path.isfile(path)

    def find_missing(self):
        result = []
        for dirpath, dirnames, filenames in os.walk(self.directory):
            if '.svn' in dirnames:
                dirnames.remove('.svn')
            for dname in dirnames[:]:
                dpath = os.path.join(dirpath, dname)
                if self.remove_this(dname, dpath):
                    dirnames.remove(dname)
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                if self.search_this(fpath) and not self.remove_this(fname, fpath):
                    with open(fpath, 'r') as f:
                        body = f.read()
                    for expr in self.expressions:
                        if not expr.search(body):
                            msg = '%s: missing %s' % (fpath, repr(expr.pattern))
                            result.append(msg)
        return result

class CheckUnexpandedStrings(Checker):
    expressions = [
        re.compile('__COPYRIGHT__'),
        re.compile('__FILE__ __REVISION__ __DATE__ __DEVELOPER__'),
    ]
    def must_be_built(self):
        return None

class CheckPassTest(Checker):
    expressions = [
        re.compile(r'\.pass_test()'),
    ]
    def must_be_built(self):
        return None

class CheckExpandedCopyright(Checker):
    expressions = [
        re.compile('Copyright.*The SCons Foundation'),
    ]
    def must_be_built(self):
        return 1

check_list = [

    CheckUnexpandedStrings(
        'src',
        search_list = [ '*.py' ],
        remove_list = [
            'engine/SCons/compat/_scons_sets.py',
            'engine/SCons/compat/_scons_subprocess.py',
            'engine/SCons/Conftest.py',
            'engine/SCons/dblite.py',
        ],
    ),

    CheckUnexpandedStrings(
        'test',
        search_list = [ '*.py' ],
    ),

    CheckPassTest(
        'test',
        search_list = [ '*.py' ],
        remove_list = [
            'Fortran/common.py',
        ],
    ),

    CheckExpandedCopyright(
        build_scons,
        remove_list = [
            'build',
            'build-stamp',
            'configure-stamp',
            'debian',
            'dist',
            'gentoo',
            'engine/SCons/compat/_scons_sets.py',
            'engine/SCons/compat/_scons_subprocess.py',
            'engine/SCons/Conftest.py',
            'engine/SCons/dblite.py',
            'MANIFEST',
            'setup.cfg',
        ],
        # We run epydoc on the *.py files, which generates *.pyc files.
        remove_patterns = [
            '*.pyc',
        ]
    ),

    CheckExpandedCopyright(
        build_local,
        remove_list = [
            'SCons/compat/_scons_sets.py',
            'SCons/compat/_scons_subprocess.py',
            'SCons/Conftest.py',
            'SCons/dblite.py',
            'scons-%s.egg-info' % scons_version,
        ],
    ),

    CheckExpandedCopyright(
        build_src,
        remove_list = [
            'bench/timeit.py',
            'bin',
            'config',
            'debian',
            'gentoo',
            'doc/design',
            'doc/MANIFEST',
            'doc/python10',
            'doc/reference',
            'doc/developer/MANIFEST',
            'doc/man/MANIFEST',
            'doc/user/cons.pl',
            'doc/user/MANIFEST',
            'doc/user/SCons-win32-install-1.jpg',
            'doc/user/SCons-win32-install-2.jpg',
            'doc/user/SCons-win32-install-3.jpg',
            'doc/user/SCons-win32-install-4.jpg',
            'examples',
            'gentoo',
            'testing/framework/TestCmd.py',
            'testing/framework/TestCmdTests.py',
            'testing/framework/TestCommon.py',
            'testing/framework/TestCommonTests.py',
            'src/MANIFEST.in',
            'src/setup.cfg',
            'src/engine/MANIFEST.in',
            'src/engine/MANIFEST-xml.in',
            'src/engine/setup.cfg',
            'src/engine/SCons/compat/_scons_sets.py',
            'src/engine/SCons/compat/_scons_subprocess.py',
            'src/engine/SCons/Conftest.py',
            'src/engine/SCons/dblite.py',
            'src/script/MANIFEST.in',
            'src/script/setup.cfg',
            'test/Fortran/.exclude_tests',
            'timings/changelog.html',
            'timings/ElectricCloud/genscons.pl',
            'timings/graph.html',
            'timings/index.html',
            'review.py',
        ],
        remove_patterns = [
            '*.js',
        ]
    ),

]

missing_strings = []
not_built = []

for collector in check_list:
    if collector.directory_exists():
        missing_strings.extend(collector.find_missing())
    elif collector.must_be_built():
        not_built.append(collector.directory)

if missing_strings:
    print("Found the following files with missing strings:")
    print("\t" + "\n\t".join(missing_strings))
    test.fail_test(1)

if not_built:
    print("Cannot check all strings, the following have apparently not been built:")
    print("\t" + "\n\t".join(not_built))
    test.no_result(1)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
