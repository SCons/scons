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
	assert current(o1, 110)
	assert current(o1, 111)
	assert not current(o1, 112)

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
