#!/usr/bin/env python

__revision__ = "test/SConstruct.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

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
