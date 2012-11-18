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

# copied from SCons/Platform/__init__.py
def platform_default():
    """Return the platform string for our execution environment.

    The returned value should map to one of the SCons/Platform/*.py
    files.  Since we're architecture independent, though, we don't
    care about the machine architecture.
    """
    osname = os.name
    if osname == 'java':
        osname = os._osType
    if osname == 'posix':
        if sys.platform == 'cygwin':
            return 'cygwin'
        elif sys.platform.find('irix') != -1:
            return 'irix'
        elif sys.platform.find('sunos') != -1:
            return 'sunos'
        elif sys.platform.find('hp-ux') != -1:
            return 'hpux'
        elif sys.platform.find('aix') != -1:
            return 'aix'
        elif sys.platform.find('darwin') != -1:
            return 'darwin'
        else:
            return 'posix'
    elif os.name == 'os2':
        return 'os2'
    else:
        return sys.platform

_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.write('SConstruct', """\
import os
env = Environment()
objs = env.SharedObject('test.c')
mylib = env.SharedLibrary('test', objs, SHLIBVERSION = '2.5.4')
env.Program(source=['testapp.c',mylib])
env.Program(target=['testapp2'],source=['testapp.c','libtest.dylib'])
instnode = env.Install("#/installtest",mylib)
env.Default(instnode)
""")

test.write('test.c', """\
int testlib(int n)
{
return n+1 ;
}
""")

test.write('testapp.c', """\
#include <stdio.h>
int main(int argc, char **argv)
{
int itest ;

itest = testlib(2) ;
printf("results: testlib(2) = %d\n",itest) ;
return 0 ;
}
""")

platform = platform_default()

test.run()

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

test.run(arguments = '-c')

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
