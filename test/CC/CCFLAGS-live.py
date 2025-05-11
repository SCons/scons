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

"""
Test behavior of CCFLAGS.

This is a live test, uses the detected C compiler.
"""

import sys

import TestSCons

test = TestSCons.TestSCons()

if sys.platform == 'win32':
    import SCons.Tool.MSCommon as msc

    if not msc.msvc_exists():
        fooflags = '-DFOO'
        barflags = '-DBAR'
    else:
        fooflags = '/nologo -DFOO'
        barflags = '/nologo -DBAR'
else:
    fooflags = '-DFOO'
    barflags = '-DBAR'

test.write('SConstruct', f"""\
DefaultEnvironment(tools=[])
foo = Environment(CCFLAGS='{fooflags}')
bar = Environment(CCFLAGS='{barflags}')

foo_obj = foo.Object(target='foo', source='prog.c')
bar_obj = bar.Object(target='bar', source='prog.c')
foo.Program(target='foo', source=foo_obj)
bar.Program(target='bar', source=bar_obj)
foo.Program(target='prog', source='prog.c', CCFLAGS='$CCFLAGS -DBAR $BAZ', BAZ='-DBAZ')
""")

test.write('prog.c', r"""
#include <stdio.h>
#include <stdlib.h>

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
#ifdef BAZ
        printf("prog.c:  BAZ\n");
#endif
        exit (0);
}
""")

test.run(arguments='.')
test.run(program=test.workpath('foo'), stdout="prog.c:  FOO\n")
test.run(program=test.workpath('bar'), stdout="prog.c:  BAR\n")
test.run(program=test.workpath('prog'), stdout="""\
prog.c:  FOO
prog.c:  BAR
prog.c:  BAZ
""")

test.write('SConstruct', f"""\
DefaultEnvironment(tools=[])
bar = Environment(CCFLAGS='{barflags}')

foo_obj = bar.Object(target='foo', source='prog.c')
bar_obj = bar.Object(target='bar', source='prog.c')
bar.Program(target='foo', source=foo_obj)
bar.Program(target='bar', source=bar_obj)
""")

test.run(arguments='.')
test.run(program=test.workpath('foo'), stdout="prog.c:  BAR\n")
test.run(program=test.workpath('bar'), stdout="prog.c:  BAR\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
