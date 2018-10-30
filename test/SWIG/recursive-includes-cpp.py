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
for pre_req in ['swig', 'python']:
    if not test.where_is(pre_req):
        test.skip_test('Can not find installed "' + pre_req + '", skipping test.%s' % os.linesep)

python, python_include, python_libpath, python_lib = \
             test.get_platform_python_info(python_h_required=True)

if sys.platform == 'win32':
    python_lib = os.path.dirname(sys.executable) + "/libs/" + ('python%d%d'%(sys.version_info[0],sys.version_info[1])) + '.lib'
    if( not os.path.isfile(python_lib)):
        test.skip_test('Can not find python lib at "' + python_lib + '", skipping test.%s' % os.linesep)

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
test.write('SConstruct', """\
import sysconfig
import sys
import os

env = Environment(
    """ + TARGET_ARCH + """
    SWIGFLAGS = [
        '-python'
    ],
    CPPPATH = [ 
        sysconfig.get_config_var("INCLUDEPY")
    ],
    SHLIBPREFIX = "",
    tools = [ 'default', 'swig' ]
)

if sys.platform == 'darwin':
    env['LIBS']=['python%d.%d'%(sys.version_info[0],sys.version_info[1])]
    env.Append(LIBPATH=[sysconfig.get_config_var("LIBDIR")])
elif sys.platform == 'win32':
    env.Append(LIBS=['python%d%d'%(sys.version_info[0],sys.version_info[1])])
    env.Append(LIBPATH=[os.path.dirname(sys.executable) + "/libs"])

env.SharedLibrary(
    'mod',
    [
        "mod.i",
        "main.c",
    ]
)
""")

if sys.platform == 'win32':
    object_suffix = ".obj"
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

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
