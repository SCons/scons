
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
Test that MSVS generation works when CPPPATH contains Dir nodes.
Also make sure changing CPPPATH causes rebuild.
"""

import os
import sys

import TestSConsMSVS

test = TestSConsMSVS.TestSConsMSVS()

if sys.platform != 'win32':
    msg = "Skipping Visual Studio test on non-Windows platform '%s'\n" % sys.platform
    test.skip_test(msg)

import SCons.Tool.MSCommon as msc
if not msc.msvs_exists():
    msg = "No MSVS toolchain found...skipping test\n"
    test.skip_test(msg)

SConscript_contents = """\
env = Environment()

sources = ['main.cpp']

program = env.Program(target = 'hello', source = sources)

if ARGUMENTS.get('moreincludes'):
  env.AppendUnique(CPPPATH = [env.Dir('.'), env.Dir('myincludes')])
else:
  env.AppendUnique(CPPPATH = [env.Dir('.')])

env.MSVSProject(target = 'Hello' + env['MSVSPROJECTSUFFIX'],
                srcs = sources,
                buildtarget = program,
                variant = 'Release')
"""

test.write('SConstruct', SConscript_contents)

test.write('main.cpp', """\
#include <stdio.h>
int main(void) {
  printf("hello, world!\\n");
}
""")

test.run()

if not os.path.exists(test.workpath('Hello.vcproj')) and \
        not os.path.exists(test.workpath('Hello.vcxproj')):
    test.fail_test("Failed to create Visual Studio project Hello.vcproj or Hello.vcxproj")
test.must_exist(test.workpath('Hello.sln'))
# vcproj = test.read('Test.vcproj', 'r')

test.run(arguments='moreincludes=1')
test.must_not_contain_any_line(test.stdout(), ['is up to date'])
test.must_contain_all_lines(test.stdout(), ['Adding', 'Hello'])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
