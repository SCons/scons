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

import os
import string
import sys

import TestSCons

test = TestSCons.TestSCons()

subdir_SConscript = os.path.join('subdir', 'SConscript')
sub1_xxx_exe = test.workpath('sub1', 'xxx.exe')
sub2_xxx_exe = test.workpath('sub2', 'xxx.exe')
sub3_xxx_exe = test.workpath('sub3', 'xxx.exe')
sub4_xxx_exe = test.workpath('sub4', 'xxx.exe')

test.subdir('subdir', 'sub1', 'sub2', 'sub3', 'sub4')

if sys.platform != 'win32':
    test.write(sub1_xxx_exe, "\n")

os.mkdir(sub2_xxx_exe)

test.write(sub3_xxx_exe, "\n")
os.chmod(sub3_xxx_exe, 0777)

test.write(sub4_xxx_exe, "\n")
os.chmod(sub4_xxx_exe, 0777)

env_path = os.environ['PATH']

pathdirs_1234 = [ test.workpath('sub1'),
                  test.workpath('sub2'),
                  test.workpath('sub3'),
                  test.workpath('sub4'),
                ] + string.split(env_path, os.pathsep)

pathdirs_1243 = [ test.workpath('sub1'),
                  test.workpath('sub2'),
                  test.workpath('sub4'),
                  test.workpath('sub3'),
                ] + string.split(env_path, os.pathsep)

test.write('SConstruct', """
SConscript('%s')
print WhereIs('xxx.exe')
print WhereIs('xxx.exe', %s)
print WhereIs('xxx.exe', %s)
print WhereIs('xxx.exe', %s)
print WhereIs('xxx.exe', %s)
""" % (subdir_SConscript,
       repr(string.join(pathdirs_1234, os.pathsep)),
       repr(string.join(pathdirs_1243, os.pathsep)),
       repr(pathdirs_1234),
       repr(pathdirs_1243),
      ))

test.write(subdir_SConscript, """
print WhereIs('xxx.exe')
print WhereIs('xxx.exe', %s)
print WhereIs('xxx.exe', %s)
print WhereIs('xxx.exe', %s)
print WhereIs('xxx.exe', %s)
""" % (repr(string.join(pathdirs_1234, os.pathsep)),
       repr(string.join(pathdirs_1243, os.pathsep)),
       repr(pathdirs_1234),
       repr(pathdirs_1243),
      ))

os.environ['PATH'] = string.join(pathdirs_1234, os.pathsep)

expect = [ test.workpath(sub3_xxx_exe),
           test.workpath(sub3_xxx_exe),
           test.workpath(sub4_xxx_exe),
           test.workpath(sub3_xxx_exe),
           test.workpath(sub4_xxx_exe),
           test.workpath(sub3_xxx_exe),
           test.workpath(sub3_xxx_exe),
           test.workpath(sub4_xxx_exe),
           test.workpath(sub3_xxx_exe),
           test.workpath(sub4_xxx_exe),
	 ]

test.run(arguments = ".",
         stdout = test.wrap_stdout(read_str = string.join(expect, "\n") + "\n",
                                   build_str = 'scons: "." is up to date.\n'))

os.environ['PATH'] = string.join(pathdirs_1243, os.pathsep)

expect = [ test.workpath(sub4_xxx_exe),
           test.workpath(sub3_xxx_exe),
           test.workpath(sub4_xxx_exe),
           test.workpath(sub3_xxx_exe),
           test.workpath(sub4_xxx_exe),
           test.workpath(sub4_xxx_exe),
           test.workpath(sub3_xxx_exe),
           test.workpath(sub4_xxx_exe),
           test.workpath(sub3_xxx_exe),
           test.workpath(sub4_xxx_exe),
	 ]

test.run(arguments = ".",
         stdout = test.wrap_stdout(read_str = string.join(expect, "\n") + "\n",
                                   build_str = 'scons: "." is up to date.\n'))

test.pass_test()
