#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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

import sys
import TestSCons
import os

if sys.platform == 'win32':
    _obj = '.obj'
    fooflags = '/nologo -DFOO'
    barflags = '/nologo -DBAR'
else:
    _obj = '.o'
    fooflags = '-DFOO'
    barflags = '-DBAR'
    
if os.name == 'posix':
    os.environ['LD_LIBRARY_PATH'] = '.'

test = TestSCons.TestSCons()

test.write('SConstruct', """
foo = Environment(SHCCFLAGS = '%s', WIN32_INSERT_DEF=1)
bar = Environment(SHCCFLAGS = '%s', WIN32_INSERT_DEF=1)
foo.SharedObject(target = 'foo%s', source = 'prog.c')
bar.SharedObject(target = 'bar%s', source = 'prog.c')
foo.SharedLibrary(target = 'foo', source = 'foo%s')
bar.SharedLibrary(target = 'bar', source = 'bar%s')

fooMain = foo.Copy(LIBS='foo', LIBPATH='.')
foo_obj = fooMain.Object(target='foomain', source='main.c')
fooMain.Program(target='fooprog', source=foo_obj)

barMain = bar.Copy(LIBS='bar', LIBPATH='.')
bar_obj = barMain.Object(target='barmain', source='main.c')
barMain.Program(target='barprog', source=bar_obj)
""" % (fooflags, barflags, _obj, _obj, _obj, _obj))

test.write('foo.def', r"""
LIBRARY        "foo"
DESCRIPTION    "Foo Shared Library"

EXPORTS
   doIt
""")

test.write('bar.def', r"""
LIBRARY        "foo"
DESCRIPTION    "Foo Shared Library"

EXPORTS
   doIt
""")

test.write('prog.c', r"""
void
doIt()
{
#ifdef FOO
	printf("prog.c:  FOO\n");
#endif
#ifdef BAR
	printf("prog.c:  BAR\n");
#endif
}
""")

test.write('main.c', r"""

void doIt();

int
main(int argc, char* argv[])
{
    doIt();
    return 0;
}
""")

test.run(arguments = '.')

test.run(program = test.workpath('fooprog'), stdout = "prog.c:  FOO\n")
test.run(program = test.workpath('barprog'), stdout = "prog.c:  BAR\n")

test.write('SConstruct', """
bar = Environment(SHCCFLAGS = '%s', WIN32_INSERT_DEF=1)
bar.SharedObject(target = 'foo%s', source = 'prog.c')
bar.SharedObject(target = 'bar%s', source = 'prog.c')
bar.SharedLibrary(target = 'foo', source = 'foo%s')
bar.SharedLibrary(target = 'bar', source = 'bar%s')

barMain = bar.Copy(LIBS='bar', LIBPATH='.')
foo_obj = barMain.Object(target='foomain', source='main.c')
bar_obj = barMain.Object(target='barmain', source='main.c')
barMain.Program(target='barprog', source=foo_obj)
barMain.Program(target='fooprog', source=bar_obj)
""" % (barflags, _obj, _obj, _obj, _obj))

test.run(arguments = '.')

test.run(program = test.workpath('fooprog'), stdout = "prog.c:  BAR\n")
test.run(program = test.workpath('barprog'), stdout = "prog.c:  BAR\n")

test.pass_test()
