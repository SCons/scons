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
Verify that expansion of construction variables whose values are functions
(that return lists that contain Nodes, even) works as expected within
a $CPPPATH list definition.

This used to cause TypeErrors when the _concat expansion tried to
join the Nodes with the strings.

Test courtesy Konstantin Bozhikov.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('list_inc1',
            'list_inc2',
            'inc1',
            'inc2',
            'inc3',
            ['inc3', 'subdir'])

test.write('SConstruct', """\
env = Environment()
def my_cpppaths( target, source, env, for_signature ):
    return [ Dir('list_inc1'), Dir('list_inc2') ]

env = Environment( CPPPATH = [Dir('inc1'), '$INC2', '$INC3/subdir', '$MY_CPPPATHS' ],
                   INC2 = Dir('inc2'),
                   INC3 = Dir('inc3'),
                   MY_CPPPATHS = my_cpppaths )

env.Program('prog.c')
""")

test.write('prog.c', """\
#include <stdio.h>
#include <stdlib.h>
#include "string_list_1.h"
#include "string_list_2.h"
#include "string_1.h"
#include "string_2.h"
#include "string_3.h"

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("prog.c\\n");
        printf("%s\\n", STRING_LIST_1);
        printf("%s\\n", STRING_LIST_2);
        printf("%s\\n", STRING_1);
        printf("%s\\n", STRING_2);
        printf("%s\\n", STRING_3);
        exit (0);
}
""")

test.write(['list_inc1', 'string_list_1.h'], """\
#define STRING_LIST_1   "list_inc1/string_list_1.h"
""")

test.write(['list_inc2', 'string_list_2.h'], """\
#define STRING_LIST_2   "list_inc2/string_list_2.h"
""")

test.write(['inc1', 'string_1.h'], """\
#define STRING_1        "inc1/string_1.h"
""")

test.write(['inc2', 'string_2.h'], """\
#define STRING_2        "inc2/string_2.h"
""")

test.write(['inc3', 'subdir', 'string_3.h'], """\
#define STRING_3        "inc3/subdir/string_3.h"
""")

test.run()

test.up_to_date(arguments = '.')

expect = """\
prog.c
list_inc1/string_list_1.h
list_inc2/string_list_2.h
inc1/string_1.h
inc2/string_2.h
inc3/subdir/string_3.h
"""

test.run(program = test.workpath('prog' + TestSCons._exe), stdout=expect)

test.write(['inc3', 'subdir', 'string_3.h'], """\
#define STRING_3        "inc3/subdir/string_3.h 2"
""")

test.not_up_to_date(arguments = '.')

expect = """\
prog.c
list_inc1/string_list_1.h
list_inc2/string_list_2.h
inc1/string_1.h
inc2/string_2.h
inc3/subdir/string_3.h 2
"""

test.run(program = test.workpath('prog' + TestSCons._exe), stdout=expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
