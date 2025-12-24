#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

"""
Verify that $SHCXXFLAGS settings are used to build shared object files.

This is a live test, uses the detected C and C++ compilers.
"""

import os
import sys

import TestSCons

test = TestSCons.TestSCons()

e = test.Environment()
fooflags = e['SHCXXFLAGS'] + ' -DFOO'
barflags = e['SHCXXFLAGS'] + ' -DBAR'

if os.name == 'posix':
    os.environ['LD_LIBRARY_PATH'] = '.'
if 'irix' in sys.platform:
    os.environ['LD_LIBRARYN32_PATH'] = '.'

test.write('SConstruct', f"""\
DefaultEnvironment(tools=[])
foo = Environment(SHCXXFLAGS='{fooflags}', WINDOWS_INSERT_DEF=1)
bar = Environment(SHCXXFLAGS='{barflags}', WINDOWS_INSERT_DEF=1)

foo_obj = foo.SharedObject(target='foo', source='prog.cpp')
foo.SharedLibrary(target='foo', source=foo_obj)

bar_obj = bar.SharedObject(target='bar', source='prog.cpp')
bar.SharedLibrary(target='bar', source=bar_obj)

fooMain = foo.Clone(LIBS='foo', LIBPATH='.')
foo_obj = fooMain.Object(target='foomain', source='main.c')
fooMain.Program(target='fooprog', source=foo_obj)

barMain = bar.Clone(LIBS='bar', LIBPATH='.')
barmain_obj = barMain.Object(target='barmain', source='main.c')
barMain.Program(target='barprog', source=barmain_obj)
""")

test.write('foo.def', """\
LIBRARY        "foo"
DESCRIPTION    "Foo Shared Library"

EXPORTS
   doIt
""")

test.write('bar.def', """\
LIBRARY        "bar"
DESCRIPTION    "Bar Shared Library"

EXPORTS
   doIt
""")

test.write('prog.cpp', r"""
#include <stdio.h>

extern "C" void
doIt()
{
#ifdef FOO
        printf("prog.cpp:  FOO\n");
#endif
#ifdef BAR
        printf("prog.cpp:  BAR\n");
#endif
}
""")

test.write('main.c', """\

void doIt();

int
main(int argc, char* argv[])
{
    doIt();
    return 0;
}
""")

test.run(arguments='.')
test.run(program=test.workpath('fooprog'), stdout="prog.cpp:  FOO\n")
test.run(program=test.workpath('barprog'), stdout="prog.cpp:  BAR\n")

test.write('SConstruct', f"""\
DefaultEnvironment(tools=[])
bar = Environment(SHCXXFLAGS='{barflags}', WINDOWS_INSERT_DEF=1)

foo_obj = bar.SharedObject(target='foo', source='prog.cpp')
bar.SharedLibrary(target='foo', source=foo_obj)

bar_obj = bar.SharedObject(target='bar', source='prog.cpp')
bar.SharedLibrary(target='bar', source=bar_obj)

barMain = bar.Clone(LIBS='bar', LIBPATH='.')
foomain_obj = barMain.Object(target='foomain', source='main.c')
barmain_obj = barMain.Object(target='barmain', source='main.c')
barMain.Program(target='barprog', source=foomain_obj)
barMain.Program(target='fooprog', source=barmain_obj)
""")

test.run(arguments='.')
test.run(program=test.workpath('fooprog'), stdout="prog.cpp:  BAR\n")
test.run(program=test.workpath('barprog'), stdout="prog.cpp:  BAR\n")

test.pass_test()
