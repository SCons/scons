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
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.subdir('sub')

test.write('build.py', r"""
import sys
contents = open(sys.argv[2], 'rb').read()
file = open(sys.argv[1], 'wb')
file.write(contents)
file.close()
""")

test.write('SConstruct', """
import os

def buildIt(env, target, source):
    contents = open(str(source[0]), 'rb').read()
    file = open(str(target[0]), 'wb')
    file.write(contents)
    file.close()
    return 0

def sub(env, target, source):
    target = str(target[0])
    source = str(source[0])
    t = open(target, 'wb')
    files = os.listdir(source)
    files.sort()
    for f in files:
        t.write(open(os.path.join(source, f), 'rb').read())
    t.close()
    return 0

env = Environment()
env.Command(target = 'f1.out', source = 'f1.in',
            action = buildIt)
env.Command(target = 'f2.out', source = 'f2.in',
            action = r'%s' + " build.py temp2 $SOURCES\\n" + r'%s' + " build.py $TARGET temp2")

env.Command(target = 'f3.out', source = 'f3.in',
            action = [ [ r'%s', 'build.py', 'temp3', '$SOURCES' ],
                       [ r'%s', 'build.py', '$TARGET', 'temp3'] ])
env.Command(target = 'f4.out', source = 'sub', action = sub)
""" % (python, python, python, python))

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write(['sub', 'f4a'], "sub/f4a\n")
test.write(['sub', 'f4b'], "sub/f4b\n")
test.write(['sub', 'f4c'], "sub/f4c\n")

test.run(arguments = '.')

test.fail_test(test.read('f1.out') != "f1.in\n")
test.fail_test(test.read('f2.out') != "f2.in\n")
test.fail_test(test.read('f3.out') != "f3.in\n")
test.fail_test(test.read('f4.out') != "sub/f4a\nsub/f4b\nsub/f4c\n")

test.pass_test()
