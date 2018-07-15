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

import SCons.compat

import os
import sys
import unittest

from collections import UserDict

import TestCmd

import SCons.Errors

from SCons.Defaults import *

class DefaultsTestCase(unittest.TestCase):
    def test_mkdir_func0(self):
        test = TestCmd.TestCmd(workdir = '')
        test.subdir('sub')
        subdir2 = test.workpath('sub', 'dir1', 'dir2')
        # Simple smoke test
        mkdir_func(subdir2)
        mkdir_func(subdir2)     # 2nd time should be OK too

    def test_mkdir_func1(self):
        test = TestCmd.TestCmd(workdir = '')
        test.subdir('sub')
        subdir1 = test.workpath('sub', 'dir1')
        subdir2 = test.workpath('sub', 'dir1', 'dir2')
        # No error if asked to create existing dir
        os.makedirs(subdir2)
        mkdir_func(subdir2)
        mkdir_func(subdir1)

    def test_mkdir_func2(self):
        test = TestCmd.TestCmd(workdir = '')
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
        except os.error as e:
            pass
        else:
            fail("expected os.error")
        

if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
