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

__revision__ = "__FILE__ __REVISION__ __DATE__ __USER__"

import sys
import unittest

import SCons.Errors
import SCons.Node.Alias

class AliasTestCase(unittest.TestCase):

    def test_AliasNameSpace(self):
        """Test creating an Alias name space
        """
        ans = SCons.Node.Alias.AliasNameSpace()
        assert not ans is None, ans

    def test_ANS_Alias(self):
        """Test the Alias() factory
        """
        ans = SCons.Node.Alias.AliasNameSpace()

        a = ans.Alias('a1')
	assert a.name == 'a1', a.name

        try:
            ans.Alias('a1')
        except SCons.Errors.UserError:
            pass
        else:
            raise TestFailed, "did not catch expected UserError"

    def test_lookup(self):
        """Test the lookup() method
        """
        ans = SCons.Node.Alias.AliasNameSpace()

        ans.Alias('a1')
        a = ans.lookup('a1')
        assert a.name == 'a1', a.name

        a1 = ans.lookup('a1')
        assert a is a1, a1

        a = ans.lookup('a2')
        assert a == None, a

    def test_Alias(self):
        """Test creating an Alias() object
        """
        a1 = SCons.Node.Alias.Alias('a')
        assert a1.name == 'a', a1.name

        a2 = SCons.Node.Alias.Alias('a')
        assert a2.name == 'a', a2.name

        assert not a1 is a2
        assert a1.name == a2.name



if __name__ == "__main__":
    suite = unittest.makeSuite(AliasTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
