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
Test that using Repository() works even when the Repository has no
SConsignFile() and the source Repository files have their signatures
saved because they're older than the max_drift time.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('build', 'src')

test.write(['build', 'SConstruct'], """\
SetOption('max_drift', 1)
Repository('..')
env = Environment()
env.Program('foo', 'src/foo.c')
""")

test.write(['src', 'foo.c'], """\
#include <stdio.h>
#include <stdlib.h>
#include "foo.h"
int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    printf("%s\\n", STRING);
    printf("src/foo.c\\n");
    exit (0);
}
""")

test.write(['src', 'foo.h'], """\
#define STRING "src/foo.h"
""")

# Make sure it's past the max_drift time,
# so the source file signatures get saved.
test.sleep(2)

test.run(chdir='build', arguments='.')

test.run(program=test.workpath('build', 'foo'),
         stdout="src/foo.h\nsrc/foo.c\n")

test.up_to_date(chdir='build', arguments='.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
