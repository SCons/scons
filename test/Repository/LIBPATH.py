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
env_zzz = Environment(LIBPATH = ['.', 'zzz'])
env_yyy = Environment(LIBPATH = ['yyy', '.'])
aaa_exe = env_zzz.Program('aaa', 'aaa.c')
bbb_exe = env_yyy.Program('bbb', 'bbb.c')
def write_LIBDIRFLAGS(env, target, source):
    pre = env.subst('$LIBDIRPREFIX')
    suf = env.subst('$LIBDIRSUFFIX')
    with open(str(target[0]), 'w') as f:
        for arg in env.subst('$_LIBDIRFLAGS', target=target).split():
            if arg[:len(pre)] == pre:
                arg = arg[len(pre):]
            if arg[-len(suf):] == suf:
                arg = arg[:-len(pre)]
            f.write(arg + '\n')
    return 0
env_zzz.Command('zzz.out', aaa_exe, write_LIBDIRFLAGS)
env_yyy.Command('yyy.out', bbb_exe, write_LIBDIRFLAGS)

if env_yyy['PLATFORM'] == 'darwin':
    # The Mac OS X linker complains about nonexistent directories
    # specified as -L arguments.  Suppress its warnings so we don't
    # treat the warnings on stderr as a failure.
    env_yyy.Append(LINKFLAGS=['-w'])
    env_zzz.Append(LINKFLAGS=['-w'])
""")

test.write(['work', 'aaa.c'], r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("work/aaa.c\n");
        exit (0);
}
""")

test.write(['work', 'bbb.c'], r"""
#include <stdio.h>
#include <stdlib.h>
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
test.must_match(['work', 'zzz.out'],'\n'.join(dirs) + '\n', mode='r')

#dirs = [workpath_bar_yyy, '.', workpath_foo, workpath_bar]
dirs = ['yyy', workpath_foo_yyy, workpath_bar_yyy,
        '.', workpath_foo, workpath_bar]
test.must_match(['work', 'yyy.out'], '\n'.join(dirs) + '\n', mode='r')

#
test.run(chdir = 'work', options = '-c', arguments = ".")

test.subdir(['work', 'zzz'], ['work', 'yyy'])

#
test.run(chdir = 'work', options = opts, arguments = ".")

#dirs = ['.', workpath_foo, workpath_bar, 'zzz', workpath_foo_zzz]
dirs = ['.', workpath_foo, workpath_bar,
        'zzz', workpath_foo_zzz, workpath_bar_zzz]
test.must_match(['work', 'zzz.out'], '\n'.join(dirs) + '\n', mode='r')

#dirs = ['yyy', workpath_bar_yyy, '.', workpath_foo, workpath_bar]
dirs = ['yyy', workpath_foo_yyy, workpath_bar_yyy,
        '.', workpath_foo, workpath_bar]
test.must_match(['work', 'yyy.out'], '\n'.join(dirs) + '\n', mode='r')

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
