#!/usr/bin/env python

__revision__ = "test/t0001.t __REVISION__ __DATE__ __DEVELOPER__"

from TestCmd import TestCmd

test = TestCmd(program = 'scons.py', workdir = '', interpreter = 'python')

test.write('SConstruct', """
import os
print "SConstruct", os.getcwd()
Conscript('SConscript')
""")

# XXX I THINK THEY SHOULD HAVE TO RE-IMPORT OS HERE,
# WHICH THEY DO FOR THE SECOND TEST BELOW, BUT NOT THE FIRST...
test.write('SConscript', """
import os
print "SConscript " + os.getcwd()
""")

wpath = test.workpath()

test.run(chdir = '.')
test.fail_test(test.stdout() != ("SConstruct %s\nSConscript %s\n" % (wpath, wpath)))

test.run(chdir = '.', arguments = '-f SConscript')
test.fail_test(test.stdout() != ("SConscript %s\n" % wpath))

test.pass_test()
