#! /usr/bin/env python

"""
Support functions for all the tests.
"""

#
# __COPYRIGHT__
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
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

if __name__ == '__main__':
    import sys
    import os.path
    sys.path.append(os.path.abspath('../../../src/engine'))

from SCons.Environment import Base

path = Base()['ENV']['PATH']

def isExecutableOfToolAvailable(test, tool):
    for executable in {
        'dmd': ['dmd', 'gdmd'],
        'gdc': ['gdc'],
        'ldc': ['ldc2', 'ldc'],
    }[tool]:
        if test.where_is(executable, path):
            return True
    return False


if __name__ == '__main__':
    import unittest
    sys.path.append(os.path.abspath('../../../testing/framework'))

    import TestSCons

    class VariousTests(unittest.TestCase):
        """
        These tests are somewhat self referential in that
        isExecutableOfToolAvailable uses where_is to do most of it's
        work and we use the same function in the tests.
        """
        def setUp(self):
            self.test = TestSCons.TestSCons()

        def tearDown(self):
            self.test = None

        def test_None_tool(self):
            self.assertRaises(KeyError, isExecutableOfToolAvailable, self.test, None)

        def test_dmd_tool(self):
            self.assertEqual(
                self.test.where_is('dmd', path) is not None or self.test.where_is('gdmd', path) is not None,
                isExecutableOfToolAvailable(self.test, 'dmd'))

        def test_gdc_tool(self):
            self.assertEqual(
                self.test.where_is('gdc', path) is not None,
                isExecutableOfToolAvailable(self.test, 'gdc'))

        def test_ldc_tool(self):
            self.assertEqual(
                self.test.where_is('ldc2', path) is not None or self.test.where_is('ldc', path) is not None,
                isExecutableOfToolAvailable(self.test, 'ldc'))

    unittest.main()
