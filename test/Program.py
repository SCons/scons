#!/usr/bin/env python
#
# Copyright (c) 2001 Steven Knight
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import os.path
import time

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
test.up_to_date(arguments = 'foo1 foo2')

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
test.up_to_date(arguments = 'foo1 foo2')

# make sure the programs don't get rebuilt, because nothing changed:
oldtime1 = os.path.getmtime(test.workpath('foo1'))
oldtime2 = os.path.getmtime(test.workpath('foo2'))
time.sleep(1) # introduce a small delay, to make the test valid
test.run(arguments = 'foo1 foo2')
test.fail_test(not (oldtime1 == os.path.getmtime(test.workpath('foo1'))))
test.fail_test(not (oldtime2 == os.path.getmtime(test.workpath('foo2'))))

test.pass_test()
