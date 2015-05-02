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

import sys
import TestSCons

if sys.platform == 'win32':
    _exe = '.exe'
else:
    _exe = ''



test = TestSCons.TestSCons()

test.subdir('repository', 'work1')

repository = test.workpath('repository')
repository_foo_c = test.workpath('repository', 'foo.c')
work1_foo = test.workpath('work1', 'foo' + _exe)
work1_foo_c = test.workpath('work1', 'foo.c')

test.write(['repository', 'SConstruct'], r"""
env = Environment()
env.Program(target= 'foo', source = Split('aaa.c bbb.c foo.c'))
""")

test.write(['repository', 'aaa.c'], r"""
#include <stdio.h>
void
aaa(void)
{
      printf("repository/aaa.c\n");
}
""")

test.write(['repository', 'bbb.c'], r"""
#include <stdio.h>
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

opts = '-Y ' + repository

# Make the entire repository non-writable, so we'll detect
# if we try to write into it accidentally.
test.writable('repository', 0)

test.run(chdir = 'work1', options = opts, arguments = '.')

test.run(program = work1_foo, stdout = """repository/aaa.c
repository/bbb.c
repository/foo.c
""")

test.up_to_date(chdir = 'work1', options = opts, arguments = '.')

#
test.write(['work1', 'bbb.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
bbb(void)
{
      printf("work1/bbb.c\n");
}
""")

test.run(chdir = 'work1', options = opts, arguments = '.')

test.run(program = work1_foo, stdout = """repository/aaa.c
work1/bbb.c
repository/foo.c
""")

test.up_to_date(chdir = 'work1', options = opts, arguments = '.')

#
test.write(['work1', 'aaa.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
aaa(void)
{
      printf("work1/aaa.c\n");
}
""")

test.write(['work1', 'foo.c'], r"""
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
      printf("work1/foo.c\n");
      exit (0);
}
""")

test.run(chdir = 'work1', options = opts, arguments = '.')

test.run(program = work1_foo, stdout = """work1/aaa.c
work1/bbb.c
work1/foo.c
""")

test.up_to_date(chdir = 'work1', options = opts, arguments = '.')

#
test.unlink(['work1', 'bbb.c'])
test.unlink(['work1', 'foo.c'])

test.run(chdir = 'work1', options = opts, arguments = '.')

test.run(program = work1_foo, stdout = """work1/aaa.c
repository/bbb.c
repository/foo.c
""")

test.up_to_date(chdir = 'work1', options = opts, arguments = '.')



#
test.subdir('r.NEW', 'r.OLD', 'work2')

workpath_r_NEW = test.workpath('r.NEW')
workpath_r_OLD = test.workpath('r.OLD')
work2_foo = test.workpath('work2', 'foo' + _exe)

SConstruct = """
env = Environment()
env.Program(target = 'foo', source = 'foo.c')
"""

test.write(['r.OLD', 'SConstruct'], SConstruct)

test.write(['r.NEW', 'SConstruct'], SConstruct)

test.write(['r.OLD', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
      argv[argc++] = "--";
      printf("r.OLD/foo.c\n");
      exit (0);
}
""")

opts = '-Y %s -Y %s' % (workpath_r_NEW, workpath_r_OLD)

# Make the repositories non-writable, so we'll detect
# if we try to write into them accidentally.
test.writable('r.OLD', 0)
test.writable('r.NEW', 0)

test.run(chdir = 'work2', options = opts, arguments = '.')

test.run(program = work2_foo, stdout = "r.OLD/foo.c\n")

test.up_to_date(chdir = 'work2', options = opts, arguments = '.')

#
test.writable('r.NEW', 1)

test.write(['r.NEW', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
      argv[argc++] = "--";
      printf("r.NEW/foo.c\n");
      exit (0);
}
""")

test.writable('r.NEW', 0)

test.run(chdir = 'work2', options = opts, arguments = '.')

test.run(program = work2_foo, stdout = "r.NEW/foo.c\n")

test.up_to_date(chdir = 'work2', options = opts, arguments = '.')

#
test.write(['work2', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
      argv[argc++] = "--";
      printf("work2/foo.c\n");
      exit (0);
}
""")

test.run(chdir = 'work2', options = opts, arguments = '.')

test.run(program = work2_foo, stdout = "work2/foo.c\n")

test.up_to_date(chdir = 'work2', options = opts, arguments = '.')

#
test.writable('r.OLD', 1)
test.writable('r.NEW', 1)

test.write(['r.OLD', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
      argv[argc++] = "--";
      printf("r.OLD/foo.c 2\n");
      exit (0);
}
""")

test.write(['r.NEW', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
      argv[argc++] = "--";
      printf("r.NEW/foo.c 2\n");
      exit (0);
}
""")

test.writable('r.OLD', 0)
test.writable('r.NEW', 0)

test.up_to_date(chdir = 'work2', options = opts, arguments = '.')

#
test.unlink(['work2', 'foo.c'])

test.run(chdir = 'work2', options = opts, arguments = '.')

test.run(program = work2_foo, stdout = "r.NEW/foo.c 2\n")

test.up_to_date(chdir = 'work2', options = opts, arguments = '.')

#
test.writable('r.NEW', 1)

test.unlink(['r.NEW', 'foo.c'])

test.writable('r.NEW', 0)

test.run(chdir = 'work2', options = opts, arguments = '.')

test.run(program = work2_foo, stdout = "r.OLD/foo.c 2\n")

test.up_to_date(chdir = 'work2', options = opts, arguments = '.')



#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
