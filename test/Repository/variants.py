#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

import os.path
import sys
import time

from TestSCons import TestSCons, _exe, _obj

test = TestSCons()

test.subdir(
    'repository',
    ['repository', 'src1'],
    ['repository', 'src2'],
    ['repository', 'src2', 'include'],
    ['repository', 'src2', 'xxx'],
    ['repository', 'build2'],
    ['repository', 'build2', 'foo'],
    ['repository', 'build2', 'bar'],
    'work1',
    ['work1', 'src1'],
    'work2',
    ['work2', 'src2'],
    ['work2', 'src2', 'include'],
    ['work2', 'src2', 'xxx'],
)

aaa_obj = 'aaa' + _obj
bbb_obj = 'bbb' + _obj
main_obj = 'main' + _obj

xxx_exe = 'xxx' + _exe

repository_build1_foo_xxx = test.workpath('repository', 'build1', 'foo', 'xxx')
work1_build1_foo_xxx = test.workpath('work1', 'build1', 'foo', 'xxx')
work1_build1_bar_xxx = test.workpath('work1', 'build1', 'bar', 'xxx')

repository_build2_foo_src2_xxx_xxx = test.workpath(
    'repository', 'build2', 'foo', 'src2', 'xxx', 'xxx'
)
repository_build2_bar_src2_xxx_xxx = test.workpath(
    'repository', 'build2', 'bar', 'src2', 'xxx', 'xxx'
)
work2_build2_foo_src2_xxx_xxx = test.workpath(
    'work2', 'build2', 'foo', 'src2', 'xxx', 'xxx'
)
work2_build2_bar_src2_xxx_xxx = test.workpath(
    'work2', 'build2', 'bar', 'src2', 'xxx', 'xxx'
)

opts = "-Y " + test.workpath('repository')

#
test.write(['repository', 'SConstruct'], r"""
OS = ARGUMENTS.get('OS', '')
build1_os = "#build1/" + OS
DefaultEnvironment(tools=[])  # test speedup
default = Environment()
ccflags = {
    '': '',
    'foo': '-DFOO',
    'bar': '-DBAR',
}
env1 = Environment(
    CCFLAGS=default.subst('$CCFLAGS %s' % ccflags[OS]), CPPPATH=build1_os
)
VariantDir(build1_os, 'src1')
SConscript(build1_os + '/SConscript', "env1")

SConscript('build2/foo/SConscript')
SConscript('build2/bar/SConscript')
""")

test.write(['repository', 'src1', 'SConscript'], r"""
Import("env1")
env1.Program('xxx', ['aaa.c', 'bbb.c', 'main.c'])
""")

test.write(['repository', 'build2', 'foo', 'SConscript'], r"""
VariantDir('src2', '#src2')

default = Environment()
env2 = Environment(
    CCFLAGS=default.subst('$CCFLAGS -DFOO'), CPPPATH=['#src2/xxx', '#src2/include']
)

SConscript('src2/xxx/SConscript', "env2")
""")

test.write(['repository', 'build2', 'bar', 'SConscript'], r"""
VariantDir('src2', '#src2')

default = Environment()
env2 = Environment(
    CCFLAGS=default.subst('$CCFLAGS -DBAR'), CPPPATH=['#src2/xxx', '#src2/include']
)

SConscript('src2/xxx/SConscript', "env2")
""")

test.write(['repository', 'src2', 'xxx', 'SConscript'], r"""
Import("env2")
env2.Program('xxx', ['main.c'])
""")

test.write(['repository', 'src1', 'iii.h'], r"""
#ifdef  FOO
#define STRING  "REPOSITORY_FOO"
#endif
#ifdef  BAR
#define STRING  "REPOSITORY_BAR"
#endif
""")

test.write(['repository', 'src1', 'aaa.c'], r"""
#include <stdio.h>
#include <stdlib.h>
#include <iii.h>
void
aaa(void)
{
        printf("repository/src1/aaa.c:  %s\n", STRING);
}
""")

test.write(['repository', 'src1', 'bbb.c'], r"""
#include <stdio.h>
#include <stdlib.h>
#include <iii.h>
void
bbb(void)
{
        printf("repository/src1/bbb.c:  %s\n", STRING);
}
""")

test.write(['repository', 'src1', 'main.c'], r"""
#include <stdio.h>
#include <stdlib.h>
#include <iii.h>
extern void aaa(void);
extern void bbb(void);
int
main(int argc, char *argv[])
{
#ifdef  BAR
        printf("Only when -DBAR.\n");
#endif
        aaa();
        bbb();
        printf("repository/src1/main.c:  %s\n", STRING);
        exit (0);
}
""")

test.write(['repository', 'src2', 'include', 'my_string.h'], r"""
#ifdef  FOO
#define INCLUDE_OS      "FOO"
#endif
#ifdef  BAR
#define INCLUDE_OS      "BAR"
#endif
#define INCLUDE_STRING  "repository/src2/include/my_string.h:  %s\n"
""")

test.write(['repository', 'src2', 'xxx', 'include.h'], r"""
#include <my_string.h>
#ifdef  FOO
#define XXX_OS          "FOO"
#endif
#ifdef  BAR
#define XXX_OS          "BAR"
#endif
#define XXX_STRING      "repository/src2/xxx/include.h:  %s\n"
""")

test.write(['repository', 'src2', 'xxx', 'main.c'], r"""
#include <stdio.h>
#include <stdlib.h>
#include <include.h>
#ifdef  FOO
#define MAIN_OS         "FOO"
#endif
#ifdef  BAR
#define MAIN_OS         "BAR"
#endif
int
main(int argc, char *argv[])
{
        printf(INCLUDE_STRING, INCLUDE_OS);
        printf(XXX_STRING, XXX_OS);
        printf("repository/src2/xxx/main.c:  %s\n", MAIN_OS);
        exit (0);
}
""")

#
test.run(chdir='repository', options=opts + " OS=foo", arguments='.')

test.run(program=repository_build1_foo_xxx, stdout="""\
repository/src1/aaa.c:  REPOSITORY_FOO
repository/src1/bbb.c:  REPOSITORY_FOO
repository/src1/main.c:  REPOSITORY_FOO
""")

database_name = test.get_sconsignname()
test.fail_test(os.path.exists(test.workpath('repository', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('repository', 'src2', database_name)))
test.fail_test(os.path.exists(test.workpath('work1', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('work2', 'src2', database_name)))

test.run(program=repository_build2_foo_src2_xxx_xxx, stdout="""\
repository/src2/include/my_string.h:  FOO
repository/src2/xxx/include.h:  FOO
repository/src2/xxx/main.c:  FOO
""")

test.run(program=repository_build2_bar_src2_xxx_xxx, stdout="""\
repository/src2/include/my_string.h:  BAR
repository/src2/xxx/include.h:  BAR
repository/src2/xxx/main.c:  BAR
""")

test.fail_test(os.path.exists(test.workpath('repository', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('repository', 'src2', database_name)))
test.fail_test(os.path.exists(test.workpath('work1', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('work2', 'src2', database_name)))

# Make the entire repository non-writable, so we'll detect
# if we try to write into it accidentally.
test.writable('repository', 0)

#
test.up_to_date(chdir='work1', options=opts + " OS=foo", arguments='build1')

test.fail_test(os.path.exists(test.workpath('work1', 'build1', 'foo', aaa_obj)))
test.fail_test(os.path.exists(test.workpath('work1', 'build1', 'foo', bbb_obj)))
test.fail_test(os.path.exists(test.workpath('work1', 'build1', 'foo', main_obj)))
test.fail_test(os.path.exists(test.workpath('work1', 'build1', 'foo', xxx_exe)))

#
test.run(chdir='work1', options=opts, arguments='OS=bar .')

test.run(program=work1_build1_bar_xxx, stdout="""\
Only when -DBAR.
repository/src1/aaa.c:  REPOSITORY_BAR
repository/src1/bbb.c:  REPOSITORY_BAR
repository/src1/main.c:  REPOSITORY_BAR
""")

test.fail_test(os.path.exists(test.workpath('repository', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('repository', 'src2', database_name)))
test.fail_test(os.path.exists(test.workpath('work1', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('work2', 'src2', database_name)))
test.up_to_date(chdir='work1', options=opts + " OS=bar", arguments='build1')

test.sleep()  # delay for timestamps
test.write(['work1', 'src1', 'iii.h'], r"""
#ifdef  FOO
#define STRING  "WORK_FOO"
#endif
#ifdef  BAR
#define STRING  "WORK_BAR"
#endif
""")

#
test.run(chdir='work1', options=opts + " OS=bar", arguments='build1')

test.run(program=work1_build1_bar_xxx, stdout="""\
Only when -DBAR.
repository/src1/aaa.c:  WORK_BAR
repository/src1/bbb.c:  WORK_BAR
repository/src1/main.c:  WORK_BAR
""")

test.fail_test(os.path.exists(test.workpath('repository', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('repository', 'src2', database_name)))
test.fail_test(os.path.exists(test.workpath('work1', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('work2', 'src2', database_name)))
test.up_to_date(chdir='work1', options=opts + " OS=bar", arguments='build1')

#
test.run(chdir='work1', options=opts + " OS=foo", arguments='build1')

test.run(program=work1_build1_foo_xxx, stdout="""\
repository/src1/aaa.c:  WORK_FOO
repository/src1/bbb.c:  WORK_FOO
repository/src1/main.c:  WORK_FOO
""")

test.fail_test(os.path.exists(test.workpath('repository', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('repository', 'src2', database_name)))
test.fail_test(os.path.exists(test.workpath('work1', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('work2', 'src2', database_name)))
test.up_to_date(chdir='work1', options=opts + " OS=foo", arguments='build1')
test.up_to_date(chdir='work2', options=opts, arguments='build2')

test.fail_test(
    os.path.exists(test.workpath('work2', 'build2', 'foo', 'src2', 'xxx', aaa_obj))
)
test.fail_test(
    os.path.exists(test.workpath('work2', 'build2', 'foo', 'src2', 'xxx', bbb_obj))
)
test.fail_test(
    os.path.exists(test.workpath('work2', 'build2', 'foo', 'src2', 'xxx', main_obj))
)
test.fail_test(
    os.path.exists(test.workpath('work2', 'build2', 'foo', 'src2', 'xxx', xxx_exe))
)
test.fail_test(
    os.path.exists(test.workpath('work2', 'build2', 'bar', 'src2', 'xxx', aaa_obj))
)
test.fail_test(
    os.path.exists(test.workpath('work2', 'build2', 'bar', 'src2', 'xxx', bbb_obj))
)
test.fail_test(
    os.path.exists(test.workpath('work2', 'build2', 'bar', 'src2', 'xxx', main_obj))
)
test.fail_test(
    os.path.exists(test.workpath('work2', 'build2', 'bar', 'src2', 'xxx', xxx_exe))
)

test.sleep()  # delay for timestamps
test.write(['work2', 'src2', 'include', 'my_string.h'], r"""
#ifdef  FOO
#define INCLUDE_OS      "FOO"
#endif
#ifdef  BAR
#define INCLUDE_OS      "BAR"
#endif
#define INCLUDE_STRING  "work2/src2/include/my_string.h:  %s\n"
""")

test.run(chdir='work2', options=opts, arguments='build2')

test.run(program=work2_build2_foo_src2_xxx_xxx, stdout="""\
work2/src2/include/my_string.h:  FOO
repository/src2/xxx/include.h:  FOO
repository/src2/xxx/main.c:  FOO
""")

test.run(program=work2_build2_bar_src2_xxx_xxx, stdout="""\
work2/src2/include/my_string.h:  BAR
repository/src2/xxx/include.h:  BAR
repository/src2/xxx/main.c:  BAR
""")

test.fail_test(os.path.exists(test.workpath('repository', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('repository', 'src2', database_name)))
test.fail_test(os.path.exists(test.workpath('work1', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('work2', 'src2', database_name)))

test.sleep()  # delay for timestamps
test.write(['work2', 'src2', 'xxx', 'include.h'], r"""
#include <my_string.h>
#ifdef  FOO
#define XXX_OS          "FOO"
#endif
#ifdef  BAR
#define XXX_OS          "BAR"
#endif
#define XXX_STRING      "work2/src2/xxx/include.h:  %s\n"
""")

test.run(chdir='work2', options=opts, arguments='build2')

test.run(program=work2_build2_foo_src2_xxx_xxx, stdout="""\
work2/src2/include/my_string.h:  FOO
work2/src2/xxx/include.h:  FOO
repository/src2/xxx/main.c:  FOO
""")

test.run(program=work2_build2_bar_src2_xxx_xxx, stdout="""\
work2/src2/include/my_string.h:  BAR
work2/src2/xxx/include.h:  BAR
repository/src2/xxx/main.c:  BAR
""")

test.fail_test(os.path.exists(test.workpath('repository', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('repository', 'src2', database_name)))
test.fail_test(os.path.exists(test.workpath('work1', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('work2', 'src2', database_name)))

test.unlink(['work2', 'src2', 'include', 'my_string.h'])
test.run(chdir='work2', options=opts, arguments='build2')

test.run(
    program=work2_build2_foo_src2_xxx_xxx,
    stdout="""\
repository/src2/include/my_string.h:  FOO
work2/src2/xxx/include.h:  FOO
repository/src2/xxx/main.c:  FOO
""",
)

test.run(
    program=work2_build2_bar_src2_xxx_xxx,
    stdout="""\
repository/src2/include/my_string.h:  BAR
work2/src2/xxx/include.h:  BAR
repository/src2/xxx/main.c:  BAR
""",
)

test.fail_test(os.path.exists(test.workpath('repository', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('repository', 'src2', database_name)))
test.fail_test(os.path.exists(test.workpath('work1', 'src1', database_name)))
test.fail_test(os.path.exists(test.workpath('work2', 'src2', database_name)))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
