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
Test helper functions for Microsoft Visual C/C++.
"""

import unittest
import os
import re

from SCons.Tool.MSCommon.MSVC import Config
from SCons.Tool.MSCommon.MSVC import Util
from SCons.Tool.MSCommon.MSVC import WinSDK

class Data:

    UTIL_PARENT_DIR = os.path.join(os.path.dirname(Util.__file__), os.pardir)

class UtilTests(unittest.TestCase):

    def test_listdir_dirs(self):
        func = Util.listdir_dirs
        for dirname, expect in [
            (None, False), ('', False), ('doesnotexist.xyz.abc', False),
            (Data.UTIL_PARENT_DIR, True),
        ]:
            dirs = func(dirname)
            self.assertTrue((len(dirs) > 0) == expect, "{}({}): {}".format(
                func.__name__, repr(dirname), 'list is empty' if expect else 'list is not empty'
            ))

    def test_process_path(self):
        func = Util.process_path
        for p, expect in [
            (None, True), ('', True),
            ('doesnotexist.xyz.abc', False), (Data.UTIL_PARENT_DIR, False),
        ]:
            rval = func(p)
            self.assertTrue((p == rval) == expect, "{}({}): {}".format(
                func.__name__, repr(p), repr(rval)
            ))

    def test_get_version_prefix(self):
        func = Util.get_version_prefix
        for version, expect in [
            (None, ''), ('', ''),
            ('.', ''), ('0..0', ''), ('.0', ''), ('0.', ''), ('0.0.', ''),
            ('0', '0'), ('0Abc', '0'), ('0 0', '0'), ('0,0', '0'),
            ('0.0', '0.0'), ('0.0.0', '0.0.0'), ('0.0.0.0', '0.0.0.0'), ('0.0.0.0.0', '0.0.0.0.0'),
            ('00.00.00000', '00.00.00000'), ('00.00.00.0', '00.00.00.0'), ('00.00.00.00', '00.00.00.00'), ('00.0.00000.0', '00.0.00000.0'),
            ('0.0A', '0.0'), ('0.0.0B', '0.0.0'), ('0.0.0.0 C', '0.0.0.0'), ('0.0.0.0.0 D', '0.0.0.0.0'),
        ]:
            prefix = func(version)
            self.assertTrue(prefix == expect, "{}({}): {} != {}".format(
                func.__name__, repr(version), repr(prefix), repr(expect)
            ))

    def test_get_msvc_version_prefix(self):
        func = Util.get_msvc_version_prefix
        for version, expect in [
            (None, ''), ('', ''),
            ('.', ''), ('0..0', ''), ('.0', ''), ('0.', ''), ('0.0.', ''),
            ('0', ''), ('0Abc', ''), ('0 0', ''), ('0,0', ''),
            ('0.0', ''), ('0.0.0', ''), ('0.0.0.0', ''), ('0.0.0.0.0', ''),
            ('1.0A', '1.0'), ('1.0.0B', '1.0'), ('1.0.0.0 C', '1.0'), ('1.0.0.0.0 D', '1.0'),
            ('1.00A', '1.0'), ('1.00.0B', '1.0'), ('1.00.0.0 C', '1.0'), ('1.00.0.0.0 D', '1.0'),
        ]:
            prefix = func(version)
            self.assertTrue(prefix == expect, "{}({}): {} != {}".format(
                func.__name__, repr(version), repr(prefix), repr(expect)
            ))

    def test_is_toolset_full(self):
        func = Util.is_toolset_full
        for toolset, expect in [
            (None, False), ('', False),
            ('14.1.', False), ('14.10.', False), ('14.10.00000.', False), ('14.10.000000', False), ('14.1Exp', False),
            ('14.1', True), ('14.10', True), ('14.10.0', True), ('14.10.00', True), ('14.10.000', True), ('14.10.0000', True), ('14.10.0000', True),
        ]:
            rval = func(toolset)
            self.assertTrue(rval == expect, "{}({}) != {}".format(
                func.__name__, repr(toolset), repr(rval)
            ))

    def test_is_toolset_140(self):
        func = Util.is_toolset_140
        for toolset, expect in [
            (None, False), ('', False),
            ('14.0.', False), ('14.00.', False), ('14.00.00000.', False), ('14.00.000000', False), ('14.0Exp', False),
            ('14.0', True), ('14.00', True), ('14.00.0', True), ('14.00.00', True), ('14.00.000', True), ('14.00.0000', True), ('14.00.0000', True),
        ]:
            rval = func(toolset)
            self.assertTrue(rval == expect, "{}({}) != {}".format(
                func.__name__, repr(toolset), repr(rval)
            ))

    def test_is_toolset_sxs(self):
        func = Util.is_toolset_sxs
        for toolset, expect in [
            (None, False), ('', False),
            ('14.2.', False), ('14.29.', False), ('14.29.1.', False), ('14.29.16.', False), ('14.29.16.1.', False),
            ('14.29.16.1', True), ('14.29.16.10', True),
        ]:
            rval = func(toolset)
            self.assertTrue(rval == expect, "{}({}) != {}".format(
                func.__name__, repr(toolset), repr(rval)
            ))

    def test_msvc_version_components(self):
        func = Util.msvc_version_components
        for vcver, expect in [
            (None, False), ('', False), ('ABC', False), ('14', False), ('14.1.', False), ('14.16', False),
            ('14.1', True), ('14.1Exp', True),
            ('14.1Bug', False),
        ]:
            comps_def = func(vcver)
            msg = 'msvc version components definition is None' if expect else 'msvc version components definition is not None'
            self.assertTrue((comps_def is not None) == expect, "{}({}): {}".format(
                func.__name__, repr(vcver), repr(msg)
            ))
        for vcver in Config.MSVC_VERSION_SUFFIX.keys():
            comps_def = func(vcver)
            self.assertNotEqual(comps_def, None, "{}({}) is None".format(
                func.__name__, repr(vcver)
            ))

    def test_msvc_extended_version_components(self):
        func = Util.msvc_extended_version_components
        # normal code paths
        for vcver, expect in [
            (None, False), ('', False), ('ABC', False), ('14', False), ('14.1.', False),
            ('14.1', True), ('14.16', True),
            ('14.1Exp', True), ('14.16Exp', True),
            ('14.16.2', True), ('14.16.27', True), ('14.16.270', True),
            ('14.16.2702', True), ('14.16.2702', True), ('14.16.27023', True),
            ('14.16.270239', False),
            ('14.16.2Exp', True), ('14.16.27Exp', True), ('14.16.270Exp', True),
            ('14.16.2702Exp', True), ('14.16.2702Exp', True), ('14.16.27023Exp', True),
            ('14.16.270239Exp', False),
            ('14.28.16.9', True), ('14.28.16.10', True),
            ('14.28.16.9Exp', False), ('14.28.16.10Exp', False),
        ]:
            comps_def = func(vcver)
            msg = 'msvc extended version components definition is None' if expect else 'msvc extended version components definition is not None'
            self.assertTrue((comps_def is not None) == expect, "{}({}): {}".format(
                func.__name__, repr(vcver), repr(msg)
            ))
        for vcver in Config.MSVC_VERSION_SUFFIX.keys():
            comps_def = func(vcver)
            self.assertNotEqual(comps_def, None, "{}({}) is None".format(
                func.__name__, repr(vcver)
            ))
        # force 'just in case' guard code path
        save_re = Util.re_extended_version
        Util.re_extended_version = re.compile(r'^(?P<version>[0-9]+)$')
        for vcver, expect in [
            ('14', False),
        ]:
            comps_def = func(vcver)
            msg = 'msvc extended version components definition is None' if expect else 'msvc extended version components definition is not None'
            self.assertTrue((comps_def is not None) == expect, "{}({}): {}".format(
                func.__name__, repr(vcver), repr(msg)
            ))
        Util.re_extended_version = save_re

    def test_msvc_sdk_version_components(self):
        func = Util.msvc_sdk_version_components
        for vcver, expect in [
            (None, False), ('', False), ('ABC', False), ('14', False), ('14.1.', False), ('14.16', False),
            ('8.1', True), ('10.0', True), ('10.0.20348.0', True),
        ]:
            comps_def = func(vcver)
            msg = 'msvc sdk version components definition is None' if expect else 'msvc sdk version components definition is not None'
            self.assertTrue((comps_def is not None) == expect, "{}({}): {}".format(
                func.__name__, repr(vcver), repr(msg)
            ))
        for vcver in Config.MSVC_VERSION_SUFFIX.keys():
            comps_def = func(vcver)
            sdk_list = WinSDK.get_msvc_sdk_version_list(vcver, msvc_uwp_app=False)
            for sdk_version in sdk_list:
                comps_def = func(sdk_version)
                self.assertNotEqual(comps_def, None, "{}({}) is None".format(
                    func.__name__, repr(vcver)
                ))

if __name__ == "__main__":
    unittest.main()

