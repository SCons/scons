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
Test the msvc_query_version_toolset method.
"""

import TestSCons

test = TestSCons.TestSCons()

test.skip_if_not_msvc()

import unittest

from SCons.Tool.MSCommon.vc import _VCVER
from SCons.Tool.MSCommon import msvc_version_components
from SCons.Tool.MSCommon import msvc_extended_version_components
from SCons.Tool.MSCommon import msvc_toolset_versions
from SCons.Tool.MSCommon import msvc_query_version_toolset
from SCons.Tool.MSCommon import MSVCArgumentError

class MsvcQueryVersionToolsetTests(unittest.TestCase):

    def test_valid_default_msvc(self):
        for prefer_newest in (True, False):
            msvc_version, msvc_toolset_version = msvc_query_version_toolset(version=None, prefer_newest=prefer_newest)
            self.assertTrue(msvc_version, "msvc_version is undefined for msvc version {}".format(repr(None)))
            version_def = msvc_version_components(msvc_version)
            if version_def.msvc_vernum > 14.0:
                # VS2017 and later for toolset version
                self.assertTrue(msvc_toolset_version, "msvc_toolset_version is undefined for msvc version {}".format(repr(None)))

    def test_valid_vcver(self):
        for symbol in _VCVER:
            version_def = msvc_version_components(symbol)
            for prefer_newest in (True, False):
                msvc_version, msvc_toolset_version = msvc_query_version_toolset(version=symbol, prefer_newest=prefer_newest)
                self.assertTrue(msvc_version, "msvc_version is undefined for msvc version {}".format(repr(symbol)))
                if version_def.msvc_vernum > 14.0:
                    # VS2017 and later for toolset version
                    self.assertTrue(msvc_toolset_version, "msvc_toolset_version is undefined for msvc version {}".format(repr(symbol)))

    def test_valid_vcver_toolsets(self):
        for symbol in _VCVER:
            toolset_list = msvc_toolset_versions(msvc_version=symbol, full=True, sxs=True)
            if toolset_list is None:
                continue
            for toolset in toolset_list:
                extended_def = msvc_extended_version_components(toolset)
                for prefer_newest in (True, False):
                    version = extended_def.msvc_toolset_version
                    msvc_version, msvc_toolset_version = msvc_query_version_toolset(version=version, prefer_newest=prefer_newest)
                    self.assertTrue(msvc_version, "msvc_version is undefined for msvc toolset version {}".format(repr(toolset)))
                    if extended_def.msvc_vernum > 14.0:
                        # VS2017 and later for toolset version
                        self.assertTrue(msvc_toolset_version, "msvc_toolset_version is undefined for msvc toolset version {}".format(repr(toolset)))

    def test_invalid_vcver(self):
        for symbol in ['6.0Exp', '14.3Exp', '99', '14.1Bug']:
            for prefer_newest in (True, False):
                with self.assertRaises(MSVCArgumentError):
                    msvc_query_version_toolset(version=symbol, prefer_newest=prefer_newest)

    def test_invalid_vcver_toolsets(self):
        for symbol in ['14.31.123456', '14.31.1.1']:
            for prefer_newest in (True, False):
                with self.assertRaises(MSVCArgumentError):
                    msvc_query_version_toolset(version=symbol, prefer_newest=prefer_newest)

unittest.main()

