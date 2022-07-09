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
Test the msvc_sdk_versions method.
"""

import TestSCons

test = TestSCons.TestSCons()

test.skip_if_not_msvc()

import unittest

from SCons.Tool.MSCommon.vc import _VCVER
from SCons.Tool.MSCommon.vc import msvc_default_version
from SCons.Tool.MSCommon import msvc_version_components
from SCons.Tool.MSCommon import msvc_extended_version_components
from SCons.Tool.MSCommon import msvc_sdk_versions
from SCons.Tool.MSCommon import msvc_toolset_versions
from SCons.Tool.MSCommon import MSVCArgumentError

class MsvcSdkVersionsTests(unittest.TestCase):

    def test_valid_default_msvc(self):
        symbol = msvc_default_version()
        version_def = msvc_version_components(symbol)
        for msvc_uwp_app in (True, False):
            sdk_list = msvc_sdk_versions(version=None, msvc_uwp_app=msvc_uwp_app)
            if version_def.msvc_vernum >= 14.0:
                self.assertTrue(sdk_list, "SDK list is empty for msvc version {}".format(repr(symbol)))
            else:
                self.assertFalse(sdk_list, "SDK list is not empty for msvc version {}".format(repr(symbol)))

    def test_valid_vcver(self):
        for symbol in _VCVER:
            version_def = msvc_version_components(symbol)
            for msvc_uwp_app in (True, False):
                sdk_list = msvc_sdk_versions(version=symbol, msvc_uwp_app=msvc_uwp_app)
                if version_def.msvc_vernum >= 14.0:
                    self.assertTrue(sdk_list, "SDK list is empty for msvc version {}".format(repr(symbol)))
                else:
                    self.assertFalse(sdk_list, "SDK list is not empty for msvc version {}".format(repr(symbol)))

    def test_valid_vcver_toolsets(self):
        for symbol in _VCVER:
            toolset_list = msvc_toolset_versions(msvc_version=symbol, full=True, sxs=True)
            if toolset_list is None:
                continue
            for toolset in toolset_list:
                extended_def = msvc_extended_version_components(toolset)
                for msvc_uwp_app in (True, False):
                    sdk_list = msvc_sdk_versions(version=extended_def.msvc_toolset_version, msvc_uwp_app=msvc_uwp_app)
                    self.assertTrue(sdk_list, "SDK list is empty for msvc toolset version {}".format(repr(toolset)))

    def test_invalid_vcver(self):
        for symbol in ['6.0Exp', '14.3Exp', '99', '14.1Bug']:
            for msvc_uwp_app in (True, False):
                with self.assertRaises(MSVCArgumentError):
                    msvc_sdk_versions(version=symbol, msvc_uwp_app=msvc_uwp_app)

    def test_invalid_vcver_toolsets(self):
        for symbol in ['14.31.123456', '14.31.1.1']:
            for msvc_uwp_app in (True, False):
                with self.assertRaises(MSVCArgumentError):
                    msvc_sdk_versions(version=symbol, msvc_uwp_app=msvc_uwp_app)

unittest.main()

