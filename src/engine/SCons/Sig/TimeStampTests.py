__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import sys
import unittest

import SCons.Sig.TimeStamp



class my_obj:
    """A dummy object class that satisfies the interface
    requirements of the TimeStamp class.
    """

    def __init__(self, value = ""):
	self.value = value

    def signature(self):
	return self.value



class TimeStampTestCase(unittest.TestCase):

    def test__init(self):
	pass	# XXX

    def test__init(self):
	pass	# XXX

    def test__end(self):
	pass	# XXX

    def test_current(self):
	"""Test deciding if an object is up-to-date

	Simple comparison of different timestamp values.
	"""
	o1 = my_obj(value = 111)
	assert SCons.Sig.TimeStamp.current(o1, 110)
	assert SCons.Sig.TimeStamp.current(o1, 111)
	assert not SCons.Sig.TimeStamp.current(o1, 112)

    def test_set(self):
	pass	# XXX

    def test_invalidate(self):
	pass	# XXX

    def test_collect(self):
	"""Test collecting a list of signatures into a new signature value
	into a new timestamp value.
	"""
	o1 = my_obj(value = 111)
	o2 = my_obj(value = 222)
	o3 = my_obj(value = 333)
	assert 111 == SCons.Sig.TimeStamp.collect(o1)
	assert 222 == SCons.Sig.TimeStamp.collect(o1, o2)
	assert 333 == SCons.Sig.TimeStamp.collect(o1, o2, o3)

    def test_signature(self):
	pass	# XXX

    def test_cmdsig(self):
	pass	# XXX

    def test_srcsig(self):
	pass	# XXX


if __name__ == "__main__":
    suite = unittest.makeSuite(TimeStampTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
