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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys
import os.path
import types

def match_normcase(lines, matches):
    if not type(lines) is types.ListType:
        lines = string.split(lines, "\n")
    if not type(matches) is types.ListType:
        matches = string.split(matches, "\n")
    if len(lines) != len(matches):
        return
    for i in range(len(lines)):
        if os.path.normcase(lines[i]) != os.path.normcase(matches[i]):
            return
    return 1

test = TestSCons.TestSCons(match=match_normcase)

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
print GetBuildPath('..')
""")

test.write(['sub', 'dir', 'SConstruct'], """
import os
print GetBuildPath('..')
""")

test.run(arguments = '-C sub .',
	 stdout = '%s\nscons: "." is up to date.\n' % wpath)

test.run(arguments = '-C sub -C dir .',
	 stdout = '%s\nscons: "." is up to date.\n' % wpath_sub)

test.run(arguments = ".",
         stdout = 'SConstruct %s\nscons: "." is up to date.\n' % wpath)

test.run(arguments = '--directory=sub/dir .',
	 stdout = '%s\nscons: "." is up to date.\n' % wpath_sub)

test.run(arguments = '-C %s -C %s .' % (wpath_sub_dir, wpath_sub),
	 stdout = '%s\nscons: "." is up to date.\n' % wpath)

test.pass_test()
 
