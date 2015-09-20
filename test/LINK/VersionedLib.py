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
import sys
import TestSCons

import SCons.Platform

_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.write('SConstruct', """\
import os
env = Environment()
objs = env.SharedObject('test.c')
mylib = env.SharedLibrary('test', objs, SHLIBVERSION = '2.5.4')
env.Program('testapp1.c', LIBS = mylib, LIBPATH='.')
env.Program('testapp2.c', LIBS = ['test'], LIBPATH='.')
instnode = env.InstallVersionedLib("#/installtest",mylib)
env.Default(instnode)
""")

test.write('test.c', """\
#if _WIN32
__declspec(dllexport)
#endif
int testlib(int n)
{
return n+1 ;
}
""")

testapp_src = """\
#if _WIN32
__declspec(dllimport)
#endif
int testlib(int n);
#include <stdio.h>
int main(int argc, char **argv)
{
int itest ;

itest = testlib(2) ;
printf("results: testlib(2) = %d\\n",itest) ;
return 0 ;
}
"""
test.write('testapp1.c', testapp_src)
test.write('testapp2.c', testapp_src)

platform = SCons.Platform.platform_default()


test.run(arguments = ['--tree=all'])

if platform == 'posix':
    # All (?) the files we expect will get created in the current directory
    files = [
    'libtest.so',
    'libtest.so.2',
    'libtest.so.2.5.4',
    'test.os',
    ]
    # All (?) the files we expect will get created in the 'installtest' directory
    instfiles = [
    'libtest.so',
    'libtest.so.2',
    'libtest.so.2.5.4',
    ]
elif platform == 'darwin':
    # All (?) the files we expect will get created in the current directory
    files = [
    'libtest.dylib',
    'libtest.2.5.4.dylib',
    'test.os',
    ]
    # All (?) the files we expect will get created in the 'installtest' directory
    instfiles = [
    'libtest.dylib',
    'libtest.2.5.4.dylib',
    ]
elif platform == 'cygwin':
    # All (?) the files we expect will get created in the current directory
    files = [
    'cygtest-2-5-4.dll',
    'libtest-2-5-4.dll.a',
    'libtest.dll.a',
    'test.os',
    ]
    # All (?) the files we expect will get created in the 'installtest' directory
    instfiles = [
    'cygtest-2-5-4.dll',
    'libtest-2-5-4.dll.a',
    'libtest.dll.a',
    ]
elif platform == 'win32':
    # All (?) the files we expect will get created in the current directory
    files = [
    'test.dll',
    'test.lib',
    'test.obj',
    ]
    # All (?) the files we expect will get created in the 'installtest' directory
    instfiles = [
    'test.dll',
    'test.lib',
    ]
elif platform == 'sunos':
    # All (?) the files we expect will get created in the current directory
    files = [
    'libtest.so',
    'libtest.so.2',
    'libtest.so.2.5.4',
    'so_test.os',
    ]
    # All (?) the files we expect will get created in the 'installtest' directory
    instfiles = [
    'libtest.so',
    'libtest.so.2',
    'libtest.so.2.5.4',
    ]
else:
    # All (?) the files we expect will get created in the current directory
    files= [
    'libtest.so',
    'test.os']
    # All (?) the files we expect will get created in the 'installtest' directory
    instfiles = []

for f in files:
    test.must_exist([ f])
for f in instfiles:
    test.must_exist(['installtest', f])

# modify test.c and make sure it can recompile when links already exist
test.write('test.c', """\
#if _WIN32
__declspec(dllexport)
#endif
int testlib(int n)
{
return n+11 ;
}
""")

test.run()

test.run(arguments = ['-c'])

for f in files:
    test.must_not_exist([ f])
for f in instfiles:
    test.must_not_exist(['installtest', f])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
