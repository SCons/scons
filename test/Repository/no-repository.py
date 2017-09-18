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

python = TestSCons.python

if sys.platform == 'win32':
    _exe = '.exe'
else:
    _exe = ''

test = TestSCons.TestSCons()

test.subdir('work')

no_repository = test.workpath('no_repository')
work_foo = test.workpath('work', 'foo' + _exe)

test.write(['work', 'SConstruct'], """
Repository(r'%s')
env = Environment()
env.Program(target = 'foo', source = Split('aaa.c bbb.c foo.c'))
""" % no_repository)

test.write(['work', 'aaa.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
aaa(void)
{
        printf("work/aaa.c\n");
}
""")

test.write(['work', 'bbb.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
bbb(void)
{
        printf("work/bbb.c\n");
}
""")

test.write(['work', 'foo.c'], r"""
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
        printf("work/foo.c\n");
        exit (0);
}
""")

test.run(chdir = 'work', arguments = '.')

test.run(program = work_foo, stdout = """work/aaa.c
work/bbb.c
work/foo.c
""")

test.up_to_date(chdir = 'work', arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
