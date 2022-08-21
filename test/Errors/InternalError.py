#!/usr/bin/env python
#
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
Verify the exit status and error output if an SConstruct file
throws an InternalError.
"""

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

# Test InternalError.
test.write('SConstruct', """
assert "InternalError" not in globals()
from SCons.Errors import InternalError
raise InternalError('error inside')
""")

test.run(stdout = "scons: Reading SConscript files ...\ninternal error\n",
         stderr = r"""Traceback \(most recent call last\):
  File ".+", line \d+, in .+
  File ".+", line \d+, in .+
  File ".+", line \d+, in .+
  File ".+SConstruct", line \d+, in .+
    raise InternalError\('error inside'\)
(SCons\.Errors\.|)InternalError: error inside
""", status=2)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
