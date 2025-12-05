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
Verify that manifest files get embedded correctly in EXEs and DLLs
"""

import TestSCons

_exe = TestSCons._exe
_dll = TestSCons._dll
_lib = TestSCons._lib

test = TestSCons.TestSCons()

test.skip_if_not_msvc()

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = Environment(WINDOWS_EMBED_MANIFEST=True)
env.Append(CCFLAGS='/MD')
env.Append(LINKFLAGS='/MANIFEST')
env.Append(SHLINKFLAGS='/MANIFEST')
exe = env.Program('test.cpp')
dll = env.SharedLibrary('testdll.cpp')
env.Command(
    'exe-extracted.manifest',
    exe,
    '$MT /nologo -inputresource:${SOURCE};1 -out:${TARGET}',
)
env.Command(
    'dll-extracted.manifest',
    dll,
    '$MT /nologo -inputresource:${SOURCE};2 -out:${TARGET}',
)
env2 = Environment(WINDOWS_EMBED_MANIFEST=True)  # no /MD here
env2.Program('test-nomanifest', env2.Object('test-nomanifest', 'test.cpp'))
""")

test.write('test.cpp', """\
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv)
{
    printf("test.cpp\\n");
    exit (0);
}
""")

test.write('testdll.cpp', """\
#include <stdio.h>
#include <stdlib.h>

__declspec(dllexport) int
testdll(int argc, char *argv)
{
    printf("testdll.cpp\\n");
    return 0;
}
""")

test.run(arguments='.')

test.must_exist('test%s' % _exe)
test.must_exist('test%s.manifest' % _exe)
test.must_contain('exe-extracted.manifest', '</assembly>', mode='r')
test.must_exist('testdll%s' % _dll)
test.must_exist('testdll%s.manifest' % _dll)
test.must_contain('dll-extracted.manifest', '</assembly>', mode='r')

test.pass_test()
