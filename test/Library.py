#!/usr/bin/env python
#
# Copyright (c) 2001 Steven Knight
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

#XXX Need to switch TestBld to Program() when LIBS variable is working.
test.write('SConstruct', """
TestBld = Builder(name='TestBld',
                  action='cc -o %(target)s %(source)s -L./ -lfoo1 -lfoo2 -lfoo3')
env = Environment(BUILDERS=[ TestBld, Library ])
env.Library(target = 'foo1', source = 'f1.c')
env.Library(target = 'foo2', source = 'f2a.c f2b.c f2c.c')
env.Library(target = 'foo3', source = ['f3a.c', 'f3b.c', 'f3c.c'])
env.TestBld(target = 'prog', source = 'prog.c')
env.Depends(target = 'prog', dependency = 'libfoo1.a libfoo2.a libfoo3.a')
""")

test.write('f1.c', """
void
f1(void)
{
	printf("f1.c\n");
}
""")

test.write('f2a.c', """
void
f2a(void)
{
	printf("f2a.c\n");
}
""")

test.write('f2b.c', """
void
f2b(void)
{
	printf("f2b.c\n");
}
""")

test.write('f2c.c', """
void
f2c(void)
{
	printf("f2c.c\n");
}
""")

test.write('f3a.c', """
void
f3a(void)
{
	printf("f3a.c\n");
}
""")

test.write('f3b.c', """
void
f3b(void)
{
	printf("f3b.c\n");
}
""")

test.write('f3c.c', """
f3c(void)
{
	printf("f3c.c\n");
}
""")

test.write('prog.c', """
void f1(void);
void f2a(void);
void f2b(void);
void f2c(void);
void f3a(void);
void f3b(void);
void f3c(void);
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
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

test.run(arguments = 'libfoo1.a libfoo2.a libfoo3.a prog')

test.run(program = test.workpath('prog'),
         stdout = "f1.c\nf2a.c\nf2b.c\nf2c.c\nf3a.c\nf3b.c\nf3c.c\nprog.c\n")

test.pass_test()
