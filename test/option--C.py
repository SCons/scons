#!/usr/bin/env python

__revision__ = "test/option--C.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

wpath = test.workpath()
wpath_sub = test.workpath('sub')
wpath_sub_dir = test.workpath('sub', 'dir')

test.subdir('sub', ['sub', 'dir'])

test.write('SConstruct', """
import os
print "SConstruct", os.getcwd()
""")

test.write(['sub', 'SConstruct'], """
import os
print "sub/SConstruct", os.getcwd()
""")

test.write(['sub', 'dir', 'SConstruct'], """
import os
print "sub/dir/SConstruct", os.getcwd()
""")

test.run(chdir = '.', arguments = '-C sub')

test.fail_test(test.stdout() != "sub/SConstruct %s\n" % wpath_sub)
test.fail_test(test.stderr() != "")

test.run(chdir = '.', arguments = '-C sub -C dir')

test.fail_test(test.stdout() != "sub/dir/SConstruct %s\n" % wpath_sub_dir)
test.fail_test(test.stderr() != "")

test.run(chdir = '.')

test.fail_test(test.stdout() != "SConstruct %s\n" % wpath)
test.fail_test(test.stderr() != "")

test.run(chdir = '.', arguments = '--directory=sub/dir')

test.fail_test(test.stdout() != "sub/dir/SConstruct %s\n" % wpath_sub_dir)
test.fail_test(test.stderr() != "")

test.run(chdir = '.', arguments = '-C %s -C %s' % (wpath_sub_dir, wpath_sub))

test.fail_test(test.stdout() != "sub/SConstruct %s\n" % wpath_sub)
test.fail_test(test.stderr() != "")

test.pass_test()
 
