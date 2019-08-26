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

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.subdir('subdir', ['subdir', 'ccc'])

ccc_ccc_in = os.path.join('ccc', 'ccc.in')
subdir_SConscript = os.path.join('subdir', 'SConscript')

test.write('SConstruct', r"""
SConscript(r'%s')
""" % subdir_SConscript)

test.write(subdir_SConscript, r"""
def cat(env, source, target):
    target = str(target[0])
    with open(target, "wb") as f:
        for src in source:
            with open(str(src), "rb") as ifp:
                f.write(ifp.read())

b = Builder(action=cat, suffix='.out', src_suffix='.in')
env = Environment(BUILDERS={'Build':b})
env.Build('aaa.in')
n = env.Build('bbb.in', 'bbb.input')
env.Build(n)
env.Build(source = r'%s')
""" % ccc_ccc_in)

test.write(['subdir', 'aaa.in'], "subdir/aaa.in\n")
test.write(['subdir', 'bbb.input'], "subdir/bbb.input\n")
test.write(['subdir', 'ccc', 'ccc.in'], "subdir/ccc/ccc.in\n")

#
test.run(arguments = '.')

test.fail_test(test.read(['subdir', 'aaa.out']) != b"subdir/aaa.in\n")
test.fail_test(test.read(['subdir', 'bbb.out']) != b"subdir/bbb.input\n")
test.fail_test(test.read(['subdir', 'ccc', 'ccc.out']) != b"subdir/ccc/ccc.in\n")

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
