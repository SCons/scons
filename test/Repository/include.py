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

repository = test.workpath('repository')
work_foo = test.workpath('work', 'foo' + _exe)
work_foo_h = test.workpath('work', 'foo.h')

test.write(['work', 'SConstruct'], """
Repository(r'%s')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(CPPPATH = ['.'])
env.Program(target = 'foo', source = 'foo.c')
""" % repository)

test.write(['repository', 'foo.h'], r"""
#define STRING1 "repository/foo.h"
#include <bar.h>
""")

test.write(['repository', 'bar.h'], r"""
#define STRING2 "repository/bar.h"
""")

test.write(['repository', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
#include <foo.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("%s\n", STRING1);
        printf("%s\n", STRING2);
        printf("repository/foo.c\n");
        exit (0);
}
""")

# Make the entire repository non-writable, so we'll detect
# if we try to write into it accidentally.
test.writable('repository', 0)

test.run(chdir = 'work', arguments = '.')

test.run(program = work_foo, stdout =
"""repository/foo.h
repository/bar.h
repository/foo.c
""")

test.up_to_date(chdir = 'work', arguments = '.')

#
test.write(['work', 'foo.h'], r"""
#define STRING1 "work/foo.h"
#include <bar.h>
""")

test.run(chdir = 'work', arguments = '.')

test.run(program = work_foo, stdout =
"""work/foo.h
repository/bar.h
repository/foo.c
""")

test.up_to_date(chdir = 'work', arguments = '.')

#
test.write(['work', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
#include <foo.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("%s\n", STRING1);
        printf("%s\n", STRING2);
        printf("work/foo.c\n");
        exit (0);
}
""")

test.run(chdir = 'work', arguments = '.')

test.run(program = work_foo, stdout =
"""work/foo.h
repository/bar.h
work/foo.c
""")

test.up_to_date(chdir = 'work', arguments = '.')

#
test.write(['work', 'bar.h'], r"""
#define STRING2 "work/bar.h"
""")

test.run(chdir = 'work', arguments = '.')

test.run(program = work_foo, stdout =
"""work/foo.h
work/bar.h
work/foo.c
""")

test.up_to_date(chdir = 'work', arguments = '.')

#
test.writable('repository', 1)
test.unlink(['work', 'foo.h'])
test.writable('repository', 0)

test.run(chdir = 'work', arguments = '.')

test.run(program = work_foo, stdout =
"""repository/foo.h
work/bar.h
work/foo.c
""")

test.up_to_date(chdir = 'work', arguments = '.')

#
test.writable('repository', 1)
test.unlink(['work', 'foo.c'])
test.writable('repository', 0)

test.run(chdir = 'work', arguments = '.')

test.run(program = work_foo, stdout =
"""repository/foo.h
work/bar.h
repository/foo.c
""")

test.up_to_date(chdir = 'work', arguments = '.')

#
test.writable('repository', 1)
test.unlink(['work', 'bar.h'])
test.writable('repository', 0)

test.run(chdir = 'work', arguments = '.')

test.run(program = work_foo, stdout =
"""repository/foo.h
repository/bar.h
repository/foo.c
""")

test.up_to_date(chdir = 'work', arguments = '.')

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
