#!/usr/bin/env python
#
# __COPYRIGHT__
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

"""
This test verifies (on Windows systems) that we fail gracefully and
provide informative messages if someone tries to use a path name
with an invalid drive letter.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import sys
from string import ascii_uppercase

import TestSCons

test = TestSCons.TestSCons()

if sys.platform != 'win32':
    msg = "Skipping drive-letter test on non-Windows platform '%s'\n" % sys.platform
    test.skip_test(msg)

# start at the end looking for unused drive letter
bad_drive = None
for d in reversed(ascii_uppercase):
    if not os.path.isdir(d + ':' + os.sep):
        bad_drive = d + ':'
        break

if bad_drive is None:
    print("All drive letters appear to be in use.")
    print("Cannot test SCons handling of invalid Windows drive letters.")
    test.no_result(1)

test.write('SConstruct', """
def cat(env, source, target):
    target = str(target[0])
    source = list(map(str, source))
    print('cat(%%s) > %%s' %% (source, target))
    with open(target, "wb") as ofp:
        for src in source:
            with open(src, "rb") as ifp:
                ofp.write(ifp.read())

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

test.must_match('aaa.out', "aaa.in\n", mode='r')

# This next test used to provide a slightly different error message:
# "scons: *** Do not know how to make File target `%snot_mentioned'.  Stop.\n"
# Right now, it doesn't seem important enough to track down exactly
# why this changed and fix it, but we'll preserve it here in case it
# becomes an issue or some refactoring restores the old behavior.

test.run(arguments = bad_drive + 'not_mentioned',
         stderr = "scons: *** Do not know how to make File target `%snot_mentioned' (%snot_mentioned).  Stop.\n" % (bad_drive, bad_drive),
         status = 2)

expect = "scons: *** [%sno_target_1] No drive `%s' for target `%sno_target_1'.\n" % (bad_drive, bad_drive, bad_drive)
test.run(arguments=bad_drive + 'no_target_1', stderr=expect, status=2)

expect = "scons: *** [%sno_target_2] Source `ccc.does_not_exist' not found, needed by target `%sno_target_2'.\n" % (bad_drive, bad_drive)
test.run(arguments=bad_drive + 'no_target_2', stderr=expect, status=2)

expect = "scons: *** [ddd.out] Source `%sno_source' not found, needed by target `ddd.out'.\n" % bad_drive
test.run(arguments='ddd.out', stderr=expect, status=2)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
