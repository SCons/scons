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

import os
import os.path
import string
import sys
import TestSCons

test = TestSCons.TestSCons()

if sys.platform in ['win32', 'cygwin']:
    lib_static_lib = 'static.lib'
    lib_shared_dll ='shared.dll'
    arflag_init = '/LIBPATH:' + test.workpath()
    arflag = ' /LIBPATH:' + test.workpath()
    linkflag_init = '/LIBPATH:' + test.workpath()
    linkflag = ' /LIBPATH:' + test.workpath()
else:
    lib_shared_dll = 'libshared.so'
    lib_static_lib = 'libstatic.a'
    arflag_init = 'r'
    arflag = 'o'
    linkflag_init = '-L' + test.workpath()
    linkflag = ' -L' + test.workpath()

test.write('SConstruct', """
arflags = r'%s'
while len(arflags) <= 8100:
    arflags = arflags + r'%s'

linkflags = r'%s'
while len(linkflags) <= 8100:
    linkflags = linkflags + r'%s'

env = Environment(ARFLAGS = '$ARXXX', ARXXX = arflags,
                  LINKFLAGS = '$LINKXXX', LINKXXX = linkflags)
env.Program(target = 'foo', source = 'foo.c')

env.StaticLibrary(target = 'static', source = 'static.c')
# SharedLibrary() uses $LINKFLAGS by default.
env.SharedLibrary(target = 'shared', source = 'shared.c', no_import_lib=1)
""" % (arflag_init, arflag, linkflag_init, linkflag))

test.write('foo.c', r"""
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("foo.c\n");
	exit (0);
}
""")

test.write('static.c', r"""
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("static.c\n");
	exit (0);
}
""")

test.write('shared.c', r"""
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("shared.c\n");
	exit (0);
}
""")


test.run(arguments = '.')

test.up_to_date(arguments = '.')

test.run(program = test.workpath('foo'), stdout = "foo.c\n")

test.fail_test(not os.path.exists(lib_static_lib))

test.fail_test(not os.path.exists(lib_shared_dll))

test.pass_test()
