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
This is a regression test for a bug in earlier versions of the
--interactive command line option (specifically the original prototype
submitted by Adam Simpkins, who created this test case).

It tests to make sure that cached state is cleared between files for
nodes in both the build tree and the source tree when VariantDirs are used.
This is needed especially with VariantDirs created with duplicate=0, since
the scanners scan the files in the source tree.  Any cached implicit
deps must be cleared on the source files.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.subdir('src',
            ['src', 'inc'])

# Create the top-level SConstruct file
test.write('SConstruct', """
BUILD_ENV = Environment()
Export('BUILD_ENV')

hdr_dir = '#build/include'
BUILD_ENV['HDR_DIR'] = hdr_dir
BUILD_ENV.Append(CPPPATH = hdr_dir)

BUILD_ENV.VariantDir('build', 'src', duplicate = 0)
SConscript('build/SConscript')

Command('1', [], Touch('$TARGET'))
Command('2', [], Touch('$TARGET'))
""")

# Create the src/SConscript file
test.write(['src', 'SConscript'], """
Import('BUILD_ENV')
BUILD_ENV.Install(BUILD_ENV['HDR_DIR'], ['inc/foo.h'])
BUILD_ENV.Program('foo', ['foo.c'])
""")

# Create src/foo.c
test.write(['src', 'foo.c'], """
#include <stdio.h>

#define FOO_PRINT_STRING "Hello from foo.c"

int main(void)
{
    printf(FOO_PRINT_STRING "\\n");
    return 0;
}
""")

# Create src/inc/foo.h
test.write(['src', 'inc', 'foo.h'], """
#ifndef INCLUDED_foo_h
#define INCLUDED_foo_h

#define FOO_PRINT_STRING "Hello from foo.h"

#endif /* INCLUDED_foo_h */
""")

# Start scons, to build only "build/foo"
build_foo_exe   = os.path.join('build', 'foo' + TestSCons._exe)
_build_foo_exe_ = '"%s"' % build_foo_exe.replace('\\', '\\\\')
abs_foo_exe     = test.workpath(build_foo_exe)

scons = test.start(arguments = '--interactive', combine=1)



# Build build/foo
scons.send('build %(_build_foo_exe_)s 1\n' % locals())

test.wait_for(test.workpath('1'))

# Run foo, and make sure it prints correctly
test.run(program = abs_foo_exe, stdout = 'Hello from foo.c\n')



# Update foo.c to include foo.h
test.write(['src', 'foo.c'], """
#include "foo.h"
#include <stdio.h>

int main(void)
{
    printf(FOO_PRINT_STRING "\\n");
    return 0;
}
""")

# Build build/foo
scons.send('build %(_build_foo_exe_)s 2\n' % locals())

test.wait_for(test.workpath('2'))

# Run foo, and make sure it prints correctly
test.run(program = abs_foo_exe, stdout = 'Hello from foo.h\n')



scons.send('exit\n')

test.finish(scons)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
