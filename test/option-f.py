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

test.run(arguments = '-f SConscript')
test.fail_test(test.stdout() != ("SConscript %s\n" % wpath))
test.fail_test(test.stderr() != "")

test.run(arguments = '-f ' + subdir_BuildThis)
test.fail_test(test.stdout() != ("subdir/BuildThis %s\n" % wpath))
test.fail_test(test.stderr() != "")

test.run(arguments = '--file=SConscript')
test.fail_test(test.stdout() != ("SConscript %s\n" % wpath))
test.fail_test(test.stderr() != "")

test.run(arguments = '--file=' + subdir_BuildThis)
test.fail_test(test.stdout() != ("subdir/BuildThis %s\n" % wpath))
test.fail_test(test.stderr() != "")

test.run(arguments = '--makefile=SConscript')
test.fail_test(test.stdout() != ("SConscript %s\n" % wpath))
test.fail_test(test.stderr() != "")

test.run(arguments = '--makefile=' + subdir_BuildThis)
test.fail_test(test.stdout() != ("subdir/BuildThis %s\n" % wpath))
test.fail_test(test.stderr() != "")

test.run(arguments = '--sconstruct=SConscript')
test.fail_test(test.stdout() != ("SConscript %s\n" % wpath))
test.fail_test(test.stderr() != "")

test.run(arguments = '--sconstruct=' + subdir_BuildThis)
test.fail_test(test.stdout() != ("subdir/BuildThis %s\n" % wpath))
test.fail_test(test.stderr() != "")

test.run(arguments = '-f -', stdin = """
import os
print "STDIN " + os.getcwd()
""")
test.fail_test(test.stdout() != ("STDIN %s\n" % wpath))
test.fail_test(test.stderr() != "")

test.run(arguments = '-f no_such_file')
test.fail_test(test.stdout() != "")
test.fail_test(test.stderr() != "Ignoring missing script 'no_such_file'\n")

test.pass_test()
