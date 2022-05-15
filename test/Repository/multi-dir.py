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

import sys

from TestSCons import TestSCons

test = TestSCons()

test.subdir('work',
            ['work', 'src'],
            ['work', 'include'],
            'repository',
            ['repository', 'src'],
            ['repository', 'include'])

workpath_repository = test.workpath('repository')
work_include_my_string_h = test.workpath('work', 'include', 'my_string.h')
work_src_xxx = test.workpath('work', 'src', 'xxx')
repository_src_xxx = test.workpath('repository', 'src', 'xxx')

opts = "-Y " + workpath_repository

test.write(['repository', 'SConstruct'], """
env = Environment(CPPPATH = ['#src', '#include'])
SConscript('src/SConscript', "env")
""")

test.write(['repository', 'src', 'SConscript'], """
Import("env")
env.Program(target = 'xxx', source = 'main.c')
""")

test.write(['repository', 'include', 'my_string.h'], r"""
#define MY_STRING       "repository/include/my_string.h"
""")

test.write(['repository', 'src', 'include.h'], r"""
#include <my_string.h>
#define LOCAL_STRING    "repository/src/include.h"
""")

test.write(['repository', 'src', 'main.c'], r"""
#include <stdio.h>
#include <stdlib.h>
#include <include.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("%s\n", MY_STRING);
        printf("%s\n", LOCAL_STRING);
        printf("repository/src/main.c\n");
        exit (0);
}
""")

# Make the repository non-writable,
# so we'll detect if we try to write into it accidentally.
test.writable('repository', 0)

test.run(chdir = 'work', options = opts, arguments = ".")

test.run(program = work_src_xxx, stdout =
"""repository/include/my_string.h
repository/src/include.h
repository/src/main.c
""")

#
test.write(['work', 'include', 'my_string.h'], r"""
#define MY_STRING       "work/include/my_string.h"
""")

test.run(chdir = 'work', options = opts, arguments = ".")

test.run(program = work_src_xxx, stdout =
"""work/include/my_string.h
repository/src/include.h
repository/src/main.c
""")

test.write(['work', 'src', 'include.h'], r"""
#include <my_string.h>
#define LOCAL_STRING    "work/src/include.h"
""")

test.run(chdir = 'work', options = opts, arguments = ".")

test.run(program = work_src_xxx, stdout =
"""work/include/my_string.h
work/src/include.h
repository/src/main.c
""")

#
test.unlink(work_include_my_string_h)

test.run(chdir = 'work', options = opts, arguments = ".")

test.run(program = work_src_xxx, stdout =
"""repository/include/my_string.h
work/src/include.h
repository/src/main.c
""")

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
