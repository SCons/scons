#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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
This test verifies that we fail gracefully and provide informative
messages if someone tries to build a target that hasn't been defined
or uses a nonexistent source file.  On Windows systems, it checks
to make sure that this applies to invalid drive letters as well.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import os.path
import string
import sys

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment()
env.Command("aaa.out", "aaa.in", "should never get executed")
env.Command("bbb.out", "bbb.in", "should never get executed")
""")

test.run(arguments = 'foo',
         stderr = "scons: *** Do not know how to make target `foo'.  Stop.\n",
         status = 2)

test.run(arguments = '-k foo/bar foo',
         stderr = """scons: *** Do not know how to make target `foo/bar'.
scons: *** Do not know how to make target `foo'.
""",
         status = 2)

test.run(arguments = "aaa.out",
         stderr = "scons: *** No Builder for target `aaa.in', needed by `aaa.out'.  Stop.\n",
         status = 2)

test.run(arguments = "-k bbb.out aaa.out",
         stderr = """scons: *** No Builder for target `bbb.in', needed by `bbb.out'.
scons: *** No Builder for target `aaa.in', needed by `aaa.out'.
""",
         status = 2)

if sys.platform == 'win32':
    bad_drive = None
    for i in range(len(string.uppercase)-1, -1, -1):
        d = string.uppercase[i]
        if not os.path.isdir(d + ':' + os.sep):
            bad_drive = d + ':' + '\\' + os.sep
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
env.Build(bad_drive + 'no_target', 'bbb.in')
env.Build('ccc.out', bad_drive + 'no_source')
""" % bad_drive)

    test.write("aaa.in", "aaa.in\n")

    test.write("no_target", "no_target\n")

    test.write("no_source", "no_source\n")

    test.run(arguments = 'aaa.out')

    test.fail_test(test.read('aaa.out') != "aaa.in\n")

    test.run(arguments = bad_drive + 'no_target',
             stderr = "scons: *** Do not know how to make target `%sno_target'.  Stop.\n" % bad_drive,
             status = 2)

    test.run(arguments = 'ccc.out',
             stderr = "scons: *** No Builder for target `%sno_source', needed by `ccc.out'.  Stop.\n" % bad_drive,
             status = 2)

test.pass_test()
