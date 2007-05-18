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
import stat
import string
import sys

Version = "0.97"

man_pages = [
    'scons.1',
    'sconsign.1',
    'scons-time.1',
]

(head, tail) = os.path.split(sys.argv[0])

if head:
    os.chdir(head)
    sys.argv[0] = tail

is_win32 = 0
if not sys.platform == 'win32':
    try:
        if sys.argv[1] == 'bdist_wininst':
            is_win32 = 1
    except IndexError:
        pass
else:
    is_win32 = 1

try:
    import distutils
    import distutils.core
    import distutils.command.install
    import distutils.command.install_data
    import distutils.command.install_lib
    import distutils.command.install_scripts
    import distutils.command.build_scripts
except ImportError:
    sys.stderr.write("""Could not import distutils.

Building or installing SCons from this package requires that the Python
distutils be installed.  See the README or README.txt file from this
package for instructions on where to find distutils for installation on
your system, or on how to install SCons from a different package.
""")
    sys.exit(1)

_install = distutils.command.install.install
_install_data = distutils.command.install_data.install_data
_install_lib = distutils.command.install_lib.install_lib
_install_scripts = distutils.command.install_scripts.install_scripts
_build_scripts = distutils.command.build_scripts.build_scripts

class _options:
    pass

Options = _options()

Installed = []

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
                    ('no-scons-script', None,
                     "don't install 'scons', only install 'scons-%s'" % Version),
                    ('no-version-script', None,
                     "don't install 'scons-%s', only install 'scons'" % Version),
                    ('install-bat', None,
                     "install 'scons.bat' script"),
                    ('no-install-bat', None,
                     "do not install 'scons.bat' script"),
                    ('install-man', None,
                     "install SCons man pages"),
                    ('no-install-man', None,
                     "do not install SCons man pages"),
                    ('standard-lib', None,
                     "install SCons library in standard Python location"),
                    ('standalone-lib', None,
                     "install SCons library in separate standalone directory"),
                    ('version-lib', None,
                     "install SCons library in version-numbered directory"),
                   ]
    boolean_options = _install.boolean_options + [
                       'no-scons-script',
                       'no-version-script',
                       'install-bat',
                       'no-install-bat',
                       'install-man',
                       'no-install-man',
                       'standard-lib',
                       'standalone-lib',
                       'version-lib'
                      ]

    if hasattr(os, 'symlink'):
        user_options.append(
                    ('hardlink-scons', None,
                     "hard link 'scons' to the version-numbered script, don't make a separate 'scons' copy"),
                     )
        boolean_options.append('hardlink-script')

    if hasattr(os, 'symlink'):
        user_options.append(
                    ('symlink-scons', None,
                     "make 'scons' a symbolic link to the version-numbered script, don't make a separate 'scons' copy"),
                     )
        boolean_options.append('symlink-script')

    def initialize_options(self):
        _install.initialize_options(self)
        self.no_scons_script = 0
        self.no_version_script = 0
        self.install_bat = 0
        self.no_install_bat = not is_win32
        self.install_man = 0
        self.no_install_man = is_win32
        self.standard_lib = 0
        self.standalone_lib = 0
        self.version_lib = 0
        self.hardlink_scons = 0
        self.symlink_scons = 0
        # Don't warn about having to put the library directory in the
        # search path.
        self.warn_dir = 0

    def finalize_options(self):
        _install.finalize_options(self)
        if self.install_bat:
            Options.install_bat = 1
        else:
            Options.install_bat = not self.no_install_bat
        if self.install_man:
            Options.install_man = 1
        else:
            Options.install_man = not self.no_install_man
        Options.standard_lib = self.standard_lib
        Options.standalone_lib = self.standalone_lib
        Options.version_lib = self.version_lib
        Options.install_scons_script = not self.no_scons_script
        Options.install_version_script = not self.no_version_script
        Options.hardlink_scons = self.hardlink_scons
        Options.symlink_scons = self.symlink_scons

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
    def finalize_options(self):
        _install_lib.finalize_options(self)
        args = self.distribution.script_args
        if not set_explicitly("lib", args):
            # They didn't explicitly specify the installation
            # directory for libraries...
            is_win32 = sys.platform == "win32" or args[0] == 'bdist_wininst'
            prefix = get_scons_prefix(self.install_dir, is_win32)
            if Options.standalone_lib:
                # ...but they asked for a standalone directory.
                self.install_dir = os.path.join(prefix, "scons")
            elif Options.version_lib or not Options.standard_lib:
                # ...they asked for a version-specific directory,
                # or they get it by default.
                self.install_dir = os.path.join(prefix, "scons-%s" % Version)

        msg = "Installed SCons library modules into %s" % self.install_dir
        Installed.append(msg)

class install_scripts(_install_scripts):
    def finalize_options(self):
        _install_scripts.finalize_options(self)
        self.build_dir = os.path.join('build', 'scripts')
        msg = "Installed SCons scripts into %s" % self.install_dir
        Installed.append(msg)

    def do_nothing(self, *args, **kw):
        pass

    def hardlink_scons(self, src, dst, ver):
        try: os.unlink(dst)
        except OSError: pass
        os.link(ver, dst)

    def symlink_scons(self, src, dst, ver):
        try: os.unlink(dst)
        except OSError: pass
        os.symlink(os.path.split(ver)[1], dst)

    def copy_scons(self, src, dst, *args):
        try: os.unlink(dst)
        except OSError: pass
        self.copy_file(src, dst)
        self.outfiles.append(dst)

    def report(self, msg, args):
        # Wrapper around self.announce, used by older distutils versions.
        self.announce(msg % args)

    def run(self):
        # This "skip_build/build_scripts" block is cut-and-paste from
        # distutils.
        if not self.skip_build:
            self.run_command('build_scripts')

        # Custom SCons installation stuff.
        if Options.hardlink_scons:
            create_basename_script = self.hardlink_scons
        elif Options.symlink_scons:
            create_basename_script = self.symlink_scons
        elif Options.install_scons_script:
            create_basename_script = self.copy_scons
        else:
            create_basename_script = self.do_nothing

        if Options.install_version_script:
            create_version_script = self.copy_scons
        else:
            create_version_script = self.do_nothing

        inputs = self.get_inputs()
        bat_scripts = filter(lambda x: x[-4:] == '.bat', inputs)
        non_bat_scripts = filter(lambda x: x[-4:] != '.bat', inputs)

        self.outfiles = []
        self.mkpath(self.install_dir)

        for src in non_bat_scripts:
            base = os.path.basename(src)
            scons = os.path.join(self.install_dir, base)
            scons_ver = scons + '-' + Version
            create_version_script(src, scons_ver)
            create_basename_script(src, scons, scons_ver)

        if Options.install_bat:
            if is_win32:
                bat_install_dir = get_scons_prefix(self.install_dir, is_win32)
            else:
                bat_install_dir = self.install_dir
            for src in bat_scripts:
                scons_bat = os.path.join(bat_install_dir, 'scons.bat')
                scons_version_bat = os.path.join(bat_install_dir,
                                                 'scons-' + Version + '.bat')
                self.copy_scons(src, scons_bat)
                self.copy_scons(src, scons_version_bat)

        # This section is cut-and-paste from distutils, modulo being
        # able 
        if os.name == 'posix':
            try: report = distutils.log.info
            except AttributeError: report = self.report
            # Set the executable bits (owner, group, and world) on
            # all the scripts we just installed.
            for file in self.get_outputs():
                if self.dry_run:
                    report("changing mode of %s", file)
                else:
                    mode = ((os.stat(file)[stat.ST_MODE]) | 0555) & 07777
                    report("changing mode of %s", file)
                    os.chmod(file, mode)

class build_scripts(_build_scripts):
    def finalize_options(self):
        _build_scripts.finalize_options(self)
        self.build_dir = os.path.join('build', 'scripts')

class install_data(_install_data):
    def initialize_options(self):
        _install_data.initialize_options(self)
    def finalize_options(self):
        _install_data.finalize_options(self)
        if Options.install_man:
            if is_win32:
                dir = 'Doc'
            else:
                dir = os.path.join('man', 'man1')
            self.data_files = [(dir, man_pages)]
            man_dir = os.path.join(self.install_dir, dir)
            msg = "Installed SCons man pages into %s" % man_dir
            Installed.append(msg)
        else:
            self.data_files = []

description = """Open Source next-generation build tool.
Improved, cross-platform substitute for the classic Make
utility.  In short, SCons is an easier, more reliable
and faster way to build software."""

scripts = [
    'script/scons',
    'script/sconsign',
    'script/scons-time',

    # We include scons.bat in the list of scripts, even on UNIX systems,
    # because we provide an option to allow it be installed explicitly,
    # for example if you're installing from UNIX on a share that's
    # accessible to Windows and you want the scons.bat.
    'script/scons.bat',
]

#if is_win32:
#    scripts = scripts + [
#        'script/scons-post-install.py'
#    ]

arguments = {
    'name'             : "scons",
    'version'          : Version,
    'description'      : description,
    'author'           : 'Steven Knight',
    'author_email'     : 'knight@baldmt.com',
    'url'              : "http://www.scons.org/",
    'packages'         : ["SCons",
                          "SCons.compat",
                          "SCons.Node",
                          "SCons.Optik",
                          "SCons.Options",
                          "SCons.Platform",
                          "SCons.Scanner",
                          "SCons.Script",
                          "SCons.Sig",
                          "SCons.Tool"],
    'package_dir'      : {'' : 'engine'},
    'data_files'       : [('man/man1', man_pages)],
    'scripts'          : scripts,
    'cmdclass'         : {'install'         : install,
                          'install_lib'     : install_lib,
                          'install_data'    : install_data,
                          'install_scripts' : install_scripts,
                          'build_scripts'   : build_scripts}
}

apply(distutils.core.setup, (), arguments)

if Installed:
    print string.join(Installed, '\n')
