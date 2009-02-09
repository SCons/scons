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

#
test.subdir('repository', ['repository', 'src'])

#
workpath_repository = test.workpath('repository')
repository_foo = test.workpath('repository', 'foo' + _exe)
repository_src_bar = test.workpath('repository', 'src', 'bar' + _exe)

#
test.write(['repository', 'SConstruct'], """
Repository(r'%s')
SConscript('src/SConscript')
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

test.write(['repository', 'src', 'SConscript'], """
env = Environment()
env.Program(target = 'bar', source = ['aaa.c', 'bbb.c', 'bar.c'])
""")

test.write(['repository', 'src', 'aaa.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
aaa(void)
{
        printf("repository/src/aaa.c\n");
}
""")

test.write(['repository', 'src', 'bbb.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
bbb(void)
{
        printf("repository/src/bbb.c\n");
}
""")

test.write(['repository', 'src', 'bar.c'], r"""
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
        printf("repository/src/bar.c\n");
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

test.run(program = repository_src_bar, stdout =
"""repository/src/aaa.c
repository/src/bbb.c
repository/src/bar.c
""")

#
test.up_to_date(chdir = 'repository', arguments = ".")

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
