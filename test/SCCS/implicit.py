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
Test transparent SCCS checkouts of implicit dependencies.
"""

import TestSCons

test = TestSCons.TestSCons()

sccs = test.where_is('sccs')
if not sccs:
    print "Could not find SCCS, skipping test(s)."
    test.pass_test(1)



test.subdir('SCCS')

test.write('foo.c', """\
#include "foo.h"
int
main(int argc, char *argv[]) {
    printf(STR);
    printf("foo.c\\n");
}
""")
test.run(program = sccs, arguments = "create foo.c", stderr = None)
test.unlink('foo.c')
test.unlink(',foo.c')

test.write('foo.h', """\
#define STR     "foo.h\\n"
""")
test.run(program = sccs, arguments = "create foo.h", stderr = None)
test.unlink('foo.h')
test.unlink(',foo.h')

test.write('SConstruct', """
env = Environment()
env.Program('foo.c')
""")

test.run(stderr = """\
foo.c 1.1: 6 lines
foo.h 1.1: 1 lines
""")



test.pass_test()
