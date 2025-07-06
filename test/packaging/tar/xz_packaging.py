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
This tests the SRC xz packager, which does the following:
 - create a tar package from the specified files
"""
import os
import os.path
import subprocess
import TestCmd
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()
tar = test.detect('TAR', 'tar')
if not tar:
    test.skip_test('tar not found, skipping test\n')

if TestCmd.IS_WINDOWS:

    # Windows 10 and later supplies windows/system32/tar.exe (bsdtar).
    # Not all versions support xz compression.  Check the version string
    # for liblzma support.

    def windows_system32_bsdtar_have_xz(tar):

        # Don't skip test if not confident this is the windows/system32/tar.exe (bsdtar).

        tar = os.path.normcase(os.path.abspath(tar))

        # windows tar.exe:
        #   %systemroot%/system32/tar.exe

        windir = os.environ.get("SystemRoot")
        if not windir:
            windir = os.environ.get("windir")
        if windir:
            expected = os.path.normcase(os.path.abspath(os.path.join(windir, "System32", "tar.exe")))
            if tar != expected:
                return False

        try:
            result = subprocess.run([f"{tar}", "--version"], capture_output=True, text=True, check=True)
            version_str = result.stdout
        except:
            version_str = None

        if not version_str:
            return False

        # print("tar.exe version:", version_str)

        # tar.exe --version (Windows 10, GH windows-2022):
        #   bsdtar 3.5.2 - libarchive 3.5.2 zlib/1.2.5.f-ipp

        # tar.exe --version (Windows 11):
        #   bsdtar 3.7.7 - libarchive 3.7.7 zlib/1.2.5.f-ipp liblzma/5.4.3 bz2lib/1.0.8 libzstd/1.5.4

        # tar.exe --version (GH windows-2025):
        #   bsdtar 3.7.7 - libarchive 3.7.7 zlib/1.2.13.1-motley liblzma/5.4.3 bz2lib/1.0.8 libzstd/1.5.5

        version_comps = version_str.split()
        if len(version_comps) < 5:
            return False

        for indx, expected in [
            (0, "bsdtar"), (2, "-"), (3, "libarchive"),
        ]:
            if version_comps[indx].lower() != expected:
                return False

        # Reasonably confident this is the windows/system32/tar.exe (bsdtar).

        # bsdtar_version = version_comps[1]
        # libarchive_version = version_comps[4]

        for component in version_comps[5:]:
            if component.lower().startswith("liblzma/"):
                # Don't skip test: xz/liblzma appears to be supported.
                return False

        # Skip test: xz/liblzma appears to be unsupported.
        return True

    skip_test = windows_system32_bsdtar_have_xz(tar)
    if skip_test:
        test.skip_test('windows tar found; xz not supported, skipping test\n')

test.subdir('src')

test.write([ 'src', 'main.c'], r"""
int main( int argc, char* argv[] )
{
  return 0;
}
""")

test.write('SConstruct', """
Program( 'src/main.c' )
env=Environment(tools=['packaging', 'filesystem', 'tar'])

env.Package( PACKAGETYPE  = 'src_tarxz',
             target       = 'src.tar.xz',
             PACKAGEROOT  = 'test',
             source       = [ 'src/main.c', 'SConstruct' ] )
""")

test.run(arguments='', stderr=None)

test.must_exist('src.tar.xz')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
