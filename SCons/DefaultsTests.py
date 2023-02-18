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

import os
import unittest
import collections

import TestCmd

from SCons.Defaults import mkdir_func, _defines, processDefines
from SCons.Errors import UserError


class DummyEnvironment(collections.UserDict):
    def __init__(self, **kwargs):
        super().__init__()
        self.data.update(kwargs)

    def subst(self, str_subst, target=None, source=None, conv=None):
        if str_subst[0] == '$':
            return self.data[str_subst[1:]]
        return str_subst

    def subst_list(self, str_subst, target=None, source=None, conv=None):
        if str_subst[0] == '$':
            return [self.data[str_subst[1:]]]
        return [[str_subst]]


class DefaultsTestCase(unittest.TestCase):
    def test_mkdir_func0(self):
        test = TestCmd.TestCmd(workdir='')
        test.subdir('sub')
        subdir2 = test.workpath('sub', 'dir1', 'dir2')
        # Simple smoke test
        mkdir_func(subdir2)
        mkdir_func(subdir2)  # 2nd time should be OK too

    def test_mkdir_func1(self):
        test = TestCmd.TestCmd(workdir='')
        test.subdir('sub')
        subdir1 = test.workpath('sub', 'dir1')
        subdir2 = test.workpath('sub', 'dir1', 'dir2')
        # No error if asked to create existing dir
        os.makedirs(subdir2)
        mkdir_func(subdir2)
        mkdir_func(subdir1)

    def test_mkdir_func2(self):
        test = TestCmd.TestCmd(workdir='')
        test.subdir('sub')
        subdir1 = test.workpath('sub', 'dir1')
        subdir2 = test.workpath('sub', 'dir1', 'dir2')
        file = test.workpath('sub', 'dir1', 'dir2', 'file')

        # make sure it does error if asked to create a dir
        # where there's already a file
        os.makedirs(subdir2)
        test.write(file, "test\n")
        try:
            mkdir_func(file)
        except OSError as e:
            pass
        else:
            self.fail("expected OSError")

    def test__defines_no_target_or_source_arg(self):
        """
        Verify that _defines() function can handle either or neither source or
        target being specified
        """
        env = DummyEnvironment()

        with self.subTest():
            # Neither source or target specified
            x = _defines('-D', ['A', 'B', 'C'], 'XYZ', env)
            self.assertEqual(x, ['-DAXYZ', '-DBXYZ', '-DCXYZ'])

        with self.subTest():
            # only source specified
            y = _defines('-D', ['AA', 'BA', 'CA'], 'XYZA', env, 'XYZ')
            self.assertEqual(y, ['-DAAXYZA', '-DBAXYZA', '-DCAXYZA'])

        with self.subTest():
            # source and target specified
            z = _defines('-D', ['AAB', 'BAB', 'CAB'], 'XYZAB', env, 'XYZ', 'abc')
            self.assertEqual(z, ['-DAABXYZAB', '-DBABXYZAB', '-DCABXYZAB'])

    def test_processDefines(self):
        """Verify correct handling in processDefines."""
        env = DummyEnvironment()

        with self.subTest():
            # macro name only
            rv = processDefines('name')
            self.assertEqual(rv, ['name'])

        with self.subTest():
            # macro with value
            rv = processDefines('name=val')
            self.assertEqual(rv, ['name=val'])

        with self.subTest():
            # space-separated macros
            rv = processDefines('name1 name2=val2')
            self.assertEqual(rv, ['name1', 'name2=val2'])

        with self.subTest():
            # single list
            rv = processDefines(['name', 'val'])
            self.assertEqual(rv, ['name', 'val'])

        with self.subTest():
            # single tuple
            rv = processDefines(('name', 'val'))
            self.assertEqual(rv, ['name=val'])

        with self.subTest():
            # single dict
            rv = processDefines({'foo': None, 'name': 'val'})
            self.assertEqual(rv, ['foo', 'name=val'])

        with self.subTest():
            # compound list
            rv = processDefines(['foo', ('name', 'val'), ['name2', 'val2']])
            self.assertEqual(rv, ['foo', 'name=val', 'name2=val2'])

        with self.subTest():
            # invalid tuple
            with self.assertRaises(
                UserError, msg="Invalid tuple should throw SCons.Errors.UserError"
            ):
                rv = processDefines([('name', 'val', 'bad')])


if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
