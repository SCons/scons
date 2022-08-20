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
Test use of pre-compiled headers when the source .cpp file shows
up in both the env.PCH() and the env.Program() source list.

Issue 2505:  http://github.com/SCons/scons/issues/2505
"""

import TestSCons

test = TestSCons.TestSCons()

test.skip_if_not_msvc()

test.write('SConstruct', """\
env = Environment(tools=['msvc', 'mslink'])
env['PCH'] = env.PCH('Source1.cpp')[0]
env['PCHSTOP'] = 'Header1.hpp'
env.Program('foo', ['foo.cpp', 'Source2.cpp', 'Source1.cpp'])
""" % locals())

test.write('Header1.hpp', r"""
""")

test.write('Source1.cpp', r"""
#include <stdio.h>

#include "Header1.hpp"

void
Source1(void) {
    printf("Source1.cpp\n");
}
""")

test.write('Source2.cpp', r"""
#include <stdio.h>

#include "Header1.hpp"

void
Source2(void) {
    printf("Source2.cpp\n");
}
""")

test.write('foo.cpp', r"""
#include <stdio.h>

#include "Header1.hpp"

void Source1(void);
void Source2(void);

int
main(int argc, char *argv[])
{
    Source1();
    Source2();
    printf("foo.cpp\n");
}
""")

test.run(arguments = ".")

test.run(program=test.workpath('foo'+TestSCons._exe),
         stdout="Source1.cpp\nSource2.cpp\nfoo.cpp\n")



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
