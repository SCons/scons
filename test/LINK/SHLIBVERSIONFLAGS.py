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
import re

import TestSCons
import SCons.Platform
import SCons.Defaults

linkers = [ 'gnulink', 'cyglink', 'sunlink' ]

foo_c_src = "void foo() {}\n"

env = SCons.Defaults.DefaultEnvironment()
platform = SCons.Platform.platform_default()
tool_list = SCons.Platform.DefaultToolList(platform, env)

test = TestSCons.TestSCons()
test.write('foo.c', foo_c_src)
test.write('SConstruct', "SharedLibrary('foo','foo.c',SHLIBVERSION='1.2.3')\n")

if 'gnulink' in tool_list:
    test.run(stdout = r".+ -Wl,-Bsymbolic -Wl,-soname=libfoo.so.1( .+)+", match = TestSCons.match_re_dotall)
    test.run(arguments = ['-c'])
elif 'sunlink' in tool_list:
    test.run(stdout = r".+ -h libfoo.so.1( .+)+", match = TestSCons.match_re_dotall)
    test.run(arguments = ['-c'])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
