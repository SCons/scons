#!/usr/bin/env python
#
# Copyright (c) 2001 Steven Knight
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
import sys
import TestSCons

python = sys.executable

test = TestSCons.TestSCons()

test.subdir('one', 'two', 'three')

test.write('build.py', r"""
import sys
contents = open(sys.argv[2], 'rb').read()
file = open(sys.argv[1], 'wb')
file.write(contents)
file.close()
""")

test.write(['one', 'SConstruct'], """
B = Builder(name = 'B', action = r'%s ../build.py $TARGET $SOURCES')
env = Environment(BUILDERS = [B])
env.B(target = 'foo.out', source = 'foo.in')
env.B(target = 'bar.out', source = 'bar.in')
Default('foo.out')
""" % python)

test.write(['two', 'SConstruct'], """
B = Builder(name = 'B', action = r'%s ../build.py $TARGET $SOURCES')
env = Environment(BUILDERS = [B])
env.B(target = 'foo.out', source = 'foo.in')
env.B(target = 'bar.out', source = 'bar.in')
Default('foo.out', 'bar.out')
""" % python)

test.write(['three', 'SConstruct'], """
B = Builder(name = 'B', action = r'%s ../build.py $TARGET $SOURCES')
env = Environment(BUILDERS = [B])
env.B(target = 'foo.out', source = 'foo.in')
env.B(target = 'bar.out', source = 'bar.in')
Default('foo.out bar.out')
""" % python)

for dir in ['one', 'two', 'three']:

    foo_in = os.path.join(dir, 'foo.in')
    bar_in = os.path.join(dir, 'bar.in')

    test.write(foo_in, foo_in + "\n");

    test.write(bar_in, bar_in + "\n");

    test.run(chdir = dir)	# no arguments, use the Default

test.fail_test(test.read(test.workpath('one', 'foo.out')) != "one/foo.in\n")
test.fail_test(os.path.exists(test.workpath('one', 'bar')))

test.fail_test(test.read(test.workpath('two', 'foo.out')) != "two/foo.in\n")
test.fail_test(test.read(test.workpath('two', 'bar.out')) != "two/bar.in\n")

test.fail_test(test.read(test.workpath('three', 'foo.out')) != "three/foo.in\n")
test.fail_test(test.read(test.workpath('three', 'bar.out')) != "three/bar.in\n")

test.pass_test()
