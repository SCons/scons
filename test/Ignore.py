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

import sys
import TestSCons

python = sys.executable

test = TestSCons.TestSCons()

test.subdir('subdir')

test.write('build.py', r"""
import sys
contents = open(sys.argv[2], 'rb').read() + open(sys.argv[3], 'rb').read()
file = open(sys.argv[1], 'wb')
for arg in sys.argv[2:]:
    file.write(open(arg, 'rb').read())
file.close()
""")

test.write('SConstruct', """
Foo = Builder(action = r"%s build.py $TARGET $SOURCES")
Bar = Builder(action = r"%s build.py $TARGET $SOURCES")
env = Environment(BUILDERS = { 'Foo' : Foo, 'Bar' : Bar })
env.Foo(target = 'f1.out', source = ['f1a.in', 'f1b.in'])
env.Ignore(target = 'f1.out', dependency = 'f1b.in')
SConscript('subdir/SConscript', "env")
""" % (python, python))

test.write(['subdir', 'SConscript'], """
Import("env")
env.Bar(target = 'f2.out', source = ['f2a.in', 'f2b.in'])
env.Ignore('f2.out', 'f2a.in')
""")

test.write('f1a.in', "f1a.in\n")
test.write('f1b.in', "f1b.in\n")

test.write(['subdir', 'f2a.in'], "subdir/f2a.in\n")
test.write(['subdir', 'f2b.in'], "subdir/f2b.in\n")

test.run(arguments = '.')

test.fail_test(test.read('f1.out') != "f1a.in\nf1b.in\n")
test.fail_test(test.read(['subdir', 'f2.out']) !=
               "subdir/f2a.in\nsubdir/f2b.in\n")

test.up_to_date(arguments = '.')

test.write('f1b.in', "f1b.in 2\n")
test.write(['subdir', 'f2a.in'], "subdir/f2a.in 2\n")

test.up_to_date(arguments = '.')

test.fail_test(test.read('f1.out') != "f1a.in\nf1b.in\n")
test.fail_test(test.read(['subdir', 'f2.out']) !=
               "subdir/f2a.in\nsubdir/f2b.in\n")

test.write('f1a.in', "f1a.in 2\n")
test.write(['subdir', 'f2b.in'], "subdir/f2b.in 2\n")

test.run(arguments = '.')

test.fail_test(test.read('f1.out') != "f1a.in 2\nf1b.in 2\n")
test.fail_test(test.read(['subdir', 'f2.out']) !=
               "subdir/f2a.in 2\nsubdir/f2b.in 2\n")

test.up_to_date(arguments = '.')

test.pass_test()
