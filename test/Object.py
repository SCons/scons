#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

test.pass_test()	#XXX Short-circuit until this is supported.

test.write('SConstruct', """
f1 = env.Object(target = 'f1', source = 'f1.c')
f2 = env.Object(target = 'f2', source = 'f2.c')
f3 = env.Object(target = 'f3', source = 'f3.c')
env.Program(target = 'prog1', source = 'f1.o f2.o f3.o prog.c')
env.Program(target = 'prog2', source = [f1, f2, f3, 'prog.c'])
env.Program(target = 'prog3', source = ['f1.o', f2, 'f3.o prog.c'])
""")

test.write('f1.c', """
void
f1(void)
{
	printf("f1.c\n");
}
""")

test.write('f2.c', """
void
f2(void)
{
	printf("f2.c\n");
}
""")

test.write('f3.c', """
void
f3(void)
{
	printf("f3.c\n");
}
""")

test.write('prog.c', """
extern void f1(void);
extern void f2(void);
extern void f3(void);
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	f1();
	f2();
	f3();
	printf("prog.c\n");
}
""")

stdout = "f1.c\nf2.c\nf3.c\nprog.c\n"

test.run(arguments = 'prog1 prog2 prog3')

test.run(program = test.workpath('prog1'), stdout = stdout)

test.run(program = test.workpath('prog2'), stdout = stdout)

test.run(program = test.workpath('prog3'), stdout = stdout)

test.pass_test()
