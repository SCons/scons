#!/usr/bin/env python

__revision__ = "test/option-f.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import os.path

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

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

test.run(chdir = '.', arguments = '-f SConscript')
test.fail_test(test.stdout() != ("SConscript %s\n" % wpath))

test.run(chdir = '.', arguments = '-f ' + subdir_BuildThis)
test.fail_test(test.stdout() != ("subdir/BuildThis %s\n" % wpath))

test.pass_test()
