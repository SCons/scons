#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment()
env.Program(target = 'foo', source = 'foo.c')
""")

test.write('foo.c', """
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("foo.c\n");
	exit (0);
}
""")

test.run(arguments = 'foo')

test.run(program = test.workpath('foo'), stdout = "foo.c\n")

test.pass_test()
