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
else:
    _exe = ''

test = TestSCons.TestSCons()

test.subdir('sub1', 'sub2')

foo_exe = test.workpath('foo' + _exe)

test.write('SConstruct', """
env = Environment(LIBS=['bar'], LIBPATH = '.')
env.Program(target='foo', source='foo.c')
SConscript('sub1/SConscript', 'env')
SConscript('sub2/SConscript', 'env')
""")

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

test.write('foo.c', r"""
void bar();
void baz();

int main(void)
{
   bar();
   baz();
   return 0;
}
""")

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

test.run(program=foo_exe, stdout='sub1/bar.c\nsub1/baz.c\n')

#
test.write('SConstruct', """
env = Environment()
env.Program(target='foo', source='foo.c', LIBS=['baz', 'bar'], LIBPATH = '.')
SConscript('sub1/SConscript', 'env')
SConscript('sub2/SConscript', 'env')
""")

test.run(arguments = '.')

test.run(program=foo_exe, stdout='sub1/bar.c\nsub2/baz.c\n')

#
test.write('SConstruct', """
env = Environment(LIBS=['bar', 'baz'], LIBPATH = '.')
env.Program(target='foo', source='foo.c')
SConscript('sub1/SConscript', 'env')
SConscript('sub2/SConscript', 'env')
""")

test.run(arguments = '.', stderr=None)

# on IRIX, ld32 prints out a warning saying that libbaz.a isn't used
sw = 'ld32: WARNING 84 : ./libbaz.a is not used for resolving any symbol.\n'
test.fail_test(not test.stderr() in ['', sw])

test.run(program=foo_exe, stdout='sub1/bar.c\nsub1/baz.c\n')

#
test.write('SConstruct', """
env = Environment()
env.Program(target='foo', source='foo.c', LIBS=['bar', 'baz'], LIBPATH = '.')
SConscript('sub1/SConscript', 'env')
SConscript('sub2/SConscript', 'env')
""")

test.run(arguments = '.')

test.run(program=foo_exe, stdout='sub1/bar.c\nsub1/baz.c\n')

test.write(['sub1', 'baz.c'], r"""
#include <stdio.h>

void baz()
{
   printf("sub1/baz.c 2\n");
}
""")

test.run(arguments = '.', stderr=None)
test.fail_test(not test.stderr() in ['', sw])

test.run(program=foo_exe, stdout='sub1/bar.c\nsub1/baz.c 2\n')

test.pass_test()
