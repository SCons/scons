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

# TODO: issue #4376: since Python 3.12, CPython's posixpath.py does a test
#   import of 'posix', expecting it to fail on win32. However, if
#   SCons/Platform is in sys.path, it will find our posix module instead.
#   This happens in this unittest, since it's the script path. Remove
#   it before the stdlib imports. Better way to handle this problem?
import sys

if 'Platform' in sys.path[0]:
    platpath = sys.path.pop(0)
# pylint: disable=wrong-import-position
import collections
import unittest
import os
import sys

import SCons.compat
import SCons.Platform.virtualenv
import SCons.Util
# pylint: enable=wrong-import-position

# TODO: this test does a lot of fiddling with obsolete sys.real_prefix.
#   The 'virtualenv' tool used to force this in, but now uses venv-style
#   to follow Python since 3.3. Simplify once we think it's safe enough.

class Environment(collections.UserDict):
    """Mock environment for testing."""

    def Detect(self, cmd):
        return cmd

    def AppendENVPath(self, key, value) -> None:
        if SCons.Util.is_List(value):
            value = os.path.pathsep.join(value)
        if 'ENV' not in self:
            self['ENV'] = {}
        current = self['ENV'].get(key)
        if not current:
            self['ENV'][key] = value
        else:
            self['ENV'][key] = os.path.pathsep.join([current, value])

    def PrependENVPath(self, key, value) -> None:
        if SCons.Util.is_List(value):
            value = os.path.pathsep.join(value)
        if 'ENV' not in self:
            self['ENV'] = {}
        current = self['ENV'].get(key)
        if not current:
            self['ENV'][key] = value
        else:
            self['ENV'][key] = os.path.pathsep.join([value, current])


class SysPrefixes:
    """Context manager to mock/restore sys.{prefix,real_prefix.base_prefix}."""

    def __init__(self, prefix, real_prefix=None, base_prefix=None) -> None:
        self._prefix = prefix
        self._real_prefix = real_prefix
        self._base_prefix = base_prefix

    def start(self) -> None:
        self._store()
        sys.prefix = self._prefix
        if self._real_prefix is None:
            if hasattr(sys, 'real_prefix'):
                del sys.real_prefix
        else:
            sys.real_prefix = self._real_prefix
        if self._base_prefix is None:
            if hasattr(sys, 'base_prefix'):
                # Since 3.3, python always sets base_prefix. We used to
                # delete it, but now we need it to behave like Python:
                # if not pretending to be in a venv, should match sys.prefix.
                sys.base_prefix = sys.prefix
        else:
            sys.base_prefix = self._base_prefix

    def stop(self) -> None:
        self._restore()

    def __enter__(self):
        self.start()
        attrs = ('prefix', 'real_prefix', 'base_prefix')
        return {k: getattr(sys, k) for k in attrs if hasattr(sys, k)}

    def __exit__(self, *args) -> None:
        self.stop()

    def _store(self) -> None:
        s = dict()
        if hasattr(sys, 'real_prefix'):
            s['real_prefix'] = sys.real_prefix
        if hasattr(sys, 'base_prefix'):
            s['base_prefix'] = sys.base_prefix
        s['prefix'] = sys.prefix
        self._stored = s

    def _restore(self) -> None:
        s = self._stored
        if 'real_prefix' in s:
            sys.real_prefix = s['real_prefix']
        if 'base_prefix' in s:
            sys.base_prefix = s['base_prefix']
        if 'prefix' in s:
            sys.prefix = s['prefix']
        del self._stored


def _p(p):
    """Convert path string *p* from posix format to os-specific format."""
    drive = []
    if p.startswith('/') and sys.platform == 'win32':
        drive = ['C:']
    pieces = p.split('/')
    return os.path.sep.join(drive + pieces)


class _is_path_in_TestCase(unittest.TestCase):
    def test_false(self) -> None:
        for args in [
            ('', ''),
            ('', _p('/foo/bar')),
            (_p('/foo/bar'), ''),
            (_p('/foo/bar'), _p('/foo/bar')),
            (_p('/foo/bar'), _p('/foo/bar/geez')),
            (_p('/'), _p('/foo')),
            (_p('foo'), _p('foo/bar')),
        ]:
            with self.subTest():
                assert SCons.Platform.virtualenv._is_path_in(*args) is False, (
                    "_is_path_in(%r, %r) should be False" % args
                )

    def test__true(self) -> None:
        for args in [
            (_p('/foo'), _p('/')),
            (_p('/foo/bar'), _p('/foo')),
            (_p('/foo/bar/geez'), _p('/foo/bar')),
            (_p('/foo//bar//geez'), _p('/foo/bar')),
            (_p('/foo/bar/geez'), _p('/foo//bar')),
            (_p('/foo/bar/geez'), _p('//foo//bar')),
        ]:
            with self.subTest():
                assert SCons.Platform.virtualenv._is_path_in(*args) is True, (
                    "_is_path_in(%r, %r) should be True" % args
                )


class IsInVirtualenvTestCase(unittest.TestCase):
    def test_false(self) -> None:
        # "without virtualenv" - always false
        with SysPrefixes(_p('/prefix')):
            for p in [_p(''), _p('/foo'), _p('/prefix'), _p('/prefix/foo')]:
                with self.subTest():
                    assert SCons.Platform.virtualenv.IsInVirtualenv(p) is False, (
                        f"IsInVirtualenv({p!r}) should be False"
                    )

        # "with virtualenv"
        with SysPrefixes(_p('/virtualenv/prefix'), real_prefix=_p('/real/prefix')):
            for p in [
                _p(''),
                _p('/real/prefix/foo'),
                _p('/virtualenv/prefix'),
                _p('/virtualenv/prefix/bar/..'),
                _p('/virtualenv/prefix/bar/../../bleah'),
                _p('/virtualenv/bleah'),
            ]:
                with self.subTest():
                    assert SCons.Platform.virtualenv.IsInVirtualenv(p) is False, (
                        f"IsInVirtualenv({p!r}) should be False"
                    )

        # "with venv"
        with SysPrefixes(_p('/virtualenv/prefix'), base_prefix=_p('/base/prefix')):
            for p in [
                _p(''),
                _p('/base/prefix/foo'),
                _p('/virtualenv/prefix'),
                _p('/virtualenv/prefix/bar/..'),
                _p('/virtualenv/prefix/bar/../../bleah'),
                _p('/virtualenv/bleah'),
            ]:
                with self.subTest():
                    assert SCons.Platform.virtualenv.IsInVirtualenv(p) is False, (
                        f"IsInVirtualenv({p!r}) should be False"
                    )

    def test_true(self) -> None:
        # "with virtualenv"
        with SysPrefixes(_p('/virtualenv/prefix'), real_prefix=_p('/real/prefix')):
            for p in [_p('/virtualenv/prefix/foo'), _p('/virtualenv/prefix/foo/bar')]:
                with self.subTest():
                    assert SCons.Platform.virtualenv.IsInVirtualenv(p) is True, (
                        f"IsInVirtualenv({p!r}) should be True"
                    )

        # "with venv"
        with SysPrefixes(_p('/virtualenv/prefix'), base_prefix=_p('/base/prefix')):
            for p in [_p('/virtualenv/prefix/foo'), _p('/virtualenv/prefix/foo/bar')]:
                with self.subTest():
                    assert SCons.Platform.virtualenv.IsInVirtualenv(p) is True, (
                        f"IsInVirtualenv({p!r}) should be True"
                    )


class _inject_venv_pathTestCase(unittest.TestCase):
    def path_list(self):
        return [
            _p('/virtualenv/prefix/bin'),
            _p('/virtualenv/prefix'),
            _p('/virtualenv/prefix/../bar'),
            _p('/home/user/.local/bin'),
            _p('/usr/bin'),
            _p('/opt/bin'),
        ]

    def test_with_path_string(self) -> None:
        env = Environment()
        path_string = os.path.pathsep.join(self.path_list())
        with self.subTest(), SysPrefixes(
            _p('/virtualenv/prefix'), real_prefix=_p('/real/prefix')
        ):
            SCons.Platform.virtualenv._inject_venv_path(env, path_string)
            assert env['ENV']['PATH'] == _p('/virtualenv/prefix/bin'), env['ENV'][
                'PATH'
            ]

    def test_with_path_list(self) -> None:
        env = Environment()
        with self.subTest(), SysPrefixes(
            _p('/virtualenv/prefix'), real_prefix=_p('/real/prefix')
        ):
            SCons.Platform.virtualenv._inject_venv_path(env, self.path_list())
            assert env['ENV']['PATH'] == _p('/virtualenv/prefix/bin'), env['ENV'][
                'PATH'
            ]


class VirtualenvTestCase(unittest.TestCase):
    """Test the Virtualenv() function."""

    def test_no_venv(self) -> None:
        def _msg(given) -> str:
            return f"Virtualenv() should be empty, not {given!r}"

        with self.subTest(), SysPrefixes(_p('/prefix')):
            ve = SCons.Platform.virtualenv.Virtualenv()
            self.assertEqual(ve, "", msg=_msg(ve))

        with self.subTest(), SysPrefixes(
            _p('/base/prefix'), base_prefix=_p('/base/prefix')
        ):
            ve = SCons.Platform.virtualenv.Virtualenv()
            self.assertEqual(ve, "", msg=_msg(ve))

    def test_virtualenv(self) -> None:
        def _msg(expected, given) -> str:
            return f"Virtualenv() should == {_p(expected)!r}, not {given!r}"

        with self.subTest(), SysPrefixes(
            _p('/virtualenv/prefix'), real_prefix=_p('/real/prefix')
        ):
            ve = SCons.Platform.virtualenv.Virtualenv()
            assert ve == _p('/virtualenv/prefix'), _msg('/virtualenv/prefix', ve)

        with self.subTest(), SysPrefixes(
            _p('/same/prefix'), real_prefix=_p('/same/prefix')
        ):
            ve = SCons.Platform.virtualenv.Virtualenv()
            assert ve == _p('/same/prefix'), _msg('/same/prefix', ve)

        with SysPrefixes(_p('/virtualenv/prefix'), base_prefix=_p('/base/prefix')):
            ve = SCons.Platform.virtualenv.Virtualenv()
            assert ve == _p('/virtualenv/prefix'), _msg('/virtualenv/prefix', ve)


if __name__ == "__main__":
    unittest.main()
