#
# Copyright (c) 2001, 2002 Steven Knight
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

import sys
import unittest

import SCons.Errors
import SCons.Platform

class PlatformTestCase(unittest.TestCase):
    def test_Platform(self):
        """Test the Platform() function"""
        p = SCons.Platform.Platform('cygwin')
        assert str(p) == 'cygwin', p
        env = {}
        p(env)
        assert env['PROGSUFFIX'] == '.exe', env
        assert env['LIBSUFFIX'] == '.a', env

        p = SCons.Platform.Platform('posix')
        assert str(p) == 'posix', p
        env = {}
        p(env)
        assert env['PROGSUFFIX'] == '', env
        assert env['LIBSUFFIX'] == '.a', env

        p = SCons.Platform.Platform('win32')
        assert str(p) == 'win32', p
        env = {}
        p(env)
        assert env['PROGSUFFIX'] == '.exe', env
        assert env['LIBSUFFIX'] == '.lib', env
        assert str

        try:
            p = SCons.Platform.Platform('_does_not_exist_')
        except SCons.Errors.UserError:
            pass
        else:
            raise

        env = {}
        SCons.Platform.Platform()(env)
        assert env != {}, env


if __name__ == "__main__":
    suite = unittest.makeSuite(PlatformTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
