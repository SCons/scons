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
Test behavior of SHCFLAGS.

This is a live test, uses the detected C compiler.
"""

import os
import sys

import TestSCons

test = TestSCons.TestSCons()

e = test.Environment()
fooflags = e['SHCFLAGS'] + ' -DFOO'
barflags = e['SHCFLAGS'] + ' -DBAR'

if os.name == 'posix':
    os.environ['LD_LIBRARY_PATH'] = '.'
if sys.platform.find('irix') > -1:
    os.environ['LD_LIBRARYN32_PATH'] = '.'

test.write('SConstruct', f"""\
DefaultEnvironment(tools=[])
foo = Environment(SHCFLAGS='{fooflags}', WINDOWS_INSERT_DEF=1)
bar = Environment(SHCFLAGS='{barflags}', WINDOWS_INSERT_DEF=1)

foo_obj = foo.SharedObject(target='foo', source='prog.c')
foo.SharedLibrary(target='foo', source=foo_obj)

bar_obj = bar.SharedObject(target='bar', source='prog.c')
bar.SharedLibrary(target='bar', source=bar_obj)

fooMain = foo.Clone(LIBS='foo', LIBPATH='.')
foomain_obj = fooMain.Object(target='foomain', source='main.c')
fooMain.Program(target='fooprog', source=foomain_obj)

barMain = bar.Clone(LIBS='bar', LIBPATH='.')
barmain_obj = barMain.Object(target='barmain', source='main.c')
barMain.Program(target='barprog', source=barmain_obj)
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

test.write('prog.c', r"""
#include <stdio.h>

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

test.run(arguments='.')
test.run(program=test.workpath('fooprog'), stdout="prog.c:  FOO\n")
test.run(program=test.workpath('barprog'), stdout="prog.c:  BAR\n")

test.write('SConstruct', f"""\
DefaultEnvironment(tools=[])
bar = Environment(SHCFLAGS='{barflags}', WINDOWS_INSERT_DEF=1)

foo_obj = bar.SharedObject(target='foo', source='prog.c')
bar.SharedLibrary(target='foo', source=foo_obj)

bar_obj = bar.SharedObject(target='bar', source='prog.c')
bar.SharedLibrary(target='bar', source=bar_obj)

barMain = bar.Clone(LIBS='bar', LIBPATH='.')
foomain_obj = barMain.Object(target='foomain', source='main.c')
barmain_obj = barMain.Object(target='barmain', source='main.c')
barMain.Program(target='barprog', source=foomain_obj)
barMain.Program(target='fooprog', source=barmain_obj)
""")

test.run(arguments='.')
test.run(program=test.workpath('fooprog'), stdout="prog.c:  BAR\n")
test.run(program=test.workpath('barprog'), stdout="prog.c:  BAR\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
