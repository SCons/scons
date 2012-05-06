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
Test construction variable expansion in Builder paths.
"""

import os.path

import TestSCons

_exe = TestSCons._exe
_obj = TestSCons._obj

test = TestSCons.TestSCons()

test.subdir('sub')

test.write('SConstruct', """\
env = Environment(SUBDIR = 'sub')
env.Program(target = 'foo1', source = env.Object(source = r'%s'))
env.Program(source = env.Object(target = r'%s', source = 'f2.c'))
env.Program('foo3', r'%s')
env.Program(r'%s')
""" % (os.path.join('$SUBDIR', 'f1.c'),
       os.path.join('$SUBDIR', 'foo2'),
       os.path.join('$SUBDIR', 'f3.c'),
       os.path.join('$SUBDIR', 'foo4.c')))

test.write(['sub', 'f1.c'], r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("sub/f1.c\n");
        exit (0);
}
""")

test.write('f2.c', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("f2.c\n");
        exit (0);
}
""")

test.write(['sub', 'f3.c'], r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("sub/f3.c\n");
        exit (0);
}
""")

test.write(['sub', 'foo4.c'], r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("sub/foo4.c\n");
        exit (0);
}
""")

test.run(arguments = '.')

test.run(program = test.workpath('foo1' + _exe), stdout = "sub/f1.c\n")
test.run(program = test.workpath('sub', 'foo2' + _exe), stdout = "f2.c\n")
test.run(program = test.workpath('foo3' + _exe), stdout = "sub/f3.c\n")
test.run(program = test.workpath('sub','foo4' + _exe), stdout = "sub/foo4.c\n")

test.fail_test(not os.path.exists(test.workpath('sub', 'f1' + _obj)))
test.fail_test(not os.path.exists(test.workpath('sub', 'foo2' + _obj)))
test.fail_test(not os.path.exists(test.workpath('sub', 'f3' + _obj)))
test.fail_test(not os.path.exists(test.workpath('sub', 'foo4' + _obj)))

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
