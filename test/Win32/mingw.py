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
This tests the MinGW C/C++ compiler support.
This test requires MinGW to be installed.
"""

import os
import sys

import TestSCons
import TestCmd

test = TestSCons.TestSCons(match = TestCmd.match_re_dotall)

# MinGW is Windows only:
if sys.platform != 'win32':
    msg = "Skipping mingw test on non-Windows platform '%s'\n" % sys.platform
    test.skip_test(msg)

test.write('SConstruct',"""
import sys
from SCons.Tool.mingw import exists

DefaultEnvironment(tools=[])
env = Environment()
if exists(env):
    print('mingw exists')
sys.exit(0)
""")

test.run()
if 'mingw exists' not in test.stdout():
    test.skip_test("No MinGW on this system, skipping test.\n")

test.subdir('header')

# Do the actual testing:
test.write('SConstruct',"""
DefaultEnvironment(tools=[])
env = Environment(tools=['mingw'])
assert env['CC'] == 'gcc'
env.StaticLibrary('static', 'static.cpp')
env.SharedLibrary('shared', 'shared.cpp')
env.SharedLibrary('cshared', ['cshared.c', 'cshared.def'], WINDOWS_INSERT_DEF=1)
env.Program(
    'test',
    ['test.cpp', env.RES('resource.rc', CPPPATH=['header'])],
    LIBS=['static', 'shared', 'cshared'],
    LIBPATH=['.'],
)
""")

test.write('test.cpp', '''
#include <stdio.h>
#include <windows.h>
#include "resource.h"

void shared_func(void);
void static_func(void);
extern "C" void cshared_func(void);

int main(void)
{
    printf("%s\\n", "test.cpp");
    shared_func();
    static_func();
    cshared_func();

    char test[1024];
    LoadString(GetModuleHandle(NULL), IDS_TEST, test, sizeof(test));
    printf("%d %s\\n", IDS_TEST, test);

    return 0;
}
''')

test.write('resource.rc', '''
#include "resource.h"
#include <resource2.h>

STRINGTABLE DISCARDABLE
BEGIN
    IDS_TEST RESOURCE_RC
END
''')

test.write('resource.h', '''
#define IDS_TEST 2001
''')

test.write('static.cpp', '''
#include <stdio.h>

void static_func(void)
{
    printf("%s\\n", "static.cpp");
}
''')

test.write('shared.cpp', '''
#include <stdio.h>

void shared_func(void)
{
    printf("%s\\n", "shared.cpp");
}
''')

test.write('cshared.c', '''
#include <stdio.h>

void cshared_func(void)
{
    printf("%s\\n", "cshared.c");
}
''')

test.write('cshared.def', '''
EXPORTS
cshared_func
''')



test.write('header/resource2.h', '''
#define RESOURCE_RC "resource.rc"
''')

# the mingw linker likes to print "Creating library file: libfoo.a" to stderr, but
# we'd like for this test to pass once this bug is fixed, so match anything at all
# that comes out of stderr:
test.run(arguments='test.exe', stderr='.*')
# ensure the source def for cshared.def got used, and there wasn't a target def for chshared.dll:
test.fail_test('cshared.def' not in test.stdout())
test.fail_test('-Wl,--output-def,cshared.def' in test.stdout())
# ensure the target def got generated for the shared.dll:
test.fail_test(not os.path.exists(test.workpath('cshared.def')))
test.fail_test(os.path.exists(test.workpath('shared.def')))
test.run(program=test.workpath('test.exe'), stdout='test.cpp\nshared.cpp\nstatic.cpp\ncshared.c\n2001 resource.rc\n')

# ensure that modifying the header causes the resource to be rebuilt:
test.write('resource.h', '''
#define IDS_TEST 2002
''')
test.run(arguments='test.exe', stderr='.*')
test.run(program=test.workpath('test.exe'), stdout='test.cpp\nshared.cpp\nstatic.cpp\ncshared.c\n2002 resource.rc\n')

# Test with specifying the default tool to make sure msvc setting doen't ruin it
# for mingw:
test.write('SConstruct',"""
env=Environment(tools=['default', 'mingw'])
assert env['CC'] == 'gcc'
env.SharedLibrary('shared', 'shared.cpp')
env.Program('test', 'test.cpp', LIBS=['static', 'shared', 'cshared'], LIBPATH=['.'])
""")

test.write('test.cpp', '''
#include <stdio.h>

void shared_func(void);

int main(void)
{
    printf("%s\\n", "test.cpp2");
    shared_func();
    return 0;
}
''')

test.write('shared.cpp', '''
#include <stdio.h>

void shared_func(void)
{
    printf("%s\\n", "shared.cpp2");
}
''')

# the mingw linker likes to print "Creating library file: libfoo.a" to stderr, but
# we'd like for this test to pass once this bug is fixed, so match anything at all
# that comes out of stderr:
test.run(arguments='test.exe', stderr='.*')
test.run(program=test.workpath('test.exe'), stdout='test.cpp2\nshared.cpp2\n')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
