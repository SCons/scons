__revision__ = "Sig/MD5Tests.py __REVISION__ __DATE__ __DEVELOPER__"

import sys
import unittest

import scons.Sig.MD5



class my_obj:
    """A dummy object class that satisfies the interface
    requirements of the MD5 class.
    """

    def __init__(self, value = ""):
	self.value = value
	self.sig = None

    def signature(self):
	if not self.sig:
	    self.sig = scons.Sig.MD5.signature(self.value)
	return self.sig

    def current(self, sig):
	return scons.Sig.MD5.current(self, sig)



class MD5TestCase(unittest.TestCase):

    def test__init(self):
	pass	# XXX

    def test__end(self):
	pass	# XXX

    def test_current(self):
	"""Test the ability to decide if an object is up-to-date
	with different signature values.
	"""
	o111 = my_obj(value = '111')
	assert not o111.current(scons.Sig.MD5.signature('110'))
	assert     o111.current(scons.Sig.MD5.signature('111'))
	assert not o111.current(scons.Sig.MD5.signature('112'))

    def test_set(self):
	pass	# XXX

    def test_invalidate(self):
	pass	# XXX

    def test_collect(self):
	"""Test the ability to collect a sequence of object signatures
	into a new signature value.
	"""
	o1 = my_obj(value = '111')
	o2 = my_obj(value = '222')
	o3 = my_obj(value = '333')
	assert '698d51a19d8a121ce581499d7b701668' == scons.Sig.MD5.collect(o1)
	assert '8980c988edc2c78cc43ccb718c06efd5' == scons.Sig.MD5.collect(o1, o2)
	assert '53fd88c84ff8a285eb6e0a687e55b8c7' == scons.Sig.MD5.collect(o1, o2, o3)

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
