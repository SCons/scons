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

Verify that we do rebuild things when the contents of
two .h files are swapped, changing the order in which
dependency signatures show up in the calculated list,
but 

"""

import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.subdir('work1', 'work2')

work1_foo = test.workpath('work1', 'foo' + _exe)
work2_foo = test.workpath('work2', 'foo' + _exe)

content1 = """\
#ifndef STRING
#define STRING  "content1"
#endif
"""

content2 = """\
#ifndef STRING
#define STRING  "content2"
#endif
"""



test.write(['work1', 'SConstruct'], """\
env = Environment(CPPPATH = ['.'])
env.Program(target = 'foo', source = 'foo.c')
""")

test.write(['work1', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
#include <aaa.h>
#include <bbb.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("%s\n", STRING);
        exit (0);
}
""")

test.write(['work1', 'aaa.h'], content1)
test.write(['work1', 'bbb.h'], content2)

test.run(chdir = 'work1')

test.run(program = work1_foo, stdout = "content1\n")

test.write(['work1', 'aaa.h'], content2)
test.write(['work1', 'bbb.h'], content1)

test.run(chdir = 'work1')

test.run(program = work1_foo, stdout = "content2\n")



test.write(['work2', 'SConstruct'], """\
env = Environment(CPPPATH = ['.'])
env.Program(target = 'foo', source = 'foo.c')
""")

test.write(['work2', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
#include "aaa.h"
#include "bbb.h"
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("%s\n", STRING);
        exit (0);
}
""")

test.write(['work2', 'aaa.h'], content1)
test.write(['work2', 'bbb.h'], content2)

test.run(chdir = 'work2')

test.run(program = work2_foo, stdout = "content1\n")

test.write(['work2', 'aaa.h'], content2)
test.write(['work2', 'bbb.h'], content1)

test.run(chdir = 'work2')

test.run(program = work2_foo, stdout = "content2\n")



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
