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
Test VariantDir handling of #include files in subdirectories.

When a source file #includes a file that is not in the current directory,
we have to make sure that the file gets copied to the variant dir. (This
was not the case for 0.98.5 and earlier)

Test case supplied by Jared Grubb, based on a minimal example supplied
by Ali Tofigh, filed as https://github.com/SCons/scons/issues/2121
"""

import TestSCons

test = TestSCons.TestSCons()

#-------------------------------------------------------------------------------
#1- Create dep.cpp and the SConstruct. dep.h is missing and the build is
#expected to fail with 2.
#-------------------------------------------------------------------------------

test.subdir('src')
test.subdir('src/utils')
test.write(['src', 'main.cpp'], """\
#include "main.h"
#include "utils/util.h"

int main(int argc, char* argv[])
{
    return MAIN_VALUE+UTIL_VALUE;
}
""")

test.write(['src', 'main.h'], """\
#define MAIN_VALUE 2
""")

test.write(['src', 'utils', 'util.h'], """\
#define UTIL_VALUE -2
""")

test.write('SConstruct', """
env = Environment()
env.VariantDir('bin', 'src')
o = env.Object('bin/main', 'bin/main.cpp')
env.Program('bin/main', o)
""")

test.run(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
