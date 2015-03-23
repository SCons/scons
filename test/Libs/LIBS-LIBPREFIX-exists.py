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
Verify that we don't add $LIBPREFIX to library names in $LIBS that
already have the prefix on them.
"""

import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

blender_exe = test.workpath('blender' + _exe)

test.subdir('src', ['src', 'component1'], ['src', 'component2'])

test.write('SConstruct', """\
SConscript(['src/SConscript'])

libpath = (['lib'])
libraries = (['libtest_component2',
              'libtest_component1'])

# To remove the dependency problem, you should rename blender to mlender.
Program(source='main.c',
        target='blender',
        LIBS=libraries,
        LIBPREFIX='lib',
        LIBPATH=libpath,
        CPPPATH=['src/component2'])
""")

test.write('main.c', """\
#include <stdlib.h>
#include "message2.h"

int main (void)
{
    DisplayMessage2();
    exit (0);
}
""")

test.write(['src', 'SConscript'], """\
SConscript(['component1/SConscript',
            'component2/SConscript'])
""")

test.write(['src', 'component1', 'SConscript'], """\
source_files = ['message1.c']
Library(target='../../lib/libtest_component1',
        source=source_files,
        LINKFLAGS='')
""")

test.write(['src', 'component1', 'message1.c'], """\
#include <stdio.h>

void DisplayMessage1 (void)
{
    printf ("src/component1/message.c\\n");
}
""")

test.write(['src', 'component1', 'message1.h'], """\
void DisplayMessage1 (void);
""")

test.write(['src', 'component2', 'SConscript'], """\
source_files = ['message2.c']
include_paths = ['../component1']
Library(target='../../lib/libtest_component2',
        source=source_files,
        CPPPATH=include_paths)
""")

test.write(['src', 'component2', 'message2.h'], """\
void DisplayMessage2 (void);
""")

test.write(['src', 'component2', 'message2.c'], """\
#include <stdio.h>
#include "message1.h"

void DisplayMessage2 (void)
{
    DisplayMessage1();
    printf ("src/component2/hello.c\\n");
}
""")

test.run(arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

test.run(program=blender_exe,
         stdout='src/component1/message.c\nsrc/component2/hello.c\n')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
