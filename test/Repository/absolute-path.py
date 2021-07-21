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

from TestSCons import TestSCons, _exe

test = TestSCons()

test.subdir('repository',
            ['repository', 'src'],
            'subdir',
            'work')

src_SConscript = os.path.join('src', 'SConscript')
subdir_aaa_c = test.workpath('subdir', 'aaa.c')
work_src_foo = test.workpath('work', 'src', 'foo' + _exe)

opts = "-Y " + test.workpath('repository')

test.write(['repository', 'SConstruct'], r"""
SConscript(r'%s')
""" % src_SConscript)

test.write(['repository', 'src', 'SConscript'], r"""
env = Environment()
env.Program('foo', ['aaa.c', r'%s', 'foo.c'])
""" % subdir_aaa_c)

test.write(['repository', 'src', 'aaa.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
src_aaa(void)
{
        printf("repository/src/aaa.c\n");
}
""")

test.write(['subdir', 'aaa.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
subdir_aaa(void)
{
        printf("subdir/aaa.c\n");
}
""")

test.write(['repository', 'src', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
extern void src_aaa(void);
extern void subdir_aaa(void);
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        src_aaa();
        subdir_aaa();
        printf("repository/src/foo.c\n");
        exit (0);
}
""")

# Make the entire repository non-writable, so we'll detect
# if we try to write into it accidentally.
test.writable('repository', 0)

test.run(chdir = 'work', options = opts, arguments = '.')

test.run(program = work_src_foo, stdout = """repository/src/aaa.c
subdir/aaa.c
repository/src/foo.c
""")

test.up_to_date(chdir = 'work', options = opts, arguments = '.')

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
