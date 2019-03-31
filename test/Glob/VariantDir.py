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
Verify that default use of the Glob() function within a VariantDir()
finds the local file Nodes.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('src')
test.subdir('src/sub1')

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
VariantDir('var1', 'src')
VariantDir('var2', 'src')

SConscript('var1/SConscript')
SConscript('var2/SConscript')
SConscript('var1/sub1/SConscript')
SConscript('var2/sub1/SConscript')
SConscript('src/sub1/SConscript', src_dir = 'src', variant_dir = 'var3', duplicate=0)
""")

test.write(['src', 'SConscript'], """\
env = Environment(tools=[]) 

def concatenate(target, source, env):
    with open(str(target[0]), 'wb') as ofp:
        for s in source:
            with open(str(s), 'rb') as ifp:
                ofp.write(ifp.read())

env['BUILDERS']['Concatenate'] = Builder(action=concatenate)

env.Concatenate('f.out', sorted(Glob('f*.in'), key=lambda t: t.name))
env.Concatenate('fex.out', sorted(Glob('f*.in', exclude = 'f1.in'), key=lambda t: t.name))
""")

test.write(['src', 'sub1', 'SConscript'], """\
env = Environment(tools=[])

def concatenate(target, source, env):
    with open(str(target[0]), 'wb') as ofp:
        for s in source:
            with open(str(s), 'rb') as ifp:
                ofp.write(ifp.read())

env['BUILDERS']['Concatenate'] = Builder(action=concatenate)

env.Concatenate('f.out', sorted(Glob('f*.in'), key=lambda t: t.name))
env.Concatenate('fex.out', sorted(Glob('f*.in', exclude = 'f1.in'), key=lambda t: t.name))
""")

test.write(['src', 'f1.in'], "src/f1.in\n")
test.write(['src', 'f2.in'], "src/f2.in\n")
test.write(['src', 'f3.in'], "src/f3.in\n")
test.write(['src', 'sub1', 'f1.in'], "src/sub1/f1.in\n")
test.write(['src', 'sub1', 'f2.in'], "src/sub1/f2.in\n")
test.write(['src', 'sub1', 'f3.in'], "src/sub1/f3.in\n")


test.run(arguments = '.')

test.must_match(['var1', 'f.out'], "src/f1.in\nsrc/f2.in\nsrc/f3.in\n")
test.must_match(['var2', 'f.out'], "src/f1.in\nsrc/f2.in\nsrc/f3.in\n")
test.must_match(['var1', 'fex.out'], "src/f2.in\nsrc/f3.in\n")
test.must_match(['var2', 'fex.out'], "src/f2.in\nsrc/f3.in\n")

test.must_match(['var1', 'sub1', 'f.out'], "src/sub1/f1.in\nsrc/sub1/f2.in\nsrc/sub1/f3.in\n")
test.must_match(['var2', 'sub1', 'f.out'], "src/sub1/f1.in\nsrc/sub1/f2.in\nsrc/sub1/f3.in\n")
test.must_match(['var1', 'sub1', 'fex.out'], "src/sub1/f2.in\nsrc/sub1/f3.in\n")
test.must_match(['var2', 'sub1', 'fex.out'], "src/sub1/f2.in\nsrc/sub1/f3.in\n")

test.must_match(['var3', 'sub1', 'f.out'], "src/sub1/f1.in\nsrc/sub1/f2.in\nsrc/sub1/f3.in\n")
test.must_match(['var3', 'sub1', 'fex.out'], "src/sub1/f2.in\nsrc/sub1/f3.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
