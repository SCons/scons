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
Verify that SWIG include directives produce the correct dependencies
in cases of recursive inclusion.
"""

import os
import sys
import TestSCons
import TestCmd
from SCons.Defaults import DefaultEnvironment

DefaultEnvironment( tools = [ 'swig' ] )

test = TestSCons.TestSCons()

# Check for prerequisites of this test.
if not test.where_is('swig'):
    test.skip_test('Can not find installed "swig", skipping test.%s' % os.linesep)

python, python_include, python_libpath, python_lib = \
             test.get_platform_python_info(python_h_required=True)

if TestCmd.IS_WINDOWS:
    if not os.path.isfile(os.path.join(python_libpath, python_lib)):
        test.skip_test(f"Can not find python lib {python_libh!r}, skipping test.\n")

test.write("recursive.h", """\
/* An empty header file. */
""")

test.write("main.h", """\
#include "recursive.h"
""")

test.write("main.c", """\
#include "main.h"
""")

test.write("mod.i", """\
%module mod

%include "main.h"

#include "main.h"
""")


if TestCmd.IS_WINDOWS:
    if TestCmd.IS_64_BIT:
        TARGET_ARCH = "TARGET_ARCH = 'x86_64',"
    else:
        TARGET_ARCH = "TARGET_ARCH = 'x86',"
else:
    TARGET_ARCH = ""
test.write('SConstruct', f"""\
import os
import sys
import sysconfig

DefaultEnvironment()
env = Environment(
    {TARGET_ARCH}
    SWIGFLAGS=['-python'],
    CPPPATH=[sysconfig.get_config_var("INCLUDEPY")],
    SHLIBPREFIX="",
    tools=['default', 'swig'],
)

if sys.platform == 'darwin':
    env['LIBS'] = [f'python{sys.version_info.major}.{sys.version_info.minor}']
    env.Append(LIBPATH=[sysconfig.get_config_var("LIBDIR")])
elif sys.platform == 'win32':
    env.Append(LIBS=[f'python{sys.version_info.major}{sys.version_info.minor}.lib'])
    env.Append(LIBPATH=[os.path.dirname(sys.executable) + "/libs"])

env.SharedLibrary('mod', ["mod.i", "main.c"])
""")

if sys.platform == 'win32':
    object_suffix = ".obj"
elif sys.platform == 'sunos5':
    object_suffix = ".pic.o"
else:
    object_suffix = ".os"

expectMain = """\
+-main%s
  +-main.c
  +-main.h
  +-recursive.h""" % object_suffix

expectMod = """\
+-mod_wrap%s
  +-mod_wrap.c
  | +-mod.i
  | +-main.h
  | +-recursive.h""" % object_suffix

# Validate that the recursive dependencies are found with SWIG scanning first.
test.run( arguments = '--tree=all mod_wrap'+object_suffix +' main'+object_suffix)

test.must_contain_all( test.stdout(), expectMain )
test.must_contain_all( test.stdout(), expectMod )


# Validate that the recursive dependencies are found consistently.
test.run( arguments = '--tree=all main'+object_suffix +' mod_wrap'+object_suffix)

test.must_contain_all( test.stdout(), expectMain )
test.must_contain_all( test.stdout(), expectMod )

test.run()
test.up_to_date()

test.pass_test()
