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
Test that the logic that "guesses" the associated VariantDir for a
subdirectory correctly builds targets in the VariantDir subdirectory.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir(['work'], ['work', 'src'])

test.write(['work', 'SConstruct'], """
c_builddir = r'%s'
VariantDir(c_builddir, '.', duplicate=0)
SConscript(c_builddir + '/SConscript')
""" % test.workpath('debug'))

test.write(['work', 'SConscript'], """
SConscript('src/SConscript')
""")

test.write(['work', 'src', 'SConscript'], """
env = Environment(OBJSUFFIX='.obj',
                  PROGSUFFIX='.exe')
env.Program('test.cpp')
""")

test.write(['work', 'src', 'test.cpp'], """\
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[])
{
    printf("work/src/test.cpp\\n");
}
""")

test.run(chdir = 'work', arguments = '.')

test.must_exist(test.workpath('debug', 'src', 'test.obj'))
test.must_exist(test.workpath('debug', 'src', 'test.exe'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
