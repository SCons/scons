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

import collections
import unittest
import os
import sys

import SCons.compat
import SCons.Platform.virtualenv
import SCons.Util

class Environment(collections.UserDict):
    def Detect(self, cmd):
        return cmd

    def AppendENVPath(self, key, value):
        if SCons.Util.is_List(value):
            value =  os.path.pathsep.join(value)
        if 'ENV' not in self:
            self['ENV'] = {}
        current = self['ENV'].get(key)
        if not current:
            self['ENV'][key] = value
        else:
            self['ENV'][key] = os.path.pathsep.join([current, value])

    def PrependENVPath(self, key, value):
        if SCons.Util.is_List(value):
            value =  os.path.pathsep.join(value)
        if 'ENV' not in self:
            self['ENV'] = {}
        current = self['ENV'].get(key)
        if not current:
            self['ENV'][key] = value
        else:
            self['ENV'][key] = os.path.pathsep.join([value, current])

class SysPrefixes:
    """Used to temporarily mock sys.prefix, sys.real_prefix and sys.base_prefix"""
    def __init__(self, prefix, real_prefix=None, base_prefix=None):
        self._prefix = prefix
        self._real_prefix = real_prefix
        self._base_prefix = base_prefix

    def start(self):
        self._store()
        sys.prefix = self._prefix
        if self._real_prefix is None:
            if hasattr(sys, 'real_prefix'):
                del sys.real_prefix
        else:
            sys.real_prefix = self._real_prefix
        if self._base_prefix is None:
            if hasattr(sys, 'base_prefix'):
                del sys.base_prefix
        else:
            sys.base_prefix = self._base_prefix

    def stop(self):
        self._restore()

    def __enter__(self):
        self.start()
        attrs = ('prefix', 'real_prefix', 'base_prefix')
        return {k: getattr(sys, k) for k in attrs if hasattr(sys, k)}

    def __exit__(self, *args):
        self.stop()

    def _store(self):
        s = dict()
        if hasattr(sys, 'real_prefix'):
            s['real_prefix'] = sys.real_prefix
        if hasattr(sys, 'base_prefix'):
            s['base_prefix'] = sys.base_prefix
        s['prefix'] = sys.prefix
        self._stored = s

    def _restore(self):
        s = self._stored
        if 'real_prefix' in s:
            sys.real_prefix = s['real_prefix']
        if 'base_prefix' in s:
            sys.base_prefix = s['base_prefix']
        if 'prefix' in s:
            sys.prefix = s['prefix']
        del self._stored

def _p(p):
    """Converts path string **p** from posix format to os-specific format."""
    drive = []
    if p.startswith('/') and sys.platform == 'win32':
            drive = ['C:']
    pieces = p.split('/')
    return os.path.sep.join(drive + pieces)


class _is_path_in_TestCase(unittest.TestCase):
    def test_false(self):
        for args in [   ('',''),
                        ('', _p('/foo/bar')),
                        (_p('/foo/bar'), ''),
                        (_p('/foo/bar'), _p('/foo/bar')),
                        (_p('/foo/bar'), _p('/foo/bar/geez')),
                        (_p('/'), _p('/foo')),
                        (_p('foo'), _p('foo/bar')) ]:
            assert SCons.Platform.virtualenv._is_path_in(*args) is False, "_is_path_in(%r, %r) should be False" % args

    def test__true(self):
        for args in [   (_p('/foo'), _p('/')),
                        (_p('/foo/bar'), _p('/foo')),
                        (_p('/foo/bar/geez'), _p('/foo/bar')),
                        (_p('/foo//bar//geez'), _p('/foo/bar')),
                        (_p('/foo/bar/geez'), _p('/foo//bar')),
                        (_p('/foo/bar/geez'), _p('//foo//bar')) ]:
            assert SCons.Platform.virtualenv._is_path_in(*args) is True, "_is_path_in(%r, %r) should be True" % args

class IsInVirtualenvTestCase(unittest.TestCase):
    def test_false(self):
        # "without wirtualenv" - always false
        with SysPrefixes(_p('/prefix')):
            for p in [  _p(''),
                        _p('/foo'),
                        _p('/prefix'),
                        _p('/prefix/foo') ]:
                assert SCons.Platform.virtualenv.IsInVirtualenv(p) is False, "IsInVirtualenv(%r) should be False" % p

        # "with virtualenv"
        with SysPrefixes(_p('/virtualenv/prefix'), real_prefix=_p('/real/prefix')):
            for p in [  _p(''),
                        _p('/real/prefix/foo'),
                        _p('/virtualenv/prefix'),
                        _p('/virtualenv/prefix/bar/..'),
                        _p('/virtualenv/prefix/bar/../../bleah'),
                        _p('/virtualenv/bleah') ]:
                assert SCons.Platform.virtualenv.IsInVirtualenv(p) is False, "IsInVirtualenv(%r) should be False" % p

        # "with venv"
        with SysPrefixes(_p('/virtualenv/prefix'), base_prefix=_p('/base/prefix')):
            for p in [  _p(''),
                        _p('/base/prefix/foo'),
                        _p('/virtualenv/prefix'),
                        _p('/virtualenv/prefix/bar/..'),
                        _p('/virtualenv/prefix/bar/../../bleah'),
                        _p('/virtualenv/bleah') ]:
                assert SCons.Platform.virtualenv.IsInVirtualenv(p) is False, "IsInVirtualenv(%r) should be False" % p

    def test_true(self):
        # "with virtualenv"
        with SysPrefixes(_p('/virtualenv/prefix'), real_prefix=_p('/real/prefix')):
            for p in [  _p('/virtualenv/prefix/foo'),
                        _p('/virtualenv/prefix/foo/bar') ]:
                assert SCons.Platform.virtualenv.IsInVirtualenv(p) is True, "IsInVirtualenv(%r) should be True" % p

        # "with venv"
        with SysPrefixes(_p('/virtualenv/prefix'), base_prefix=_p('/base/prefix')):
            for p in [  _p('/virtualenv/prefix/foo'),
                        _p('/virtualenv/prefix/foo/bar') ]:
                assert SCons.Platform.virtualenv.IsInVirtualenv(p) is True, "IsInVirtualenv(%r) should be True" % p

class _inject_venv_pathTestCase(unittest.TestCase):
    def path_list(self):
        return [
            _p('/virtualenv/prefix/bin'),
            _p('/virtualenv/prefix'),
            _p('/virtualenv/prefix/../bar'),
            _p('/home/user/.local/bin'),
            _p('/usr/bin'),
            _p('/opt/bin')
        ]
    def test_with_path_string(self):
        env = Environment()
        path_string = os.path.pathsep.join(self.path_list())
        with SysPrefixes(_p('/virtualenv/prefix'), real_prefix=_p('/real/prefix')):
            SCons.Platform.virtualenv._inject_venv_path(env, path_string)
            assert env['ENV']['PATH'] == _p('/virtualenv/prefix/bin'), env['ENV']['PATH']

    def test_with_path_list(self):
        env = Environment()
        with SysPrefixes(_p('/virtualenv/prefix'), real_prefix=_p('/real/prefix')):
            SCons.Platform.virtualenv._inject_venv_path(env, self.path_list())
            assert env['ENV']['PATH'] == _p('/virtualenv/prefix/bin'), env['ENV']['PATH']

class VirtualenvTestCase(unittest.TestCase):
    def test_none(self):
        def _msg(given):
            return "Virtualenv() should be None, not %s" % repr(given)

        with SysPrefixes(_p('/prefix')):
            ve = SCons.Platform.virtualenv.Virtualenv()
            assert ve is None , _msg(ve)
        with SysPrefixes(_p('/base/prefix'), base_prefix=_p('/base/prefix')):
            ve = SCons.Platform.virtualenv.Virtualenv()
            assert ve is None, _msg(ve)

    def test_not_none(self):
        def _msg(expected, given):
            return "Virtualenv() should == %r, not %s" % (_p(expected), repr(given))

        with SysPrefixes(_p('/virtualenv/prefix'), real_prefix=_p('/real/prefix')):
            ve = SCons.Platform.virtualenv.Virtualenv()
            assert ve == _p('/virtualenv/prefix'), _msg('/virtualenv/prefix', ve)
        with SysPrefixes(_p('/same/prefix'), real_prefix=_p('/same/prefix')):
            ve = SCons.Platform.virtualenv.Virtualenv()
            assert ve == _p('/same/prefix'),  _msg('/same/prefix', ve)
        with SysPrefixes(_p('/virtualenv/prefix'), base_prefix=_p('/base/prefix')):
            ve = SCons.Platform.virtualenv.Virtualenv()
            assert ve == _p('/virtualenv/prefix'),  _msg('/virtualenv/prefix', ve)


if __name__ == "__main__":
    unittest.main()


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
