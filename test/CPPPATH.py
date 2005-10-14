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

_exe = TestSCons._exe

prog = 'prog' + _exe
subdir_prog = os.path.join('subdir', 'prog' + _exe)
variant_prog = os.path.join('variant', 'prog' + _exe)

args = prog + ' ' + subdir_prog + ' ' + variant_prog

test = TestSCons.TestSCons()

test.subdir('foobar',
            'include',
            'subdir',
            ['subdir', 'include'],
            'inc2')

test.write('SConstruct', """
env = Environment(CPPPATH = ['$FOO', '${TARGET.dir}', '${SOURCE.dir}'],
                  FOO='include')
obj = env.Object(target='foobar/prog', source='subdir/prog.c')
env.Program(target='prog', source=obj)
SConscript('subdir/SConscript', "env")

BuildDir('variant', 'subdir', 0)
include = Dir('include')
env = Environment(CPPPATH=[include, '#foobar', '#subdir'])
SConscript('variant/SConscript', "env")
""")

test.write(['subdir', 'SConscript'],
"""
Import("env")
env.Program(target='prog', source='prog.c')
""")

test.write(['include', 'foo.h'],
r"""
#define FOO_STRING "include/foo.h 1\n"
#include <bar.h>
""")

test.write(['include', 'bar.h'],
r"""
#define BAR_STRING "include/bar.h 1\n"
""")

test.write(['subdir', 'sss.h'],
r"""
#define SSS_STRING      "subdir/sss.h\n"
""")

test.write(['foobar', 'ttt.h'],
r"""
#define TTT_STRING      "foobar/ttt.h\n"
""")

test.write(['subdir', 'ttt.h'],
r"""
#define TTT_STRING      "subdir/ttt.h\n"
""")

test.write(['subdir', 'prog.c'],
r"""
#include <foo.h>
#include <sss.h>
#include <ttt.h>
#include <stdio.h>

int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    printf("subdir/prog.c\n");
    printf(FOO_STRING);
    printf(BAR_STRING);
    printf(SSS_STRING);
    printf(TTT_STRING);
    return 0;
}
""")

test.write(['subdir', 'include', 'foo.h'],
r"""
#define FOO_STRING "subdir/include/foo.h 1\n"
#include "bar.h"
""")

test.write(['subdir', 'include', 'bar.h'],
r"""
#define BAR_STRING "subdir/include/bar.h 1\n"
""")



test.run(arguments = args)

test.run(program = test.workpath(prog),
         stdout = """\
subdir/prog.c
include/foo.h 1
include/bar.h 1
subdir/sss.h
foobar/ttt.h
""")

test.run(program = test.workpath(subdir_prog),
         stdout = """\
subdir/prog.c
subdir/include/foo.h 1
subdir/include/bar.h 1
subdir/sss.h
subdir/ttt.h
""")

test.run(program = test.workpath(variant_prog),
         stdout = """\
subdir/prog.c
include/foo.h 1
include/bar.h 1
subdir/sss.h
foobar/ttt.h
""")



# Make sure we didn't duplicate the source file in the variant subdirectory.
test.fail_test(os.path.exists(test.workpath('variant', 'prog.c')))

test.up_to_date(arguments = args)

test.write(['include', 'foo.h'],
r"""
#define FOO_STRING "include/foo.h 2\n"
#include "bar.h"
""")

test.run(arguments = args)

test.run(program = test.workpath(prog),
         stdout = """\
subdir/prog.c
include/foo.h 2
include/bar.h 1
subdir/sss.h
foobar/ttt.h
""")

test.run(program = test.workpath(subdir_prog),
         stdout = """\
subdir/prog.c
subdir/include/foo.h 1
subdir/include/bar.h 1
subdir/sss.h
subdir/ttt.h
""")

test.run(program = test.workpath(variant_prog),
         stdout = """\
subdir/prog.c
include/foo.h 2
include/bar.h 1
subdir/sss.h
foobar/ttt.h
""")



# Make sure we didn't duplicate the source file in the variant subdirectory.
test.fail_test(os.path.exists(test.workpath('variant', 'prog.c')))

test.up_to_date(arguments = args)



#
test.write(['include', 'bar.h'],
r"""
#define BAR_STRING "include/bar.h 2\n"
""")

test.run(arguments = args)

test.run(program = test.workpath(prog),
         stdout = """\
subdir/prog.c
include/foo.h 2
include/bar.h 2
subdir/sss.h
foobar/ttt.h
""")

test.run(program = test.workpath(subdir_prog),
         stdout = """\
subdir/prog.c
subdir/include/foo.h 1
subdir/include/bar.h 1
subdir/sss.h
subdir/ttt.h
""")

test.run(program = test.workpath(variant_prog),
         stdout = """\
subdir/prog.c
include/foo.h 2
include/bar.h 2
subdir/sss.h
foobar/ttt.h
""")

# Make sure we didn't duplicate the source file in the variant subdirectory.
test.fail_test(os.path.exists(test.workpath('variant', 'prog.c')))

test.up_to_date(arguments = args)



# Change CPPPATH and make sure we don't rebuild because of it.
test.write('SConstruct', """
env = Environment(CPPPATH = Split('inc2 include ${TARGET.dir} ${SOURCE.dir}'))
obj = env.Object(target='foobar/prog', source='subdir/prog.c')
env.Program(target='prog', source=obj)
SConscript('subdir/SConscript', "env")

BuildDir('variant', 'subdir', 0)
include = Dir('include')
env = Environment(CPPPATH=['inc2', include, '#foobar', '#subdir'])
SConscript('variant/SConscript', "env")
""")

test.up_to_date(arguments = args)



#
test.write(['inc2', 'foo.h'],
r"""
#define FOO_STRING "inc2/foo.h 1\n"
#include <bar.h>
""")

test.run(arguments = args)

test.run(program = test.workpath(prog),
         stdout = """\
subdir/prog.c
inc2/foo.h 1
include/bar.h 2
subdir/sss.h
foobar/ttt.h
""")

test.run(program = test.workpath(subdir_prog),
         stdout = """\
subdir/prog.c
subdir/include/foo.h 1
subdir/include/bar.h 1
subdir/sss.h
subdir/ttt.h
""")

test.run(program = test.workpath(variant_prog),
         stdout = """\
subdir/prog.c
include/foo.h 2
include/bar.h 2
subdir/sss.h
foobar/ttt.h
""")

test.up_to_date(arguments = args)



# Check that neither a null-string CPPPATH nor a
# a CPPPATH containing null values blows up.
test.write('SConstruct', """
env = Environment(CPPPATH = '')
env.Library('one', source = 'empty1.c')
env = Environment(CPPPATH = [None])
env.Library('two', source = 'empty2.c')
env = Environment(CPPPATH = [''])
env.Library('three', source = 'empty3.c')
""")

test.write('empty1.c', "int a=0;\n")
test.write('empty2.c', "int b=0;\n")
test.write('empty3.c', "int c=0;\n")

test.run(arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)



test.pass_test()
