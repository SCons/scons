#!/usr/bin/env python

__revision__ = "test/SConscript.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

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

test.run(chdir = '.')
test.fail_test(test.stdout() != ("SConstruct %s\nSConscript %s\n" % (wpath, wpath)))

test.pass_test()
