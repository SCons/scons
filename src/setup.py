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
import os.path
import string
import sys

(head, tail) = os.path.split(sys.argv[0])

if head:
    os.chdir(head)
    sys.argv[0] = tail

try:
    import distutils.core
    import distutils.command.install
    import distutils.command.install_lib
    import distutils.command.install_scripts
except ImportError:
    sys.stderr.write("""Could not import distutils.

Building or installing SCons from this package requires that the Python
distutils be installed.  See the README or README.txt file from this
package for instructions on where to find distutils for installation on
your system, or on how to install SCons from a different package.
""")
    sys.exit(1)

_install = distutils.command.install.install
_install_lib = distutils.command.install_lib.install_lib
_install_scripts = distutils.command.install_scripts.install_scripts

standard_lib = 0
standalone_lib = 0
version_lib = 0

installed_lib_dir = None
installed_scripts_dir = None

def set_explicitly(name, args):
    """
    Return if the installation directory was set explicitly by the
    user on the command line.  This is complicated by the fact that
    "install --install-lib=/foo" gets turned into "install_lib
    --install-dir=/foo" internally.
    """
    if args[0] == "install_" + name:
        s = "--install-dir="
    else:
        # The command is something else (usually "install")
        s = "--install-%s=" % name
    set = 0
    length = len(s)
    for a in args[1:]:
        if a[:length] == s:
            set = 1
            break
    return set

class install(_install):
    user_options = _install.user_options + [
                    ('standard-lib', None,
                     "install SCons library in standard Python location"),
                    ('standalone-lib', None,
                     "install SCons library in separate standalone directory"),
                    ('version-lib', None,
                     "install SCons library in version-specific directory")
                   ]
    boolean_options = _install.boolean_options + [
                       'standard-lib',
                       'standalone-lib',
                       'version-lib'
                      ]

    def initialize_options(self):
        _install.initialize_options(self)
        self.standard_lib = 0
        self.standalone_lib = 0
        self.version_lib = 0
        self.warn_dir = 0

    def finalize_options(self):
        _install.finalize_options(self)
        global standard_lib, standalone_lib, version_lib
        standard_lib = self.standard_lib
        standalone_lib = self.standalone_lib
        version_lib = self.version_lib

def get_scons_prefix(libdir, is_win32):
    """
    Return the right prefix for SCons library installation.  Find
    this by starting with the library installation directory
    (.../site-packages, most likely) and crawling back up until we reach
    a directory name beginning with "python" (or "Python").
    """
    drive, head = os.path.splitdrive(libdir)
    while head:
        if head == os.sep:
            break
        head, tail = os.path.split(head)
        if string.lower(tail)[:6] == "python":
            # Found the Python library directory...
            if is_win32:
                # ...on Win32 systems, "scons" goes in the directory:
                #    C:\PythonXX => C:\PythonXX\scons
                return os.path.join(drive + head, tail)
            else:
                # ...on other systems, "scons" goes above the directory:
                #    /usr/lib/pythonX.X => /usr/lib/scons
                return os.path.join(drive + head)
    return libdir

class install_lib(_install_lib):
    def initialize_options(self):
        _install_lib.initialize_options(self)
        global standard_lib, standalone_lib, version_lib
        self.standard_lib = standard_lib
        self.standalone_lib = standalone_lib
        self.version_lib = version_lib

    def finalize_options(self):
        _install_lib.finalize_options(self)
        args = self.distribution.script_args
        if not set_explicitly("lib", args):
            # They didn't explicitly specify the installation
            # directory for libraries...
            is_win32 = sys.platform == "win32" or args[0] == 'bdist_wininst'
            prefix = get_scons_prefix(self.install_dir, is_win32)
            standard_dir = os.path.join(self.install_dir, "SCons")
            version_dir = os.path.join(prefix, "scons-__VERSION__")
            standalone_dir = os.path.join(prefix, "scons")
            if self.version_lib:
                # ...but they asked for a version-specific directory.
                self.install_dir = version_dir
            elif self.standalone_lib:
                # ...but they asked for a standalone directory.
                self.install_dir = standalone_dir
            elif not self.standard_lib:
                # ...and they didn't explicitly ask for the standard
                # directory, so guess based on what's out there.
                try:
                    e = filter(lambda x: x[:6] == "scons-", os.listdir(prefix))
                except:
                    e = None
                if e:
                    # We found a path name (e.g.) /usr/lib/scons-XXX,
                    # so pick the version-specific directory.
                    self.install_dir = version_dir
                elif os.path.exists(standalone_dir) or \
                     not os.path.exists(standard_dir):
                    # There's already a standalone directory, or
                    # there's no SCons library in the standard
                    # directory, so go with the standalone.
                    self.install_dir = standalone_dir
        global installed_lib_dir
        installed_lib_dir = self.install_dir

class install_scripts(_install_scripts):
    def finalize_options(self):
        _install_scripts.finalize_options(self)
        global installed_scripts_dir
        installed_scripts_dir = self.install_dir

arguments = {
    'name'             : "scons",
    'version'          : "__VERSION__",
    'packages'         : ["SCons",
                          "SCons.Node",
                          "SCons.Optik",
                          "SCons.Platform",
                          "SCons.Scanner",
                          "SCons.Script",
                          "SCons.Sig",
                          "SCons.Tool"],
    'package_dir'      : {'' : 'engine'},
    'scripts'          : ['script/scons', 'script/sconsign'],
    'cmdclass'         : {'install'         : install,
                          'install_lib'     : install_lib,
                          'install_scripts' : install_scripts}
}

try:
    if sys.argv[1] == "bdist_wininst":
        arguments['data_files'] = [('.', ["script/scons.bat"])]
except IndexError:
    pass

apply(distutils.core.setup, (), arguments)

if installed_lib_dir:
    print "Installed SCons library modules into %s" % installed_lib_dir
if installed_scripts_dir:
    print "Installed SCons script into %s" % installed_scripts_dir
