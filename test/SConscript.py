#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
import os
print "SConstruct", os.getcwd()
Conscript('SConscript')
""")

# XXX I THINK THEY SHOULD HAVE TO RE-IMPORT OS HERE
test.write('SConscript', """
import os
print "SConscript " + os.getcwd()
""")

wpath = test.workpath()

test.run(stdout = "SConstruct %s\nSConscript %s\n" % (wpath, wpath))

test.pass_test()
