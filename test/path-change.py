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
Make sure that changing the location - but not the name - of a
source file triggers a rebuild (issue #2311).
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('src1')
test.subdir('src2')

test.write('SConstruct', """

vars = Variables()
vars.AddVariables(
      PathVariable('SRCDIR', 'name the subdir to take the sources from', 'src1'))
env = Environment(variables = vars)
Export('env')

env.Object(target='hello.o', source=['$SRCDIR/hello.c'])
env.Program(target = 'hello', source = ['hello.o'])
""")

hello_text=r"""

#include <stdio.h>
#include <stdlib.h>
int
main()
{
        printf("%s\n");
        exit (0);
}

"""

test.write('src1/hello.c', hello_text % 'src1/hello')
test.write('src2/hello.c', hello_text % 'src2/hello')

test.not_up_to_date(options='SRCDIR=src1')
test.up_to_date(options='SRCDIR=src1')
test.not_up_to_date(options='SRCDIR=src2')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
