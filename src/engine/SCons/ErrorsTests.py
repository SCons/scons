__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import sys
import unittest
import SCons.Errors


class ErrorsTestCase(unittest.TestCase):
    def test_InternalError(self):
	"""Test the InternalError exception."""
        try:
            raise SCons.Errors.InternalError, "test internal error"
        except SCons.Errors.InternalError, e:
            assert e.args == "test internal error"

    def test_UserError(self):
	"""Test the UserError exception."""
        try:
            raise SCons.Errors.UserError, "test user error"
        except SCons.Errors.UserError, e:
            assert e.args == "test user error"



if __name__ == "__main__":
    suite = unittest.makeSuite(ErrorsTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
