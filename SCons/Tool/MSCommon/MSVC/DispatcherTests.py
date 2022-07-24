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

"""
Test internal method dispatcher for Microsoft Visual C/C++.
"""

import unittest

from SCons.Tool.MSCommon import MSVC

MSVC.Dispatcher.register_modulename(__name__)


class Data:
    reset_count = 0
    verify_count = 0


# current module - not callable
_reset = None
reset = None
_verify = None
verify = None


class StaticMethods:
    @staticmethod
    def _reset():
        Data.reset_count += 1

    @staticmethod
    def reset():
        Data.reset_count += 1

    @staticmethod
    def _verify():
        Data.verify_count += 1

    @staticmethod
    def verify():
        Data.verify_count += 1


class ClassMethods:
    @classmethod
    def _reset(cls):
        Data.reset_count += 1

    @classmethod
    def reset(cls):
        Data.reset_count += 1

    @classmethod
    def _verify(cls):
        Data.verify_count += 1

    @classmethod
    def verify(cls):
        Data.verify_count += 1


class NotCallable:
    _reset = None
    reset = None

    _verify = None
    _verify = None


MSVC.Dispatcher.register_class(StaticMethods)
MSVC.Dispatcher.register_class(ClassMethods)
MSVC.Dispatcher.register_class(NotCallable)


class DispatcherTests(unittest.TestCase):
    def test_dispatcher_reset(self):
        MSVC.Dispatcher.reset()
        self.assertTrue(Data.reset_count == 4, "MSVC.Dispatcher.reset() count failed")
        Data.reset_count = 0

    def test_dispatcher_verify(self):
        MSVC.Dispatcher.verify()
        self.assertTrue(Data.verify_count == 4, "MSVC.Dispatcher.verify() count failed")
        Data.verify_count = 0

    def test_msvc_reset(self):
        MSVC._reset()
        self.assertTrue(Data.reset_count == 4, "MSVC._reset() count failed")
        Data.reset_count = 0

    def test_msvc_verify(self):
        MSVC._verify()
        self.assertTrue(Data.verify_count == 4, "MSVC._verify() count failed")
        Data.verify_count = 0


if __name__ == "__main__":
    unittest.main()
