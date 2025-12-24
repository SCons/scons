# MIT License
#
# Copyright The SCons Foundation
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

"""Test Warnings module."""

import unittest

import SCons.Warnings
from SCons.Warnings import (
    DependencyWarning,
    DeprecatedWarning,
    MandatoryDeprecatedWarning,
    SConsWarning,
    WarningOnByDefault,
)


class TestOutput:
    """Callable class to use as ``_warningOut`` for capturing test output.

    If we've already been called can reset by ``instance.out = None``
    """
    def __init__(self) -> None:
        self.out = None

    def __call__(self, x) -> None:
        args = x.args[0]
        if len(args) == 1:
            args = args[0]
        self.out = str(args)

class WarningsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        # Setup global state
        SCons.Warnings._enabled = []
        SCons.Warnings._warningAsException = False
        to = TestOutput()
        SCons.Warnings._warningOut = to

    def test_Warning(self) -> None:
        """Test warn function."""
        to = SCons.Warnings._warningOut

        SCons.Warnings.enableWarningClass(SConsWarning)
        SCons.Warnings.warn(DeprecatedWarning, "Foo")
        assert to.out == "Foo", to.out
        SCons.Warnings.warn(DependencyWarning, "Foo", 1)
        assert to.out == "('Foo', 1)", to.out

    def test_WarningAsExc(self) -> None:
        """Test warnings as exceptions."""
        to = SCons.Warnings._warningOut

        SCons.Warnings.enableWarningClass(WarningOnByDefault)
        old = SCons.Warnings.warningAsException(True)
        self.assertFalse(old)
        # an enabled warning should raise exception
        self.assertRaises(SConsWarning, SCons.Warnings.warn, WarningOnByDefault, "Foo")
        to.out = None
        # a disabled exception should not raise
        SCons.Warnings.warn(DeprecatedWarning, "Foo")
        assert to.out == None, to.out

        # make sure original behavior can be restored
        prev = SCons.Warnings.warningAsException(old)
        self.assertTrue(prev)
        SCons.Warnings.warn(WarningOnByDefault, "Foo")
        assert to.out == "Foo", to.out

    def test_Disable(self) -> None:
        """Test disabling/enabling warnings."""
        to = SCons.Warnings._warningOut

        # No warnings by default
        SCons.Warnings.warn(DeprecatedWarning, "Foo")
        assert to.out is None, to.out

        SCons.Warnings.enableWarningClass(SConsWarning)
        SCons.Warnings.warn(DeprecatedWarning, "Foo")
        assert to.out == "Foo", to.out

        to.out = None
        SCons.Warnings.suppressWarningClass(DeprecatedWarning)
        SCons.Warnings.warn(DeprecatedWarning, "Foo")
        assert to.out is None, to.out

        SCons.Warnings.warn(MandatoryDeprecatedWarning, "Foo")
        assert to.out is None, to.out

        # Dependency warnings should still be enabled though
        SCons.Warnings.enableWarningClass(SConsWarning)
        SCons.Warnings.warn(DependencyWarning, "Foo")
        assert to.out == "Foo", to.out

        # Try reenabling all warnings...
        SCons.Warnings.enableWarningClass(SConsWarning)

        SCons.Warnings.enableWarningClass(SConsWarning)
        SCons.Warnings.warn(DeprecatedWarning, "Foo")
        assert to.out == "Foo", to.out

if __name__ == "__main__":
    unittest.main()
