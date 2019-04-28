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
Test that dependencies in generated header files get re-scanned correctly
and that generated header files don't cause circular dependencies.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
def writeFile(target, contents):
    with open(str(target[0]), 'w') as f:
        f.write(contents)
    return 0

env = Environment()
libgen = env.StaticLibrary('gen', 'gen.cpp')
Default(libgen)
env.Command('gen2.h', [],
            lambda env,target,source: writeFile(target, 'int foo = 3;\\n'))
env.Command('gen.h', [],
            lambda env,target,source: writeFile(target, '#include "gen2.h"\\n'))
env.Command('gen.cpp', [],
            lambda env,target,source: writeFile(target, '#include "gen.h"\\n'))
""")

test.run(stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

test.up_to_date(arguments = '.')

test.write('SConstruct', """\
env = Environment()

def gen_a_h(target, source, env):
    with open(str(target[0]), 'w') as t, open(str(source[0]), 'r') as s:
        s.readline()
        t.write(s.readline()[:-1] + ';\\n')

MakeHeader = Builder(action = gen_a_h)
env_no_scan = env.Clone(SCANNERS=[], BUILDERS={'MakeHeader' : MakeHeader})
env_no_scan.MakeHeader('a.h', 'a.c')

env.StaticObject('a.c')
""")

test.write('a.c', """\
#include "a.h"
void a(void)
{
        ;
}
""")

test.run()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
