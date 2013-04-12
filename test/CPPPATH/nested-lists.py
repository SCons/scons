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

"""
Verify that CPPPATH values consisting of nested lists work correctly.
"""

import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.subdir('inc1', 'inc2', 'inc3')

test.write('SConstruct', """
env = Environment(CPPPATH = ['inc1', ['inc2', ['inc3']]])
env.Program('prog.c')
""")

test.write('prog.c', """\
#include <stdio.h>
#include <stdlib.h>

#include "one.h"
#include "two.h"
#include "three.h"
int
main(int argc, char *argv[])
{
    printf("%s\\n", ONE);
    printf("%s\\n", TWO);
    printf("%s\\n", THREE);
    return (0);
}
""")

test.write(['inc1', 'one.h'], """\
#define ONE     "1"
""")

test.write(['inc2', 'two.h'], """\
#define TWO     "2"
""")

test.write(['inc3', 'three.h'], """\
#define THREE   "3"
""")

test.run(arguments = '.')

test.run(program = test.workpath('prog' + _exe), stdout = "1\n2\n3\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
