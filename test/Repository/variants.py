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
import time
import TestSCons

test = TestSCons.TestSCons()

test.subdir('repository', ['repository', 'src'],
            'work1', ['work1', 'src'],
            'work2', ['work2', 'src'])

repository_build_foo_xxx = test.workpath('repository', 'build', 'foo', 'xxx')
work1_build_foo_xxx = test.workpath('work1', 'build', 'foo', 'xxx')
work1_build_bar_xxx = test.workpath('work1', 'build', 'bar', 'xxx')

opts = "-Y " + test.workpath('repository')

#
test.write(['repository', 'SConstruct'], r"""
OS = ARGUMENTS['OS']
build_os = "#build/" + OS
ccflags = {
    'foo' : '-DFOO',
    'bar' : '-DBAR',
}
env = Environment(CCFLAGS = ccflags[OS],
                  CPPPATH = build_os)
BuildDir(build_os, 'src')
SConscript(build_os + '/SConscript', "env")
""")

test.write(['repository', 'src', 'SConscript'], r"""
Import("env")
env.Program('xxx', ['aaa.c', 'bbb.c', 'main.c'])
""")

test.write(['repository', 'src', 'iii.h'], r"""
#ifdef	FOO
#define	STRING	"REPOSITORY_FOO"
#endif
#ifdef	BAR
#define	STRING	"REPOSITORY_BAR"
#endif
""")

test.write(['repository', 'src', 'aaa.c'], r"""
#include <iii.h>
void
aaa(void)
{
	printf("repository/src/aaa.c:  %s\n", STRING);
}
""")

test.write(['repository', 'src', 'bbb.c'], r"""
#include <iii.h>
void
bbb(void)
{
	printf("repository/src/bbb.c:  %s\n", STRING);
}
""")

test.write(['repository', 'src', 'main.c'], r"""
#include <iii.h>
extern void aaa(void);
extern void bbb(void);
int
main(int argc, char *argv[])
{
#ifdef	BAR
	printf("Only when -DBAR.\n");
#endif
	aaa();
	bbb();
	printf("repository/src/main.c:  %s\n", STRING);
	exit (0);
}
""")

#
test.run(chdir = 'repository', options = opts + " OS=foo", arguments = '.')

test.run(program = repository_build_foo_xxx, stdout =
"""repository/src/aaa.c:  REPOSITORY_FOO
repository/src/bbb.c:  REPOSITORY_FOO
repository/src/main.c:  REPOSITORY_FOO
""")

test.fail_test(os.path.exists(test.workpath('repository', 'src', '.sconsign')))
test.fail_test(os.path.exists(test.workpath('src', '.sconsign')))

# Make the entire repository non-writable, so we'll detect
# if we try to write into it accidentally.
test.writable('repository', 0)

#
test.up_to_date(chdir = 'work1', options = opts + " OS=foo", arguments = '.')

test.fail_test(os.path.exists(test.workpath('work1', 'build', 'foo', 'aaa.o')))
test.fail_test(os.path.exists(test.workpath('work1', 'build', 'foo', 'bbb.o')))
test.fail_test(os.path.exists(test.workpath('work1', 'build', 'foo', 'main.o')))
test.fail_test(os.path.exists(test.workpath('work1', 'build', 'foo', 'xxx')))

#
test.run(chdir = 'work1', options = opts, arguments = 'OS=bar .')

test.run(program = work1_build_bar_xxx, stdout =
"""Only when -DBAR.
repository/src/aaa.c:  REPOSITORY_BAR
repository/src/bbb.c:  REPOSITORY_BAR
repository/src/main.c:  REPOSITORY_BAR
""")

test.fail_test(os.path.exists(test.workpath('repository', 'src', '.sconsign')))
test.fail_test(os.path.exists(test.workpath('src', '.sconsign')))

test.up_to_date(chdir = 'work1', options = opts + " OS=bar", arguments = '.')

#
time.sleep(2)
test.write(['work1', 'src', 'iii.h'], r"""
#ifdef	FOO
#define	STRING	"WORK_FOO"
#endif
#ifdef	BAR
#define	STRING	"WORK_BAR"
#endif
""")

#
test.run(chdir = 'work1', options = opts + " OS=bar", arguments = '.')

test.run(program = work1_build_bar_xxx, stdout =
"""Only when -DBAR.
repository/src/aaa.c:  WORK_BAR
repository/src/bbb.c:  WORK_BAR
repository/src/main.c:  WORK_BAR
""")

test.fail_test(os.path.exists(test.workpath('repository', 'src', '.sconsign')))
test.fail_test(os.path.exists(test.workpath('src', '.sconsign')))

test.up_to_date(chdir = 'work1', options = opts + " OS=bar", arguments = '.')

#
test.run(chdir = 'work1', options = opts + " OS=foo", arguments = '.')

test.run(program = work1_build_foo_xxx, stdout =
"""repository/src/aaa.c:  WORK_FOO
repository/src/bbb.c:  WORK_FOO
repository/src/main.c:  WORK_FOO
""")

test.fail_test(os.path.exists(test.workpath('repository', 'src', '.sconsign')))
test.fail_test(os.path.exists(test.workpath('src', '.sconsign')))

test.up_to_date(chdir = 'work1', options = opts + " OS=foo", arguments = '.')

#
test.pass_test()
