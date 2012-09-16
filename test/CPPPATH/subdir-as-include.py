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
This is an obscure test case. When a file without a suffix is included in 
a c++ build and there is a directory with the same name as that file in a
sub-build directory, verify that an Errno 21 is not thrown upon trying to
recursively scan the contents of includes. The Errno 21 indicates that
the directory with the same name was trying to be scanned as the include
file, which it clearly is not.
"""

import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.subdir('inc1', ['inc1', 'iterator'])

test.write('SConstruct', """
env = Environment(CPPPATH = [Dir('inc1')])
env.Program('prog.cpp')

Export('env')
SConscript('inc1/SConscript', variant_dir='inc1/build', duplicate=0)
""")

test.write('prog.cpp', """\
#include <stdio.h>
#include <stdlib.h>

#include "one.h"
#include <iterator>
int main(int argc, char* argv[])
{
    printf("%s\\n", ONE);
    return 0;
}
""")

test.write(['inc1', 'SConscript'], """\
Import('env')
oneenv = env.Clone()
oneenv.Program('one.cpp')
""")

test.write(['inc1', 'one.h'], """\
#define ONE     "1"
""")

test.write(['inc1', 'one.cpp'], """\
#include <iterator>
#include <stdio.h>
#include "one.h"

int main(int argc, char* argv[])
{
    printf("%s\\n", ONE);
    return 0;
}
""")

test.run(arguments = '.')

test.run(program = test.workpath('prog' + _exe), stdout = "1\n")
test.run(program = test.workpath('inc1/build/one' + _exe), stdout = "1\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
