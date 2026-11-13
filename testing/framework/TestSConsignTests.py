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
Unit tests for the TestSConsign module.
"""

import unittest
import os
import sys

# Add the directory containing the framework modules to sys.path
sys.path.insert(0, os.path.dirname(__file__))

import TestSConsign
import TestCmd

class TestSConsignTestCase(unittest.TestCase):
    def test_run_sconsign(self):
        """Test the run_sconsign() method"""
        # We need to mock things to avoid actually looking for scripts on disk
        # and to avoid running anything.

        # Mock environment variables that TestSConsign.__init__ uses
        os.environ['SCONS'] = 'dummy_scons'
        os.environ['SCONSIGN'] = 'dummy_sconsign'

        class MockTestSConsign(TestSConsign.TestSConsign):
            def __init__(self, **kw):
                self.run_called_with = []
                super().__init__(**kw)
            def run(self, *args, **kw):
                self.run_called_with.append((args, kw))
                return None

        test = MockTestSConsign(workdir='')

        # Test run_sconsign
        test.run_sconsign(arguments='-e file.sconsign', stdout='expected stdout')

        self.assertEqual(len(test.run_called_with), 1)
        args, kw = test.run_called_with[0]

        self.assertEqual(kw['arguments'], '-e file.sconsign')
        self.assertEqual(kw['stdout'], 'expected stdout')
        self.assertEqual(kw['program'], 'dummy_sconsign')
        self.assertEqual(kw['interpreter'], sys.executable)

    def test_set_sconsign(self):
        """Test the set_sconsign() method"""
        os.environ['SCONS'] = 'dummy_scons'
        os.environ['SCONSIGN'] = 'dummy_sconsign'

        test = TestSConsign.TestSConsign(workdir='')
        self.assertEqual(test.my_kw['program'], 'dummy_sconsign')

        test.set_sconsign('new_sconsign')
        self.assertEqual(test.my_kw['program'], 'new_sconsign')

if __name__ == '__main__':
    unittest.main()
