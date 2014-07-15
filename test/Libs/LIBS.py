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
    import SCons.Tool.MSCommon as msc
    if not msc.msvc_exists():
        bar_lib = 'libbar.a'
else:
    _exe = ''
    bar_lib = 'libbar.a'

test = TestSCons.TestSCons()

test.subdir('sub1', 'sub2')

foo1_exe = test.workpath('foo1' + _exe)
foo2_exe = test.workpath('foo2' + _exe)
foo3_exe = test.workpath('foo3' + _exe)
foo4_exe = test.workpath('foo4' + _exe)
foo5_exe = test.workpath('foo5' + _exe)
slprog_exe = test.workpath('slprog' + _exe)

test.write('SConstruct', """
env = Environment(LIBS=['bar'], LIBPATH = '.')
env.Program(target='foo1', source='foo1.c')
env2 = Environment(LIBS=[File(r'%s')], LIBPATH = '.')
env2.Program(target='foo2', source='foo2.c')
env3 = Environment(LIBS='bar', LIBPATH = '.')
env3.Program(target='foo3', source='foo3.c')
env4 = Environment(LIBS=File(r'%s'), LIBPATH = '.')
env4.Program(target='foo4', source='foo4.c')
env5 = Environment(LIBS=['bar', '$UNSPECIFIED'], LIBPATH = '.')
env5.Program(target='foo5', source='foo5.c')
sl = env.StaticLibrary('sl.c')
env.Program(target='slprog.c', LIBS=[sl])
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
test.write('foo5.c', foo_contents)

test.write('sl.c', """\
#include <stdio.h>
void
sl(void)
{
        printf("sl.c\\n");
}
""")

test.write('slprog.c', """\
#include <stdio.h>
int
main(int argc, char *argv[])
{
        sl();
        printf("slprog.c\\n");
        exit (0);
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

# ar sometimes produces a "warning" on stderr -- ar: creating sub1/libbar.a
test.run(arguments = '.', stderr=None)

test.run(program=foo1_exe, stdout='sub1/bar.c\nsub1/baz.c\n')
test.run(program=foo2_exe, stdout='sub1/bar.c\nsub1/baz.c\n')
test.run(program=foo3_exe, stdout='sub1/bar.c\nsub1/baz.c\n')
test.run(program=foo4_exe, stdout='sub1/bar.c\nsub1/baz.c\n')
test.run(program=foo5_exe, stdout='sub1/bar.c\nsub1/baz.c\n')
test.run(program=slprog_exe, stdout='sl.c\nslprog.c\n')

#
test.write('SConstruct', """
env = Environment(LIBS=['baz'])
env.Program(target='foo1', source='foo1.c', LIBS=['$LIBS', 'bar'], LIBPATH = '.')
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


# on IRIX, ld32 prints out a warning saying that libbaz.a isn't used
sw = 'ld32: WARNING 84 : ./libbaz.a is not used for resolving any symbol.\n'
test.run(arguments = '.',
         stderr='(%s|%s'%(sw, TestSCons.noisy_ar[1:]),
         match=TestSCons.match_re_dotall)
#test.fail_test(not test.stderr() in ['', sw])

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

test.run(arguments = '.',
         stderr='(%s|%s'%(sw, TestSCons.noisy_ar[1:]),
         match=TestSCons.match_re_dotall)
#test.fail_test(not test.stderr() in ['', sw, TestSCons.noisy_ar])

test.run(program=foo1_exe, stdout='sub1/bar.c\nsub1/baz.c 2\n')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
