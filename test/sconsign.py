#!/usr/bin/env python
#
# Copyright (c) 2001, 2002, 2003 Steven Knight
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
import TestSCons
import TestCmd
import cPickle

test = TestSCons.TestSCons(match = TestCmd.match_re)

test.subdir('sub1', 'sub2', 'sub3')

test.write('SConstruct', """
def build1(target, source, env):
    open(str(target[0]), 'wb').write(open(str(source[0]), 'rb').read())
    return None

def build2(target, source, env):
    import os
    import os.path
    open(str(target[0]), 'wb').write(open(str(source[0]), 'rb').read())
    dir, file = os.path.split(str(target[0]))
    os.chmod(dir, 0555)
    return None

B1 = Builder(action = build1)
B2 = Builder(action = build2)
env = Environment(BUILDERS = { 'B1' : B1, 'B2' : B2 })
env.B1(target = 'sub1/foo.out', source = 'foo.in')
env.B2(target = 'sub2/foo.out', source = 'foo.in')
env.B2(target = 'sub3/foo.out', source = 'foo.in')
""")

test.write('foo.in', "foo.in\n")

sub1__sconsign = test.workpath('sub1', '.sconsign')
sub2__sconsign = test.workpath('sub2', '.sconsign')
sub3__sconsign = test.workpath('sub3', '.sconsign')

cPickle.dump({}, open(sub1__sconsign, 'wb'), 1)
cPickle.dump({}, open(sub2__sconsign, 'wb'), 1)

os.chmod(sub1__sconsign, 0444)

test.run(arguments = '.')

test.fail_test(test.read(sub1__sconsign) == "")
test.fail_test(test.read(sub2__sconsign) == "")

os.chmod(sub1__sconsign, 0666)

test.write('SConstruct', """
def build1(target, source, env):
    open(str(target[0]), 'wb').write(open(str(source[0]), 'rb').read())
    return None

B1 = Builder(action = build1)
env = Environment(BUILDERS = { 'B1' : B1})
env.B1(target = 'sub1/foo.out', source = 'foo.in')
""")

stderr = '''
scons: warning: Ignoring corrupt .sconsign file: sub1.\.sconsign
.*
'''

stdout = test.wrap_stdout('build1\("sub1.foo\.out", "foo\.in"\)\n')

test.write(sub1__sconsign, 'not:a:sconsign:file')
test.run(arguments = '.', stderr=stderr, stdout=stdout)

test.write(sub1__sconsign, '\0\0\0\0\0\0\0\0\0\0\0\0\0\0')
test.run(arguments = '.', stderr=stderr, stdout=stdout)


test.pass_test()
