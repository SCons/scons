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

import os.path
import unittest

import SCons.Errors
import SCons.Variables

import TestCmd
from TestCmd import IS_WINDOWS, IS_ROOT

class PathVariableTestCase(unittest.TestCase):
    def test_PathVariable(self) -> None:
        """Test PathVariable creation"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PathVariable('test',
                                          'test build variable help',
                                          '/default/path'))

        o = opts.options[0]
        assert o.key == 'test', o.key
        assert o.help == 'test build variable help ( /path/to/test )', repr(o.help)
        assert o.default == '/default/path', o.default
        assert o.validator is not None, o.validator
        assert o.converter is None, o.converter

    def test_PathExists(self):
        """Test the PathExists validator"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PathVariable('test',
                                          'test build variable help',
                                          '/default/path',
                                          SCons.Variables.PathVariable.PathExists))

        test = TestCmd.TestCmd(workdir='')
        test.write('exists', 'exists\n')

        o = opts.options[0]
        o.validator('X', test.workpath('exists'), {})

        dne = test.workpath('does_not_exist')
        with self.assertRaises(SCons.Errors.UserError) as cm:
            o.validator('X', dne, {})
        e = cm.exception
        self.assertEqual(str(e), f"Path for variable 'X' does not exist: {dne}")

    def test_PathIsDir(self):
        """Test the PathIsDir validator"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PathVariable('test',
                                          'test build variable help',
                                          '/default/path',
                                          SCons.Variables.PathVariable.PathIsDir))

        test = TestCmd.TestCmd(workdir='')
        test.subdir('dir')
        test.write('file', "file\n")

        o = opts.options[0]
        o.validator('X', test.workpath('dir'), {})

        f = test.workpath('file')
        with self.assertRaises(SCons.Errors.UserError) as cm:
            o.validator('X', f, {})
        e = cm.exception
        self.assertEqual(str(e), f"Directory path for variable 'X' is a file: {f}")

        dne = test.workpath('does_not_exist')
        with self.assertRaises(SCons.Errors.UserError) as cm:
            o.validator('X', dne, {})
        e = cm.exception
        self.assertEqual(str(e), f"Directory path for variable 'X' does not exist: {dne}")

    def test_PathIsDirCreate(self):
        """Test the PathIsDirCreate validator."""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PathVariable('test',
                                          'test build variable help',
                                          '/default/path',
                                          SCons.Variables.PathVariable.PathIsDirCreate))

        test = TestCmd.TestCmd(workdir='')
        test.write('file', "file\n")

        o = opts.options[0]

        d = test.workpath('dir')
        o.validator('X', d, {})
        assert os.path.isdir(d)

        f = test.workpath('file')
        with self.assertRaises(SCons.Errors.UserError) as cm:
            o.validator('X', f, {})
        e = cm.exception
        self.assertEqual(str(e), f"Path for variable 'X' is a file, not a directory: {f}")


    @unittest.skipIf(IS_ROOT, "Skip creating bad directory if running as root.")
    def test_PathIsDirCreate_bad_dir(self):
        """Test the PathIsDirCreate validator with an uncreatable dir.

        Split from :meth:`test_PathIsDirCreate` to be able to skip on root.
        We want to be able to skip only this one testcase and run the rest.
        """
        opts = SCons.Variables.Variables()
        opts.Add(
            SCons.Variables.PathVariable(
                'test',
                'test build variable help',
                '/default/path',
                SCons.Variables.PathVariable.PathIsDirCreate,
            )
        )

        test = TestCmd.TestCmd(workdir='')
        o = opts.options[0]

        # pick a directory path that can't be mkdir'd
        if IS_WINDOWS:
            f = r'\\noserver\noshare\yyy\zzz'
        else:
            f = '/yyy/zzz'
        with self.assertRaises(SCons.Errors.UserError) as cm:
            o.validator('X', f, {})
        e = cm.exception
        self.assertEqual(str(e), f"Path for variable 'X' could not be created: {f}")


    def test_PathIsFile(self):
        """Test the PathIsFile validator."""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PathVariable('test',
                                          'test build variable help',
                                          '/default/path',
                                          SCons.Variables.PathVariable.PathIsFile))

        test = TestCmd.TestCmd(workdir='')
        test.subdir('dir')
        test.write('file', "file\n")

        o = opts.options[0]
        o.validator('X', test.workpath('file'), {})

        d = test.workpath('d')
        with self.assertRaises(SCons.Errors.UserError) as cm:
            o.validator('X', d, {})
        e = cm.exception
        self.assertEqual(str(e), f"File path for variable 'X' does not exist: {d}")

        dne = test.workpath('does_not_exist')
        with self.assertRaises(SCons.Errors.UserError) as cm:
            o.validator('X', dne, {})
        e = cm.exception
        self.assertEqual(str(e), f"File path for variable 'X' does not exist: {dne}")

    def test_PathAccept(self) -> None:
        """Test the PathAccept validator"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PathVariable('test',
                                          'test build variable help',
                                          '/default/path',
                                          SCons.Variables.PathVariable.PathAccept))

        test = TestCmd.TestCmd(workdir='')
        test.subdir('dir')
        test.write('file', "file\n")

        o = opts.options[0]
        o.validator('X', test.workpath('file'), {})

        d = test.workpath('d')
        o.validator('X', d, {})

        dne = test.workpath('does_not_exist')
        o.validator('X', dne, {})

    def test_validator(self):
        """Test the PathVariable validator argument"""
        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PathVariable('test',
                                          'test variable help',
                                          '/default/path'))

        test = TestCmd.TestCmd(workdir='')
        test.write('exists', 'exists\n')

        o = opts.options[0]
        o.validator('X', test.workpath('exists'), {})

        dne = test.workpath('does_not_exist')
        with self.assertRaises(SCons.Errors.UserError) as cm:
            o.validator('X', dne, {})
        e = cm.exception
        self.assertEqual(str(e), f"Path for variable 'X' does not exist: {dne}")

        class ValidatorError(Exception):
            pass

        def my_validator(key, val, env):
            raise ValidatorError(f"my_validator() got called for {key!r}, {val!r}!")

        opts = SCons.Variables.Variables()
        opts.Add(SCons.Variables.PathVariable('test2',
                                          'more help',
                                          '/default/path/again',
                                          my_validator))
        o = opts.options[0]
        with self.assertRaises(ValidatorError) as cm:
            o.validator('Y', 'value', {})
        e = cm.exception
        self.assertEqual(str(e), "my_validator() got called for 'Y', 'value'!")


if __name__ == "__main__":
    unittest.main()
