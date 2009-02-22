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

"""
XXX Put a description of the test here.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment()
env.Library('main', 'main.c')
env.Library('one', 'one.c')
env.Library('two', 'two.c')
env.Program('prog', [], LIBS=['main', 'one', 'two'], LIBPATH=['.'])
""")

test.write('main.c', """\
#include <stdio.h>
#include <stdlib.h>
extern void one(void);
extern void two(void);
int
main(int argc, char *argv[])
{
    printf("main.c\\n");
    one();
    two();
    exit (0);
}
""")

test.write('one.c', """\
#include <stdio.h>
#include <stdlib.h>
void
one(void)
{
    printf("one.c\\n");
}
""")

test.write('two.c', """\
#include <stdio.h>
#include <stdlib.h>
void
two(void)
{
    printf("two.c\\n");
}
""")

test.run(arguments = '.')

test.run(program=test.workpath('prog'), stdout="main.c\none.c\ntwo.c\n")

test.pass_test()
