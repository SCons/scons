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

import sys
import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.write('SConstruct', """\
Program('main', [
    'main.c',
    Object('foo.o', 'foo.c'),
    Object('FOO.o', 'bar.c')])
""")

test.write('main.c', """\
#include <stdlib.h>

void foo();
void bar();
int main(void) {
    foo();
    bar();
    exit (0);
}
""")

test.write('foo.c', """\
#include <stdio.h>
void foo() {
    puts("foo");
}
""")

test.write('bar.c', """\
#include <stdio.h>
void bar() {
    puts("bar");
}
""")

if sys.platform[:6] == 'darwin':
    test.skip_test("Skipping test on Darwin/OSX; it has partial case sensitivity.\n")

if sys.platform in ['cygwin', 'win32']:
    sys.stdout.write("Using case-insensitive filesystem, testing for failure\n")
    sys.stdout.flush()

    test.run(stderr = None, status = None)
    test.fail_test(test.stderr().split('\n')[0] ==
                   "scons: *** Multiple ways to build the same target were specified for: foo.o")

else:
    sys.stdout.write("Not using case-insensitive filesystem, testing for success\n")
    sys.stdout.flush()

    test.run()
    test.run(program = test.workpath('main' + _exe), stdout = "foo\nbar\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
