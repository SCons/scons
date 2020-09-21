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

foo_c_src = "void foo() {}\n"

env = SCons.Defaults.DefaultEnvironment()
platform = SCons.Platform.platform_default()
tool_list = SCons.Platform.DefaultToolList(platform, env)

test = TestSCons.TestSCons()
if 'gnulink' in tool_list:
    versionflags = r".+ -Wl,-soname=libfoo.so.1( .+)+"
    soname='libfoo.so.4'
    sonameVersionFlags=r".+ -Wl,-soname=%s( .+)+" % soname

elif 'sunlink' in tool_list:
    versionflags = r".+ -h libfoo.so.1( .+)+"
    soname='libfoo.so.4'
    sonameVersionFlags=r".+ -h %s( .+)+" % soname
elif 'applelink' in tool_list:
    versionflags = r".+ 'libfoo.1.dylib'->'libfoo.1.2.3.dylib'(.+)+"
    soname='libfoo.4.dylib'
    sonameVersionFlags=r".+ '%s'->'libfoo.1.2.3.dylib'(.+)+" % soname
else:
    test.skip_test('No testable linkers found, skipping the test\n')


# stdout must not contain SHLIBVERSIONFLAGS if there is no SHLIBVERSION provided
test.write('foo.c', foo_c_src)
test.write('SConstruct', "SharedLibrary('foo','foo.c')\n")
test.run()
test.fail_test(test.match_re_dotall(test.stdout(), versionflags))
test.run(arguments = ['-c'])

# stdout must contain SHLIBVERSIONFLAGS if there is SHLIBVERSION provided
test = TestSCons.TestSCons()
test.write('foo.c', foo_c_src)
test.write('SConstruct', "SharedLibrary('foo','foo.c',SHLIBVERSION='1.2.3')\n")
test.run(stdout = versionflags, match = TestSCons.match_re_dotall)
test.run(arguments = ['-c'])

# stdout must contain SHLIBVERSIONFLAGS if there is SHLIBVERSION provided
test = TestSCons.TestSCons()
test.write('foo.c', foo_c_src)
test.write('SConstruct', """
SharedLibrary('foo','foo.c',SHLIBVERSION='1.2.3',SONAME='%s')
""" % soname)
test.run(stdout = sonameVersionFlags, match = TestSCons.match_re_dotall)
test.run(arguments = ['-c'])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
