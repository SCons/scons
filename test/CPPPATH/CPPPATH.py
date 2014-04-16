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

import os.path

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

VariantDir('variant', 'subdir', 0)
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
test.must_not_exist(test.workpath('variant', 'prog.c'))

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
test.must_not_exist(test.workpath('variant', 'prog.c'))

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
test.must_not_exist(test.workpath('variant', 'prog.c'))

test.up_to_date(arguments = args)



# Change CPPPATH and make sure we don't rebuild because of it.
test.write('SConstruct', """
env = Environment(CPPPATH = Split('inc2 include ${TARGET.dir} ${SOURCE.dir}'))
obj = env.Object(target='foobar/prog', source='subdir/prog.c')
env.Program(target='prog', source=obj)
SConscript('subdir/SConscript', "env")

VariantDir('variant', 'subdir', 0)
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



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
