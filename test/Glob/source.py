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
Verify that use of the Glob() function within a VariantDir() returns the
file Nodes in the source directory when the source= keyword argument is
specified (and duplicate=0 is specified for the VariantDir()).
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('src', 'var1', 'var2')

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = Environment(tools=[]) 

def concatenate(target, source, env):
    with open(str(target[0]), 'wb') as ofp:
        for s in source:
            with open(str(s), 'rb') as ifp:
                ofp.write(ifp.read())

env['BUILDERS']['Concatenate'] = Builder(action=concatenate)

Export("env")

VariantDir('var1', 'src', duplicate=0)
VariantDir('var2', 'src', duplicate=0)

SConscript('var1/SConscript')
SConscript('var2/SConscript')
""")

test.write(['var1', 'SConscript'], """\
Import("env")

env.Concatenate('f.out', sorted(Glob('f[45].in', source=True),
                                key=lambda t: t.name))
""")

test.write(['var2', 'SConscript'], """\
Import("env")

f_in = sorted(Glob('f[67].in'), key=lambda a: a.name)
env.Concatenate('f.out', f_in)
""")

test.write(['src', 'f1.in'], "src/f1.in\n")
test.write(['src', 'f2.in'], "src/f2.in\n")

test.write(['src', 'f4.in'], "src/f4.in\n")
test.write(['src', 'f5.in'], "src/f5.in\n")
test.write(['src', 'f6.in'], "src/f6.in\n")
test.write(['src', 'f7.in'], "src/f7.in\n")

test.run(arguments = '.')

test.must_match(['var1', 'f.out'], "src/f4.in\nsrc/f5.in\n")
test.must_match(['var2', 'f.out'], "src/f6.in\nsrc/f7.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
