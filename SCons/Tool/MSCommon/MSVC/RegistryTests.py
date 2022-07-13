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
Test windows registry functions for Microsoft Visual C/C++.
"""

import unittest
import sys

from SCons.Tool.MSCommon.MSVC import Config
from SCons.Tool.MSCommon.MSVC import Registry

@unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
class RegistryTests(unittest.TestCase):

    _sdk_versions = None

    @classmethod
    def setUpClass(cls):
        cls._sdk_versions = []
        sdk_seen = set()
        for vs_def in Config.VISUALSTUDIO_DEFINITION_LIST:
            if not vs_def.vc_sdk_versions:
                continue
            for sdk_version in vs_def.vc_sdk_versions:
                if sdk_version in sdk_seen:
                    continue
                sdk_seen.add(sdk_version)
                cls._sdk_versions.append(sdk_version)

    def setUp(self):
        self.sdk_versions = self.__class__._sdk_versions

    def test_sdk_query_paths(self):
        for sdk_version in self.sdk_versions:
            _ = Registry.sdk_query_paths(sdk_version)

    def test_vstudio_sxs_vc7(self):
        suffix = Registry.vstudio_sxs_vc7('14.0')
        _ = Registry.microsoft_query_paths(suffix)

    def test_microsoft_query_keys(self):
        val = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
        for suffix in ['Temp', 'Tmp']:
            _ = Registry.registry_query_path(Registry.HKEY_LOCAL_MACHINE, val, suffix, expand=True)
            _ = Registry.registry_query_path(Registry.HKEY_LOCAL_MACHINE, val, suffix, expand=False)

    def test_registry_query_path(self):
        # need a better test for when VS2015 is no longer installed
        for component_reg in ('enterprise', 'professional', 'community'):
            suffix = Registry.devdiv_vs_servicing_component('14.0', component_reg)
            rval = Registry.microsoft_query_keys(suffix, component_reg)
            if not rval:
                continue

    def test_windows_kit_query_paths(self):
        for sdk_version in self.sdk_versions:
            _ = Registry.windows_kit_query_paths(sdk_version)

if __name__ == "__main__":
    unittest.main()

