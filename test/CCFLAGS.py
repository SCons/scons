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

test = TestSCons.TestSCons()

test.write('SConstruct', """
foo = Environment(CCFLAGS = '-DFOO')
bar = Environment(CCFLAGS = '-DBAR')
foo.Object(target = 'foo.o', source = 'prog.c')
bar.Object(target = 'bar.o', source = 'prog.c')
foo.Program(target = 'foo', source = 'foo.o')
bar.Program(target = 'bar', source = 'bar.o')
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


test.run(arguments = '.')

test.run(program = test.workpath('foo'), stdout = "prog.c:  FOO\n")
test.run(program = test.workpath('bar'), stdout = "prog.c:  BAR\n")

test.write('SConstruct', """
bar = Environment(CCFLAGS = '-DBAR')
bar.Object(target = 'foo.o', source = 'prog.c')
bar.Object(target = 'bar.o', source = 'prog.c')
bar.Program(target = 'foo', source = 'foo.o')
bar.Program(target = 'bar', source = 'bar.o')
""")

test.run(arguments = '.')

test.run(program = test.workpath('foo'), stdout = "prog.c:  BAR\n")
test.run(program = test.workpath('bar'), stdout = "prog.c:  BAR\n")

test.pass_test()
