#
# Copyright (c) 2001, 2002, 2003 Steven Knight
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

from SCons.Sig.TimeStamp import current, collect, signature, to_string, from_string



class my_obj:
    """A dummy object class that satisfies the interface
    requirements of the TimeStamp class.
    """

    def __init__(self, value = 0):
	self.value = value

    def get_signature(self):
	return self.value

    def get_timestamp(self):
        return self.value


class TimeStampTestCase(unittest.TestCase):

    def test_current(self):
	"""Test deciding if an object is up-to-date

	Simple comparison of different timestamp values.
	"""
	o1 = my_obj(value = 111)
	assert not current(o1.get_signature(), 110)
	assert current(o1.get_signature(), 111)
	assert current(o1.get_signature(), 112)

    def test_collect(self):
	"""Test collecting a list of signatures into a new signature value
	into a new timestamp value.
	"""
        
	assert 111 == collect((111,))
	assert 222 == collect((111, 222))
	assert 333 == collect((333, 222, 111))

    def test_signature(self):
        """Test generating a signature"""
        o1 = my_obj(value = 111)
        assert 111 == signature(o1)

    def test_to_string(self):
        assert '111' == to_string(111)

    def test_from_string(self):
        assert 111 == from_string('111')


if __name__ == "__main__":
    suite = unittest.makeSuite(TimeStampTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
