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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os.path
import os
import string
import sys
import TestSCons

python = sys.executable

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
contents = open(sys.argv[2], 'rb').read()
file = open(sys.argv[1], 'wb')
file.write(contents)
file.close()
""")

test.write('SConstruct', """
B = Builder(name = "B", action = r'%s build.py $TARGETS $SOURCES')
env = Environment(BUILDERS = [B])
env.B(target = 'f1.out', source = 'f1.in')
env.B(target = 'f2.out', source = 'f2.in')
""" % python)

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")



test.run(arguments = 'f1.out')

test.run(arguments = 'f1.out f2.out', stdout =
"""scons: "f1.out" is up to date.
%s build.py f2.out f2.in
""" % python)

atime = os.path.getatime(test.workpath('f1.in'))
mtime = os.path.getmtime(test.workpath('f1.in'))

test.run(arguments = '--max-drift=0 f1.out f2.out', stdout =
"""scons: "f1.out" is up to date.
scons: "f2.out" is up to date.
""")

test.write('f1.in', "f1.in delta\n")
os.utime(test.workpath('f1.in'), (atime,mtime))

test.run(arguments = '--max-drift=0 f1.out f2.out', stdout =
"""scons: "f1.out" is up to date.
scons: "f2.out" is up to date.
""")

test.run(arguments = '--max-drift=-1 f1.out f2.out', stdout =
"""%s build.py f1.out f1.in
scons: "f2.out" is up to date.
"""%python)

test.pass_test()

