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

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment(LIBS = [ 'foo1', 'libfoo2' ],
                  LIBPATH = [ '.' ])
env.Library(target = 'foo1', source = 'f1.c')
Library(target = 'libfoo2', source = Split('f2a.c f2b.c f2c.c'))
libtgt=env.Library(target = 'foo3', source = ['f3a.c', 'f3b.c', 'f3c.cpp'])
env.Program(target = 'prog', source = [ 'prog.cpp', libtgt ])
""")

test.write('f1.c', r"""
#include <stdio.h>
void
f1(void)
{
        printf("f1.c\n");
}
""")

test.write('f2a.c', r"""
#include <stdio.h>
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
void
f2c(void)
{
        printf("f2c.c\n");
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

test.write('f3c.cpp', r"""
#include <stdio.h>
extern "C" void
f3c(void)
{
        printf("f3c.cpp\n");
}
""")

test.write('prog.cpp', r"""
#include <stdio.h>
extern "C" {
void f1(void);
void f2a(void);
void f2b(void);
void f2c(void);
void f3a(void);
void f3b(void);
void f3c(void);
}
int
main(int argc, char *argv[])
{
        argv[argc++] = (char *)"--";
        f1();
        f2a();
        f2b();
        f2c();
        f3a();
        f3b();
        f3c();
        printf("prog.c\n");
        return 0;
}
""")

test.run(arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

test.run(program = test.workpath('prog'),
         stdout = "f1.c\nf2a.c\nf2b.c\nf2c.c\nf3a.c\nf3b.c\nf3c.cpp\nprog.c\n")

# Tests whether you can reference libraries with substitutions.

test.write('SConstruct', r"""
# nrd = not referenced directly :)
Library('nrd', 'nrd.c')
p = Program('uses-nrd', 'uses-nrd.c', NRD='nrd', LIBPATH=['.'], LIBS=['$NRD'])
Default(p)
""")

test.write('nrd.c', r"""
#include <stdio.h>
void nrd() {
    puts("nrd");
}
""")

test.write('uses-nrd.c', r"""
void nrd();
int main(void) {
    nrd();
    return 0;
}
""")

test.run(stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

test.run(program = test.workpath('uses-nrd'),
         stdout = "nrd\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
