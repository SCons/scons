__revision__ = "ErrorsTests.py __REVISION__ __DATE__ __DEVELOPER__"

import sys
import unittest
from scons.Errors import InternalError, UserError


class ErrorsTestCase(unittest.TestCase):
    def test_InternalError(self):
	"""Test the InternalError exception."""
        try:
            raise InternalError, "test internal error"
        except InternalError, e:
            assert e.args == "test internal error"

    def test_UserError(self):
	"""Test the UserError exception."""
        try:
            raise UserError, "test user error"
        except UserError, e:
            assert e.args == "test user error"



if __name__ == "__main__":
    suite = unittest.makeSuite(ErrorsTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
