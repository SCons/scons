#!/usr/bin/env python
#
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
Unit tests for the TestSCons module.

This only has a few tests, could be expanded
"""

import unittest
import os
import sys
import re

# Add the directory containing the framework modules to sys.path
# sys.path.insert(0, os.path.dirname(__file__))

import TestSCons
import TestCmd

class TestSConsTestCase(unittest.TestCase):
    def test_wrap_stdout(self):
        """Test the wrap_stdout() method"""
        test = TestSCons.TestSCons(workdir='')

        # We need to cleanup the workdir created by TestSCons
        self.addCleanup(test.cleanup)

        # Test basic wrapping
        wrapped = test.wrap_stdout(build_str="Building...\n", read_str="Reading...\n")
        expect = (
            "scons: Reading SConscript files ...\n"
            "Reading...\n"
            "scons: done reading SConscript files.\n"
            "scons: Building targets ...\n"
            "Building...\n"
            "scons: done building targets.\n"
        )
        self.assertEqual(wrapped, expect)

        # Test error wrapping
        wrapped = test.wrap_stdout(build_str="Erroring...\n", error=1)
        expect = (
            "scons: Reading SConscript files ...\n"
            "scons: done reading SConscript files.\n"
            "scons: Building targets ...\n"
            "Erroring...\n"
            "scons: building terminated because of errors.\n"
        )
        self.assertEqual(wrapped, expect)

        # Test cleaning wrapping
        wrapped = test.wrap_stdout(build_str="Cleaning...\n", cleaning=1)
        expect = (
            "scons: Reading SConscript files ...\n"
            "scons: done reading SConscript files.\n"
            "scons: Cleaning targets ...\n"
            "Cleaning...\n"
            "scons: done cleaning targets.\n"
        )
        self.assertEqual(wrapped, expect)

    def test_up_to_date(self):
        """Test the up_to_date() method"""
        # We need to mock the run() method because we don't want to actually run scons
        class MockTestSCons(TestSCons.TestSCons):
            def __init__(self, **kw):
                self.run_called_with = []
                super().__init__(**kw)
            def run(self, **kw):
                self.run_called_with.append(kw)

        test = MockTestSCons(workdir='')
        test.up_to_date(arguments='target1 target2', read_str="Reading...\n")

        self.assertEqual(len(test.run_called_with), 1)
        kw = test.run_called_with[0]
        self.assertEqual(kw['arguments'], 'target1 target2')
        self.assertEqual(kw['match'], test.match_re_dotall)

        # Check if stdout pattern is correct
        stdout_pattern = kw['stdout']
        self.assertTrue(stdout_pattern.endswith('.*'))
        # The pattern should contain both targets as up to date
        self.assertIn(re.escape("scons: `target1' is up to date.\n"), stdout_pattern)
        self.assertIn(re.escape("scons: `target2' is up to date.\n"), stdout_pattern)

    def test_not_up_to_date(self):
        """Test the not_up_to_date() method"""
        class MockTestSCons(TestSCons.TestSCons):
            def __init__(self, **kw):
                self.run_called_with = []
                super().__init__(**kw)
            def run(self, **kw):
                self.run_called_with.append(kw)

        test = MockTestSCons(workdir='')
        test.not_up_to_date(arguments='target1', read_str="Reading...\n")

        self.assertEqual(len(test.run_called_with), 1)
        kw = test.run_called_with[0]
        self.assertEqual(kw['arguments'], 'target1')

        stdout_pattern = kw['stdout']
        # Should contain a negative lookahead for the up-to-date message
        self.assertIn("(?!scons: `target1' is up to date.)", stdout_pattern)

if __name__ == '__main__':
    unittest.main()
