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

from __future__ import annotations

import functools
import hashlib
import sys
import unittest
import unittest.mock
import warnings
from collections import namedtuple

import SCons.Errors
from SCons.Util.hashes import (
    ALLOWED_HASH_FORMATS,
    _attempt_get_hash_function,
    _attempt_init_of_python_3_9_hash_object,
    _get_hash_object,
    _set_allowed_viable_default_hashes,
    hash_collect,
    hash_signature,
    set_hash_format,
)


class HashTestCase(unittest.TestCase):
    def test_collect(self) -> None:
        """Test collecting a list of signatures into a new signature value"""
        for algorithm, expected in {
            'md5': ('698d51a19d8a121ce581499d7b701668',
                    '8980c988edc2c78cc43ccb718c06efd5',
                    '53fd88c84ff8a285eb6e0a687e55b8c7'),
            'sha1': ('6216f8a75fd5bb3d5f22b6f9958cdede3fc086c2',
                     '42eda1b5dcb3586bccfb1c69f22f923145271d97',
                     '2eb2f7be4e883ebe52034281d818c91e1cf16256'),
            'sha256': ('f6e0a1e2ac41945a9aa7ff8a8aaa0cebc12a3bcc981a929ad5cf810a090e11ae',
                       '25235f0fcab8767b7b5ac6568786fbc4f7d5d83468f0626bf07c3dbeed391a7a',
                       'f8d3d0729bf2427e2e81007588356332e7e8c4133fae4bceb173b93f33411d17'),
        }.items():
            # if the current platform does not support the algorithm we're looking at,
            # skip the test steps for that algorithm, but display a warning to the user
            if algorithm not in ALLOWED_HASH_FORMATS:
                warnings.warn("Missing hash algorithm {} on this platform, cannot test with it".format(algorithm), ResourceWarning)
            else:
                hs = functools.partial(hash_signature, hash_format=algorithm)
                s = list(map(hs, ('111', '222', '333')))

                assert expected[0] == hash_collect(s[0:1], hash_format=algorithm)
                assert expected[1] == hash_collect(s[0:2], hash_format=algorithm)
                assert expected[2] == hash_collect(s, hash_format=algorithm)

    def test_MD5signature(self) -> None:
        """Test generating a signature"""
        for algorithm, expected in {
            'md5': ('698d51a19d8a121ce581499d7b701668',
                    'bcbe3365e6ac95ea2c0343a2395834dd'),
            'sha1': ('6216f8a75fd5bb3d5f22b6f9958cdede3fc086c2',
                     '1c6637a8f2e1f75e06ff9984894d6bd16a3a36a9'),
            'sha256': ('f6e0a1e2ac41945a9aa7ff8a8aaa0cebc12a3bcc981a929ad5cf810a090e11ae',
                       '9b871512327c09ce91dd649b3f96a63b7408ef267c8cc5710114e629730cb61f'),
        }.items():
            # if the current platform does not support the algorithm we're looking at,
            # skip the test steps for that algorithm, but display a warning to the user
            if algorithm not in ALLOWED_HASH_FORMATS:
                warnings.warn("Missing hash algorithm {} on this platform, cannot test with it".format(algorithm), ResourceWarning)
            else:
                s = hash_signature('111', hash_format=algorithm)
                assert expected[0] == s, s

                s = hash_signature('222', hash_format=algorithm)
                assert expected[1] == s, s


# This uses mocking out, which is platform specific. However, the FIPS
# behavior this is testing is also platform-specific, and only would be
# visible in hosts running Linux with the `fips_mode` kernel flag along
# with using OpenSSL.

class FIPSHashTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        ###############################
        # algorithm mocks, can check if we called with usedforsecurity=False for python >= 3.9
        self.fake_md5=lambda usedforsecurity=True: (usedforsecurity, 'md5')
        self.fake_sha1=lambda usedforsecurity=True: (usedforsecurity, 'sha1')
        self.fake_sha256=lambda usedforsecurity=True: (usedforsecurity, 'sha256')
        ###############################

        ###############################
        # hashlib mocks
        md5Available = unittest.mock.Mock(md5=self.fake_md5)
        del md5Available.sha1
        del md5Available.sha256
        self.md5Available=md5Available

        md5Default = unittest.mock.Mock(md5=self.fake_md5, sha1=self.fake_sha1)
        del md5Default.sha256
        self.md5Default=md5Default

        sha1Default = unittest.mock.Mock(sha1=self.fake_sha1, sha256=self.fake_sha256)
        del sha1Default.md5
        self.sha1Default=sha1Default

        sha256Default = unittest.mock.Mock(sha256=self.fake_sha256, **{'md5.side_effect': ValueError, 'sha1.side_effect': ValueError})
        self.sha256Default=sha256Default

        all_throw = unittest.mock.Mock(**{'md5.side_effect': ValueError, 'sha1.side_effect': ValueError, 'sha256.side_effect': ValueError})
        self.all_throw=all_throw

        no_algorithms = unittest.mock.Mock()
        del no_algorithms.md5
        del no_algorithms.sha1
        del no_algorithms.sha256
        del no_algorithms.nonexist
        self.no_algorithms=no_algorithms

        unsupported_algorithm = unittest.mock.Mock(unsupported=self.fake_sha256)
        del unsupported_algorithm.md5
        del unsupported_algorithm.sha1
        del unsupported_algorithm.sha256
        del unsupported_algorithm.unsupported
        self.unsupported_algorithm=unsupported_algorithm
        ###############################

        ###############################
        # system version mocks
        VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')
        v3_8 = VersionInfo(3, 8, 199, 'super-beta', 1337)
        v3_9 = VersionInfo(3, 9, 0, 'alpha', 0)
        v4_8 = VersionInfo(4, 8, 0, 'final', 0)

        self.sys_v3_8 = unittest.mock.Mock(version_info=v3_8)
        self.sys_v3_9 = unittest.mock.Mock(version_info=v3_9)
        self.sys_v4_8 = unittest.mock.Mock(version_info=v4_8)
        ###############################

    def test_basic_failover_bad_hashlib_hash_init(self) -> None:
        """Tests that if the hashing function is entirely missing from hashlib (hashlib returns None),
        the hash init function returns None"""
        assert _attempt_init_of_python_3_9_hash_object(None) is None

    def test_basic_failover_bad_hashlib_hash_get(self) -> None:
        """Tests that if the hashing function is entirely missing from hashlib (hashlib returns None),
        the hash get function returns None"""
        assert _attempt_get_hash_function("nonexist", self.no_algorithms) is None

    def test_usedforsecurity_flag_behavior(self) -> None:
        """Test usedforsecurity flag -> should be set to 'True' on older versions of python, and 'False' on Python >= 3.9"""
        for version, expected in {
            self.sys_v3_8: (True, 'md5'),
            self.sys_v3_9: (False, 'md5'),
            self.sys_v4_8: (False, 'md5'),
        }.items():
            assert _attempt_init_of_python_3_9_hash_object(self.fake_md5, version) == expected

    def test_automatic_default_to_md5(self) -> None:
        """Test automatic default to md5 even if sha1 available"""
        for version, expected in {
            self.sys_v3_8: (True, 'md5'),
            self.sys_v3_9: (False, 'md5'),
            self.sys_v4_8: (False, 'md5'),
        }.items():
            _set_allowed_viable_default_hashes(self.md5Default, version)
            set_hash_format(None, self.md5Default, version)
            assert _get_hash_object(None, self.md5Default, version) == expected

    def test_automatic_default_to_sha256(self) -> None:
        """Test automatic default to sha256 if other algorithms available but throw"""
        for version, expected in {
            self.sys_v3_8: (True, 'sha256'),
            self.sys_v3_9: (False, 'sha256'),
            self.sys_v4_8: (False, 'sha256'),
        }.items():
            _set_allowed_viable_default_hashes(self.sha256Default, version)
            set_hash_format(None, self.sha256Default, version)
            assert _get_hash_object(None, self.sha256Default, version) == expected

    def test_automatic_default_to_sha1(self) -> None:
        """Test automatic default to sha1 if md5 is missing from hashlib entirely"""
        for version, expected in {
            self.sys_v3_8: (True, 'sha1'),
            self.sys_v3_9: (False, 'sha1'),
            self.sys_v4_8: (False, 'sha1'),
        }.items():
            _set_allowed_viable_default_hashes(self.sha1Default, version)
            set_hash_format(None, self.sha1Default, version)
            assert _get_hash_object(None, self.sha1Default, version) == expected

    def test_no_available_algorithms(self) -> None:
        """expect exceptions on no available algorithms or when all algorithms throw"""
        self.assertRaises(SCons.Errors.SConsEnvironmentError, _set_allowed_viable_default_hashes, self.no_algorithms)
        self.assertRaises(SCons.Errors.SConsEnvironmentError, _set_allowed_viable_default_hashes, self.all_throw)
        self.assertRaises(SCons.Errors.SConsEnvironmentError, _set_allowed_viable_default_hashes, self.unsupported_algorithm)

    def test_bad_algorithm_set_attempt(self) -> None:
        """expect exceptions on user setting an unsupported algorithm selections, either by host or by SCons"""

        # nonexistant hash algorithm, not supported by SCons
        _set_allowed_viable_default_hashes(self.md5Available)
        self.assertRaises(SCons.Errors.UserError, set_hash_format, 'blah blah blah', hashlib_used=self.no_algorithms)

        # md5 is default-allowed, but in this case throws when we attempt to use it
        _set_allowed_viable_default_hashes(self.md5Available)
        self.assertRaises(SCons.Errors.UserError, set_hash_format, 'md5', hashlib_used=self.all_throw)

        # user attempts to use an algorithm that isn't supported by their current system but is supported by SCons
        _set_allowed_viable_default_hashes(self.sha1Default)
        self.assertRaises(SCons.Errors.UserError, set_hash_format, 'md5', hashlib_used=self.all_throw)

        # user attempts to use an algorithm that is supported by their current system but isn't supported by SCons
        _set_allowed_viable_default_hashes(self.sha1Default)
        self.assertRaises(SCons.Errors.UserError, set_hash_format, 'unsupported', hashlib_used=self.unsupported_algorithm)

    def tearDown(self) -> None:
        """Return SCons back to the normal global state for the hashing functions."""
        _set_allowed_viable_default_hashes(hashlib, sys)
        set_hash_format(None)


if __name__ == "__main__":
    unittest.main()
