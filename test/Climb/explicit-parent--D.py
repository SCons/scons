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
Make sure explicit targets beginning with ../ get built correctly
by the -D option.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir(['subdir'])

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
def cat(env, source, target):
    target = str(target[0])
    with open(target, 'wb') as ofp:
        for src in source:
            with open(str(src), 'rb') as ifp:
                ofp.write(ifp.read())
env = Environment(tools=[], BUILDERS={'Cat':Builder(action=cat)})
env.Cat('f1.out', 'f1.in')
f2 = env.Cat('f2.out', 'f2.in')
Default(f2)
SConscript('subdir/SConscript', "env")
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")

test.write(['subdir', 'SConscript'], """\
Import("env")
f3 = env.Cat('f3.out', 'f3.in')
env.Cat('f4.out', 'f4.in')
Default(f3)
""")

test.write(['subdir', 'f3.in'], "subdir/f3.in\n")
test.write(['subdir', 'f4.in'], "subdir/f4.in\n")

test.run(chdir = 'subdir', arguments = '-D ../f1.out')

test.must_exist(test.workpath('f1.out'))
test.must_not_exist(test.workpath('f2.out'))
test.must_not_exist(test.workpath('dir', 'f3.out'))
test.must_not_exist(test.workpath('dir', 'f4.out'))


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
