#!/usr/bin/env python
#
# __COPYRIGHT__
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
import sys
import TestSCons
import string

_exe = TestSCons._exe
_obj = TestSCons._obj

prog = 'prog' + _exe
subdir_prog = os.path.join('subdir', 'prog' + _exe)
variant_prog = os.path.join('variant', 'prog' + _exe)

args = prog + ' ' + subdir_prog + ' ' + variant_prog

test = TestSCons.TestSCons()

test.subdir('include', 'subdir', ['subdir', 'include'], 'inc2')

test.write('SConstruct', """
env = Environment(CPPPATH = Split('inc2 include'))
obj = env.Object(target='prog', source='subdir/prog.c')
env.Program(target='prog', source=obj)
SConscript('subdir/SConscript', "env")

BuildDir('variant', 'subdir', 0)
include = Dir('include')
env = Environment(CPPPATH=['inc2', include])
SConscript('variant/SConscript', "env")

def copy(target, source, env):
    open(str(target[0]), 'wt').write(open(str(source[0]), 'rt').read())
nodep = env.Command('nodeps.c', 'nodeps.in', action=copy)
env.Program('nodeps', 'nodeps.c')

env.Object(['one', 'two'], ['one.c'])
""")

test.write(['subdir', 'SConscript'],
"""
Import("env")
env.Program(target='prog', source='prog.c')
""")

test.write('nodeps.in', 
r"""
int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    return 0;
}
""")


test.write(['include', 'foo.h'],
r"""
#define	FOO_STRING "include/foo.h 1\n"
#include <bar.h>
""")

test.write(['include', 'bar.h'],
r"""
#define BAR_STRING "include/bar.h 1\n"
""")

test.write(['include', 'baz.h'],
r"""
#define BAZ_STRING "include/baz.h 1\n"
""")

test.write(['subdir', 'prog.c'],
r"""
#include <foo.h>
#include <stdio.h>

int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    printf("subdir/prog.c\n");
    printf(FOO_STRING);
    printf(BAR_STRING);
    return 0;
}
""")

test.write(['subdir', 'include', 'foo.h'],
r"""
#define	FOO_STRING "subdir/include/foo.h 1\n"
#include "bar.h"
""")

test.write(['subdir', 'include', 'bar.h'],
r"""
#define BAR_STRING "subdir/include/bar.h 1\n"
""")

test.write('one.c' ,
r"""
#include <foo.h>

void one(void) { }
""")

test.run(arguments = "--implicit-cache " + args)

test.run(program = test.workpath(prog),
         stdout = "subdir/prog.c\ninclude/foo.h 1\ninclude/bar.h 1\n")

test.run(program = test.workpath(subdir_prog),
         stdout = "subdir/prog.c\nsubdir/include/foo.h 1\nsubdir/include/bar.h 1\n")

test.run(program = test.workpath(variant_prog),
         stdout = "subdir/prog.c\ninclude/foo.h 1\ninclude/bar.h 1\n")

test.up_to_date(arguments = args)

# Make sure implicit dependenies work right when one is modifed:
test.write(['include', 'foo.h'],
r"""
#define	FOO_STRING "include/foo.h 2\n"
#include "bar.h"
""")

test.run(arguments = "--implicit-cache " + args)

test.run(program = test.workpath(prog),
         stdout = "subdir/prog.c\ninclude/foo.h 2\ninclude/bar.h 1\n")

test.run(program = test.workpath(subdir_prog),
         stdout = "subdir/prog.c\nsubdir/include/foo.h 1\nsubdir/include/bar.h 1\n")

test.run(program = test.workpath(variant_prog),
         stdout = "subdir/prog.c\ninclude/foo.h 2\ninclude/bar.h 1\n")

test.up_to_date(arguments = args)

# Make sure that changing the order of includes causes rebuilds and
# doesn't produce redundant rebuilds:
test.write(['include', 'foo.h'],
r"""
#define	FOO_STRING "include/foo.h 2\n"
#include "bar.h"
#include "baz.h"
""")

test.run(arguments = "--implicit-cache " + args)

test.run(program = test.workpath(prog),
         stdout = "subdir/prog.c\ninclude/foo.h 2\ninclude/bar.h 1\n")

test.run(program = test.workpath(subdir_prog),
         stdout = "subdir/prog.c\nsubdir/include/foo.h 1\nsubdir/include/bar.h 1\n")

test.run(program = test.workpath(variant_prog),
         stdout = "subdir/prog.c\ninclude/foo.h 2\ninclude/bar.h 1\n")

test.up_to_date(arguments = args)

test.write(['include', 'foo.h'],
r"""
#define	FOO_STRING "include/foo.h 2\n"
#include "baz.h"
#include "bar.h"
""")

test.run(arguments = "--implicit-cache " + args)

test.run(program = test.workpath(prog),
         stdout = "subdir/prog.c\ninclude/foo.h 2\ninclude/bar.h 1\n")

test.run(program = test.workpath(subdir_prog),
         stdout = "subdir/prog.c\nsubdir/include/foo.h 1\nsubdir/include/bar.h 1\n")

test.run(program = test.workpath(variant_prog),
         stdout = "subdir/prog.c\ninclude/foo.h 2\ninclude/bar.h 1\n")

test.up_to_date(arguments = args)



# Add inc2/foo.h that should shadow include/foo.h, but
# because of implicit dependency caching, scons doesn't
# detect this:
test.write(['inc2', 'foo.h'],
r"""
#define FOO_STRING "inc2/foo.h 1\n"
#include <bar.h>
""")

test.run(arguments = "--implicit-cache " + args)

test.run(arguments = "--implicit-cache " + args)

test.run(program = test.workpath(prog),
         stdout = "subdir/prog.c\ninclude/foo.h 2\ninclude/bar.h 1\n")

test.run(program = test.workpath(subdir_prog),
         stdout = "subdir/prog.c\nsubdir/include/foo.h 1\nsubdir/include/bar.h 1\n")

test.run(program = test.workpath(variant_prog),
         stdout = "subdir/prog.c\ninclude/foo.h 2\ninclude/bar.h 1\n")

# Now modifying include/foo.h should make scons aware of inc2/foo.h
test.write(['include', 'foo.h'],
r"""
#define	FOO_STRING "include/foo.h 3\n"
#include "bar.h"
""")

test.run(arguments = "--implicit-cache " + args)

test.run(program = test.workpath(prog),
         stdout = "subdir/prog.c\ninc2/foo.h 1\ninclude/bar.h 1\n")

test.run(program = test.workpath(subdir_prog),
         stdout = "subdir/prog.c\nsubdir/include/foo.h 1\nsubdir/include/bar.h 1\n")

test.run(program = test.workpath(variant_prog),
         stdout = "subdir/prog.c\ninclude/foo.h 3\ninclude/bar.h 1\n")

# test in the face of a file with no dependencies where the source file is generated:
test.run(arguments = "--implicit-cache nodeps%s"%_exe)

test.write('nodeps.in', 
r"""
#include <foo.h>

int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    return 0;
}
""")

test.run(arguments = "--implicit-cache one%s"%_obj)
test.run(arguments = "--implicit-cache one%s"%_obj)

# Test forcing of implicit caching:
test.write(['include', 'foo.h'],
r"""
#define	FOO_STRING "include/foo.h 3\n"
#include "bar.h"
""")

test.run(arguments = "--implicit-cache " + args)

test.write(['include', 'foo.h'],
r"""
#define	FOO_STRING "include/foo.h 3\n"
#include "baz.h"
#include "bar.h"
""")

test.run(arguments = "--implicit-deps-unchanged " + variant_prog)
assert string.find(test.stdout(), 'is up to date') == -1, test.stdout()

test.write(['include', 'baz.h'],
r"""
#define BAZ_STRING "include/baz.h 2\n"
""")

test.run(arguments = "--implicit-deps-unchanged " + variant_prog)
assert string.find(test.stdout(), 'is up to date') != -1, test.stdout()

test.run(arguments = variant_prog)
assert string.find(test.stdout(), 'is up to date') == -1, test.stdout()

# Test forcing rescanning:
test.write(['include', 'foo.h'],
r"""
#define	FOO_STRING "include/foo.h 3\n"
#include "bar.h"
""")

test.run(arguments = "--implicit-cache " + args)

test.write(['include', 'foo.h'],
r"""
#define	FOO_STRING "include/foo.h 3\n"
#include "baz.h"
#include "bar.h"
""")

test.run(arguments = "--implicit-deps-unchanged " + variant_prog)
assert string.find(test.stdout(), 'is up to date') == -1, test.stdout()

test.write(['include', 'baz.h'],
r"""
#define BAZ_STRING "include/baz.h 2\n"
""")

test.run(arguments = "--implicit-deps-unchanged " + variant_prog)
assert string.find(test.stdout(), 'is up to date') != -1, test.stdout()

test.run(arguments = "--implicit-deps-changed " + variant_prog)
assert string.find(test.stdout(), 'is up to date') == -1, test.stdout()

# Test that Set/GetOption('implicit_cache') works:
test.write('SConstruct', """
assert not GetOption('implicit_cache')
SetOption('implicit_cache', 1)
assert GetOption('implicit_cache')
""")

test.run()

test.write('SConstruct', """
assert GetOption('implicit_cache')
SetOption('implicit_cache', 0)
assert GetOption('implicit_cache')
""")

test.run(arguments='--implicit-cache')

# Test to make sure SetOption('implicit_cache', 1) actually enables implicit caching
# by detecting the one case where implicit caching causes inaccurate builds:
test.write('SConstruct', """
SetOption('implicit_cache', 1)
env=Environment(CPPPATH=['i1', 'i2'])
env.Object('foo.c')
""")

test.subdir('i1')
test.subdir('i2')

test.write('foo.c', """
#include <foo.h>

void foo(void)
{
    FOO_H_DEFINED
    ++x;  /* reference x */
}
""")

test.write('i2/foo.h', """
#define FOO_H_DEFINED int x = 1;
""")

test.run()

test.write('i1/foo.h', """
""");

test.run()

test.pass_test()
