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
Test handling of must_exist flag and global setting requiring the
file to exist in an SConscript call
"""

import os
import TestSCons

test = TestSCons.TestSCons()

# catch the exception if is raised, send it on as a warning
# this gives us traceability of the line responsible
SConstruct_path = test.workpath('SConstruct')
test.write(SConstruct_path, """\
import sys
import traceback

import SCons.Script
from SCons.Errors import UserError
from SCons.Script.Main import find_deepest_user_frame

DefaultEnvironment(tools=[])

def user_error(e):
    "Synthesize msg from UserError."
    # Borrowed from SCons.Script._scons_user_error which we don't use
    # because it exits - we only want the message.
    etype, value, tb = sys.exc_info()
    filename, lineno, routine, _ = find_deepest_user_frame(traceback.extract_tb(tb))
    sys.stderr.write(f"\\nscons: *** {value}\\n")
    sys.stderr.write(f'File "{filename}", line {lineno}, in {routine}\\n')

# 1. Call with defaults raises exception
try:
    SConscript("missing/SConscript")
except UserError as e:
    user_error(e)

# 2. Call with must_exist=True raises exception
try:
    SConscript("missing/SConscript", must_exist=True)
except UserError as e:
    user_error(e)

# 3. Call with must_exist=False call should succeed silently
try:
    SConscript("missing/SConscript", must_exist=False)
except UserError as e:
    user_error(e)

# 4. with system setting changed, should succeed silently
SCons.Script.set_missing_sconscript_error(flag=False)
try:
    SConscript("missing/SConscript")
except UserError as e:
    user_error(e)

# 5. must_exist=True "wins" over system setting
try:
    SConscript("missing/SConscript", must_exist=True)
except UserError as e:
    user_error(e)
""",
)

missing = os.path.join("missing", "SConscript")
err1 = f"""
scons: *** missing SConscript file {missing!r}
""" + test.python_file_line(
    SConstruct_path, 21
)

err2 = f"""
scons: *** missing SConscript file {missing!r}
""" + test.python_file_line(
    SConstruct_path, 27
)

err3 = f"""
scons: *** missing SConscript file {missing!r}
""" + test.python_file_line(
    SConstruct_path, 33
)

err4 = f"""
scons: *** missing SConscript file {missing!r}
""" + test.python_file_line(
    SConstruct_path, 40
)

err5 = f"""
scons: *** missing SConscript file {missing!r}
""" + test.python_file_line(
    SConstruct_path, 46
)

nowarn = ""

# of the five tests, we actually expect fails from 1 and 2
expect_stderr = err1 + err2 + nowarn + nowarn + nowarn
test.run(arguments=".", stderr=expect_stderr)
test.pass_test()
