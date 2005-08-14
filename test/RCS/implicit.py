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
Test transparent RCS checkouts of implicit dependencies.
"""

import TestSCons

test = TestSCons.TestSCons()

rcs = test.where_is('rcs')
if not rcs:
    test.skip_test("Could not find 'rcs'; skipping test(s).\n")

ci = test.where_is('ci')
if not ci:
    test.skip_test("Could not find 'ci'; skipping test(s).\n")

co = test.where_is('co')
if not co:
    test.skip_test("Could not find 'co'; skipping test(s).\n")



test.subdir('RCS')

test.write('foo.c', """\
#include "foo.h"
int
main(int argc, char *argv[]) {
    printf(STR);
    printf("foo.c\\n");
}
""")
test.run(program = ci,
         arguments = "-f -tfoo.c foo.c",
         stderr = None)

test.write('foo.h', """\
#define STR     "foo.h\\n"
""")
test.run(program = ci,
         arguments = "-f -tfoo.h foo.h",
         stderr = None)

test.write('SConstruct', """
DefaultEnvironment(RCS_CO = r'%s')
env = Environment()
env.Program('foo.c')
""" % co)

test.run(stderr="""\
RCS/foo.c,v  -->  foo.c
revision 1.1
done
RCS/foo.h,v  -->  foo.h
revision 1.1
done
""")



#
test.pass_test()
