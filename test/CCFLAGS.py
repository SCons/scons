#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

test.pass_test()	#XXX Short-circuit until this is implemented.

test.write('SConstruct', """
foo = Environment(CCFLAGS = '-DFOO')
bar = Environment(CCFLAGS = '-DBAR')
foo.Program(target = 'progfoo', source = 'prog.c')
bar.Program(target = 'progbar', source = 'prog.c')
""")

test.write('prog.c', """
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
#ifdef FOO
	printf("prog.c:  FOO\n");
#endif
#ifdef BAR
	printf("prog.c:  BAR\n");
#endif
	exit (0);
}
""")


test.run(arguments = 'progfoo progbar')

test.run(program = test.workpath('progfoo'), stdout = "prog.c:  FOO\n")
test.run(program = test.workpath('progbar'), stdout = "prog.c:  BAR\n")

test.pass_test()
