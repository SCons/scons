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

test.write('build.py', r"""
import sys
file = open(sys.argv[1], 'wb')
file.write(sys.argv[2] + "\n")
file.write(open(sys.argv[3], 'rb').read())
file.close
sys.exit(0)
""")

test.write('SConstruct', """
B = Builder(action = r'%s build.py $TARGET 1 $SOURCES')
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
""" % python)

test.write('foo.in', "foo.in\n")

test.run(arguments = '.')

test.fail_test(test.read('foo.out') != "1\nfoo.in\n")

test.up_to_date(arguments = '.')

test.write('SConstruct', """
B = Builder(action = r'%s build.py $TARGET 2 $SOURCES')
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
""" % python)

test.run(arguments = '.')

test.fail_test(test.read('foo.out') != "2\nfoo.in\n")

test.up_to_date(arguments = '.')

test.write('SConstruct', """
import os
import string
def func(env, target, source):
    cmd = r'%s build.py %%s 3 %%s' %% (string.join(map(str, target)),
                                       string.join(map(str, source)))
    print cmd
    return os.system(cmd)
B = Builder(action = func)
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
""" % python)

test.run(arguments = '.', stderr = None)

test.fail_test(test.read('foo.out') != "3\nfoo.in\n")

test.up_to_date(arguments = '.')

test.write('SConstruct', """
import os
assert not globals().has_key('string')
import string
class bld:
    def __init__(self):
        self.cmd = r'%s build.py %%s 4 %%s'
    def __call__(self, env, target, source):
        cmd = self.get_contents(env, target, source)
	print cmd
        return os.system(cmd)
    def get_contents(self, env, target, source):
        return self.cmd %% (string.join(map(str, target)),
                            string.join(map(str, source)))
B = Builder(action = bld())
env = Environment(BUILDERS = { 'B' : B })
env.B(target = 'foo.out', source = 'foo.in')
""" % python)

test.run(arguments = '.')

test.fail_test(test.read('foo.out') != "4\nfoo.in\n")

test.up_to_date(arguments = '.')

test.pass_test()
