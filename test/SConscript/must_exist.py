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

'''
Test handling of must_exist flag and global setting requiring the
file to exist in an SConscript call
'''

import TestSCons

test = TestSCons.TestSCons()

# catch the exception if is raised, send it on as a warning
# this gives us traceability of the line responsible
SConstruct_path = test.workpath('SConstruct')
test.write(SConstruct_path, """\
import SCons
from SCons.Warnings import _warningOut
import sys

# 1. call should succeed with deprecation warning
try:
    SConscript('missing/SConscript')
except SCons.Errors.UserError as e:
    if _warningOut:
        _warningOut(e)
# 2. call should succeed with warning
try:
    SConscript('missing/SConscript')
except SCons.Errors.UserError as e:
    if _warningOut:
        _warningOut(e)
# 3. call should raise exception
try:
    SConscript('missing/SConscript', must_exist=True)
except SCons.Errors.UserError as e:
    if _warningOut:
        _warningOut(e)
# 4. call should succeed with warning
try:
    SConscript('missing/SConscript', must_exist=False)
except SCons.Errors.UserError as e:
    if _warningOut:
        _warningOut(e)
SCons.Script.set_missing_sconscript_error()
# 5. with system setting changed, should raise exception
try:
    SConscript('missing/SConscript')
except SCons.Errors.UserError as e:
    if _warningOut:
        _warningOut(e)
# 6. must_exist=False should override system setting
try:
    SConscript('missing/SConscript', must_exist=False)
except SCons.Errors.UserError as e:
    if _warningOut:
        _warningOut(e)
""")

# we should see two exceptions as "Fatal" and
# and see four warnings, the first having the depr message
warn1 = """
scons: warning: Calling missing SConscripts without error is deprecated.
Transition by adding must_exist=0 to SConscript calls.
Missing SConscript 'missing/SConscript'
""" + test.python_file_line(SConstruct_path, 7)

warn2 = """
scons: warning: Ignoring missing SConscript 'missing/SConscript'
""" + test.python_file_line(SConstruct_path, 13)

err1 = """
scons: warning: Fatal: missing SConscript 'missing/SConscript'
""" + test.python_file_line(SConstruct_path, 22)

warn3 = """
scons: warning: Ignoring missing SConscript 'missing/SConscript'
""" + test.python_file_line(SConstruct_path, 25)

err2 = """
scons: warning: Fatal: missing SConscript 'missing/SConscript'
""" + test.python_file_line(SConstruct_path, 35)

warn4 = """
scons: warning: Ignoring missing SConscript 'missing/SConscript'
""" + test.python_file_line(SConstruct_path, 38)

expect_stderr = warn1 + warn2 + err1 + warn3 + err2 + warn4
test.run(arguments = ".", stderr = expect_stderr)
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
