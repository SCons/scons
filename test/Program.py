#!/usr/bin/env python

__revision__ = "test/Program.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', """
env = Environment()
env.Program(target = 'foo', source = 'foo.c')
""")

test.write('foo.c', """
int
main(int argc, char *argv[])
{
	printf("foo.c\n");
	exit (0);
}
""")

test.run(chdir = '.', arguments = 'foo')

test.run(program = test.workpath('foo'))

test.fail_test(test.stdout() != "foo.c\n")

test.pass_test()
