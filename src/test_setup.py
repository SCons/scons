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
Test how the setup.py script installs SCons.

Note that this is an installation test, not a functional test, so the
name of this script doesn't end in *Tests.py.
"""

import os
import os.path
import shutil
import string
import sys

#try:
#    version = os.environ['SCONS_VERSION']
#except KeyError:
#    version = '__VERSION__'
version = '0.96'

scons_version = 'scons-%s' % version

import TestSCons

python = TestSCons.python

class MyTestSCons(TestSCons.TestSCons):

    scripts = [
        'scons',
        'sconsign',
    ]

    man_pages = [
        'scons.1',
        'sconsign.1',
    ]

    def __init__(self):
        TestSCons.TestSCons.__init__(self)
        self.root = self.workpath('root')
        self.prefix = self.root + sys.prefix

        self.lib_dir = os.path.join(self.prefix, 'lib')
        self.standard_lib = os.path.join(self.lib_dir,
                                         'python%s' % sys.version[:3],
                                         'site-packages/')
        self.standalone_lib = os.path.join(self.lib_dir, 'scons')
        self.version_lib = os.path.join(self.lib_dir, scons_version)

        self.bin_dir = os.path.join(self.prefix, 'bin')

        self.man_dir = os.path.join(self.prefix, 'man', 'man1')

    def run(self, *args, **kw):
        kw['chdir'] = scons_version
        kw['program'] = python
        kw['stderr'] = None
        return apply(TestSCons.TestSCons.run, (self,)+args, kw)

    def must_have_installed_lib(self, lib):
        lines = string.split(self.stdout(), '\n')
        line = 'Installed SCons library modules into %s' % lib
        self.fail_test(not line in lines)

    def must_have_installed_scripts(self):
        lines = string.split(self.stdout(), '\n')
        line = 'Installed SCons scripts into %s' % self.bin_dir
        self.fail_test(not line in lines)
        for script in self.scripts:
            self.must_exist([self.bin_dir, script])

    def must_have_installed_man_pages(self):
        lines = string.split(self.stdout(), '\n')
        line = 'Installed SCons man pages into %s' % self.man_dir
        self.fail_test(not line in lines)
        for mp in self.man_pages:
            self.must_exist([self.man_dir, mp])

try:
    cwd = os.environ['SCONS_CWD']
except KeyError:
    cwd = os.getcwd()

tar_gz = os.path.join(cwd, 'build', 'dist', '%s.tar.gz' % scons_version)

if not os.path.isfile(tar_gz):
    print "Did not find an SCons package `%s'." % tar_gz
    print "Cannot test package installation."
    test.no_result(1)

test = MyTestSCons()

test.subdir(test.root)

# Unpack the .tar.gz file.  This should create the scons_version/
# subdirectory from which we execute the setup.py script therein.
os.system("gunzip -c %s | tar xf -" % tar_gz)

# Verify that a virgin installation installs the standalone library,
# the scripts and the man pages.
test.run(arguments = 'setup.py install --root=%s' % test.root)
test.must_have_installed_lib(test.standalone_lib)
test.must_have_installed_scripts()
test.must_have_installed_man_pages()

# Verify that --standard-lib installs into the Python standard library.
test.run(arguments = 'setup.py install --root=%s --standard-lib' % test.root)
test.must_have_installed_lib(test.standard_lib)

# Verify that --standalone-lib installs the standalone library.
test.run(arguments = 'setup.py install --root=%s --standalone-lib' % test.root)
test.must_have_installed_lib(test.standalone_lib)

# Verify that --version-lib installs into a version-specific library directory.
test.run(arguments = 'setup.py install --root=%s --version-lib' % test.root)
test.must_have_installed_lib(test.version_lib)

# Now that all of the libraries are in place,
# verify that a default installation finds the version-specific library first.
test.run(arguments = 'setup.py install --root=%s' % test.root)
test.must_have_installed_lib(test.version_lib)

shutil.rmtree(test.version_lib)

# Now with only the standard and standalone libraries in place,
# verify that a default installation finds the standalone library first.
test.run(arguments = 'setup.py install --root=%s' % test.root)
test.must_have_installed_lib(test.standalone_lib)

shutil.rmtree(test.standalone_lib)

# Now with only the standard libraries in place,
# verify that a default installation installs the standard library.
test.run(arguments = 'setup.py install --root=%s' % test.root)
test.must_have_installed_lib(test.standard_lib)

# Verify that we don't warn about the directory in which we've
# installed the modules when using a non-standard prefix.
other_prefix = test.workpath('other-prefix')
test.subdir(other_prefix)
test.run(arguments = 'setup.py install --prefix=%s' % other_prefix)
test.fail_test(string.find(test.stderr(),
                           "you'll have to change the search path yourself")
               != -1)

# All done.
test.pass_test()
