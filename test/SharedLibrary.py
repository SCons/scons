#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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

import os
import string
import sys

import TestCmd
import TestSCons

test = TestSCons.TestSCons(match=TestCmd.match_re)

test.write('SConstruct', """
env=Environment(WIN32_INSERT_DEF=1)
env2 = Environment(LIBS = [ 'foo1', 'foo2', 'foo3' ],
                   LIBPATH = [ '.' ])
env.SharedLibrary(target = 'foo1', source = 'f1.c')
env.SharedLibrary(target = 'foo2', source = Split('f2a.c f2b.c f2c.c'))
env.SharedLibrary(target = 'foo3', source = ['f3a.c', 'f3b.c', 'f3c.c'])
env2.Program(target = 'prog', source = 'prog.c')
""")

test.write('SConstructFoo', """
env=Environment()
obj = env.Object('foo', 'foo.c')
Default(env.SharedLibrary(target = 'foo', source = obj))
""")

test.write('SConstructFoo2', """
env=Environment()
obj = env.SharedObject('bar', 'foo.c')
Default(env.Library(target = 'foo', source = obj))
""")

test.write('foo.c', r"""
#include <stdio.h>

void
f1(void)
{
	printf("foo.c\n");
        fflush(stdout);
}
""")


test.write('f1.c', r"""
#include <stdio.h>

void
f1(void)
{
	printf("f1.c\n");
        fflush(stdout);
}
""")

test.write("foo1.def", r"""
LIBRARY        "foo1"
DESCRIPTION    "Foo1 Shared Library"

EXPORTS
   f1
""")

test.write('f2a.c', r"""
void
f2a(void)
{
	printf("f2a.c\n");
}
""")

test.write('f2b.c', r"""
void
f2b(void)
{
	printf("f2b.c\n");
}
""")

test.write('f2c.c', r"""
#include <stdio.h>

void
f2c(void)
{
	printf("f2c.c\n");
        fflush(stdout);
}
""")

test.write("foo2.def", r"""
LIBRARY        "foo2"
DESCRIPTION    "Foo2 Shared Library"

EXPORTS
   f2a
   f2b
   f2c
""")

test.write('f3a.c', r"""
void
f3a(void)
{
	printf("f3a.c\n");
}
""")

test.write('f3b.c', r"""
void
f3b(void)
{
	printf("f3b.c\n");
}
""")

test.write('f3c.c', r"""
#include <stdio.h>

f3c(void)
{
	printf("f3c.c\n");
        fflush(stdout);
}
""")

test.write("foo3.def", r"""
LIBRARY        "foo3"
DESCRIPTION    "Foo3 Shared Library"

EXPORTS
   f3a
   f3b
   f3c
""")

test.write('prog.c', r"""
void f1(void);
void f2a(void);
void f2b(void);
void f2c(void);
void f3a(void);
void f3b(void);
void f3c(void);
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	f1();
	f2a();
	f2b();
	f2c();
	f3a();
	f3b();
	f3c();
	printf("prog.c\n");
        return 0;
}
""")

test.run(arguments = '.')

if os.name == 'posix':
    os.environ['LD_LIBRARY_PATH'] = '.'

test.run(program = test.workpath('prog'),
         stdout = "f1.c\nf2a.c\nf2b.c\nf2c.c\nf3a.c\nf3b.c\nf3c.c\nprog.c\n")

test.run(arguments = '-f SConstructFoo', status=2, stderr='''
SCons error: Source file: foo\..* is static and is not compatible with shared target: .*
'''
)

test.run(arguments = '-f SConstructFoo2', status=2, stderr='''
SCons error: Source file: bar\..* is shared and is not compatible with static target: .*
'''
)

if sys.platform == 'win32':
    # Make sure we don't insert a .def source file (when
    # WIN32_INSERT_DEF is set) and a .lib target file if
    # they're specified explicitly.

    test.write('SConstructBar', '''
env = Environment(WIN32_INSERT_DEF=1)
env2 = Environment(LIBS = [ 'foo4' ],
                   LIBPATH = [ '.' ])
env.SharedLibrary(target = ['foo4', 'foo4.lib'], source = ['f4.c', 'foo4.def'])
env2.Program(target = 'progbar', source = 'progbar.c')
''')

    test.write('f4.c', r"""
#include <stdio.h>

f4(void)
{
        printf("f4.c\n");
        fflush(stdout);
}
""")

    test.write("foo4.def", r"""
LIBRARY        "foo4"
DESCRIPTION    "Foo4 Shared Library"

EXPORTS
   f4
""")

    test.write('progbar.c', r"""
void f4(void);
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        f4();
        printf("progbar.c\n");
        return 0;
}
""")

    test.run(arguments = '-f SConstructBar .')

    # Make sure there is (at most) one mention each of the
    # appropriate .def and .lib files per line.
    for line in string.split(test.stdout(), '\n'):
        test.fail_test(string.count(line, 'foo4.def') > 1)
        test.fail_test(string.count(line, 'foo4.lib') > 1)

    test.run(program = test.workpath('progbar'),
             stdout = "f4.c\nprogbar.c\n")

test.pass_test()
