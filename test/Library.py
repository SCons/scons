#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

test.pass_test()	#XXX Short-circuit until this is implemented.

test.write('SConstruct', """
env = Environment(LIBS = 'foo1 foo2 foo3')
env.Library(target = 'foo1', source = 'f1.c')
env.Library(target = 'foo2', source = 'f2a.c f2b.c f2c.c')
env.Library(target = 'foo3', source = ['f3a.c', 'f3b.c', 'f3c.c'])
env.Program(target = 'prog', source = 'prog.c')
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
}
""")

test.run(arguments = 'libfoo1.a libfoo2.a libfoo3.a')

test.run(program = test.workpath('prog'),
	stdout = "f1.c\nf2a.c\nf2b.c\nf2c.c\nf3a.c\nf3b.c\nf3c.c\nprog.c\n")

test.pass_test()
