#!/usr/bin/env python
#
# Copyright (c) 2001, 2002, 2003 Steven Knight
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

"""
This test verifies (on Windows systems) that we fail gracefully and
provide informative messages if someone tries to use a path name
with an invalid drive letter.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import os.path
import string
import sys

import TestSCons

test = TestSCons.TestSCons()

if sys.platform != 'win32':
    test.pass_test()

bad_drive = None
for i in range(len(string.uppercase)-1, -1, -1):
    d = string.uppercase[i]
    if not os.path.isdir(d + ':' + os.sep):
        bad_drive = d + ':'
        break

if bad_drive is None:
    print "All drive letters appear to be in use."
    print "Cannot test SCons handling of invalid Win32 drive letters."
    test.no_result(1);

test.write('SConstruct', """
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    print 'cat(%%s) > %%s' %% (source, target)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()

bad_drive = '%s'
env = Environment(BUILDERS={'Build':Builder(action=cat)})
env.Build('aaa.out', 'aaa.in')
env.Build(bad_drive + 'no_target_1', 'bbb.exists')
env.Build(bad_drive + 'no_target_2', 'ccc.does_not_exist')
env.Build('ddd.out', bad_drive + 'no_source')
""" % (bad_drive + '\\' + os.sep))

bad_drive = bad_drive + os.sep

test.write("aaa.in", "aaa.in\n")
test.write("bbb.exists", "bbb.exists\n")

test.write("no_target_1", "no_target_1\n")
test.write("no_target_2", "no_target_2\n")
test.write("no_source", "no_source\n")

test.run(arguments = 'aaa.out')

test.fail_test(test.read('aaa.out') != "aaa.in\n")

test.run(arguments = bad_drive + 'not_mentioned',
         stderr = "scons: *** Do not know how to make target `%snot_mentioned'.  Stop.\n" % bad_drive,
         status = 2)

test.run(arguments = bad_drive + 'no_target_1',
         stderr = "scons: *** No drive `%s' for target `%sno_target_1'.  Stop.\n" % (bad_drive, bad_drive),
         status = 2)

test.run(arguments = bad_drive + 'no_target_2',
         stderr = "scons: *** No Builder for target `ccc.does_not_exist', needed by `%sno_target_2'.  Stop.\n" % bad_drive,
         status = 2)

test.run(arguments = 'ddd.out',
         stderr = "scons: *** No Builder for target `%sno_source', needed by `ddd.out'.  Stop.\n" % bad_drive,
         status = 2)

test.pass_test()
