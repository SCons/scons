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

import os.path
import time

import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

foo1 = test.workpath('foo1' + _exe)
foo2 = test.workpath('foo2' + _exe)
foo3 = test.workpath('foo3' + _exe)
foo4 = test.workpath('foo4' + _exe)
foo5 = test.workpath('foo5' + _exe)
foo_args = 'foo1%s foo2%s foo3%s foo4%s foo5%s' % (_exe, _exe, _exe, _exe, _exe)

test.write('SConstruct', """
env = Environment()
env.Program(target = 'foo1', source = 'f1.c')
env.Program(target = 'foo2', source = Split('f2a.c f2b.c f2c.c'))
f3a = File('f3a.c')
f3b = File('f3b.c')
Program(target = 'foo3', source = [f3a, [f3b, 'f3c.c']])
env.Program('foo4', 'f4.c')
env.Program('foo5.c')
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

test.write('f2a.c', r"""
#include <stdio.h>
#include <stdlib.h>
void
f2a(void)
{
        printf("f2a.c\n");
}
""")

test.write('f2b.c', r"""
#include <stdio.h>
void
f2b(void)
{
        printf("f2b.c\n");
}
""")

test.write('f2c.c', r"""
#include <stdio.h>
#include <stdlib.h>
extern void f2a(void);
extern void f2b(void);
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        f2a();
        f2b();
        printf("f2c.c\n");
        exit (0);
}
""")

test.write('f3a.c', r"""
#include <stdio.h>
void
f3a(void)
{
        printf("f3a.c\n");
}
""")

test.write('f3b.c', r"""
#include <stdio.h>
void
f3b(void)
{
        printf("f3b.c\n");
}
""")

test.write('f3c.c', r"""
#include <stdio.h>
#include <stdlib.h>
extern void f3a(void);
extern void f3b(void);
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        f3a();
        f3b();
        printf("f3c.c\n");
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

test.write('foo5.c', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("foo5.c\n");
        exit (0);
}
""")

test.run(arguments = '.')

test.run(program = foo1, stdout = "f1.c\n")
test.run(program = foo2, stdout = "f2a.c\nf2b.c\nf2c.c\n")
test.run(program = foo3, stdout = "f3a.c\nf3b.c\nf3c.c\n")
test.run(program = foo4, stdout = "f4.c\n")
test.run(program = foo5, stdout = "foo5.c\n")

test.up_to_date(arguments = '.')

test.write('f1.c', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("f1.c X\n");
        exit (0);
}
""")

test.write('f3b.c', r"""
#include <stdio.h>
void
f3b(void)
{
        printf("f3b.c X\n");
}
""")

test.write('f4.c', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("f4.c X\n");
        exit (0);
}
""")

test.write('foo5.c', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("foo5.c X\n");
        exit (0);
}
""")

test.run(arguments = '.')

test.run(program = foo1, stdout = "f1.c X\n")
test.run(program = foo2, stdout = "f2a.c\nf2b.c\nf2c.c\n")
test.run(program = foo3, stdout = "f3a.c\nf3b.c X\nf3c.c\n")
test.run(program = foo4, stdout = "f4.c X\n")
test.run(program = foo5, stdout = "foo5.c X\n")

test.up_to_date(arguments = '.')

# make sure the programs didn't get rebuilt, because nothing changed:
oldtime1 = os.path.getmtime(foo1)
oldtime2 = os.path.getmtime(foo2)
oldtime3 = os.path.getmtime(foo3)
oldtime4 = os.path.getmtime(foo4)
oldtime5 = os.path.getmtime(foo5)

time.sleep(2) # introduce a small delay, to make the test valid

test.run(arguments = foo_args)

test.fail_test(oldtime1 != os.path.getmtime(foo1))
test.fail_test(oldtime2 != os.path.getmtime(foo2))
test.fail_test(oldtime3 != os.path.getmtime(foo3))
test.fail_test(oldtime4 != os.path.getmtime(foo4))
test.fail_test(oldtime5 != os.path.getmtime(foo5))

test.write('f1.c', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("f1.c Y\n");
        exit (0);
}
""")

test.write('f3b.c', r"""
#include <stdio.h>
#include <stdlib.h>
void
f3b(void)
{
        printf("f3b.c Y\n");
}
""")

test.write('f4.c', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("f4.c Y\n");
        exit (0);
}
""")

test.write('foo5.c', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("foo5.c Y\n");
        exit (0);
}
""")

test.run(arguments = foo_args)

test.run(program = foo1, stdout = "f1.c Y\n")
test.run(program = foo2, stdout = "f2a.c\nf2b.c\nf2c.c\n")
test.run(program = foo3, stdout = "f3a.c\nf3b.c Y\nf3c.c\n")
test.run(program = foo4, stdout = "f4.c Y\n")
test.run(program = foo5, stdout = "foo5.c Y\n")

test.up_to_date(arguments = foo_args)

test.write('f1.c', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("f1.c Z\n");
        exit (0);
}
""")

test.write('f3b.c', r"""
#include <stdio.h>
#include <stdlib.h>
void
f3b(void)
{
        printf("f3b.c Z\n");
}
""")

test.write('f4.c', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("f4.c Z\n");
        exit (0);
}
""")

test.write('foo5.c', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("foo5.c Z\n");
        exit (0);
}
""")

test.run(arguments = foo_args)

test.run(program = foo1, stdout = "f1.c Z\n")
test.run(program = foo2, stdout = "f2a.c\nf2b.c\nf2c.c\n")
test.run(program = foo3, stdout = "f3a.c\nf3b.c Z\nf3c.c\n")
test.run(program = foo4, stdout = "f4.c Z\n")
test.run(program = foo5, stdout = "foo5.c Z\n")

test.up_to_date(arguments = foo_args)

# make sure the programs didn't get rebuilt, because nothing changed:
oldtime1 = os.path.getmtime(foo1)
oldtime2 = os.path.getmtime(foo2)
oldtime3 = os.path.getmtime(foo3)
oldtime4 = os.path.getmtime(foo4)
oldtime5 = os.path.getmtime(foo5)

time.sleep(2) # introduce a small delay, to make the test valid

test.run(arguments = foo_args)

test.fail_test(not (oldtime1 == os.path.getmtime(foo1)))
test.fail_test(not (oldtime2 == os.path.getmtime(foo2)))
test.fail_test(not (oldtime3 == os.path.getmtime(foo3)))
test.fail_test(not (oldtime4 == os.path.getmtime(foo4)))
test.fail_test(not (oldtime5 == os.path.getmtime(foo5)))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
