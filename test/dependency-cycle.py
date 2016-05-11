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

import TestSCons
import TestCmd

test = TestSCons.TestSCons(match = TestCmd.match_re)

test.write('SConstruct', """
env = Environment()
foo1 = env.Library(target = 'foo1', source = 'f1.c')
foo2 = env.Library(target = 'foo2', source = 'f1.c')
foo3 = env.Library(target = 'foo3', source = 'f1.c')
env.Depends(foo1, foo2)
env.Depends(foo2, foo3)
env.Depends(foo3, foo1)
""")

test.write('f1.c', r"""
#include <stdio.h>
void
f1(void)
{
        printf("f1.c\n");
} 
""")

test.run(arguments = ".", stderr=r"""
scons: \*\*\* Found dependency cycle\(s\):
  .*foo(1|3|2).* -> .*foo(3|2|1).* -> .*foo(2|1|3).* -> .*foo(1|3|2).*
  .*foo(3|1|2).* -> .*foo(2|3|1).* -> .*foo(1|2|3).* -> .*foo(3|1|2).*

.*
""", status=2)

test.fail_test(test.stdout() == "")


test.pass_test()


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
