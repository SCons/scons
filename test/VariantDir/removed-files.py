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
Test VariantDir handling of removal of source files.

A C++ Program is created and compiled. First, a header is missing. Then
the header is added and the compilation should succeed, then the header
is removed and the compilation should fail again.

Previous versions of SCons did not remove the header from the build
directory after the source directory's header was removed, which caused
the compilation to succeed even after the source file was removed.

Test case supplied by Patrick Mezard--many thanks.
"""

import TestSCons

test = TestSCons.TestSCons()

#-------------------------------------------------------------------------------
#1- Create dep.cpp and the SConstruct. dep.h is missing and the build is
#expected to fail with 2.
#-------------------------------------------------------------------------------

test.subdir('src')

test.write(['src', 'dep.cpp'], """\
#include "dep.h"

int main(int argc, char* argv[])
{
        return test_dep();
}
""")

test.write('SConstruct', """
env = Environment()
env.VariantDir('bin', 'src')
o = env.Object('bin/dep', 'bin/dep.cpp')
env.Program('bin/dep', o)
""")

test.run(arguments = '.', stderr=None, status=2)


#-------------------------------------------------------------------------------
#2- Add dep.h and check the build is OK.
#-------------------------------------------------------------------------------

test.write(['src', 'dep.h'], """\
#ifndef DEP_H
#define DEP_H

inline int test_dep()
{
        return 1;
}

#endif //DEP_H
""")

test.run(arguments = '.')


#-------------------------------------------------------------------------------
#3- Remove dep.h. The build is expected to fail again like in [1].
#-------------------------------------------------------------------------------

test.unlink(['src', 'dep.h'])

test.run(arguments = '.', stderr=None, status=2)


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
