# MIT License
#
# Copyright The SCons Foundation
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
A testing framework for the SCons software construction tool.

A TestSConsTar environment object is created via the usual invocation:

    test = TestSConsTar()

TestSConsTar is a subsclass of TestSCons, which is in turn a subclass
of TestCommon, which is in turn is a subclass of TestCmd), and hence
has available all of the methods and attributes from those classes,
as well as any overridden or additional methods or attributes defined
in this subclass.
"""

import os
import os.path
import subprocess
import sys

from TestSCons import *
from TestSCons import __all__

__all__.extend([
    'TestSConsTar',
    'windows_system_tar_gz',
    'windows_system_tar_bz2',
    'windows_system_tar_xz',
    'windows_system_tar_lzma',
])

if sys.platform == 'win32':

    # Windows 10 and later supplies windows/system32/tar.exe (bsdtar).
    # Not all versions support all compression types.  Check the version
    # string for library support.

    # windows tar.exe:
    #   %systemroot%/system32/tar.exe

    # tar.exe --version (Windows 10, GH windows-2022):
    #   bsdtar 3.5.2 - libarchive 3.5.2 zlib/1.2.5.f-ipp

    # tar.exe --version (Windows 11):
    #   bsdtar 3.7.7 - libarchive 3.7.7 zlib/1.2.5.f-ipp liblzma/5.4.3 bz2lib/1.0.8 libzstd/1.5.4

    # tar.exe --version (GH windows-2025):
    #   bsdtar 3.7.7 - libarchive 3.7.7 zlib/1.2.13.1-motley liblzma/5.4.3 bz2lib/1.0.8 libzstd/1.5.5

    def _is_windows_system_tar(tar):

        if not tar:
            return False

        tar = os.path.normcase(os.path.abspath(tar))
        if not os.path.exists(tar):
            return False

        if not tar.endswith('tar.exe'):
            return False

        windir = os.environ.get("SystemRoot")
        if not windir:
            windir = os.environ.get("windir")

        if not windir:
            windir = os.path.join(os.environ.get("SystemDrive", "C:") + os.path.sep, "Windows")

        windows_tar = os.path.normcase(os.path.abspath(os.path.join(windir, "System32", "tar.exe")))
        rval = bool(tar == windows_tar)

        return rval

    def _windows_system_tar_have_library(tar, libname):

        is_wintar = _is_windows_system_tar(tar)
        if not is_wintar:
            return is_wintar, None

        try:
            result = subprocess.run([f"{tar}", "--version"], capture_output=True, text=True, check=True)
            version_str = result.stdout.strip()
        except:
            version_str = None

        if not version_str:
            return is_wintar, None

        # print(f"{tar} --version => {version_str!r}")

        version_comps = version_str.split()
        if len(version_comps) < 5:
            return is_wintar, None

        for indx, expected in [
            (0, "bsdtar"), (2, "-"), (3, "libarchive"),
        ]:
            if version_comps[indx].lower() != expected:
                return is_wintar, None

        # bsdtar_version = version_comps[1]
        # libarchive_version = version_comps[4]

        kind = libname + "/"

        have_library = False
        for component in version_comps[5:]:
            if component.lower().startswith(kind):
                have_library = True
                break

        return is_wintar, have_library

    def windows_system_tar_gz(tar):
        is_wintar, have_library = _windows_system_tar_have_library(tar, 'zlib')
        return is_wintar, have_library

    def windows_system_tar_bz2(tar):
        is_wintar, have_library = _windows_system_tar_have_library(tar, 'bz2lib')
        return is_wintar, have_library

    def windows_system_tar_xz(tar):
        is_wintar, have_library = _windows_system_tar_have_library(tar, 'liblzma')
        return is_wintar, have_library

    def windows_system_tar_lzma(tar):
        is_wintar, have_library = _windows_system_tar_have_library(tar, 'liblzma')
        return is_wintar, have_library

else:

    def windows_system_tar_gz(tar):
        return False, None

    def windows_system_tar_bz2(tar):
        return False, None

    def windows_system_tar_xz(tar):
        return False, None

    def windows_system_tar_lzma(tar):
        return False, None

class TestSConsTar(TestSCons):
    pass
