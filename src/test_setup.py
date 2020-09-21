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
import sys

try: WindowsError
except NameError: WindowsError = OSError

import TestSCons

version = TestSCons.TestSCons.scons_version

scons_version = 'scons-%s' % version

python = TestSCons.python

class MyTestSCons(TestSCons.TestSCons):

    _lib_modules = [
        # A representative smattering of build engine modules.
        '__init__.py',
        'Action.py',
        'Builder.py',
        'Environment.py',
        'Util.py',
    ]

    _base_scripts = [
        'scons',
        'sconsign',
    ]

    _version_scripts = [
        'scons-%s' % version,
        'sconsign-%s' % version,
    ]

    _bat_scripts = [
        'scons.bat',
    ]

    _bat_version_scripts = [
        'scons-%s.bat' % version,
    ]

    _man_pages = [
        'scons.1',
        'sconsign.1',
    ]

    def __init__(self):
        TestSCons.TestSCons.__init__(self)
        self.root = self.workpath('root')
        self.prefix = self.root + os.path.splitdrive(sys.prefix)[1]

        if sys.platform == 'win32':
            self.bin_dir = os.path.join(self.prefix, 'Scripts')
            self.bat_dir = self.prefix
            self.standalone_lib = os.path.join(self.prefix, 'scons')
            self.standard_lib = os.path.join(self.prefix,
                                             'Lib',
                                             'site-packages',
                                             '')
            self.version_lib = os.path.join(self.prefix, scons_version)
            self.man_dir = os.path.join(self.prefix, 'Doc')
        else:
            self.bin_dir = os.path.join(self.prefix, 'bin')
            self.bat_dir = self.bin_dir
            self.lib_dir = os.path.join(self.prefix, 'lib')
            self.standalone_lib = os.path.join(self.lib_dir, 'scons')
            self.standard_lib = os.path.join(self.lib_dir,
                                             'python%s' % sys.version[:3],
                                             'site-packages',
                                             '')
            self.version_lib = os.path.join(self.lib_dir, scons_version)
            self.man_dir = os.path.join(self.prefix, 'man', 'man1')

        self.prepend_bin_dir = lambda p: os.path.join(self.bin_dir, p)
        self.prepend_bat_dir = lambda p: os.path.join(self.bat_dir, p)
        self.prepend_man_dir = lambda p: os.path.join(self.man_dir, p)

    def run(self, *args, **kw):
        kw['chdir'] = scons_version
        kw['program'] = python
        kw['stderr'] = None
        return TestSCons.TestSCons.run(self, *args, **kw)

    def remove(self, dir):
        try: shutil.rmtree(dir)
        except (OSError, WindowsError): pass

    def stdout_lines(self):
        return self.stdout().split('\n')


    def lib_line(self, lib):
        return 'Installed SCons library modules into %s' % lib

    def lib_paths(self, lib_dir):
        return [os.path.join(lib_dir, 'SCons', p) for p in self._lib_modules]

    def scripts_line(self):
        return 'Installed SCons scripts into %s' % self.bin_dir

    def base_script_paths(self):
        scripts = self._base_scripts
        return list(map(self.prepend_bin_dir, scripts))

    def version_script_paths(self):
        scripts = self._version_scripts
        return list(map(self.prepend_bin_dir, scripts))

    def bat_script_paths(self):
        scripts = self._bat_scripts + self._bat_version_scripts
        return list(map(self.prepend_bat_dir, scripts))

    def man_page_line(self):
        return 'Installed SCons man pages into %s' % self.man_dir

    def man_page_paths(self):
        return list(map(self.prepend_man_dir, self._man_pages))


    def must_have_installed(self, paths):
        for p in paths:
            self.must_exist(p)

    def must_not_have_installed(self, paths):
        for p in paths:
            self.must_not_exist(p)

try:
    cwd = os.environ['SCONS_CWD']
except KeyError:
    cwd = os.getcwd()

test = MyTestSCons()

test.subdir(test.root)

tar_gz = os.path.join(cwd, 'build', 'dist', '%s.tar.gz' % scons_version)
zip = os.path.join(cwd, 'build', 'dist', '%s.zip' % scons_version)

if os.path.isfile(zip):
    try:
        import zipfile
    except ImportError:
        pass
    else:
        with zipfile.ZipFile(zip, 'r') as zf:

            for name in zf.namelist():
                dname = os.path.dirname(name)
                try:
                    os.makedirs(dname)
                except FileExistsError:
                    pass
                # if the file exists, then delete it before writing
                # to it so that we don't end up trying to write to a symlink:
                if os.path.isfile(name) or os.path.islink(name):
                    os.unlink(name)
                if not os.path.isdir(name):
                    with open(name, 'w') as ofp:
                        ofp.write(zf.read(name))

if not os.path.isdir(scons_version) and os.path.isfile(tar_gz):
    # Unpack the .tar.gz file.  This should create the scons_version/
    # subdirectory from which we execute the setup.py script therein.
    os.system("gunzip -c %s | tar xf -" % tar_gz)

if not os.path.isdir(scons_version):
    print("Cannot test package installation, found none of the following packages:")
    print("\t" + tar_gz)
    print("\t" + zip)
    test.no_result(1)

# Verify that a virgin installation installs the version library,
# the scripts and (on UNIX/Linux systems) the man pages.
test.run(arguments = 'setup.py install --root=%s' % test.root)
test.fail_test(not test.lib_line(test.version_lib) in test.stdout_lines())
test.must_have_installed(test.lib_paths(test.version_lib))

# Verify that --standard-lib installs into the Python standard library.
test.run(arguments = 'setup.py install --root=%s --standard-lib' % test.root)
test.fail_test(not test.lib_line(test.standard_lib) in test.stdout_lines())
test.must_have_installed(test.lib_paths(test.standard_lib))

# Verify that --standalone-lib installs the standalone library.
test.run(arguments = 'setup.py install --root=%s --standalone-lib' % test.root)
test.fail_test(not test.lib_line(test.standalone_lib) in test.stdout_lines())
test.must_have_installed(test.lib_paths(test.standalone_lib))

# Verify that --version-lib installs into a version-specific library directory.
test.run(arguments = 'setup.py install --root=%s --version-lib' % test.root)
test.fail_test(not test.lib_line(test.version_lib) in test.stdout_lines())

# Now that all of the libraries are in place,
# verify that a default installation still installs the version library.
test.run(arguments = 'setup.py install --root=%s' % test.root)
test.fail_test(not test.lib_line(test.version_lib) in test.stdout_lines())

test.remove(test.version_lib)

# Now with only the standard and standalone libraries in place,
# verify that a default installation still installs the version library.
test.run(arguments = 'setup.py install --root=%s' % test.root)
test.fail_test(not test.lib_line(test.version_lib) in test.stdout_lines())

test.remove(test.version_lib)
test.remove(test.standalone_lib)

# Now with only the standard libraries in place,
# verify that a default installation still installs the version library.
test.run(arguments = 'setup.py install --root=%s' % test.root)
test.fail_test(not test.lib_line(test.version_lib) in test.stdout_lines())



#
test.run(arguments = 'setup.py install --root=%s' % test.root)
test.fail_test(not test.scripts_line() in test.stdout_lines())
if sys.platform == 'win32':
    test.must_have_installed(test.base_script_paths())
    test.must_have_installed(test.version_script_paths())
    test.must_have_installed(test.bat_script_paths())
else:
    test.must_have_installed(test.base_script_paths())
    test.must_have_installed(test.version_script_paths())
    test.must_not_have_installed(test.bat_script_paths())

test.remove(test.prefix)

test.run(arguments = 'setup.py install --root=%s --no-install-bat' % test.root)
test.fail_test(not test.scripts_line() in test.stdout_lines())
test.must_have_installed(test.base_script_paths())
test.must_have_installed(test.version_script_paths())
test.must_not_have_installed(test.bat_script_paths())

test.remove(test.prefix)

test.run(arguments = 'setup.py install --root=%s --install-bat' % test.root)
test.fail_test(not test.scripts_line() in test.stdout_lines())
test.must_have_installed(test.base_script_paths())
test.must_have_installed(test.version_script_paths())
test.must_have_installed(test.bat_script_paths())

test.remove(test.prefix)

test.run(arguments = 'setup.py install --root=%s --no-scons-script' % test.root)
test.fail_test(not test.scripts_line() in test.stdout_lines())
test.must_not_have_installed(test.base_script_paths())
test.must_have_installed(test.version_script_paths())
# Doesn't matter whether we installed the .bat scripts or not.

test.remove(test.prefix)

test.run(arguments = 'setup.py install --root=%s --no-version-script' % test.root)
test.fail_test(not test.scripts_line() in test.stdout_lines())
test.must_have_installed(test.base_script_paths())
test.must_not_have_installed(test.version_script_paths())
# Doesn't matter whether we installed the .bat scripts or not.



test.remove(test.man_dir)

test.run(arguments = 'setup.py install --root=%s' % test.root)
if sys.platform == 'win32':
    test.fail_test(test.man_page_line() in test.stdout_lines())
    test.must_not_have_installed(test.man_page_paths())
else:
    test.fail_test(not test.man_page_line() in test.stdout_lines())
    test.must_have_installed(test.man_page_paths())

test.remove(test.man_dir)

test.run(arguments = 'setup.py install --root=%s --no-install-man' % test.root)
test.fail_test(test.man_page_line() in test.stdout_lines())
test.must_not_have_installed(test.man_page_paths())

test.remove(test.man_dir)

test.run(arguments = 'setup.py install --root=%s --install-man' % test.root)
test.fail_test(not test.man_page_line() in test.stdout_lines())
test.must_have_installed(test.man_page_paths())



# Verify that we don't warn about the directory in which we've
# installed the modules when using a non-standard prefix.
other_prefix = test.workpath('other-prefix')
test.subdir(other_prefix)
test.run(arguments = 'setup.py install --prefix=%s' % other_prefix)
test.fail_test("you'll have to change the search path yourself" in test.stderr())

# All done.
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
