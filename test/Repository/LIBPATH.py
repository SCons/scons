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

import string
import TestSCons

test = TestSCons.TestSCons()

test.subdir('foo', ['foo', 'zzz'], 'bar', ['bar', 'yyy'], 'work')

workpath_foo = test.workpath('foo')
workpath_foo_yyy = test.workpath('foo', 'yyy')
workpath_foo_zzz = test.workpath('foo', 'zzz')
workpath_bar = test.workpath('bar')
workpath_bar_yyy = test.workpath('bar', 'yyy')
workpath_bar_zzz = test.workpath('bar', 'zzz')
workpath_work = test.workpath('work')

test.write(['work', 'SConstruct'], r"""
import string
env_zzz = Environment(LIBPATH = ['.', 'zzz'])
env_yyy = Environment(LIBPATH = ['yyy', '.'])
aaa_exe = env_zzz.Program('aaa', 'aaa.c')
bbb_exe = env_yyy.Program('bbb', 'bbb.c')
def write_LIBDIRFLAGS(env, target, source):
    pre = env.subst('$LIBDIRPREFIX')
    suf = env.subst('$LIBDIRSUFFIX')
    f = open(str(target[0]), 'wb')
    for arg in string.split(env.subst('$_LIBDIRFLAGS')):
	if arg[:len(pre)] == pre:
	    arg = arg[len(pre):]
	if arg[-len(suf):] == suf:
	    arg = arg[:-len(pre)]
        f.write(arg + '\n')
    f.close()
    return 0
env_zzz.Command('zzz.out', aaa_exe, write_LIBDIRFLAGS)
env_yyy.Command('yyy.out', bbb_exe, write_LIBDIRFLAGS)
""")

test.write(['work', 'aaa.c'], r"""
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("work/aaa.c\n");
	exit (0);
}
""")

test.write(['work', 'bbb.c'], r"""
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("work/bbb.c\n");
	exit (0);
}
""")

#
opts = "-Y %s -Y %s -Y %s" % (workpath_foo, workpath_work, workpath_bar)
test.run(chdir = 'work', options = opts, arguments = ".")

#dirs = ['.', workpath_foo, workpath_bar, workpath_foo_zzz]
dirs = ['.', workpath_foo, workpath_bar,
        'zzz', workpath_foo_zzz, workpath_bar_zzz]
test.fail_test(test.read(['work', 'zzz.out']) !=
               string.join(dirs, '\n') + '\n')

#dirs = [workpath_bar_yyy, '.', workpath_foo, workpath_bar]
dirs = ['yyy', workpath_foo_yyy, workpath_bar_yyy,
        '.', workpath_foo, workpath_bar]
test.fail_test(test.read(['work', 'yyy.out']) !=
               string.join(dirs, '\n') + '\n')

#
test.run(chdir = 'work', options = '-c', arguments = ".")

test.subdir(['work', 'zzz'], ['work', 'yyy'])

#
test.run(chdir = 'work', options = opts, arguments = ".")

#dirs = ['.', workpath_foo, workpath_bar, 'zzz', workpath_foo_zzz]
dirs = ['.', workpath_foo, workpath_bar,
        'zzz', workpath_foo_zzz, workpath_bar_zzz]
test.fail_test(test.read(['work', 'zzz.out']) !=
               string.join(dirs, '\n') + '\n')

#dirs = ['yyy', workpath_bar_yyy, '.', workpath_foo, workpath_bar]
dirs = ['yyy', workpath_foo_yyy, workpath_bar_yyy,
        '.', workpath_foo, workpath_bar]
test.fail_test(test.read(['work', 'yyy.out']) !=
               string.join(dirs, '\n') + '\n')

#
test.pass_test()
