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
# This test exercises the AddPreAction() and AddPostAction() API
# functions, which add pre-build and post-build actions to nodes.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import stat
import sys
import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.write('SConstruct', """
import os.path

env = Environment(XXX='bar%s')

def before(env, target, source):
    f=open(str(target[0]), "wb")
    f.write("Foo\\n")
    f.close()
    f=open("before.txt", "ab")
    f.write(str(target[0]) + "\\n")
    f.close()

def after(env, target, source):
    fin = open(str(target[0]), "rb")
    fout = open("after_" + str(target[0]), "wb")
    fout.write(fin.read())
    fout.close()
    fin.close()

foo = env.Program(source='foo.c', target='foo')
AddPreAction(foo, before)
AddPostAction('foo%s', after)

bar = env.Program(source='bar.c', target='bar')
env.AddPreAction('$XXX', before)
env.AddPostAction('$XXX', after)
""" % (_exe, _exe))

test.write('foo.c', r"""
#include <stdio.h>

int main(void)
{
    printf("foo.c\n");
    return 0;
}
""")

test.write('bar.c', r"""
#include <stdio.h>

int main(void)
{
    printf("bar.c\n");
    return 0;
}
""")


test.run(arguments='.')

test.run(program=test.workpath('foo'+ _exe), stdout="foo.c\n")
test.run(program=test.workpath('bar'+ _exe), stdout="bar.c\n")

test.fail_test(test.read('before.txt', 'rb') != "bar%s\nfoo%s\n" % (_exe, _exe))

after_foo_exe = test.workpath('after_foo' + _exe)
os.chmod(after_foo_exe, os.stat(after_foo_exe)[stat.ST_MODE] | stat.S_IXUSR)
test.run(program=test.workpath(after_foo_exe), stdout="foo.c\n")

after_bar_exe = test.workpath('after_bar' + _exe)
os.chmod(after_bar_exe, os.stat(after_bar_exe)[stat.ST_MODE] | stat.S_IXUSR)
test.run(program=test.workpath(after_bar_exe), stdout="bar.c\n")

test.pass_test()
