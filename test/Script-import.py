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
Test that a module that we import into an SConscript file can itself
easily import the global SCons variables, and a handful of other variables
directly from SCons.Script modules.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
import m1
""")

test.write("m1.py", """\
from SCons.Script import *
SConscript('SConscript')
""")

test.write('SConscript', """\
import m2
import m3
import m4
""")

test.write("m2.py", """\
from SCons.Script import *
Command("file.out", "file.in", Copy("$TARGET", "$SOURCE"))
""")

test.write("m3.py", """\
import SCons.Script

SCons.Script.BuildTask
SCons.Script.CleanTask
SCons.Script.QuestionTask

old_SCons_Script_variables = [
    'OptParser',
    'keep_going_on_error',
    'print_explanations',
    'print_includes',
    'print_objects',
    'print_time',
    'memory_stats',
    'ignore_errors',
    'repositories',
    'print_dtree',
    'print_tree',
    'sconscript_time',
    'command_time',
    'exit_status',
    'profiling',
]

for var in old_SCons_Script_variables:
    try:
        getattr(SCons.Script, var)
    except AttributeError:
        pass
    else:
        raise Exception("unexpected variable SCons.Script.%s" % var)
""")

test.write("m4.py", """\
import SCons.Script.SConscript
SCons.Script.SConscript.Arguments
SCons.Script.SConscript.ArgList
SCons.Script.SConscript.BuildTargets
SCons.Script.SConscript.CommandLineTargets
SCons.Script.SConscript.DefaultTargets
""")

test.write("file.in", "file.in\n")

test.run(arguments = '.')

test.must_match("file.out", "file.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
