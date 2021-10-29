#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

import os
import sys

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
import sys

env = Environment(WINDOWS_INSERT_DEF=1)
env2 = Environment(LIBS=['foo1', 'foo2', 'foo3'], LIBPATH=['.'])
env.SharedLibrary(target='foo1', source='f1.c')
if sys.platform == 'win32':
    env.StaticLibrary(target='foo1-static', source='f1.c')
else:
    env.StaticLibrary(target='foo1', source='f1.c')
SharedLibrary(target='foo2', source=Split('f2a.c f2b.c f2c.c'), WINDOWS_INSERT_DEF=1)
env.SharedLibrary(target='foo3', source=['f3a.c', 'f3b.c', 'f3c.c'], no_import_lib=1)
env2.Program(target='prog', source='prog.c')
""")

test.write('SConstructFoo', """
env = Environment()
obj = env.Object('foo', 'foo.c')
Default(env.SharedLibrary(target='foo', source=obj))
""")

test.write('SConstructFoo2', """
env = Environment()
obj = env.SharedObject('bar', 'foo.c')
Default(env.Library(target='foo', source=obj))
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
#include <stdio.h>

void
f2a(void)
{
        printf("f2a.c\n");
}
""")

test.write('f2b.c', r"""
#include <stdio.h>
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
#include <stdio.h>
void
f3a(void)
{
        printf("f3a.c\n");
}
""")

test.write('f3b.c', r"""
#include <stdio.h>
void
f3b(void)
{
        printf("f3b.c\n");
}
""")

test.write('f3c.c', r"""
#include <stdio.h>

void
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
#include <stdio.h>
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

test.run(arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

if os.name == 'posix':
    os.environ['LD_LIBRARY_PATH'] = '.'
if sys.platform.find('irix') != -1:
    os.environ['LD_LIBRARYN32_PATH'] = '.'

test.run(program = test.workpath('prog'),
         stdout = "f1.c\nf2a.c\nf2b.c\nf2c.c\nf3a.c\nf3b.c\nf3c.c\nprog.c\n")

if sys.platform == 'cygwin':
    # Cygwin: Make sure the DLLs are prefixed correctly.
    test.must_exist('cygfoo1.dll', 'cygfoo2.dll', 'cygfoo3.dll')
    test.must_exist('libfoo1.dll.a', 'libfoo2.dll.a')
    test.must_not_exist('foo3.dll.a')


if sys.platform == 'win32' or sys.platform.find('irix') != -1:
    test.run(arguments='-f SConstructFoo')
else:
    expect = r"scons: \*\*\* \[.*\] Source file: foo\..* is static and is not compatible with shared target: .*"
    test.run(arguments='-f SConstructFoo', status=2, stderr=expect,
             match=TestSCons.match_re_dotall)
    # Run it again to make sure that we still get the error
    # even though the static objects already exist.
    test.run(arguments='-f SConstructFoo', status=2, stderr=expect,
             match=TestSCons.match_re_dotall)

test.run(arguments='-f SConstructFoo2',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

if sys.platform == 'win32':
    # Make sure we don't insert a .def source file (when
    # WINDOWS_INSERT_DEF is set) and a .lib target file if
    # they're specified explicitly.

    test.write('SConstructBar', '''
env = Environment(WINDOWS_INSERT_DEF=1)
env2 = Environment(LIBS = [ 'foo4' ],
                   LIBPATH = [ '.' ])
env.SharedLibrary(target = ['foo4', 'foo4.lib'], source = ['f4.c', 'foo4.def'])
env2.Program(target = 'progbar', source = 'progbar.c')
''')

    test.write('f4.c', r"""
#include <stdio.h>

void f4(void)
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
#include <stdio.h>
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
    for line in test.stdout().split('\n'):
        test.fail_test(line.count('foo4.def') > 1)
        test.fail_test(line.count('foo4.lib') > 1)

    test.run(program = test.workpath('progbar'),
             stdout = "f4.c\nprogbar.c\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
