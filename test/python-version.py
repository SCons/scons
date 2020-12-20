#!/usr/bin/env python
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

"""
Verify the behavior of our check for unsupported or deprecated versions
of Python.
"""

import re

import TestCmd
import TestSCons

test = TestSCons.TestSCons(match = TestCmd.match_re_dotall,ignore_python_version=0)

test.write('SConstruct', "\n")

test.write('SetOption-deprecated', "SetOption('warn', 'no-deprecated')\n")

test.write('SetOption-python', "SetOption('warn', ['no-python-version'])\n")

if TestSCons.unsupported_python_version():

    error = r"scons: \*\*\* SCons version \S+ does not run under Python version %s."
    error = error % re.escape(TestSCons.python_version_string()) + "\n"
    test.run(arguments = '-Q', status = 1, stderr = error)

else:

    if TestSCons.deprecated_python_version():

        test.run(arguments = '-Q', stderr = TestSCons.deprecated_python_expr)

    else:

        test.run(arguments = '-Q')

    test.run(arguments = '-Q --warn=no-deprecated')

    test.run(arguments = '-f SetOption-deprecated -Q')

    test.run(arguments = '-f SetOption-python -Q')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
