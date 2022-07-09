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
Test msvc_version_components and msvc_extended_version_components functions.
"""

import unittest

from SCons.Tool.MSCommon.vc import _VCVER
from SCons.Tool.MSCommon import msvc_version_components
from SCons.Tool.MSCommon import msvc_extended_version_components

class MsvcVersionComponentsTests(unittest.TestCase):

    def test_valid_msvc_versions(self):
        for symbol in _VCVER:
            version_def = msvc_version_components(symbol)
            self.assertNotEqual(version_def, None, "Components tuple is None for {}".format(symbol))

    def test_invalid_msvc_versions(self):
        for symbol in ['14', '14Bug', '14.31', '14.31Bug']:
            version_def = msvc_version_components(symbol)
            self.assertEqual(version_def, None, "Components tuple is not None for {}".format(symbol))

    def test_valid_msvc_extended_versions(self):
        for symbol in _VCVER:
            extended_def = msvc_extended_version_components(symbol)
            self.assertNotEqual(extended_def, None, "Components tuple is None for {}".format(symbol))
        for symbol in ['14.31', '14.31.1', '14.31.12', '14.31.123', '14.31.1234', '14.31.12345', '14.31.17.2']:
            extended_def = msvc_extended_version_components(symbol)
            self.assertNotEqual(extended_def, None, "Components tuple is None for {}".format(symbol))

    def test_invalid_extended_msvc_versions(self):
        for symbol in ['14', '14.3Bug', '14.31Bug', '14.31.123456', '14.3.17', '14.3.1.1']:
            extended_def = msvc_extended_version_components(symbol)
            self.assertEqual(extended_def, None, "Components tuple is not None for {}".format(symbol))

if __name__ == "__main__":
    unittest.main()

