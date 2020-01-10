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
Verify that SetOption('implicit_cache', 1) actually enables implicit
caching by detecting the case where implicit caching causes inaccurate
builds:  a same-named file dropped into a directory earlier in the
CPPPATH list will *not* be detected because we use what's in the cache.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
DefaultEnvironment(tools=[])
SetOption('implicit_cache', 1)
env=Environment(CPPPATH=['i1', 'i2'])
env.Object('foo.c')
""")

test.subdir('i1')
test.subdir('i2')

test.write('foo.c', """
#include <foo.h>

void foo(void)
{
    FOO_H_DEFINED
    ++x;  /* reference x */
}
""")

test.write('i2/foo.h', """
#define FOO_H_DEFINED int x = 1;
""")

test.run(arguments = '.')

test.write('i1/foo.h', """
this line will cause a syntax error if it's included by a rebuild
""")

test.up_to_date(arguments = '.')


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
