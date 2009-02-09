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
Verify that expansion of construction variables whose values are
lists works as expected within a $CPPPATH list definition.

Previously, the stringification of the expansion of the individual
variables would turn a list like ['sub1', 'sub2'] below into "-Isub1 sub2"
on the command line.

Test case courtesy Daniel Svensson.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('sub1', 'sub2', 'sub3', 'sub4')

test.write('SConstruct', """\
class _inc_test:
    def __init__(self, name):
        self.name = name

    def __call__(self, target, source, env, for_signature):
        return env.something[self.name]

env = Environment()

env.something = {}
env.something['test'] = ['sub1', 'sub2']

env['INC_PATHS1'] = _inc_test

env['INC_PATHS2'] = ['sub3', 'sub4']

env.Append(CPPPATH = ['${INC_PATHS1("test")}', '$INC_PATHS2'])
env.Program('test', 'test.c')
""")

test.write('test.c', """\
#include <stdio.h>
#include <stdlib.h>
#include "string1.h"
#include "string2.h"
#include "string3.h"
#include "string4.h"

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("test.c\\n");
        printf("%s\\n", STRING1);
        printf("%s\\n", STRING2);
        printf("%s\\n", STRING3);
        printf("%s\\n", STRING4);
        exit (0);
}
""")

test.write(['sub1', 'string1.h'], """\
#define STRING1 "sub1/string1.h"
""")

test.write(['sub2', 'string2.h'], """\
#define STRING2 "sub2/string2.h"
""")

test.write(['sub3', 'string3.h'], """\
#define STRING3 "sub3/string3.h"
""")

test.write(['sub4', 'string4.h'], """\
#define STRING4 "sub4/string4.h"
""")

test.run()

test.up_to_date(arguments = '.')

expect = """\
test.c
sub1/string1.h
sub2/string2.h
sub3/string3.h
sub4/string4.h
"""

test.run(program = test.workpath('test' + TestSCons._exe), stdout=expect)

test.write(['sub2', 'string2.h'], """\
#define STRING2 "sub2/string2.h 2"
""")

test.not_up_to_date(arguments = '.')

expect = """\
test.c
sub1/string1.h
sub2/string2.h 2
sub3/string3.h
sub4/string4.h
"""

test.run(program = test.workpath('test' + TestSCons._exe), stdout=expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
