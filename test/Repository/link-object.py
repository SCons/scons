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

from TestSCons import TestSCons, _exe

test = TestSCons()

test.subdir('repository', 'work')

workpath_repository = test.workpath('repository')
repository_foo = test.workpath('repository', 'foo' + _exe)
work_foo = test.workpath('work', 'foo' + _exe)

test.write(['repository', 'SConstruct'], """
Repository(r'%s')
env = Environment()
env.Program(target = 'foo', source = ['aaa.c', 'bbb.c', 'foo.c'])
""" % workpath_repository)

test.write(['repository', 'aaa.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
aaa(void)
{
        printf("repository/aaa.c\n");
}
""")

test.write(['repository', 'bbb.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
bbb(void)
{
        printf("repository/bbb.c\n");
}
""")

test.write(['repository', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
extern void aaa(void);
extern void bbb(void);
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        aaa();
        bbb();
        printf("repository/foo.c\n");
        exit (0);
}
""")

#
test.run(chdir = 'repository', arguments = ".")

test.run(program = repository_foo, stdout =
"""repository/aaa.c
repository/bbb.c
repository/foo.c
""")

test.up_to_date(chdir = 'repository', arguments = ".")

# Make the repository non-writable,
# so we'll detect if we try to write into it accidentally.
test.writable('repository', 0)

#
test.write(['work', 'SConstruct'], """
Repository(r'%s')
env = Environment()
env.Program(target = 'foo', source = ['aaa.c', 'bbb.c', 'foo.c'])
""" % workpath_repository)

test.up_to_date(chdir = 'work', arguments = ".")

#
test.write(['work', 'bbb.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
bbb(void)
{
        printf("work/bbb.c\n");
}
""")

#
test.run(chdir = 'work', arguments = ".")

test.run(program = work_foo, stdout =
"""repository/aaa.c
work/bbb.c
repository/foo.c
""")

test.up_to_date(chdir = 'work', arguments = ".")

#
test.unlink(['work', 'bbb.c'])

#
test.run(chdir = 'work', arguments = ".")

test.run(program = work_foo, stdout =
"""repository/aaa.c
repository/bbb.c
repository/foo.c
""")

test.up_to_date(chdir = 'work', arguments = ".")

#
test.writable('repository', 1)

#
test.up_to_date(chdir = 'repository', arguments = ".")

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
