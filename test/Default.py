#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import TestSCons

test = TestSCons.TestSCons()

test.subdir('one', 'two', 'three')

test.write(['one', 'SConstruct'], """
env = Environment()
env.Program(target = 'foo', source = 'foo.c')
env.Program(target = 'bar', source = 'bar.c')
Default('foo')
""")

test.write(['two', 'SConstruct'], """
env = Environment()
env.Program(target = 'foo', source = 'foo.c')
env.Program(target = 'bar', source = 'bar.c')
Default('foo', 'bar')
""")

test.write(['three', 'SConstruct'], """
env = Environment()
env.Program(target = 'foo', source = 'foo.c')
env.Program(target = 'bar', source = 'bar.c')
Default('foo bar')
""")

for dir in ['one', 'two', 'three']:

    foo_c = os.path.join(dir, 'foo.c')
    bar_c = os.path.join(dir, 'bar.c')

    test.write(foo_c, """
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("%s\n");
	exit (0);
}
""" % foo_c)

    test.write(bar_c, """
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("%s\n");
	exit (0);
}
""" % bar_c)

    test.run(chdir = dir)	# no arguments, use the Default

test.run(program = test.workpath('one', 'foo'), stdout = "one/foo.c\n")
test.fail_test(os.path.exists(test.workpath('one', 'bar')))

test.run(program = test.workpath('two', 'foo'), stdout = "two/foo.c\n")
test.run(program = test.workpath('two', 'bar'), stdout = "two/bar.c\n")

test.run(program = test.workpath('three', 'foo'), stdout = "three/foo.c\n")
test.run(program = test.workpath('three', 'bar'), stdout = "three/bar.c\n")

test.pass_test()
