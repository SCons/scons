__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import sys
import unittest

from SCons.Sig.MD5 import current, collect, signature, to_string, from_string




class my_obj:
    """A dummy object class that satisfies the interface
    requirements of the MD5 class.
    """

    def __init__(self, value = ""):
	self.value = value
        
    def get_signature(self):
        if not hasattr(self, "sig"):
	    self.sig = signature(self)
	return self.sig

    def get_contents(self):
	return self.value



class MD5TestCase(unittest.TestCase):

    def test_current(self):
	"""Test deciding if an object is up-to-date

	Simple comparison of different "signature" values.
	"""
	obj = my_obj('111')
	assert not current(obj, signature(my_obj('110')))
	assert     current(obj, signature(my_obj('111')))
	assert not current(obj, signature(my_obj('112')))

    def test_collect(self):
	"""Test collecting a list of signatures into a new signature value
	"""
        s = map(signature, map(my_obj, ('111', '222', '333')))
        
        assert '698d51a19d8a121ce581499d7b701668' == collect(s[0:1])
        assert '8980c988edc2c78cc43ccb718c06efd5' == collect(s[0:2])
	assert '53fd88c84ff8a285eb6e0a687e55b8c7' == collect(s)

    def test_signature(self):
        """Test generating a signature"""
	o1 = my_obj(value = '111')
        assert '698d51a19d8a121ce581499d7b701668' == signature(o1)

    def test_to_string(self):
        assert '698d51a19d8a121ce581499d7b701668' == to_string('698d51a19d8a121ce581499d7b701668')

    def test_from_string(self):
        assert '698d51a19d8a121ce581499d7b701668' == from_string('698d51a19d8a121ce581499d7b701668')

if __name__ == "__main__":
    suite = unittest.makeSuite(MD5TestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
