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
Test constants and initialized data structures for Microsoft Visual C/C++.
"""

import unittest

from SCons.Tool.MSCommon import vc
from SCons.Tool.MSCommon.MSVC import Config
from SCons.Tool.MSCommon.MSVC.Exceptions import MSVCInternalError


class Patch:
    class vc:
        class _VCVER:
            _VCVER = vc._VCVER

            @classmethod
            def enable_copy(cls):
                hook = list(cls._VCVER)
                vc._VCVER = hook
                return hook

            @classmethod
            def restore(cls):
                vc._VCVER = cls._VCVER

    class Config:
        class MSVC_VERSION_INTERNAL:
            MSVC_VERSION_INTERNAL = Config.MSVC_VERSION_INTERNAL

            @classmethod
            def enable_copy(cls):
                hook = dict(cls.MSVC_VERSION_INTERNAL)
                Config.MSVC_VERSION_INTERNAL = hook
                return hook

            @classmethod
            def restore(cls):
                Config.MSVC_VERSION_INTERNAL = cls.MSVC_VERSION_INTERNAL


class ConfigTests(unittest.TestCase):

    def test_vcver(self):
        # all vc._VCVER in Config.MSVC_VERSION_SUFFIX
        _VCVER = Patch.vc._VCVER.enable_copy()
        _VCVER.append('99.9')
        with self.assertRaises(MSVCInternalError):
            Config.verify()
        Patch.vc._VCVER.restore()

    def test_msvc_version_internal(self):
        # all vc._VCVER numstr in Config.MSVC_VERSION_INTERNAL
        MSVC_VERSION_INTERNAL = Patch.Config.MSVC_VERSION_INTERNAL.enable_copy()
        del MSVC_VERSION_INTERNAL['14.3']
        with self.assertRaises(MSVCInternalError):
            Config.verify()
        Patch.Config.MSVC_VERSION_INTERNAL.restore()

    def test_verify(self):
        Config.verify()


if __name__ == "__main__":
    unittest.main()
