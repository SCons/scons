#!/usr/bin/env python

__revision__ = "test/option-f.py __REVISION__ __DATE__ __DEVELOPER__"

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
	 stderr = "Ignoring missing script 'no_such_file'\n")

test.pass_test()
