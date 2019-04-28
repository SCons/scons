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
Verify that we can Clean() files in a VariantDir() that's underneath us.
(At one point this didn't work because we were using str() instead of
abspath to remove the files, which would interfere with the removal by
returning a path relative to the VariantDir(), not the top-level SConstruct
directory, if the source directory was the top-level directory.)
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
VariantDir('build0', '.', duplicate=0)
VariantDir('build1', '.', duplicate=1)

def build_sample(target, source, env):
    targetdir = str(target[0].dir)
    target = str(target[0])
    with open(target, 'w') as ofd, open(str(source[0]), 'r') as ifd:
        ofd.write(ifd.read())
    with open(targetdir+'/sample.junk', 'w') as f:
        f.write('Side effect!\\n')

t0 = Command("build0/sample.out", "sample.in", build_sample)
t1 = Command("build1/sample.out", "sample.in", build_sample)

Clean(t0, 'build0/sample.junk')
Clean(t1, 'build1/sample.junk')
""")

test.write('sample.in', "sample.in\n")

test.run(arguments = '.')

test.must_match(['build0', 'sample.out'], "sample.in\n", mode='r')
test.must_exist(['build0', 'sample.junk'])

test.must_match(['build1', 'sample.out'], "sample.in\n", mode='r')
test.must_exist(['build1', 'sample.junk'])

test.run(arguments = '-c .')

test.must_not_exist(['build', 'sample.out'])
test.must_not_exist(['build', 'sample.junk'])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
