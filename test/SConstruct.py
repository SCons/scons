#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import TestSCons

test = TestSCons.TestSCons(match = TestCmd.match_re)

test.run(stdout = "",
	stderr = """
SCons error: No SConstruct file found.
File "\S+scons(\.py)?", line \d+, in main
""")

test.match_func = TestCmd.match_exact

wpath = test.workpath()

test.write('sconstruct', """
import os
print "sconstruct", os.getcwd()
""")

test.run(stdout = "sconstruct %s\n" % wpath)

test.write('Sconstruct', """
import os
print "Sconstruct", os.getcwd()
""")

test.run(stdout = "Sconstruct %s\n" % wpath)

test.write('SConstruct', """
import os
print "SConstruct", os.getcwd()
""")

test.run(stdout = "SConstruct %s\n" % wpath)

test.pass_test()
