__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import sys
import unittest

import SCons.Sig.MD5



class my_obj:
    """A dummy object class that satisfies the interface
    requirements of the MD5 class.
    """

    def __init__(self, value = ""):
	self.value = value
	self.sig = None

    def signature(self):
	if not self.sig:
	    self.sig = SCons.Sig.MD5.signature(self.value)
	return self.sig

    def current(self, sig):
	return SCons.Sig.MD5.current(self, sig)



class MD5TestCase(unittest.TestCase):

    def test__init(self):
	pass	# XXX

    def test__end(self):
	pass	# XXX

    def test_current(self):
	"""Test deciding if an object is up-to-date

	Simple comparison of different "signature" values.
	"""
	o111 = my_obj(value = '111')
	assert not o111.current(SCons.Sig.MD5.signature('110'))
	assert     o111.current(SCons.Sig.MD5.signature('111'))
	assert not o111.current(SCons.Sig.MD5.signature('112'))

    def test_set(self):
	pass	# XXX

    def test_invalidate(self):
	pass	# XXX

    def test_collect(self):
	"""Test collecting a list of signatures into a new signature value
	"""
	o1 = my_obj(value = '111')
	o2 = my_obj(value = '222')
	o3 = my_obj(value = '333')
	assert '698d51a19d8a121ce581499d7b701668' == SCons.Sig.MD5.collect(o1)
	assert '8980c988edc2c78cc43ccb718c06efd5' == SCons.Sig.MD5.collect(o1, o2)
	assert '53fd88c84ff8a285eb6e0a687e55b8c7' == SCons.Sig.MD5.collect(o1, o2, o3)

    def test_signature(self):
	pass	# XXX

    def test_cmdsig(self):
	pass	# XXX

    def test_srcsig(self):
	pass	# XXX


if __name__ == "__main__":
    suite = unittest.makeSuite(MD5TestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
