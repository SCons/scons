#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

test.pass_test()	#XXX Short-circuit until this is supported.

test.subdir('subdir')

test.write('SConstruct', """
env = Environment()
env.Program(target = 'aaa', source = 'aaa.c')
env.Program(target = 'bbb', source = 'bbb.c')
SConscript('subdir/SConscript')
""")

test.write(['subdir', 'SConscript'], """
env = Environment()
env.Program(target = 'ccc', source = 'ccc.c')
env.Program(target = 'ddd', source = 'ddd.c')
""")

test.write('aaa.c', """
int
main(int argc, char *argv)
{
	argv[argc++] = "--";
	printf("aaa.c\n");
	exit (0);
}
""")

test.write('bbb.c', """
int
main(int argc, char *argv)
{
	argv[argc++] = "--";
	printf("bbb.c\n");
	exit (0);
}
""")

test.write(['subdir', 'ccc.c'], """
int
main(int argc, char *argv)
{
	argv[argc++] = "--";
	printf("subdir/ccc.c\n");
	exit (0);
}
""")

test.write(['subdir', 'ddd.c'], """
int
main(int argc, char *argv)
{
	argv[argc++] = "--";
	printf("subdir/ddd.c\n");
	exit (0);
}
""")

test.run(arguments = '-d .', stdout = """
Target aaa: aaa.o
Checking aaa
  Checking aaa.o
    Checking aaa.c
  Rebuilding aaa.o: out of date.
cc -c -o aaa.o aaa.c
Rebuilding aaa: out of date.
cc -o aaa aaa.o
Target aaa.o: aaa.c
Target bbb: bbb.o
Checking bbb
  Checking bbb.o
    Checking bbb.c
  Rebuilding bbb.o: out of date.
cc -c -o bbb.o bbb.c
Rebuilding bbb: out of date.
cc -o bbb bbb.o
Target bbb.o: bbb.c
Target subdir/ccc/g: subdir/ccc.o
Checking subdir/ccc/g
  Checking subdir/ccc/g.o
    Checking subdir/ccc/g.c
  Rebuilding subdir/ccc/g.o: out of date.
cc -c -o subdir/ccc/g.o subdir/ccc.c
Rebuilding subdir/ccc/g: out of date.
cc -o subdir/ccc/g subdir/ccc.o
Target subdir/ccc/g.o: subdir/ccc.c
Target subdir/ddd/g: subdir/ddd.o
Checking subdir/ddd/g
  Checking subdir/ddd/g.o
    Checking subdir/ddd/g.c
  Rebuilding subdir/ddd/g.o: out of date.
cc -c -o subdir/ddd/g.o subdir/ddd.c
Rebuilding subdir/ddd/g: out of date.
cc -o subdir/ddd/g subdir/ddd.o
Target subdir/ddd/g.o: subdir/ddd.c
""")

test.run(program = test.workpath('aaa'), stdout = "aaa.c\n")
test.run(program = test.workpath('bbb'), stdout = "bbb.c\n")
test.run(program = test.workpath('subdir/ccc'), stdout = "subdir/ccc.c\n")
test.run(program = test.workpath('subdir/ddd'), stdout = "subdir/ddd.c\n")

test.pass_test()
 
