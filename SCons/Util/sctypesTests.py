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

import os
import unittest
from collections import UserDict, UserList, UserString

from SCons.Util.sctypes import (
    get_env_bool,
    get_environment_var,
    get_os_env_bool,
    is_Dict,
    is_List,
    is_String,
    is_Tuple,
    to_bytes,
    to_str,
    to_String,
)

# These sctypes classes have no unit tests.
# Null, NullSeq

class OsEnviron:
    """Used to temporarily mock os.environ"""

    def __init__(self, environ) -> None:
        self._environ = environ

    def start(self) -> None:
        self._stored = os.environ
        os.environ = self._environ

    def stop(self) -> None:
        os.environ = self._stored
        del self._stored

    def __enter__(self):
        self.start()
        return os.environ

    def __exit__(self, *args) -> None:
        self.stop()


class get_env_boolTestCase(unittest.TestCase):
    def test_missing(self) -> None:
        env = {}
        var = get_env_bool(env, 'FOO')
        assert var is False, "var should be False, not %s" % repr(var)
        env = {'FOO': '1'}
        var = get_env_bool(env, 'BAR')
        assert var is False, "var should be False, not %s" % repr(var)

    def test_true(self) -> None:
        for arg in ['TRUE', 'True', 'true',
                    'YES', 'Yes', 'yes',
                    'Y', 'y',
                    'ON', 'On', 'on',
                    '1', '20', '-1']:
            env = {'FOO': arg}
            var = get_env_bool(env, 'FOO')
            assert var is True, 'var should be True, not %s' % repr(var)

    def test_false(self) -> None:
        for arg in ['FALSE', 'False', 'false',
                    'NO', 'No', 'no',
                    'N', 'n',
                    'OFF', 'Off', 'off',
                    '0']:
            env = {'FOO': arg}
            var = get_env_bool(env, 'FOO', True)
            assert var is False, 'var should be True, not %s' % repr(var)

    def test_default(self) -> None:
        env = {'FOO': 'other'}
        var = get_env_bool(env, 'FOO', True)
        assert var is True, 'var should be True, not %s' % repr(var)
        var = get_env_bool(env, 'FOO', False)
        assert var is False, 'var should be False, not %s' % repr(var)


class get_os_env_boolTestCase(unittest.TestCase):
    def test_missing(self) -> None:
        with OsEnviron({}):
            var = get_os_env_bool('FOO')
            assert var is False, "var should be False, not %s" % repr(var)
        with OsEnviron({'FOO': '1'}):
            var = get_os_env_bool('BAR')
            assert var is False, "var should be False, not %s" % repr(var)

    def test_true(self) -> None:
        for arg in ['TRUE', 'True', 'true',
                    'YES', 'Yes', 'yes',
                    'Y', 'y',
                    'ON', 'On', 'on',
                    '1', '20', '-1']:
            with OsEnviron({'FOO': arg}):
                var = get_os_env_bool('FOO')
                assert var is True, 'var should be True, not %s' % repr(var)

    def test_false(self) -> None:
        for arg in ['FALSE', 'False', 'false',
                    'NO', 'No', 'no',
                    'N', 'n',
                    'OFF', 'Off', 'off',
                    '0']:
            with OsEnviron({'FOO': arg}):
                var = get_os_env_bool('FOO', True)
                assert var is False, 'var should be True, not %s' % repr(var)

    def test_default(self) -> None:
        with OsEnviron({'FOO': 'other'}):
            var = get_os_env_bool('FOO', True)
            assert var is True, 'var should be True, not %s' % repr(var)
            var = get_os_env_bool('FOO', False)
            assert var is False, 'var should be False, not %s' % repr(var)


class TestSctypes(unittest.TestCase):
    def test_is_Dict(self) -> None:
        assert is_Dict({})
        assert is_Dict(UserDict())
        try:
            class mydict(dict):
                pass
        except TypeError:
            pass
        else:
            assert is_Dict(mydict({}))
        assert not is_Dict([])
        assert not is_Dict(())
        assert not is_Dict("")


    def test_is_List(self) -> None:
        assert is_List([])
        assert is_List(UserList())
        try:
            class mylist(list):
                pass
        except TypeError:
            pass
        else:
            assert is_List(mylist([]))
        assert not is_List(())
        assert not is_List({})
        assert not is_List("")

    def test_is_String(self) -> None:
        assert is_String("")
        assert is_String(UserString(''))
        try:
            class mystr(str):
                pass
        except TypeError:
            pass
        else:
            assert is_String(mystr(''))
        assert not is_String({})
        assert not is_String([])
        assert not is_String(())

    def test_is_Tuple(self) -> None:
        assert is_Tuple(())
        try:
            class mytuple(tuple):
                pass
        except TypeError:
            pass
        else:
            assert is_Tuple(mytuple(()))
        assert not is_Tuple([])
        assert not is_Tuple({})
        assert not is_Tuple("")

    def test_to_Bytes(self) -> None:
        """ Test the to_Bytes method"""
        self.assertEqual(to_bytes('Hello'),
                         bytearray('Hello', 'utf-8'),
                         "Check that to_bytes creates byte array when presented with non byte string.")

    def test_to_String(self) -> None:
        """Test the to_String() method."""
        assert to_String(1) == "1", to_String(1)
        assert to_String([1, 2, 3]) == str([1, 2, 3]), to_String([1, 2, 3])
        assert to_String("foo") == "foo", to_String("foo")
        assert to_String(None) == 'None'
        # test low level string converters too
        assert to_str(None) == 'None'
        assert to_bytes(None) == b'None'

        s1 = UserString('blah')
        assert to_String(s1) == s1, s1
        assert to_String(s1) == 'blah', s1

        class Derived(UserString):
            pass

        s2 = Derived('foo')
        assert to_String(s2) == s2, s2
        assert to_String(s2) == 'foo', s2

    def test_get_env_var(self) -> None:
        """Testing get_environment_var()."""
        assert get_environment_var("$FOO") == "FOO", get_environment_var("$FOO")
        assert get_environment_var("${BAR}") == "BAR", get_environment_var("${BAR}")
        assert get_environment_var("$FOO_BAR1234") == "FOO_BAR1234", get_environment_var("$FOO_BAR1234")
        assert get_environment_var("${BAR_FOO1234}") == "BAR_FOO1234", get_environment_var("${BAR_FOO1234}")
        assert get_environment_var("${BAR}FOO") is None, get_environment_var("${BAR}FOO")
        assert get_environment_var("$BAR ") is None, get_environment_var("$BAR ")
        assert get_environment_var("FOO$BAR") is None, get_environment_var("FOO$BAR")
        assert get_environment_var("$FOO[0]") is None, get_environment_var("$FOO[0]")
        assert get_environment_var("${some('complex expression')}") is None, get_environment_var(
            "${some('complex expression')}")


if __name__ == "__main__":
    unittest.main()
