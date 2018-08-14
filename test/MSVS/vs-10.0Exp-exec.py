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

"""
Test that we can actually build a simple program using our generated
Visual Studio 10.0 project (.vcxproj) and solution (.sln) files
using Visual C++ 10.0 Express edition.
"""

import os
import sys

import TestSConsMSVS

test = TestSConsMSVS.TestSConsMSVS()

if sys.platform != 'win32':
    msg = "Skipping Visual Studio test on non-Windows platform '%s'\n" % sys.platform
    test.skip_test(msg)

msvs_version = '10.0Exp'

if not msvs_version in test.msvs_versions():
    msg = "Visual Studio %s not installed; skipping test.\n" % msvs_version
    test.skip_test(msg)



# Let SCons figure out the Visual Studio environment variables for us and
# print out a statement that we can exec to suck them into our external
# environment so we can execute devenv and really try to build something.

test.run(arguments = '-n -q -Q -f -', stdin = """\
env = Environment(tools = ['msvc'], MSVS_VERSION='%(msvs_version)s')
if env.WhereIs('cl'):
    print("os.environ.update(%%s)" %% repr(env['ENV']))
""" % locals())

if(test.stdout() == ""):
    msg = "Visual Studio %s missing cl.exe; skipping test.\n" % msvs_version
    test.skip_test(msg)

exec(test.stdout())



test.subdir('sub dir')

test.write(['sub dir', 'SConstruct'], """\
env=Environment(MSVS_VERSION = '%(msvs_version)s')

env.MSVSProject(target = 'foo.vcxproj',
                srcs = ['foo.c'],
                buildtarget = 'foo.exe',
                variant = 'Release')

env.Program('foo.c')
""" % locals())

test.write(['sub dir', 'foo.c'], r"""
int
main(int argc, char *argv)
{
    printf("foo.c\n");
    exit (0);
}
""")

test.run(chdir='sub dir', arguments='.')

test.vcproj_sys_path(test.workpath('sub dir', 'foo.vcxproj'))

import SCons.Platform.win32
system_dll_path = os.path.join( SCons.Platform.win32.get_system_root(), 'System32' )
os.environ['PATH'] = os.environ['PATH'] + os.pathsep + system_dll_path

test.run(chdir='sub dir',
         program=[test.get_msvs_executable(msvs_version)],
         arguments=['foo.sln', '/build', 'Release'])

test.run(program=test.workpath('sub dir', 'foo'), stdout="foo.c\n")



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
