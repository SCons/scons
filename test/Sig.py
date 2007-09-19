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
Verify that we generate the proper warning, but don't die, when someone
tries to import the SCons.Sig module (which no longer exists) and
use the things we used to define therein.
"""

import TestSCons

test = TestSCons.TestSCons()

SConstruct = test.workpath('SConstruct')

test.write(SConstruct, """
import SCons.Sig
x = SCons.Sig.default_calc
x = SCons.Sig.default_module
x = SCons.Sig.MD5.current()
x = SCons.Sig.MD5.collect()
x = SCons.Sig.MD5.signature()
x = SCons.Sig.MD5.to_string()
x = SCons.Sig.MD5.from_string()
x = SCons.Sig.TimeStamp.current()
x = SCons.Sig.TimeStamp.collect()
x = SCons.Sig.TimeStamp.signature()
x = SCons.Sig.TimeStamp.to_string()
x = SCons.Sig.TimeStamp.from_string()
""")

expect = """
scons: warning: The SCons.Sig module no longer exists.
    Remove the following "import SCons.Sig" line to eliminate this warning:
""" + test.python_file_line(SConstruct, 2)

test.run(arguments = '.', stderr=expect)

test.pass_test()
