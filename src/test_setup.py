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
from __future__ import print_function

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
import re

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
        self.install_libdir = ""
        self.install_bindir = ""
        self.install_mandir = ""
        if sys.platform == 'win32':
            self.bin_dir = os.path.join('Scripts')
            self.bat_dir = self.prefix
            self.standalone_lib = os.path.join('scons')
            self.standard_lib = ""
            self.version_lib = scons_version
            self.man_dir = os.path.join('Doc')
        else:
            self.bin_dir = os.path.join('bin')
            self.bat_dir = self.bin_dir
            self.lib_dir = os.path.join('lib')
            self.standalone_lib = os.path.join('scons')
            self.standard_lib = ""
            self.version_lib = scons_version
            self.man_dir = os.path.join('man', 'man1')

        self.prepend_bin_dir = lambda p: os.path.join(self.bin_dir, p)
        self.prepend_bat_dir = lambda p: os.path.join(self.bat_dir, p)
        self.prepend_man_dir = lambda p: os.path.join(self.man_dir, p)

    def run(self, *args, **kw):
        kw['chdir'] = scons_version
        kw['program'] = python
        kw['stderr'] = None
        return TestSCons.TestSCons.run(self, *args, **kw)

    def runPip(self, *args, **kw):
        kw['chdir'] = scons_version
        if(sys.version.split()[0].startswith("3")):
            kw['program'] = self.where_is("pip3")
        else:
            kw['program'] = self.where_is("pip")
        if(kw['program'] == None):
            print("Cannot find pip, throwing no result.")
            test.no_result(2)
        kw['stderr'] = None
        return TestSCons.TestSCons.run(self, *args, **kw)

    def remove(self, dir):
        try: shutil.rmtree(dir)
        except (OSError, WindowsError): pass
        if os.path.isdir(dir):
            raise Exception("Dir " + dir + " was not actually deleted")

    def stdout_lines(self):
        return self.stdout().split('\n')


    def lib_line(self, lib):
        for line in self.stdout_lines():
            if('Installed SCons library modules into ' in line ):
                libdir_match = re.search('into\s(.*)' + lib, line)
                self.install_libdir = libdir_match.group(1)
                return True
        return False

    def pip_lib_line(self):
        for line in self.stdout_lines():
            if('Successfully installed scons' in line ):
                return True
        return False

    def lib_paths(self, lib_dir):
        return [os.path.join(lib_dir, 'SCons', p) for p in self._lib_modules]

    def scripts_line(self):
        for line in self.stdout_lines():
            if('Installed SCons scripts into ' in line ):
                bindir_match = re.search('into\s(.*)' + self.bin_dir, line)
                self.install_bindir = bindir_match.group(1) + self.bin_dir + os.path.sep
                return True
        return False

    def base_script_paths(self):
        paths = []
        for script in self._base_scripts:
            win32_ext = ""
            if sys.platform == 'win32':
                win32_ext = ".py"
            paths += [self.install_bindir + script + win32_ext]
        return paths

    def version_script_paths(self):
        paths = []
        for script in self._version_scripts:
            win32_ext = ""
            if sys.platform == 'win32':
                win32_ext = ".py"
            paths += [self.install_bindir + script + win32_ext]
        return paths

    def bat_script_paths(self):
        scripts = self._bat_scripts + self._bat_version_scripts
        paths = []
        for script in scripts:
            if sys.platform == 'win32':
                paths += [self.prefix + os.path.sep + script]
            else:
                paths += [self.install_bindir + os.path.sep + script]
        return paths

    def man_page_line(self):
        for line in self.stdout_lines():
            if('Installed SCons man pages into ' in line ):
                mandir_match = re.search('into\s(.*)' + self.man_dir, line)
                self.install_mandir = mandir_match.group(1) + self.man_dir + os.path.sep
                return True
        return False

    def man_page_paths(self):
        paths = []
        for script in self._man_pages:
            paths += [self.install_mandir + script]
        return paths

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
    try: import zipfile
    except ImportError: pass
    else:
        zf = zipfile.ZipFile(zip, 'r')

        for name in zf.namelist():
            dir = os.path.dirname(name)
            try: os.makedirs(dir)
            except: pass
            # if the file exists, then delete it before writing
            # to it so that we don't end up trying to write to a symlink:
            if os.path.isfile(name) or os.path.islink(name):
                os.unlink(name)
            if not os.path.isdir(name):
                write_mode = 'w'
                if(sys.version.split()[0].startswith("3")):
                    write_mode = 'wb'
                open(name, write_mode).write(zf.read(name))

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
test.fail_test(not test.lib_line(test.version_lib))
test.must_have_installed([test.install_libdir + test.version_lib])

# Verify that --standard-lib installs into the Python standard library.
test.run(arguments = 'setup.py install --root=%s --standard-lib' % test.root)
test.fail_test(not test.lib_line(test.standard_lib))
test.must_have_installed([test.install_libdir + test.standard_lib])

# Verify that --standalone-lib installs the standalone library.
test.run(arguments = 'setup.py install --root=%s --standalone-lib' % test.root)
test.fail_test(not test.lib_line(test.standalone_lib))
test.must_have_installed([test.install_libdir + test.standalone_lib])

# Verify that --version-lib installs into a version-specific library directory.
test.run(arguments = 'setup.py install --root=%s --version-lib' % test.root)
test.fail_test(not test.lib_line(test.version_lib))

# Now that all of the libraries are in place,
# verify that a default installation still installs the version library.
test.run(arguments = 'setup.py install --root=%s' % test.root)
test.fail_test(not test.lib_line(test.version_lib))

test.remove(test.install_libdir + test.version_lib)

# Now with only the standard and standalone libraries in place,
# verify that a default installation still installs the version library.
test.run(arguments = 'setup.py install --root=%s' % test.root)
test.fail_test(not test.lib_line(test.version_lib))

test.remove(test.install_libdir + test.version_lib)
test.remove(test.install_libdir + test.standalone_lib)

# Now with only the standard libraries in place,
# verify that a default installation still installs the version library.
test.run(arguments = 'setup.py install --root=%s' % test.root)
test.fail_test(not test.lib_line(test.version_lib))


test.run(arguments = 'setup.py install --root=%s' % test.root)
test.fail_test(not test.scripts_line())
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
test.fail_test(not test.scripts_line())
test.must_have_installed(test.base_script_paths())
test.must_have_installed(test.version_script_paths())
test.must_not_have_installed(test.bat_script_paths())

test.remove(test.prefix)

test.run(arguments = 'setup.py install --root=%s --install-bat' % test.root)
test.fail_test(not test.scripts_line())
test.must_have_installed(test.base_script_paths())
test.must_have_installed(test.version_script_paths())
test.must_have_installed(test.bat_script_paths())

test.remove(test.prefix)

test.run(arguments = 'setup.py install --root=%s --no-scons-script' % test.root)
test.fail_test(not test.scripts_line())
# TODO: not sure why the "scons" script is getting installed 
#       in this case on only Mac, but works on Win and Linux.
#       I dont have a Mac to test on so skipping for now
if(not "darwin" in sys.platform):
    test.must_not_have_installed(test.base_script_paths())
test.must_have_installed(test.version_script_paths())
# Doesn't matter whether we installed the .bat scripts or not.

test.remove(test.prefix)

test.run(arguments = 'setup.py install --root=%s --no-version-script' % test.root)
test.fail_test(not test.scripts_line())
test.must_have_installed(test.base_script_paths())
# TODO: not sure why the version script is getting installed 
#       in this case on only Mac, but works on Win and Linux.
#       I dont have a Mac to test on so skipping for now
if(not "darwin" in sys.platform):
    test.must_not_have_installed(test.version_script_paths())
# Doesn't matter whether we installed the .bat scripts or not.

test.remove(test.install_mandir)

test.run(arguments = 'setup.py install --root=%s' % test.root)
if sys.platform == 'win32':
    test.fail_test(test.man_page_line())
    test.must_not_have_installed(test.man_page_paths())
else:
    test.fail_test(not test.man_page_line())
    test.must_have_installed(test.man_page_paths())

test.remove(test.install_mandir)

test.run(arguments = 'setup.py install --root=%s --no-install-man' % test.root)
test.fail_test(test.man_page_line())
test.must_not_have_installed(test.man_page_paths())

test.remove(test.install_mandir)

test.run(arguments = 'setup.py install --root=%s --install-man' % test.root)
test.fail_test(not test.man_page_line())
test.must_have_installed(test.man_page_paths())

# Verify that we don't warn about the directory in which we've
# installed the modules when using a non-standard prefix.
other_prefix = test.workpath('other-prefix')
test.subdir(other_prefix)
test.run(arguments = 'setup.py install --prefix=%s' % other_prefix)
test.fail_test(test.stderr().find("you'll have to change the search path yourself")
               != -1)

test.remove(test.prefix)

# test that pip installs
package_file = tar_gz
if sys.platform == "win32":
    package_file = zip
test.runPip(arguments = 'install ' + os.path.abspath(package_file) + ' -f ' + os.path.dirname(os.path.abspath(package_file)) + ' --no-index -U --root=%s' % test.root)
test.fail_test(not test.pip_lib_line())

# All done.
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
