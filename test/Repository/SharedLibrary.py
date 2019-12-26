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
Verify that we can create a local shared library containing shared
object files built in a repository.
"""

import os
import sys

import TestSCons

test = TestSCons.TestSCons()

#
test.subdir('repository', 'work')

#
opts = '-Y ' + test.workpath('repository')

#
test.write(['repository', 'SConstruct'], """\
env = Environment()
f1 = env.SharedObject('f1.c')
f2 = env.SharedObject('f2.c')
f3 = env.SharedObject('f3.c')
if ARGUMENTS.get('PROGRAM'):
    lib = env.SharedLibrary(target = 'foo',
                            source = f1 + f2 + f3,
                            WINDOWS_INSERT_DEF = 1)
    env.Program(target='prog', source='prog.c', LIBS='foo', LIBPATH=['.'])
""")

for fx in ['1', '2', '3']:
    test.write(['repository', 'f%s.c' % fx], r"""
#include <stdio.h>

void
f%s(void)
{
        printf("f%s.c\n");
        fflush(stdout);
}
""" % (fx,fx))

test.write(['repository', "foo.def"], r"""
LIBRARY        "foo"
DESCRIPTION    "Foo Shared Library"

EXPORTS
   f1
   f2
   f3
""")

test.write(['repository', 'prog.c'], r"""
#include <stdio.h>
void f1(void);
void f2(void);
void f3(void);
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        f1();
        f2();
        f3();
        printf("prog.c\n");
        return 0;
}
""")

# Build the relocatable objects within the repository
test.run(chdir = 'repository', arguments = '.')

# Make the repository non-writable,
# so we'll detect if we try to write into it accidentally.
test.writable('repository', 0)

# Build the library and the program within the work area
test.run(chdir='work',
         options=opts,
         arguments='PROGRAM=1',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

# Run the program and verify that the library worked
if os.name == 'posix':
    if sys.platform[:6] == 'darwin':
        os.environ['DYLD_LIBRARY_PATH'] = test.workpath('work')
    else:
        os.environ['LD_LIBRARY_PATH'] = test.workpath('work')
if sys.platform.find('irix') != -1:
    os.environ['LD_LIBRARYN32_PATH'] = test.workpath('work')

test.run(program = test.workpath('work', 'prog'),
         stdout = "f1.c\nf2.c\nf3.c\nprog.c\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
