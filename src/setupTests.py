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
Test how the setup.py script installs SCons (specifically, its libraries).
"""

import os
import os.path
import shutil
import string
import sys

import TestSCons

python = TestSCons.python

class MyTestSCons(TestSCons.TestSCons):
    def installed(self, lib):
        lines = string.split(self.stdout(), '\n')
        return lines[-3] == 'Installed SCons library modules into %s' % lib

try:
    cwd = os.environ['SCONS_CWD']
except KeyError:
    cwd = os.getcwd()

#try:
#    version = os.environ['SCONS_VERSION']
#except KeyError:
#    version = '__VERSION__'
version = '0.93'

scons_version = 'scons-%s' % version

tar_gz = os.path.join(cwd, 'build', 'dist', '%s.tar.gz' % scons_version)

test = MyTestSCons()

if not os.path.isfile(tar_gz):
    print "Did not find an SCons package `%s'." % tar_gz
    print "Cannot test package installation."
    test.no_result(1)

test.subdir('root', 'prefix')

root = test.workpath('root')
prefix = test.workpath('prefix')

v = string.split(string.split(sys.version)[0], '.')
standard_lib = '%s/usr/lib/python%s.%s/site-packages/' % (root, v[0], v[1])
standalone_lib = '%s/usr/lib/scons' % root
version_lib = '%s/usr/lib/%s' % (root, scons_version)

os.system("gunzip -c %s | tar xf -" % tar_gz)

# Verify that a virgin installation installs the standalone library.
test.run(chdir = scons_version,
         program = python,
         arguments = 'setup.py install --root=%s' % root,
         stderr = None)
test.fail_test(not test.installed(standalone_lib))

# Verify that --standard-lib installs into the Python standard library.
test.run(chdir = scons_version,
         program = python,
         arguments = 'setup.py install --root=%s --standard-lib' % root,
         stderr = None)
lines = string.split(test.stdout(), '\n')
test.fail_test(not test.installed(standard_lib))

# Verify that --standalone-lib installs the standalone library.
test.run(chdir = scons_version,
         program = python,
         arguments = 'setup.py install --root=%s --standalone-lib' % root,
         stderr = None)
test.fail_test(not test.installed(standalone_lib))

# Verify that --version-lib installs into a version-specific library directory.
test.run(chdir = scons_version,
         program = python,
         arguments = 'setup.py install --root=%s --version-lib' % root,
         stderr = None)
test.fail_test(not test.installed(version_lib))

# Now that all of the libraries are in place,
# verify that a default installation finds the version-specific library first.
test.run(chdir = scons_version,
         program = python,
         arguments = 'setup.py install --root=%s' % root,
         stderr = None)
test.fail_test(not test.installed(version_lib))

shutil.rmtree(version_lib)

# Now with only the standard and standalone libraries in place,
# verify that a default installation finds the standalone library first.
test.run(chdir = scons_version,
         program = python,
         arguments = 'setup.py install --root=%s' % root,
         stderr = None)
test.fail_test(not test.installed(standalone_lib))

shutil.rmtree(standalone_lib)

# Now with only the standard libraries in place,
# verify that a default installation installs the standard library.
test.run(chdir = scons_version,
         program = python,
         arguments = 'setup.py install --root=%s' % root,
         stderr = None)
test.fail_test(not test.installed(standard_lib))

# Verify that we're not warning about the directory in which
# we've installed the modules when using a non-standard prefix.
test.run(chdir = scons_version,
         program = python,
         arguments = 'setup.py install --prefix=%s' % prefix,
         stderr = None)
test.fail_test(string.find(test.stderr(),
                           "you'll have to change the search path yourself")
               != -1)

# All done.
test.pass_test()
