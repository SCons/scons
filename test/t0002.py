#!/usr/bin/env python

__revision__ = "test/t0002.py __REVISION__ __DATE__ __DEVELOPER__"

from TestCmd import TestCmd

test = TestCmd(program = 'scons.py',
               workdir = '',
               interpreter = 'python')

test.write('SConstruct', """
env = Environment()
env.Program(target = 'f1', source = 'f1.c')
env.Program(target = 'f2', source = 'f2.c')
env.Program(target = 'f3', source = 'f3.c')
env.Program(target = 'f4', source = 'f4.c')
""")

test.write('f1.c', """
int
main(int argc, char *argv[])
{
    printf(\"f1.c\n\");
    exit (0);
}
""")

test.write('f2.c', """
int
main(int argc, char *argv[])
{
    printf(\"f2.c\n\");
    exit (0);
}
""")


test.write('f3.c', """
int
main(int argc, char *argv[])
{
    printf(\"f3.c\n\");
    exit (0);
}
""")

test.write('f4.c', """
int
main(int argc, char *argv[])
{
    printf(\"f4.c\n\");
    exit (0);
}
""")


test.run(chdir = '.', arguments = '-j 3 f1 f2 f3 f4')

test.run(program = test.workpath('f1'))
test.fail_test(test.stdout() != "f1.c\n")

test.run(program = test.workpath('f2'))
test.fail_test(test.stdout() != "f2.c\n")

test.run(program = test.workpath('f3'))
test.fail_test(test.stdout() != "f3.c\n")

test.run(program = test.workpath('f4'))
test.fail_test(test.stdout() != "f4.c\n")


test.pass_test()
