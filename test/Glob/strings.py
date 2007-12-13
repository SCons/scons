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
Verify that use of the Glob() function with the strings= option works
when they're used in the same SConscript file (and therefore the same
directory) as input to a Builder call.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('src')

test.write('SConstruct', """\
BuildDir('var1', 'src')
BuildDir('var2', 'src')

SConscript('var1/SConscript')
SConscript('var2/SConscript')
""")

test.write(['src', 'SConscript'], """\
env = Environment() 

def concatenate(target, source, env):
    fp = open(str(target[0]), 'wb')
    for s in source:
        fp.write(open(str(s), 'rb').read())
    fp.close()

env['BUILDERS']['Concatenate'] = Builder(action=concatenate)

f_in = Glob('f*.in', strings=True)
f_in.sort()
env.Concatenate('f.out', f_in)
""")

test.write(['src', 'f1.in'], "src/f1.in\n")
test.write(['src', 'f2.in'], "src/f2.in\n")
test.write(['src', 'f3.in'], "src/f3.in\n")

test.run(arguments = '.')

test.must_match(['var1', 'f.out'], "src/f1.in\nsrc/f2.in\nsrc/f3.in\n")
test.must_match(['var2', 'f.out'], "src/f1.in\nsrc/f2.in\nsrc/f3.in\n")

test.pass_test()
