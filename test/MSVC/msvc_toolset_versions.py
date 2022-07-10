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
Test the msvc_toolset_versions method.
"""

import TestSCons

test = TestSCons.TestSCons()

test.skip_if_not_msvc()

import unittest

from SCons.Tool.MSCommon.vc import _VCVER
from SCons.Tool.MSCommon.vc import get_installed_vcs_components
from SCons.Tool.MSCommon.vc import msvc_default_version
from SCons.Tool.MSCommon import msvc_version_components
from SCons.Tool.MSCommon import msvc_toolset_versions
from SCons.Tool.MSCommon import MSVCArgumentError

installed_versions = get_installed_vcs_components()

class MsvcToolsetVersionsTests(unittest.TestCase):

    def test_valid_default_msvc(self):
        symbol = msvc_default_version()
        version_def = msvc_version_components(symbol)
        toolset_none_list = msvc_toolset_versions(msvc_version=None, full=False, sxs=False)
        toolset_full_list = msvc_toolset_versions(msvc_version=None, full=True, sxs=False)
        toolset_sxs_list = msvc_toolset_versions(msvc_version=None, full=False, sxs=True)
        toolset_all_list = msvc_toolset_versions(msvc_version=None, full=True, sxs=True)
        if version_def in installed_versions and version_def.msvc_vernum >= 14.1:
            # sxs list could be empty
            self.assertTrue(toolset_full_list, "Toolset full list is empty for msvc version {}".format(repr(None)))
            self.assertTrue(toolset_all_list, "Toolset all list is empty for msvc version {}".format(repr(None)))
        else:
            self.assertFalse(toolset_full_list, "Toolset full list is not empty for msvc version {}".format(repr(None)))
            self.assertFalse(toolset_sxs_list, "Toolset sxs list is not empty for msvc version {}".format(repr(None)))
            self.assertFalse(toolset_all_list, "Toolset all list is not empty for msvc version {}".format(repr(None)))
        self.assertFalse(toolset_none_list, "Toolset none list is not empty for msvc version {}".format(repr(None)))

    def test_valid_vcver(self):
        for symbol in _VCVER:
            version_def = msvc_version_components(symbol)
            toolset_none_list = msvc_toolset_versions(msvc_version=symbol, full=False, sxs=False)
            toolset_full_list = msvc_toolset_versions(msvc_version=symbol, full=True, sxs=False)
            toolset_sxs_list = msvc_toolset_versions(msvc_version=symbol, full=False, sxs=True)
            toolset_all_list = msvc_toolset_versions(msvc_version=symbol, full=True, sxs=True)
            if version_def in installed_versions and version_def.msvc_vernum >= 14.1:
                # sxs list could be empty
                self.assertTrue(toolset_full_list, "Toolset full list is empty for msvc version {}".format(repr(symbol)))
                self.assertTrue(toolset_all_list, "Toolset all list is empty for msvc version {}".format(repr(symbol)))
            else:
                self.assertFalse(toolset_full_list, "Toolset full list is not empty for msvc version {}".format(repr(symbol)))
                self.assertFalse(toolset_sxs_list, "Toolset sxs list is not empty for msvc version {}".format(repr(symbol)))
                self.assertFalse(toolset_all_list, "Toolset all list is not empty for msvc version {}".format(repr(symbol)))
            self.assertFalse(toolset_none_list, "Toolset none list is not empty for msvc version {}".format(repr(symbol)))

    def test_invalid_vcver(self):
        for symbol in ['6.0Exp', '14.3Exp', '99', '14.1Bug']:
            with self.assertRaises(MSVCArgumentError):
                msvc_toolset_versions(msvc_version=symbol)

unittest.main()

