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

import string

import TestSCons

test = TestSCons.TestSCons()

sccs = test.where_is('sccs')
if not sccs:
    test.skip_test("Could not find 'sccs'; skipping test(s).\n")



test.subdir('SCCS')

test.write('foo.c', """\
/* %%F%% */
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
DefaultEnvironment()['SCCSCOM'] = 'cd ${TARGET.dir} && $SCCS get ${TARGET.file}'
env = Environment()
env.Program('foo.c')
""")

test.run(stderr = None)

lines = string.split("""
sccs get foo.c
sccs get foo.h
""", '\n')

stdout = test.stdout()
missing = filter(lambda l, s=stdout: string.find(s, l) == -1, lines)
if missing:
    print "Missing the following output lines:"
    print string.join(missing, '\n')
    print "Actual STDOUT =========="
    print stdout
    test.fail_test(1)



test.pass_test()
