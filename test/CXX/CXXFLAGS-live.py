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
Verify that $CXXFLAGS settings are used to build both static
and shared object files.

This is a live test, uses the detected C++ compiler.
"""

import os
import sys

import TestSCons

test = TestSCons.TestSCons()

if os.name == 'posix':
    os.environ['LD_LIBRARY_PATH'] = '.'
if 'irix' in sys.platform:
    os.environ['LD_LIBRARYN32_PATH'] = '.'

e = test.Environment()

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
foo = Environment(WINDOWS_INSERT_DEF=1)
foo.Append(CXXFLAGS='-DFOO')
bar = Environment(WINDOWS_INSERT_DEF=1)
bar.Append(CXXFLAGS='-DBAR')

foo_obj = foo.SharedObject(target='fooshared', source='doIt.cpp')
bar_obj = bar.SharedObject(target='barshared', source='doIt.cpp')
foo.SharedLibrary(target='foo', source=foo_obj)
bar.SharedLibrary(target='bar', source=bar_obj)

fooMain = foo.Clone(LIBS='foo', LIBPATH='.')
foo_obj = fooMain.Object(target='foomain', source='main.c')
fooMain.Program(target='fooprog', source=foo_obj)

barMain = bar.Clone(LIBS='bar', LIBPATH='.')
bar_obj = barMain.Object(target='barmain', source='main.c')
barMain.Program(target='barprog', source=bar_obj)

foo_obj = foo.Object(target='foostatic', source='prog.cpp')
bar_obj = bar.Object(target='barstatic', source='prog.cpp')
foo.Program(target='foo', source=foo_obj)
bar.Program(target='bar', source=bar_obj)
""")

test.write('foo.def', r"""
LIBRARY        "foo"
DESCRIPTION    "Foo Shared Library"

EXPORTS
   doIt
""")

test.write('bar.def', r"""
LIBRARY        "bar"
DESCRIPTION    "Bar Shared Library"

EXPORTS
   doIt
""")

test.write('doIt.cpp', r"""
#include <stdio.h>

extern "C" void
doIt()
{
#ifdef FOO
        printf("doIt.cpp:  FOO\n");
#endif
#ifdef BAR
        printf("doIt.cpp:  BAR\n");
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

test.write('prog.cpp', r"""
#include <stdio.h>
#include <stdlib.h>

int
main(int argc, char *argv[])
{
        argv[argc++] = (char *)"--";
#ifdef FOO
        printf("prog.c:  FOO\n");
#endif
#ifdef BAR
        printf("prog.c:  BAR\n");
#endif
        exit (0);
}
""")

test.run(arguments='.')

test.run(program=test.workpath('fooprog'), stdout="doIt.cpp:  FOO\n")
test.run(program=test.workpath('barprog'), stdout="doIt.cpp:  BAR\n")
test.run(program=test.workpath('foo'), stdout="prog.c:  FOO\n")
test.run(program=test.workpath('bar'), stdout="prog.c:  BAR\n")

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
bar = Environment(WINDOWS_INSERT_DEF=1)
bar.Append(CXXFLAGS='-DBAR')

foo_obj = bar.SharedObject(target='foo', source='doIt.cpp')
bar_obj = bar.SharedObject(target='bar', source='doIt.cpp')
bar.SharedLibrary(target='foo', source=foo_obj)
bar.SharedLibrary(target='bar', source=bar_obj)

barMain = bar.Clone(LIBS='bar', LIBPATH='.')
foo_obj = barMain.Object(target='foomain', source='main.c')
bar_obj = barMain.Object(target='barmain', source='main.c')
barMain.Program(target='barprog', source=foo_obj)
barMain.Program(target='fooprog', source=bar_obj)
""")

test.run(arguments='.')
test.run(program=test.workpath('fooprog'), stdout="doIt.cpp:  BAR\n")
test.run(program=test.workpath('barprog'), stdout="doIt.cpp:  BAR\n")

test.pass_test()
