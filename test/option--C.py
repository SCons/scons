#!/usr/bin/env python

__revision__ = "test/option--C.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

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

test.run(arguments = '-C sub',
	 stdout = "sub/SConstruct %s\n" % wpath_sub)

test.run(arguments = '-C sub -C dir',
	 stdout = "sub/dir/SConstruct %s\n" % wpath_sub_dir)

test.run(stdout = "SConstruct %s\n" % wpath)

test.run(arguments = '--directory=sub/dir',
	 stdout = "sub/dir/SConstruct %s\n" % wpath_sub_dir)

test.run(arguments = '-C %s -C %s' % (wpath_sub_dir, wpath_sub),
	 stdout = "sub/SConstruct %s\n" % wpath_sub)

test.pass_test()
 
