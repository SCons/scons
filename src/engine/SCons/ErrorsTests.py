#
# __COPYRIGHT__
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

import errno
import os
import sys
import unittest

import SCons.Errors


class ErrorsTestCase(unittest.TestCase):
    def test_BuildError(self):
        """Test the BuildError exception."""
        try:
            raise SCons.Errors.BuildError(
                errstr = "foo", status=57, filename="file", exc_info=(1,2,3),
                node = "n", executor="e", action="a", command="c")
        except SCons.Errors.BuildError as e:
            assert e.errstr == "foo"
            assert e.status == 57
            assert e.exitstatus == 2, e.exitstatus
            assert e.filename == "file"
            assert e.exc_info == (1,2,3)

            assert e.node == "n"
            assert e.executor == "e"
            assert e.action == "a"
            assert e.command == "c"

        try:
            raise SCons.Errors.BuildError("n", "foo", 57, 3, "file", 
                                          "e", "a", "c", (1,2,3))
        except SCons.Errors.BuildError as e:
            assert e.errstr == "foo", e.errstr
            assert e.status == 57, e.status
            assert e.exitstatus == 3, e.exitstatus
            assert e.filename == "file", e.filename
            assert e.exc_info == (1,2,3), e.exc_info

            assert e.node == "n"
            assert e.executor == "e"
            assert e.action == "a"
            assert e.command == "c"

        try:
            raise SCons.Errors.BuildError()
        except SCons.Errors.BuildError as e:
            assert e.errstr == "Unknown error"
            assert e.status == 2
            assert e.exitstatus == 2
            assert e.filename is None
            assert e.exc_info == (None, None, None)

            assert e.node is None
            assert e.executor is None
            assert e.action is None
            assert e.command is None

    def test_InternalError(self):
        """Test the InternalError exception."""
        try:
            raise SCons.Errors.InternalError("test internal error")
        except SCons.Errors.InternalError as e:
            assert e.args == ("test internal error",)

    def test_UserError(self):
        """Test the UserError exception."""
        try:
            raise SCons.Errors.UserError("test user error")
        except SCons.Errors.UserError as e:
            assert e.args == ("test user error",)

    def test_ExplicitExit(self):
        """Test the ExplicitExit exception."""
        try:
            raise SCons.Errors.ExplicitExit("node")
        except SCons.Errors.ExplicitExit as e:
            assert e.node == "node"

    def test_convert_EnvironmentError_to_BuildError(self):
        """Test the convert_to_BuildError function on EnvironmentError
        exceptions.
        """
        ee = SCons.Errors.EnvironmentError("test env error")
        be = SCons.Errors.convert_to_BuildError(ee)
        assert be.errstr == "test env error"
        assert be.status == 2
        assert be.exitstatus == 2
        assert be.filename is None

    def test_convert_OSError_to_BuildError(self):
        """Test the convert_to_BuildError function on OSError
        exceptions.
        """
        ose = OSError(7, 'test oserror')
        be = SCons.Errors.convert_to_BuildError(ose)
        assert be.errstr == 'test oserror'
        assert be.status == 7
        assert be.exitstatus == 2
        assert be.filename is None


if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
