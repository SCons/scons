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

import TestSCons

_exe = TestSCons._exe

f1 = 'f1' + _exe
f2 = 'f2' + _exe
f3 = 'f3' + _exe
f4 = 'f4' + _exe

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment()
env.Program(target = 'f1', source = 'f1.c')
env.Program(target = 'f2', source = 'f2.c')
env.Program(target = 'f3', source = 'f3.c')
env.Program(target = 'f4', source = 'f4.c')
""")

test.write('f1.c', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    printf("f1.c\n");
    exit (0);
}
""")

test.write('f2.c', r"""
#include <stdio.h>
#include <stdlib.h>

int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    printf("f2.c\n");
    exit (0);
}
""")


test.write('f3.c', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    printf("f3.c\n");
    exit (0);
}
""")

test.write('f4.c', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    printf("f4.c\n");
    exit (0);
}
""")


test.run(arguments = '-j 3 %s %s %s %s' % (f1, f2, f3, f4))

test.run(program = test.workpath('f1'), stdout = "f1.c\n")

test.run(program = test.workpath('f2'), stdout = "f2.c\n")

test.run(program = test.workpath('f3'), stdout = "f3.c\n")

test.run(program = test.workpath('f4'), stdout = "f4.c\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
