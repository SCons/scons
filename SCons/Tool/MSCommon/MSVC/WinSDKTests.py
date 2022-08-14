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
Test Windows SDK functions for Microsoft Visual C/C++.
"""

import unittest

from SCons.Tool.MSCommon.MSVC import Config
from SCons.Tool.MSCommon.MSVC import WinSDK
from SCons.Tool.MSCommon.MSVC import Registry
from SCons.Tool.MSCommon.MSVC.Exceptions import MSVCInternalError

class Patch:

    class Config:

        class MSVC_SDK_VERSIONS:

            MSVC_SDK_VERSIONS = Config.MSVC_SDK_VERSIONS

            @classmethod
            def enable_copy(cls):
                hook = set(cls.MSVC_SDK_VERSIONS)
                Config.MSVC_SDK_VERSIONS = hook
                return hook

            @classmethod
            def restore(cls):
                Config.MSVC_SDK_VERSIONS = cls.MSVC_SDK_VERSIONS

    class Registry:

        class sdk_query_paths:

            sdk_query_paths = Registry.sdk_query_paths

            @classmethod
            def sdk_query_paths_duplicate(cls, version):
                sdk_roots = cls.sdk_query_paths(version)
                sdk_roots = sdk_roots + sdk_roots if sdk_roots else sdk_roots
                return sdk_roots

            @classmethod
            def enable_duplicate(cls):
                hook = cls.sdk_query_paths_duplicate
                Registry.sdk_query_paths = hook
                return hook

            @classmethod
            def restore(cls):
                Registry.sdk_query_paths = cls.sdk_query_paths

class WinSDKTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Patch.Registry.sdk_query_paths.enable_duplicate()

    @classmethod
    def tearDownClass(cls):
        Patch.Registry.sdk_query_paths.restore()

    def test_verify(self):
        MSVC_SDK_VERSIONS = Patch.Config.MSVC_SDK_VERSIONS.enable_copy()
        MSVC_SDK_VERSIONS.add('99.0')
        with self.assertRaises(MSVCInternalError):
            WinSDK.verify()
        Patch.Config.MSVC_SDK_VERSIONS.restore()

    def _run_reset(self):
        WinSDK.reset()
        self.assertFalse(WinSDK._sdk_map_cache, "WinSDK._sdk_map_cache was not reset")
        self.assertFalse(WinSDK._sdk_cache, "WinSDK._sdk_cache was not reset")

    def _run_get_msvc_sdk_version_list(self):
        for vcver in Config.MSVC_VERSION_SUFFIX.keys():
            for msvc_uwp_app in (True, False):
                _ = WinSDK.get_msvc_sdk_version_list(vcver, msvc_uwp_app=msvc_uwp_app)

    def _run_version_list_sdk_map(self):
        for vcver in Config.MSVC_VERSION_SUFFIX.keys():
            vs_def = Config.MSVC_VERSION_SUFFIX.get(vcver)
            if not vs_def.vc_sdk_versions:
                continue
            _ = WinSDK._version_list_sdk_map(vs_def.vc_sdk_versions)

    def test_version_list_sdk_map(self):
        self._run_version_list_sdk_map()
        self._run_version_list_sdk_map()
        self.assertTrue(WinSDK._sdk_map_cache, "WinSDK._sdk_map_cache is empty")

    def test_get_msvc_sdk_version_list(self):
        self._run_get_msvc_sdk_version_list()
        self._run_get_msvc_sdk_version_list()
        self.assertTrue(WinSDK._sdk_cache, "WinSDK._sdk_cache is empty")

    def test_get_msvc_sdk_version_list_empty(self):
        func = WinSDK.get_msvc_sdk_version_list
        for vcver in [None, '', '99', '99.9']:
            sdk_versions = func(vcver)
            self.assertFalse(sdk_versions, "{}: sdk versions list was not empty for msvc version {}".format(
                func.__name__, repr(vcver)
            ))

    def test_reset(self):
        self._run_reset()

if __name__ == "__main__":
    unittest.main()

