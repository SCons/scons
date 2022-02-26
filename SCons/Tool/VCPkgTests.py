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
from shutil import rmtree
from pathlib import Path
import unittest

import TestUnit

import SCons.Errors
import SCons.Tool.vcpkg
from SCons.Environment import Environment

class VCPkgTestCase(unittest.TestCase):
    def make_mock_vcpkg_dir(self, include_vcpkg_exe = False):
        """Creates a mock vcpkg directory under the temp directory and returns its path"""

        vcpkg_root = os.environ['TEMP'] + '/scons_vcpkg_test'

        # Delete it if it already exists
        rmtree(vcpkg_root, ignore_errors = True)

        os.mkdir(vcpkg_root)

        # Ensure that the .vcpkg-root sentinel file exists
        Path(vcpkg_root + '/.vcpkg-root').touch()

        if include_vcpkg_exe:
            if os.name == 'nt':
                Path(vcpkg_root + '/vcpkg.exe').touch()
            else:
                Path(vcpkg_root + '/vcpkg').touch()

        return vcpkg_root


    def test_VCPKGROOT(self):
        """Test that VCPkg() fails with an exception if the VCPKGROOT environment variable is unset or invalid"""

        env = Environment(tools=['default','vcpkg'])

        # VCPKGROOT unset (should fail)
        exc_caught = None
        try:
            if 'VCPKGROOT' in env:
                del env['VCPKGROOT']
            env.VCPkg('pretend_package')
        except SCons.Errors.UserError as e:
            exc_caught = 1
            assert "$VCPKGROOT must be set" in str(e), e
        assert exc_caught, "did not catch expected UserError"

        # VCPKGROOT pointing to a bogus path (should fail)
        exc_caught = None
        try:
            env['VCPKGROOT'] = '/usr/bin/phony/path'
            env.VCPkg('pretend_package')
        except SCons.Errors.UserError as e:
            exc_caught = 1
            assert "$VCPKGROOT must point to" in str(e), e
        assert exc_caught, "did not catch expected UserError"

        # VCPKGROOT pointing to a valid path that is not a vcpkg instance (should fail)
        exc_caught = None
        try:
            env['VCPKGROOT'] = '#/'
            env.VCPkg('pretend_package')
        except SCons.Errors.UserError as e:
            exc_caught = 1
            assert "$VCPKGROOT must point to" in str(e), e
        assert exc_caught, "did not catch expected UserError"

        # VCPKGROOT pointing to a mock vcpkg instance (should succeed)
        env['VCPKGROOT'] = self.make_mock_vcpkg_dir(include_vcpkg_exe = True)
        orig_call_vcpkg = SCons.Tool.vcpkg._call_vcpkg
        orig_get_package_version = SCons.Tool.vcpkg._get_package_version
        orig_read_vcpkg_file_list = SCons.Tool.vcpkg._read_vcpkg_file_list
        installed_package = False
        def mock_call_vcpkg_exe(env, params, check_output = False):
            if 'install' in params and 'pretend_package' in params:
                installed_pacakge = True
                return 0
            if 'depend-info' in params and check_output:
                return params[1] + ':'

            if check_output:
                return ''
            else:
                return 0
        def mock_get_package_version(env, spec):
            assert spec == 'pretend_package', "queried for unexpected package '" + spec + "'"
            return '1.0.0'
        def mock_read_vcpkg_file_list(env, list_file):
            return [env.File('$VCPKGROOT/installed/x64-windows/lib/pretend_package.lib')]
            
        SCons.Tool.vcpkg._call_vcpkg = mock_call_vcpkg_exe
        SCons.Tool.vcpkg._get_package_version = mock_get_package_version
        SCons.Tool.vcpkg._read_vcpkg_file_list = mock_read_vcpkg_file_list
        try:
            env.VCPkg('pretend_package')
        finally:
            rmtree(env['VCPKGROOT'])
            SCons.Tool.vcpkg._call_vcpkg = orig_call_vcpkg
            SCons.Tool.vcpkg._get_pacakge_version = orig_get_package_version
            SCons.Tool.vcpkg._get_pacakge_version = orig_read_vcpkg_file_list


if __name__ == "__main__":
    suite = unittest.makeSuite(VCPkgTestCase, 'test_')
    TestUnit.run(suite)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
