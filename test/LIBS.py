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

import TestSCons
import sys

if sys.platform == 'win32':
    _exe = '.exe'
    bar_lib = 'bar.lib'
else:
    _exe = ''
    bar_lib = 'libbar.a'

test = TestSCons.TestSCons()

test.subdir('sub1', 'sub2')

foo1_exe = test.workpath('foo1' + _exe)
foo2_exe = test.workpath('foo2' + _exe)
foo3_exe = test.workpath('foo3' + _exe)
foo4_exe = test.workpath('foo4' + _exe)

test.write('SConstruct', """
env = Environment(LIBS=['bar'], LIBPATH = '.')
env.Program(target='foo1', source='foo1.c')
env2 = Environment(LIBS=[File(r'%s')], LIBPATH = '.')
env2.Program(target='foo2', source='foo2.c')
env3 = Environment(LIBS='bar', LIBPATH = '.')
env3.Program(target='foo3', source='foo3.c')
env4 = Environment(LIBS=File(r'%s'), LIBPATH = '.')
env4.Program(target='foo4', source='foo4.c')
SConscript('sub1/SConscript', 'env')
SConscript('sub2/SConscript', 'env')
""" % (bar_lib, bar_lib))

test.write(['sub1', 'SConscript'], r"""
Import('env')
lib = env.Library(target='bar', source=Split('bar.c baz.c'))
env.Install('..', lib)
""")

test.write(['sub2', 'SConscript'], r"""
Import('env')
lib = env.Library(target='baz', source='baz.c')
env.Install('..', lib)
""")

foo_contents =  r"""
void bar();
void baz();

int main(void)
{
   bar();
   baz();
   return 0;
}
"""

test.write('foo1.c', foo_contents)
test.write('foo2.c', foo_contents)
test.write('foo3.c', foo_contents)
test.write('foo4.c', foo_contents)

test.write(['sub1', 'bar.c'], r"""
#include <stdio.h>

void bar()
{
   printf("sub1/bar.c\n");
}
""")

test.write(['sub1', 'baz.c'], r"""
#include <stdio.h>

void baz()
{
   printf("sub1/baz.c\n");
}
""")

test.write(['sub2', 'baz.c'], r"""
#include <stdio.h>

void baz()
{
   printf("sub2/baz.c\n");
}
""")

test.run(arguments = '.')

test.run(program=foo1_exe, stdout='sub1/bar.c\nsub1/baz.c\n')
test.run(program=foo2_exe, stdout='sub1/bar.c\nsub1/baz.c\n')
test.run(program=foo3_exe, stdout='sub1/bar.c\nsub1/baz.c\n')
test.run(program=foo4_exe, stdout='sub1/bar.c\nsub1/baz.c\n')

#
test.write('SConstruct', """
env = Environment()
env.Program(target='foo1', source='foo1.c', LIBS=['baz', 'bar'], LIBPATH = '.')
SConscript('sub1/SConscript', 'env')
SConscript('sub2/SConscript', 'env')
""")

test.run(arguments = '.')

test.run(program=foo1_exe, stdout='sub1/bar.c\nsub2/baz.c\n')

#
test.write('SConstruct', """
env = Environment(LIBS=['bar', 'baz'], LIBPATH = '.')
env.Program(target='foo1', source='foo1.c')
SConscript('sub1/SConscript', 'env')
SConscript('sub2/SConscript', 'env')
""")

test.run(arguments = '.', stderr=None)

# on IRIX, ld32 prints out a warning saying that libbaz.a isn't used
sw = 'ld32: WARNING 84 : ./libbaz.a is not used for resolving any symbol.\n'
test.fail_test(not test.stderr() in ['', sw])

test.run(program=foo1_exe, stdout='sub1/bar.c\nsub1/baz.c\n')

#
test.write('SConstruct', """
env = Environment()
env.Program(target='foo1', source='foo1.c', LIBS=['bar', 'baz'], LIBPATH = '.')
SConscript('sub1/SConscript', 'env')
SConscript('sub2/SConscript', 'env')
""")

test.run(arguments = '.')

test.run(program=foo1_exe, stdout='sub1/bar.c\nsub1/baz.c\n')

test.write(['sub1', 'baz.c'], r"""
#include <stdio.h>

void baz()
{
   printf("sub1/baz.c 2\n");
}
""")

test.run(arguments = '.', stderr=None)
test.fail_test(not test.stderr() in ['', sw])

test.run(program=foo1_exe, stdout='sub1/bar.c\nsub1/baz.c 2\n')

# Make sure we don't add $LIBPREFIX to library names that
# already have the prefix on them.
blender_exe = test.workpath('blender' + _exe)

test.subdir('src', ['src', 'component1'], ['src', 'component2'])

test.write('SConstruct', """\
SConscript(['src/SConscript'])

libpath = (['lib'])
libraries = (['libtest_component2',
              'libtest_component1'])

# To remove the dependency problem, you should rename blender to mlender.
Program (source='', target='blender', LIBS=libraries, LIBPREFIX='lib', LIBPATH=libpath)
""")

test.write(['src', 'SConscript'], """\
SConscript(['component1/SConscript',
            'component2/SConscript'])
""")

test.write(['src', 'component1', 'SConscript'], """\
source_files = ['message.c']
Library (target='../../lib/libtest_component1', source=source_files)
""")

test.write(['src', 'component1', 'message.c'], """\
#include <stdio.h>

void DisplayMessage (void)
{
    printf ("src/component1/message.c\\n");
}
""")

test.write(['src', 'component1', 'message.h'], """\
void DisplayMessage (void);
""")

test.write(['src', 'component2', 'SConscript'], """\
source_files = ['hello.c']
include_paths = ['../component1']
Library (target='../../lib/libtest_component2', source=source_files, CPPPATH=include_paths)
""")

test.write(['src', 'component2', 'hello.c'], """\
#include <stdio.h>
#include "message.h"

int main (void)
{
    DisplayMessage();
    printf ("src/component2/hello.c\\n");
    exit (0);
}
""")

test.run(arguments = '.')

test.run(program=blender_exe,
         stdout='src/component1/message.c\nsrc/component2/hello.c\n')

test.pass_test()
