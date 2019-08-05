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
Verify that toolpath works with VariantDir() for an SConscript.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('subdir', ['subdir', 'src'], ['subdir', 'src', 'tools'])

test.write('SConstruct', """\
VariantDir('build', 'subdir', duplicate=0)
SConscript('build/SConscript')
""")

test.write(['subdir', 'SConscript'], """\
env = Environment(tools = ['MyBuilder'], toolpath = ['src/tools'])
env.MyCopy('src/file.out', 'src/file.in')
""")

test.write(['subdir', 'src', 'file.in'], "subdir/src/file.in\n")

test.write(['subdir', 'src', 'tools', 'MyBuilder.py'], """\
from SCons.Script import Builder
def generate(env):
    def my_copy(target, source, env):
        with open(str(target[0]), 'wb') as f, open(str(source[0]), 'rb') as ifp:
            f.write(ifp.read())
    env['BUILDERS']['MyCopy'] = Builder(action = my_copy)

def exists(env):
    return 1
""")

test.run()

test.must_match(['build', 'src', 'file.out'], "subdir/src/file.in\n")

# We should look for the underlying tool in both the build/src/tools
# (which doesn't exist) and subdir/src/tools (which still does).  If we
# don't, the following would fail because the execution directory is
# now relative to the created VariantDir.
test.run()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
