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
#SCons.Script.PrintHelp
SCons.Script.OptParser
SCons.Script.SConscriptSettableOptions

SCons.Script.keep_going_on_error
#SCons.Script.print_dtree
SCons.Script.print_explanations
SCons.Script.print_includes
SCons.Script.print_objects
SCons.Script.print_time
#SCons.Script.print_tree
SCons.Script.memory_stats
SCons.Script.ignore_errors
#SCons.Script.sconscript_time
#SCons.Script.command_time
#SCons.Script.exit_status
#SCons.Script.profiling
SCons.Script.repositories
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
