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

for implicit_deps in ['0', '1', '2', '\"all\"']:
    # First, test a single repository.
    test = TestSCons.TestSCons()
    test.subdir('repository', 'work1')
    repository = test.workpath('repository')
    repository_foo_c = test.workpath('repository', 'foo.c')
    work1_foo = test.workpath('work1', 'foo' + _exe)
    work1_foo_c = test.workpath('work1', 'foo.c')

    test.write(['work1', 'SConstruct'], r"""
DefaultEnvironment(tools=[])
Repository(r'%s')
env = Environment(IMPLICIT_COMMAND_DEPENDENCIES=%s)
env.Program(target= 'foo', source = Split('aaa.c bbb.c foo.c'))
""" % (repository, implicit_deps))

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

    # Make the entire repository non-writable, so we'll detect
    # if we try to write into it accidentally.
    test.writable('repository', 0)

    test.run(chdir = 'work1', arguments = '.')

    test.run(program = work1_foo, stdout = """repository/aaa.c
repository/bbb.c
repository/foo.c
""")

    test.up_to_date(chdir = 'work1', arguments = '.')

    #
    test.write(['work1', 'bbb.c'], r"""
#include <stdio.h>
void
bbb(void)
{
        printf("work1/bbb.c\n");
}
""")

    test.run(chdir = 'work1', arguments = '.')

    test.run(program = work1_foo, stdout = """repository/aaa.c
work1/bbb.c
repository/foo.c
""")

    test.up_to_date(chdir = 'work1', arguments = '.')

    #
    test.write(['work1', 'aaa.c'], r"""
#include <stdio.h>
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

    test.run(chdir = 'work1', arguments = '.')

    test.run(program = work1_foo, stdout = """work1/aaa.c
work1/bbb.c
work1/foo.c
""")

    test.up_to_date(chdir = 'work1', arguments = '.')

    #
    test.unlink(['work1', 'aaa.c'])

    test.run(chdir = 'work1', arguments = '.')

    test.run(program = work1_foo, stdout = """repository/aaa.c
work1/bbb.c
work1/foo.c
""")

    test.up_to_date(chdir = 'work1', arguments = '.')

    #
    test.unlink(['work1', 'bbb.c'])
    test.unlink(['work1', 'foo.c'])

    test.run(chdir = 'work1', arguments = '.')

    test.run(program = work1_foo, stdout = """repository/aaa.c
repository/bbb.c
repository/foo.c
""")

    test.up_to_date(chdir = 'work1', arguments = '.')



    # Now, test multiple repositories.
    test.subdir('repository.new', 'repository.old', 'work2')

    repository_new = test.workpath('repository.new')
    repository_old = test.workpath('repository.old')
    work2_foo = test.workpath('work2', 'foo' + _exe)

    test.write(['work2', 'SConstruct'], r"""
DefaultEnvironment(tools=[])
Repository(r'%s')
Repository(r'%s')
env = Environment()
env.Program(target= 'foo', source = Split('aaa.c bbb.c foo.c'))
""" % (repository_new, repository_old))

    test.write(['repository.old', 'aaa.c'], r"""
#include <stdio.h>
void
aaa(void)
{
        printf("repository.old/aaa.c\n");
}
""")

    test.write(['repository.old', 'bbb.c'], r"""
#include <stdio.h>
void
bbb(void)
{
        printf("repository.old/bbb.c\n");
}
""")

    test.write(['repository.old', 'foo.c'], r"""
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
        printf("repository.old/foo.c\n");
        exit (0);
}
""")

    # Make both repositories non-writable, so we'll detect
    # if we try to write into it accidentally.
    test.writable('repository.new', 0)
    test.writable('repository.old', 0)

    test.run(chdir = 'work2', arguments = '.')

    test.run(program = work2_foo, stdout = """repository.old/aaa.c
repository.old/bbb.c
repository.old/foo.c
""")

    test.up_to_date(chdir = 'work2', arguments = '.')

    #
    test.writable('repository.new', 1)

    test.write(['repository.new', 'aaa.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
aaa(void)
{
        printf("repository.new/aaa.c\n");
}
""")

    test.write(['work2', 'bbb.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
bbb(void)
{
        printf("work2/bbb.c\n");
}
""")

    #
    test.writable('repository.new', 0)

    test.run(chdir = 'work2', arguments = '.')

    test.run(program = work2_foo, stdout = """repository.new/aaa.c
work2/bbb.c
repository.old/foo.c
""")

    test.up_to_date(chdir = 'work2', arguments = '.')

    #
    test.write(['work2', 'aaa.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
aaa(void)
{
        printf("work2/aaa.c\n");
}
""")

    test.write(['work2', 'foo.c'], r"""
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
        printf("work2/foo.c\n");
        exit (0);
}
""")

    #
    test.run(chdir = 'work2', arguments = '.')

    test.run(program = work2_foo, stdout = """work2/aaa.c
work2/bbb.c
work2/foo.c
""")

    test.up_to_date(chdir = 'work2', arguments = '.')

    #
    test.unlink(['work2', 'aaa.c'])
    test.unlink(['work2', 'bbb.c'])

    #
    test.run(chdir = 'work2', arguments = '.')

    test.run(program = work2_foo, stdout = """repository.new/aaa.c
repository.old/bbb.c
work2/foo.c
""")

    test.up_to_date(chdir = 'work2', arguments = '.')

    #
    test.unlink(['work2', 'foo.c'])

    #
    test.run(chdir = 'work2', arguments = '.')

    test.run(program = work2_foo, stdout = """repository.new/aaa.c
repository.old/bbb.c
repository.old/foo.c
""")

    test.up_to_date(chdir = 'work2', arguments = '.')

    #
    test.writable('repository.new', 1)

    test.unlink(['repository.new', 'aaa.c'])

    test.writable('repository.new', 0)

    #
    test.run(chdir = 'work2', arguments = '.')

    test.run(program = work2_foo, stdout = """repository.old/aaa.c
repository.old/bbb.c
repository.old/foo.c
""")

    test.up_to_date(chdir = 'work2', arguments = '.')


#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
