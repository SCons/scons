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
Ensure that SharedLibrary builder with SHLIBVERSION='0.1.2' can build its target
in a subdirectory containing .so.0.1.2 in name. 

This is regression test for issue mentioned in:
http://thread.gmane.org/gmane.comp.programming.tools.scons.user/27081
"""

import TestSCons
import os
import sys

import SCons.Platform
import SCons.Defaults

test = TestSCons.TestSCons()

test.write('foo.c', """
#if _WIN32
__declspec(dllexport)
#endif
int foo() { return 0; }
""")

test.write('main.c', """
#if _WIN32
__declspec(dllimport)
#endif
int foo();
int main(void)
{
  return foo();
}
""")

env = SCons.Defaults.DefaultEnvironment()
platform = SCons.Platform.platform_default()
tool_list = SCons.Platform.DefaultToolList(platform, env)

if 'applelink' in tool_list:
    subdir = 'blah.0.1.2.dylib.blah'
elif 'cyglink' in tool_list:
    subdir = 'blah-0-1-2.dll.a.blah'
else:
    subdir = 'blah.so.0.1.2.blah'

test.write('SConstruct', """
env = Environment()
env.AppendUnique(LIBPATH = [ '%s' ])
env.SharedLibrary('%s/foo', 'foo.c', SHLIBVERSION = '0.1.2')
env.Program('main.c', LIBS=['foo'])
""" % (subdir,subdir))

test.run(arguments = ['--tree=all'])

if platform == 'cygwin' or platform == 'win32':
    # PATH is used to search for *.dll libraries on windows
    path = os.environ.get('PATH','')
    if path: path = path + os.pathsep
    path = path + test.workpath(subdir)
    os.environ['PATH'] = path

if os.name == 'posix':
    os.environ['LD_LIBRARY_PATH'] = subdir
if sys.platform.find('irix') != -1:
    os.environ['LD_LIBRARYN32_PATH'] = subdir

test.run(program = test.workpath('main'))

if 'gnulink' in tool_list:
    # All (?) the files we expect will get created in the current directory
    files = [
    'libfoo.so',
    'libfoo.so.0',
    'libfoo.so.0.1.2',
    ]
    obj = 'foo.os'
elif 'applelink' in tool_list:
    # All (?) the files we expect will get created in the current directory
    files = [
    'libfoo.dylib',
    'libfoo.0.1.2.dylib',
    ]
    obj = 'foo.os'
elif 'cyglink' in tool_list:
    # All (?) the files we expect will get created in the current directory
    files = [
    'cygfoo-0-1-2.dll',
    'libfoo-0-1-2.dll.a',
    'libfoo.dll.a',
    ]
    obj = 'foo.os'
elif 'mslink' in tool_list:
    # All (?) the files we expect will get created in the current directory
    files = [
    'foo.dll',
    'foo.lib',
    ]
    obj = 'foo.obj'
elif 'sunlink' in tool_list:
    # All (?) the files we expect will get created in the current directory
    files = [
    'libfoo.so',
    'libfoo.so.0',
    'libfoo.so.0.1.2',
    ]
    obj = 'so_foo.os'
else:
    # All (?) the files we expect will get created in the current directory
    files= [
    'libfoo.so',
    ]
    obj = 'foo.os'

test.must_exist([ obj ])
for f in files:
    test.must_exist([ subdir, f ])

test.run(arguments = ['-c'])

test.must_not_exist([ obj ])
for f in files:
    test.must_not_exist([ subdir, f ])

test.must_exist(['foo.c'])
test.must_exist(['SConstruct'])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
