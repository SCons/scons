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

"""
NOTE: Installed SCons is not importable like usual Python packages. It is
      executed explicitly with command line scripts. This allows multiple
      SCons versions to coexist within single Python installation, which
      is critical for enterprise build cases. Explicit invokation is
      necessary to avoid confusion over which version of SCons is active.

      By default SCons is installed into versioned directory, e.g.
      site-packages/scons-2.1.0.alpha.20101125 and much of the stuff
      below is dedicated to make it happen on various platforms.
"""

from __future__ import print_function

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import stat
import sys

Version = "__VERSION__"

man_pages = [
    'scons.1',
    'sconsign.1',
    'scons-time.1',
]

# change to setup.py directory if it was executed from other dir
(head, tail) = os.path.split(sys.argv[0])
if head:
    os.chdir(head)
    sys.argv[0] = tail


# flag if setup.py is run on win32 or _for_ win32 platform,
# (when building windows installer on linux, for example)
is_win32 = 0
if not sys.platform == 'win32':
    try:
        if sys.argv[1] == 'bdist_wininst':
            is_win32 = 1
    except IndexError:
        pass
else:
    is_win32 = 1


import distutils
import distutils.core
import distutils.command.install
import distutils.command.install_data
import distutils.command.install_lib
import distutils.command.install_scripts
import distutils.command.build_scripts
import distutils.msvccompiler

def get_build_version():
    """ monkey patch distutils msvc version if we're not on windows.
    We need to use vc version 9 for python 2.7.x and it defaults to 6
    for non-windows platforms and there is no way to override it besides
    monkey patching"""
    return 9

distutils.msvccompiler.get_build_version = get_build_version

_install = distutils.command.install.install
_install_data = distutils.command.install_data.install_data
_install_lib = distutils.command.install_lib.install_lib
_install_scripts = distutils.command.install_scripts.install_scripts
_build_scripts = distutils.command.build_scripts.build_scripts

class _options(object):
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

    if hasattr(os, 'link'):
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
        if tail.lower()[:6] == "python":
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

def force_to_usr_local(self):
    """
    A hack to decide if we need to "force" the installation directories
    to be under /usr/local.  This is because Mac Os X Tiger and
    Leopard, by default, put the libraries and scripts in their own
    directories under /Library or /System/Library.
    """
    return (sys.platform[:6] == 'darwin' and
            (self.install_dir[:9] == '/Library/' or
             self.install_dir[:16] == '/System/Library/'))

class install_lib(_install_lib):
    def finalize_options(self):
        _install_lib.finalize_options(self)
        if force_to_usr_local(self):
            self.install_dir = '/usr/local/lib'
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
        if force_to_usr_local(self):
            self.install_dir = '/usr/local/bin'
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

    def run(self):
        # --- distutils copy/paste ---
        if not self.skip_build:
            self.run_command('build_scripts')
        # --- /distutils copy/paste ---

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
        bat_scripts = [x for x in inputs if x[-4:] == '.bat']
        non_bat_scripts = [x for x in inputs if x[-4:] != '.bat']

        self.outfiles = []
        self.mkpath(self.install_dir)

        for src in non_bat_scripts:
            base = os.path.basename(src)
            scons = os.path.join(self.install_dir, base)
            scons_ver = scons + '-' + Version
            if is_win32:
                scons += '.py'
                scons_ver += '.py'
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

        # --- distutils copy/paste ---
        if hasattr(os, 'chmod') and hasattr(os,'stat'):
            # Set the executable bits (owner, group, and world) on
            # all the scripts we just installed.
            for file in self.get_outputs():
                if self.dry_run:
                    # log.info("changing mode of %s", file)
                    pass
                else:
                    # Use symbolic versions of permissions so this script doesn't fail to parse under python3.x
                    exec_and_read_permission = stat.S_IXOTH | stat.S_IXUSR | stat.S_IXGRP | stat.S_IROTH | stat.S_IRUSR | stat.S_IRGRP
                    mode_mask = 4095 # Octal 07777 used because python3 has different octal syntax than python 2
                    mode = ((os.stat(file)[stat.ST_MODE]) | exec_and_read_permission) & mode_mask
                    # log.info("changing mode of %s to %o", file, mode)
                    os.chmod(file, mode)
        # --- /distutils copy/paste ---

class build_scripts(_build_scripts):
    def finalize_options(self):
        _build_scripts.finalize_options(self)
        self.build_dir = os.path.join('build', 'scripts')

class install_data(_install_data):
    def initialize_options(self):
        _install_data.initialize_options(self)
    def finalize_options(self):
        _install_data.finalize_options(self)
        if force_to_usr_local(self):
            self.install_dir = '/usr/local'
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

description = "Open Source next-generation build tool."

long_description = """Open Source next-generation build tool.
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

arguments = {
    'name'             : "scons",
    'version'          : Version,
    'description'      : description,
    'long_description' : long_description,
    'author'           : 'Steven Knight',
    'author_email'     : 'knight@baldmt.com',
    'url'              : "http://www.scons.org/",
    'packages'         : ["SCons",
                          "SCons.compat",
                          "SCons.Node",
                          "SCons.Options",
                          "SCons.Platform",
                          "SCons.Scanner",
                          "SCons.Script",
                          "SCons.Tool",
                          "SCons.Tool.docbook",
                          "SCons.Tool.MSCommon",
                          "SCons.Tool.packaging",
                          "SCons.Variables",
                         ],
    'package_dir'      : {'' : 'engine',
                          'SCons.Tool.docbook' : 'engine/SCons/Tool/docbook'},
    'package_data'     : {'SCons.Tool.docbook' : ['docbook-xsl-1.76.1/*',
                                                  'docbook-xsl-1.76.1/common/*',
                                                  'docbook-xsl-1.76.1/docsrc/*',
                                                  'docbook-xsl-1.76.1/eclipse/*',
                                                  'docbook-xsl-1.76.1/epub/*',
                                                  'docbook-xsl-1.76.1/epub/bin/*',
                                                  'docbook-xsl-1.76.1/epub/bin/lib/*',
                                                  'docbook-xsl-1.76.1/epub/bin/xslt/*',
                                                  'docbook-xsl-1.76.1/extensions/*',
                                                  'docbook-xsl-1.76.1/fo/*',
                                                  'docbook-xsl-1.76.1/highlighting/*',
                                                  'docbook-xsl-1.76.1/html/*',
                                                  'docbook-xsl-1.76.1/htmlhelp/*',
                                                  'docbook-xsl-1.76.1/images/*',
                                                  'docbook-xsl-1.76.1/images/callouts/*',
                                                  'docbook-xsl-1.76.1/images/colorsvg/*',
                                                  'docbook-xsl-1.76.1/javahelp/*',
                                                  'docbook-xsl-1.76.1/lib/*',
                                                  'docbook-xsl-1.76.1/manpages/*',
                                                  'docbook-xsl-1.76.1/params/*',
                                                  'docbook-xsl-1.76.1/profiling/*',
                                                  'docbook-xsl-1.76.1/roundtrip/*',
                                                  'docbook-xsl-1.76.1/slides/browser/*',
                                                  'docbook-xsl-1.76.1/slides/fo/*',
                                                  'docbook-xsl-1.76.1/slides/graphics/*',
                                                  'docbook-xsl-1.76.1/slides/graphics/active/*',
                                                  'docbook-xsl-1.76.1/slides/graphics/inactive/*',
                                                  'docbook-xsl-1.76.1/slides/graphics/toc/*',
                                                  'docbook-xsl-1.76.1/slides/html/*',
                                                  'docbook-xsl-1.76.1/slides/htmlhelp/*',
                                                  'docbook-xsl-1.76.1/slides/keynote/*',
                                                  'docbook-xsl-1.76.1/slides/keynote/xsltsl/*',
                                                  'docbook-xsl-1.76.1/slides/svg/*',
                                                  'docbook-xsl-1.76.1/slides/xhtml/*',
                                                  'docbook-xsl-1.76.1/template/*',
                                                  'docbook-xsl-1.76.1/tests/*',
                                                  'docbook-xsl-1.76.1/tools/bin/*',
                                                  'docbook-xsl-1.76.1/tools/make/*',
                                                  'docbook-xsl-1.76.1/webhelp/*',
                                                  'docbook-xsl-1.76.1/webhelp/docs/*',
                                                  'docbook-xsl-1.76.1/webhelp/docs/common/*',
                                                  'docbook-xsl-1.76.1/webhelp/docs/common/css/*',
                                                  'docbook-xsl-1.76.1/webhelp/docs/common/images/*',
                                                  'docbook-xsl-1.76.1/webhelp/docs/common/jquery/*',
                                                  'docbook-xsl-1.76.1/webhelp/docs/common/jquery/theme-redmond/*',
                                                  'docbook-xsl-1.76.1/webhelp/docs/common/jquery/theme-redmond/images/*',
                                                  'docbook-xsl-1.76.1/webhelp/docs/common/jquery/treeview/*',
                                                  'docbook-xsl-1.76.1/webhelp/docs/common/jquery/treeview/images/*',
                                                  'docbook-xsl-1.76.1/webhelp/docs/content/*',
                                                  'docbook-xsl-1.76.1/webhelp/docs/content/search/*',
                                                  'docbook-xsl-1.76.1/webhelp/docs/content/search/stemmers/*',
                                                  'docbook-xsl-1.76.1/webhelp/docsrc/*',
                                                  'docbook-xsl-1.76.1/webhelp/template/*',
                                                  'docbook-xsl-1.76.1/webhelp/template/common/*',
                                                  'docbook-xsl-1.76.1/webhelp/template/common/css/*',
                                                  'docbook-xsl-1.76.1/webhelp/template/common/images/*',
                                                  'docbook-xsl-1.76.1/webhelp/template/common/jquery/*',
                                                  'docbook-xsl-1.76.1/webhelp/template/common/jquery/theme-redmond/*',
                                                  'docbook-xsl-1.76.1/webhelp/template/common/jquery/theme-redmond/images/*',
                                                  'docbook-xsl-1.76.1/webhelp/template/common/jquery/treeview/*',
                                                  'docbook-xsl-1.76.1/webhelp/template/common/jquery/treeview/images/*',
                                                  'docbook-xsl-1.76.1/webhelp/template/content/search/*',
                                                  'docbook-xsl-1.76.1/webhelp/template/content/search/stemmers/*',
                                                  'docbook-xsl-1.76.1/webhelp/xsl/*',
                                                  'docbook-xsl-1.76.1/website/*',
                                                  'docbook-xsl-1.76.1/xhtml/*',
                                                  'docbook-xsl-1.76.1/xhtml-1_1/*',
                                                  'utils/*']},
    'data_files'       : [('man/man1', man_pages)],
    'scripts'          : scripts,
    'cmdclass'         : {'install'         : install,
                          'install_lib'     : install_lib,
                          'install_data'    : install_data,
                          'install_scripts' : install_scripts,
                          'build_scripts'   : build_scripts}
}

distutils.core.setup(**arguments)

if Installed:
    for i in Installed:
        print(i)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
