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
elif 'sunlink' in tool_list:
    versionflags = r".+ -h libfoo.so.1( .+)+"
else:
    test.skip_test('No testable linkers found, skipping the test\n')


# We expect stdout to not contain LDMODULEVERSIONFLAGS if there is no
# SHLIBVERSION nor LDMODULEVERSION provided
test.write('foo.c', foo_c_src)
test.write('SConstruct', "LoadableModule('foo','foo.c')\n")
test.run()
test.fail_test(test.match_re_dotall(test.stdout(), versionflags))
test.run(arguments = ['-c'])

for versionvar in ['SHLIBVERSION', 'LDMODULEVERSION']:
    test = TestSCons.TestSCons()
    test.write('foo.c', foo_c_src)
    test.write('SConstruct', "LoadableModule('foo','foo.c',%s='1.2.3')\n" % versionvar)
    test.run(stdout = versionflags, match = TestSCons.match_re_dotall)
    test.run(arguments = ['-c'])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
