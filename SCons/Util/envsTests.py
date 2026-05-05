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

import TestCmd

from SCons.Util.envs import (
    AddPathIfNotExists,
    AppendPath,
    PrependPath,
    is_valid_construction_var,
)

# These envs classes have no unit tests.
# MethodWrapper


class TestEnvs(unittest.TestCase):
    def test_PrependPath(self) -> None:
        """Test prepending to a path"""
        # have to specify the pathsep when adding so it's cross-platform
        # new duplicates existing - "moves to front"
        with self.subTest():
            p1: list | str = r'C:\dir\num\one;C:\dir\num\two'
            p1 = PrependPath(p1, r'C:\dir\num\two', sep=';')
            p1 = PrependPath(p1, r'C:\dir\num\three', sep=';')
            self.assertEqual(p1, r'C:\dir\num\three;C:\dir\num\two;C:\dir\num\one')

        # ... except with delete_existing false
        with self.subTest():
            p2: list | str = r'C:\dir\num\one;C:\dir\num\two'
            p2 = PrependPath(p2, r'C:\dir\num\two', sep=';', delete_existing=False)
            p2 = PrependPath(p2, r'C:\dir\num\three', sep=';', delete_existing=False)
            self.assertEqual(p2, r'C:\dir\num\three;C:\dir\num\one;C:\dir\num\two')

        # only last one is kept if there are dupes in new
        with self.subTest():
            p3: list | str = r'C:\dir\num\one'
            p3 = PrependPath(p3, r'C:\dir\num\two;C:\dir\num\three;C:\dir\num\two', sep=';')
            self.assertEqual(p3, r'C:\dir\num\two;C:\dir\num\three;C:\dir\num\one')

        # try prepending a Dir Node
        with self.subTest():
            p4: list | str = r'C:\dir\num\one'
            test = TestCmd.TestCmd(workdir='')
            test.subdir('sub')
            subdir = test.workpath('sub')
            p4 = PrependPath(p4, subdir, sep=';')
            self.assertEqual(p4, rf'{subdir};C:\dir\num\one')

        # try with initial list, adding string (result stays a list)
        with self.subTest():
            p5: list = [r'C:\dir\num\one', r'C:\dir\num\two']
            p5 = PrependPath(p5, r'C:\dir\num\two', sep=';')
            self.assertEqual(p5, [r'C:\dir\num\two', r'C:\dir\num\one'])
            p5 = PrependPath(p5, r'C:\dir\num\three', sep=';')
            self.assertEqual(p5, [r'C:\dir\num\three', r'C:\dir\num\two', r'C:\dir\num\one'])

        # try with initial string, adding list (result stays a string)
        with self.subTest():
            p6: list | str = r'C:\dir\num\one;C:\dir\num\two'
            p6 = PrependPath(p6, [r'C:\dir\num\two', r'C:\dir\num\three'], sep=';')
            self.assertEqual(p6, r'C:\dir\num\two;C:\dir\num\three;C:\dir\num\one')


    def test_AppendPath(self) -> None:
        """Test appending to a path."""
        # have to specify the pathsep when adding so it's cross-platform
        # new duplicates existing - "moves to end"
        with self.subTest():
            p1: list | str = r'C:\dir\num\one;C:\dir\num\two'
            p1 = AppendPath(p1, r'C:\dir\num\two', sep=';')
            p1 = AppendPath(p1, r'C:\dir\num\three', sep=';')
            self.assertEqual(p1, r'C:\dir\num\one;C:\dir\num\two;C:\dir\num\three')

        # ... except with delete_existing false
        with self.subTest():
            p2: list | str = r'C:\dir\num\one;C:\dir\num\two'
            p2 = AppendPath(p1, r'C:\dir\num\one', sep=';', delete_existing=False)
            p2 = AppendPath(p1, r'C:\dir\num\three', sep=';')
            self.assertEqual(p2, r'C:\dir\num\one;C:\dir\num\two;C:\dir\num\three')

        # only last one is kept if there are dupes in new
        with self.subTest():
            p3: list | str = r'C:\dir\num\one'
            p3 = AppendPath(p3, r'C:\dir\num\two;C:\dir\num\three;C:\dir\num\two', sep=';')
            self.assertEqual(p3, r'C:\dir\num\one;C:\dir\num\three;C:\dir\num\two')

        # try appending a Dir Node
        with self.subTest():
            p4: list | str = r'C:\dir\num\one'
            test = TestCmd.TestCmd(workdir='')
            test.subdir('sub')
            subdir = test.workpath('sub')
            p4 = AppendPath(p4, subdir, sep=';')
            self.assertEqual(p4, rf'C:\dir\num\one;{subdir}')

        # try with initial list, adding string (result stays a list)
        with self.subTest():
            p5: list = [r'C:\dir\num\one', r'C:\dir\num\two']
            p5 = AppendPath(p5, r'C:\dir\num\two', sep=';')
            p5 = AppendPath(p5, r'C:\dir\num\three', sep=';')
            self.assertEqual(p5, [r'C:\dir\num\one', r'C:\dir\num\two', r'C:\dir\num\three'])

        # try with initia string, adding list (result stays a string)
        with self.subTest():
            p6: list | str = r'C:\dir\num\one;C:\dir\num\two'
            p6 = AppendPath(p6, [r'C:\dir\num\two', r'C:\dir\num\three'], sep=';')
            self.assertEqual(p6, r'C:\dir\num\one;C:\dir\num\two;C:\dir\num\three')

    def test_addPathIfNotExists(self) -> None:
        """Test the AddPathIfNotExists() function"""
        env_dict = {'FOO': os.path.normpath('/foo/bar') + os.pathsep + \
                           os.path.normpath('/baz/blat'),
                    'BAR': os.path.normpath('/foo/bar') + os.pathsep + \
                           os.path.normpath('/baz/blat'),
                    'BLAT': [os.path.normpath('/foo/bar'),
                             os.path.normpath('/baz/blat')]}
        AddPathIfNotExists(env_dict, 'FOO', os.path.normpath('/foo/bar'))
        AddPathIfNotExists(env_dict, 'BAR', os.path.normpath('/bar/foo'))
        AddPathIfNotExists(env_dict, 'BAZ', os.path.normpath('/foo/baz'))
        AddPathIfNotExists(env_dict, 'BLAT', os.path.normpath('/baz/blat'))
        AddPathIfNotExists(env_dict, 'BLAT', os.path.normpath('/baz/foo'))

        assert env_dict['FOO'] == os.path.normpath('/foo/bar') + os.pathsep + \
               os.path.normpath('/baz/blat'), env_dict['FOO']
        assert env_dict['BAR'] == os.path.normpath('/bar/foo') + os.pathsep + \
               os.path.normpath('/foo/bar') + os.pathsep + \
               os.path.normpath('/baz/blat'), env_dict['BAR']
        assert env_dict['BAZ'] == os.path.normpath('/foo/baz'), env_dict['BAZ']
        assert env_dict['BLAT'] == [os.path.normpath('/baz/foo'),
                                    os.path.normpath('/foo/bar'),
                                    os.path.normpath('/baz/blat')], env_dict['BLAT']

    def test_is_valid_construction_var(self) -> None:
        """Testing is_valid_construction_var()"""
        r = is_valid_construction_var("_a")
        assert r, r
        r = is_valid_construction_var("z_")
        assert r, r
        r = is_valid_construction_var("X_")
        assert r, r
        r = is_valid_construction_var("2a")
        assert not r, r
        r = is_valid_construction_var("a2_")
        assert r, r
        r = is_valid_construction_var("/")
        assert not r, r
        r = is_valid_construction_var("_/")
        assert not r, r
        r = is_valid_construction_var("a/")
        assert not r, r
        r = is_valid_construction_var(".b")
        assert not r, r
        r = is_valid_construction_var("_.b")
        assert not r, r
        r = is_valid_construction_var("b1._")
        assert not r, r
        r = is_valid_construction_var("-b")
        assert not r, r
        r = is_valid_construction_var("_-b")
        assert not r, r
        r = is_valid_construction_var("b1-_")
        assert not r, r


if __name__ == "__main__":
    unittest.main()
