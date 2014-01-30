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

_obj = TestSCons._obj

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment()
f1 = env.Object(target = 'f1', source = 'f1.c')
f2 = Object(target = 'f2', source = 'f2.cpp')
f3 = env.Object(target = 'f3', source = 'f3.c')
mult_o = env.Object(['f4.c', 'f5.c'])
env.Program(target = 'prog1', source = Split('f1%s f2%s f3%s f4%s prog.cpp'))
env.Program(target = 'prog2', source = mult_o + [f1, f2, f3, 'prog.cpp'])
env.Program(target = 'prog3', source = ['f1%s', f2, 'f3%s', 'prog.cpp'])
""" % (_obj, _obj, _obj, _obj, _obj, _obj))

test.write('f1.c', r"""
#include <stdio.h>
void
f1(void)
{
        printf("f1.c\n");
}
""")

test.write('f2.cpp', r"""
#include <stdio.h>

void
f2(void)
{
        printf("f2.c\n");
}
""")

test.write('f3.c', r"""
#include <stdio.h>
void
f3(void)
{
        printf("f3.c\n");
}
""")

test.write('f4.c', r"""
#include <stdio.h>
void
f4(void)
{
        printf("f4.c\n");
}
""")

test.write('f5.c', r"""
#include <stdio.h>
void
f5(void)
{
        printf("f5.c\n");
}
""")

test.write('prog.cpp', r"""
#include <stdio.h>

extern "C" void f1(void);
extern void f2(void);
extern "C" void f3(void);
int
main(int argc, char *argv[])
{
        argv[argc++] = (char *)"--";
        f1();
        f2();
        f3();
        printf("prog.c\n");
        return 0;
}
""")

stdout = "f1.c\nf2.c\nf3.c\nprog.c\n"

test.run(arguments = '.')

test.run(program = test.workpath('prog1'), stdout = stdout)

test.run(program = test.workpath('prog2'), stdout = stdout)

test.run(program = test.workpath('prog3'), stdout = stdout)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
