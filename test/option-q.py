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

import os.path
import string
import sys

import TestSCons

test = TestSCons.TestSCons()

python = sys.executable

test.write('build.py', r"""
import sys
contents = open(sys.argv[2], 'rb').read()
file = open(sys.argv[1], 'wb')
file.write(contents)
file.close()
""")

test.write('SConstruct', """
B = Builder(action=r'%s build.py $TARGET $SOURCES')
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'aaa.out', source = 'aaa.in')
env.B(target = 'bbb.out', source = 'bbb.in')
""" % python)

test.write('aaa.in', "aaa.in\n")
test.write('bbb.in', "bbb.in\n")

test.run(arguments = '-q aaa.out', status = 1)

test.fail_test(os.path.exists(test.workpath('aaa.out')))

test.run(arguments = 'aaa.out')

test.fail_test(test.read('aaa.out') != "aaa.in\n")

test.run(arguments = '-q aaa.out', status = 0)

test.run(arguments = '--question bbb.out', status = 1)

test.fail_test(os.path.exists(test.workpath('bbb.out')))

test.run(arguments = 'bbb.out')

test.fail_test(test.read('bbb.out') != "bbb.in\n")

test.run(arguments = '--question bbb.out', status = 0)

test.pass_test()
 
