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
# This test exercises the addition operator of Action objects.
# Using Environment.Prepend() and Environment.Append(), you should be
# able to add new actions to existing ones, effectively adding steps
# to a build process.

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import stat
import sys
import TestSCons

if sys.platform == 'win32':
    _exe = '.exe'
else:
    _exe = ''

test = TestSCons.TestSCons()

test.write('foo.c', r"""
#include <stdio.h>

int main(void)
{
    printf("Foo\n");
    return 0;
}
""")

test.write('SConstruct', """

env=Environment()

def before(env, target, source):
    f=open(str(target[0]), "wb")
    f.write("Foo\\n")
    f.close()
    f=open("before.txt", "wb")
    f.write("Bar\\n")
    f.close()

def after(env, target, source):
    fin = open(str(target[0]), "rb")
    fout = open("after%s", "wb")
    fout.write(fin.read())
    fout.close()
    fin.close()

env.Prepend(LINKCOM=Action(before))
env.Append(LINKCOM=Action(after))
env.Program(source='foo.c', target='foo')
""" % _exe)

after_exe = test.workpath('after' + _exe)

test.run(arguments='.')
test.fail_test(open('before.txt', 'rb').read() != "Bar\n")
os.chmod(after_exe, os.stat(after_exe)[stat.ST_MODE] | stat.S_IXUSR)
test.run(program=after_exe, stdout="Foo\n")
test.pass_test()
