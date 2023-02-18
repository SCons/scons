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
Verify that use of the Scanner that evaluates CPP lines works as expected.
"""

import TestSCons

test = TestSCons.TestSCons()

m = 'Scanner evaluation of CPP lines not yet supported; skipping test.\n'
test.skip_test(m)

f1_exe = 'f1' + TestSCons._exe
f2_exe = 'f2' + TestSCons._exe
f3_exe = 'f3' + TestSCons._exe
f4_exe = 'f4' + TestSCons._exe

test.write('SConstruct', """\
env = Environment(CPPPATH=['.'])

f1 = env.Object('f1', 'fff.c', CPPDEFINES=['F1'])
f2 = env.Object('f2', 'fff.c', CPPDEFINES=[('F2', 1)])
f3 = env.Object('f3', 'fff.c', CPPDEFINES={'F3': None})
f4 = env.Object('f4', 'fff.c', CPPDEFINES={'F4': 1})

env.Program('f1', ['prog.c', f1])
env.Program('f2', ['prog.c', f2])
env.Program('f3', ['prog.c', f3])
env.Program('f4', ['prog.c', f4])
""")

test.write('f1.h', """
#define STRING  "F1"
""")

test.write('f2.h', """
#define STRING  "F2"
""")

test.write('f3.h', """
#define STRING  "F3"
""")

test.write('f4.h', """
#define STRING  "F4"
""")

test.write('fff.c', """
#ifdef  F1
#include <f1.h>
#endif
#if     F2
#include <f2.h>
#endif
#ifdef  F3
#include <f3.h>
#endif
#ifdef  F4
#include <f4.h>
#endif

char *
foo(void)
{
    return (STRING);
}
""")


test.write('prog.c', r"""
#include <stdio.h>
#include <stdlib.h>

extern char *foo(void);

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("prog.c:  %s\n", foo());
        exit (0);
}
""")



test.run(arguments = '.')
test.run(program = test.workpath('f1'), stdout = "prog.c:  F1\n")
test.run(program = test.workpath('f2'), stdout = "prog.c:  F2\n")
test.run(program = test.workpath('f3'), stdout = "prog.c:  F3\n")
test.run(program = test.workpath('f4'), stdout = "prog.c:  F4\n")

test.write('f1.h', """
#define STRING  "F1 again"
""")

test.up_to_date(arguments = '%(f2_exe)s %(f3_exe)s %(f4_exe)s' % locals())
test.not_up_to_date(arguments = '.')

test.run(program = test.workpath('f1'), stdout = "prog.c:  F1 again\n")
test.run(program = test.workpath('f2'), stdout = "prog.c:  F2\n")
test.run(program = test.workpath('f3'), stdout = "prog.c:  F3\n")
test.run(program = test.workpath('f4'), stdout = "prog.c:  F4\n")

test.write('f2.h', """
#define STRING  "F2 again"
""")

test.up_to_date(arguments = '%(f1_exe)s %(f3_exe)s %(f4_exe)s' % locals())
test.not_up_to_date(arguments = '.')

test.run(program = test.workpath('f1'), stdout = "prog.c:  F1 again\n")
test.run(program = test.workpath('f2'), stdout = "prog.c:  F2 again\n")
test.run(program = test.workpath('f3'), stdout = "prog.c:  F3\n")
test.run(program = test.workpath('f4'), stdout = "prog.c:  F4\n")

test.write('f3.h', """
#define STRING  "F3 again"
""")

test.up_to_date(arguments = '%(f1_exe)s %(f2_exe)s %(f4_exe)s' % locals())
test.not_up_to_date(arguments = '.')

test.run(program = test.workpath('f1'), stdout = "prog.c:  F1 again\n")
test.run(program = test.workpath('f2'), stdout = "prog.c:  F2 again\n")
test.run(program = test.workpath('f3'), stdout = "prog.c:  F3 again\n")
test.run(program = test.workpath('f4'), stdout = "prog.c:  F4\n")

test.write('f4.h', """
#define STRING  "F4 again"
""")

test.up_to_date(arguments = '%(f1_exe)s %(f2_exe)s %(f3_exe)s' % locals())
test.not_up_to_date(arguments = '.')

test.run(program = test.workpath('f1'), stdout = "prog.c:  F1 again\n")
test.run(program = test.workpath('f2'), stdout = "prog.c:  F2 again\n")
test.run(program = test.workpath('f3'), stdout = "prog.c:  F3 again\n")
test.run(program = test.workpath('f4'), stdout = "prog.c:  F4 again\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
