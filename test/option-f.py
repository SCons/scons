#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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

import TestSCons
import os.path

test = TestSCons.TestSCons()

test.subdir('subdir')

subdir_BuildThis = os.path.join('subdir', 'Buildthis')

test.write('SConscript', """
import os
print "SConscript " + os.getcwd()
""")

test.write(subdir_BuildThis, """
import os
print "subdir/BuildThis", os.getcwd()
""")

wpath = test.workpath()

test.run(arguments = '-f SConscript',
	 stdout = "SConscript %s\n" % wpath)

test.run(arguments = '-f ' + subdir_BuildThis,
	 stdout = "subdir/BuildThis %s\n" % wpath)

test.run(arguments = '--file=SConscript',
	 stdout = "SConscript %s\n" % wpath)

test.run(arguments = '--file=' + subdir_BuildThis,
	 stdout = "subdir/BuildThis %s\n" % wpath)

test.run(arguments = '--makefile=SConscript',
	 stdout = "SConscript %s\n" % wpath)

test.run(arguments = '--makefile=' + subdir_BuildThis,
	 stdout = "subdir/BuildThis %s\n" % wpath)

test.run(arguments = '--sconstruct=SConscript',
	 stdout = "SConscript %s\n" % wpath)

test.run(arguments = '--sconstruct=' + subdir_BuildThis,
	 stdout = "subdir/BuildThis %s\n" % wpath)

test.run(arguments = '-f -', stdin = """
import os
print "STDIN " + os.getcwd()
""",
	 stdout = "STDIN %s\n" % wpath)

test.run(arguments = '-f no_such_file',
	 stdout = "",
	 stderr = "Ignoring missing SConscript 'no_such_file'\n")

test.pass_test()
