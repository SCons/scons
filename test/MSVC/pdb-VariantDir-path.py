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
Verify that .pdb files get put in a variant_dir correctly.
"""

import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.skip_if_not_msvc()

test.subdir('src')

test.write('SConstruct', """\
env = Environment()
env.Append(BINDIR = '#bin')

Export('env')
SConscript('#src/SConscript', duplicate = 0, variant_dir = '#.build')
""")

test.write(['src', 'SConscript'], """\
Import('env')
env['PDB'] = '${TARGET}.pdb'
p = env.Program('test.exe', 'test.cpp')
env.Install(env['BINDIR'], p)
""")

test.write(['src', 'test.cpp'], """\
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv)
{
    printf("test.cpp\\n");
    exit (0);
}
""")

test.run(arguments = '.')

test.must_exist(['.build', 'test%s'     % _exe])
test.must_exist(['.build', 'test%s.pdb' % _exe])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
