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
Test Microsoft Visual C/C++ policy handlers.
"""

import unittest

import SCons.Warnings

from SCons.Tool.MSCommon.MSVC import Policy

from SCons.Tool.MSCommon.MSVC.Exceptions import (
    MSVCArgumentError,
    MSVCVersionNotFound,
    MSVCScriptExecutionError,
)

from SCons.Tool.MSCommon.MSVC.Warnings import (
    MSVCScriptExecutionWarning,
)

class PolicyTests(unittest.TestCase):

    def setUp(self):
        self.warnstack = []

    def push_warning_as_exception(self, warning_class):
        SCons.Warnings.enableWarningClass(warning_class)
        prev_state = SCons.Warnings.warningAsException()
        self.warnstack.append((warning_class, prev_state))

    def pop_warning_as_exception(self):
        warning_class, prev_state = self.warnstack.pop()
        SCons.Warnings.warningAsException(prev_state)
        SCons.Warnings.suppressWarningClass(warning_class)

    # msvc_set_notfound_policy, msvc_get_notfound_policy, and MSVC_NOTFOUND_POLICY

    def test_notfound_func_valid_symbols(self):
        def_policy = Policy.msvc_get_notfound_policy()
        last_policy = def_policy
        for notfound_def in Policy.MSVC_NOTFOUND_DEFINITION_LIST:
            for symbol in [notfound_def.symbol, notfound_def.symbol.lower(), notfound_def.symbol.upper()]:
                prev_policy = Policy.msvc_set_notfound_policy(symbol)
                self.assertTrue(prev_policy == last_policy, "notfound policy: {} != {}".format(
                    repr(prev_policy), repr(last_policy)
                ))
                cur_set_policy = Policy.msvc_set_notfound_policy()
                cur_get_policy = Policy.msvc_get_notfound_policy()
                self.assertTrue(cur_set_policy == cur_get_policy, "notfound policy: {} != {}".format(
                    repr(cur_set_policy), repr(cur_get_policy)
                ))
                last_policy = cur_get_policy
        Policy.msvc_set_notfound_policy(def_policy)

    def test_notfound_func_invalid_symbol(self):
        with self.assertRaises(MSVCArgumentError):
            Policy.msvc_set_notfound_policy('Undefined')

    def test_notfound_handler_invalid_symbol(self):
        with self.assertRaises(MSVCArgumentError):
            Policy.msvc_notfound_handler({'MSVC_NOTFOUND_POLICY': 'Undefined'}, '')

    def test_notfound_handler_ignore(self):
        def_policy = Policy.msvc_set_notfound_policy('Ignore')
        Policy.msvc_notfound_handler(None, '')
        Policy.msvc_notfound_handler({'MSVC_NOTFOUND_POLICY': None}, '')
        Policy.msvc_set_notfound_policy(def_policy)

    def test_notfound_handler_warning(self):
        # treat warning as exception for testing
        self.push_warning_as_exception(SCons.Warnings.VisualCMissingWarning)
        def_policy = Policy.msvc_set_notfound_policy('Warning')
        with self.assertRaises(SCons.Warnings.VisualCMissingWarning):
            Policy.msvc_notfound_handler(None, '')
        Policy.msvc_set_notfound_policy('Ignore')
        with self.assertRaises(SCons.Warnings.VisualCMissingWarning):
            Policy.msvc_notfound_handler({'MSVC_NOTFOUND_POLICY': 'Warning'}, '')
        Policy.msvc_set_notfound_policy(def_policy)
        self.pop_warning_as_exception()

    def test_notfound_handler_error(self):
        def_policy = Policy.msvc_set_notfound_policy('Error')
        with self.assertRaises(MSVCVersionNotFound):
            Policy.msvc_notfound_handler(None, '')
        Policy.msvc_set_notfound_policy('Ignore')
        with self.assertRaises(MSVCVersionNotFound):
            Policy.msvc_notfound_handler({'MSVC_NOTFOUND_POLICY': 'Error'}, '')
        Policy.msvc_set_notfound_policy(def_policy)

    # msvc_set_scripterror_policy, msvc_get_scripterror_policy, and MSVC_SCRIPTERROR_POLICY

    def test_scripterror_func_valid_symbols(self):
        def_policy = Policy.msvc_get_scripterror_policy()
        last_policy = def_policy
        for scripterror_def in Policy.MSVC_SCRIPTERROR_DEFINITION_LIST:
            for symbol in [scripterror_def.symbol, scripterror_def.symbol.lower(), scripterror_def.symbol.upper()]:
                prev_policy = Policy.msvc_set_scripterror_policy(symbol)
                self.assertTrue(prev_policy == last_policy, "scripterror policy: {} != {}".format(
                    repr(prev_policy), repr(last_policy)
                ))
                cur_set_policy = Policy.msvc_set_scripterror_policy()
                cur_get_policy = Policy.msvc_get_scripterror_policy()
                self.assertTrue(cur_set_policy == cur_get_policy, "scripterror policy: {} != {}".format(
                    repr(cur_set_policy), repr(cur_get_policy)
                ))
                last_policy = cur_get_policy
        Policy.msvc_set_scripterror_policy(def_policy)

    def test_scripterror_func_invalid_symbol(self):
        with self.assertRaises(MSVCArgumentError):
            Policy.msvc_set_scripterror_policy('Undefined')

    def test_scripterror_handler_invalid_symbol(self):
        with self.assertRaises(MSVCArgumentError):
            Policy.msvc_scripterror_handler({'MSVC_SCRIPTERROR_POLICY': 'Undefined'}, '')

    def test_scripterror_handler_ignore(self):
        def_policy = Policy.msvc_set_scripterror_policy('Ignore')
        Policy.msvc_scripterror_handler(None, '')
        Policy.msvc_scripterror_handler({'MSVC_SCRIPTERROR_POLICY': None}, '')
        Policy.msvc_set_scripterror_policy(def_policy)

    def test_scripterror_handler_warning(self):
        # treat warning as exception for testing
        self.push_warning_as_exception(MSVCScriptExecutionWarning)
        def_policy = Policy.msvc_set_scripterror_policy('Warning')
        with self.assertRaises(MSVCScriptExecutionWarning):
            Policy.msvc_scripterror_handler(None, '')
        Policy.msvc_set_scripterror_policy('Ignore')
        with self.assertRaises(MSVCScriptExecutionWarning):
            Policy.msvc_scripterror_handler({'MSVC_SCRIPTERROR_POLICY': 'Warning'}, '')
        Policy.msvc_set_scripterror_policy(def_policy)
        self.pop_warning_as_exception()

    def test_scripterror_handler_error(self):
        def_policy = Policy.msvc_set_scripterror_policy('Error')
        with self.assertRaises(MSVCScriptExecutionError):
            Policy.msvc_scripterror_handler(None, '')
        Policy.msvc_set_scripterror_policy('Ignore')
        with self.assertRaises(MSVCScriptExecutionError):
            Policy.msvc_scripterror_handler({'MSVC_SCRIPTERROR_POLICY': 'Error'}, '')
        Policy.msvc_set_scripterror_policy(def_policy)

if __name__ == "__main__":
    unittest.main()

