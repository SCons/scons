#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os.path
import TestSCons

test = TestSCons.TestSCons()

test.pass_test()	#XXX Short-circuit until this is implemented.

test.write('SConstruct', """
env = Environment()
Program(target = 'foo1', source = 'foo1.c')
Program(target = 'foo2', source = 'foo2.c')
Program(target = 'foo3', source = 'foo3.c')
""")

test.write('foo1.c', """
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("foo1.c\n");
	exit (0);
}
""")

test.write('foo2.c', """
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("foo2.c\n");
	exit (0);
}
""")

test.write('foo3.c', """
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("foo3.c\n");
	exit (0);
}
""")

test.run(arguments = 'foo1 foo2 foo3')

test.run(program = test.workpath('foo1'), stdout = "foo1.c\n")
test.run(program = test.workpath('foo2'), stdout = "foo2.c\n")
test.run(program = test.workpath('foo3'), stdout = "foo3.c\n")

test.run(arguments = '-c foo1')

test.fail_test(os.path.exists(test.workpath('foo1')))
test.fail_test(not os.path.exists(test.workpath('foo2')))
test.fail_test(not os.path.exists(test.workpath('foo3')))

test.run(arguments = '--clean foo2')

test.fail_test(os.path.exists(test.workpath('foo1')))
test.fail_test(os.path.exists(test.workpath('foo2')))
test.fail_test(not os.path.exists(test.workpath('foo3')))

test.run(arguments = '--remove foo3')

test.fail_test(os.path.exists(test.workpath('foo1')))
test.fail_test(os.path.exists(test.workpath('foo2')))
test.fail_test(os.path.exists(test.workpath('foo3')))

test.run(arguments = 'foo1 foo2 foo3')

test.run(program = test.workpath('foo1'), stdout = "foo1.c\n")
test.run(program = test.workpath('foo2'), stdout = "foo2.c\n")
test.run(program = test.workpath('foo3'), stdout = "foo3.c\n")

test.run(arguments = '-c .')

test.fail_test(os.path.exists(test.workpath('foo1')))
test.fail_test(os.path.exists(test.workpath('foo2')))
test.fail_test(os.path.exists(test.workpath('foo3')))

test.pass_test()
 
