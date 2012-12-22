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
Verify that setting $PDB to '${TARGET}.pdb allows us to build multiple
programs with separate .pdb files from the same environment.

Under the covers, this verifies that emitters support expansion of the
$TARGET variable (and implicitly $SOURCE), using the original specified
list(s).
"""

import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.skip_if_not_msvc()

test.write('SConstruct', """\
env = Environment(PDB = '${TARGET.base}.pdb')
env.Program('test1.cpp')
env.Program('test2.cpp')
""")

test.write('test1.cpp', """\
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv)
{
    printf("test1.cpp\\n");
    exit (0);
}
""")

test.write('test2.cpp', """\
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv)
{
    printf("test2.cpp\\n");
    exit (0);
}
""")

test.run(arguments = '.')

test.must_exist('test1%s' % _exe)
test.must_exist('test1.pdb')
test.must_exist('test2%s' % _exe)
test.must_exist('test2.pdb')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
