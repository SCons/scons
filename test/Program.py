#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

#XXX Future:  be able to interpolate

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment()
env.Program(target = 'foo1', source = 'f1.c')
env.Program(target = 'foo2', source = 'f2a.c f2b.c f2c.c')
#XXXenv.Program(target = 'foo3', source = ['f3a.c', 'f3b.c', 'f3c.c'])
""")

test.write('f1.c', """
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("f1.c\n");
	exit (0);
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

#XXXtest.run(arguments = '.')
test.run(arguments = 'foo1 foo2')

test.run(program = test.workpath('foo1'), stdout = "f1.c\n")
test.run(program = test.workpath('foo2'), stdout = "f2a.c\nf2b.c\nf2c.c\n")
#XXXtest.run(program = test.workpath('foo3'), stdout = "f3a.c\nf3b.c\nf3c.c\n")

#XXXtest.up_to_date(arguments = '.')

test.write('f1.c', """
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("f1.c X\n");
	exit (0);
}
""")

test.write('f3b.c', """
void
f3b(void)
{
	printf("f3b.c X\n");
}
""")

#XXXtest.run(arguments = '.')
test.run(arguments = 'foo1 foo2')

test.run(program = test.workpath('foo1'), stdout = "f1.c X\n")
test.run(program = test.workpath('foo2'), stdout = "f2a.c\nf2b.c\nf2c.c\n")
#XXXtest.run(program = test.workpath('foo3'), stdout = "f3a.c\nf3b.c X\nf3c.c\n")

#XXXtest.up_to_date(arguments = '.')

test.pass_test()
