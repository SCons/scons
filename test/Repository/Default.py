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

test.subdir('repository', ['repository', 'subdir'], 'work')

work_aaa_out = test.workpath('work', 'aaa.out')
work_bbb_out = test.workpath('work', 'bbb.out')
work_ccc_out = test.workpath('work', 'ccc.out')
work_subdir_ddd_out = test.workpath('work', 'subdir', 'ddd.out')
work_subdir_eee_out = test.workpath('work', 'subdir', 'eee.out')
work_subdir_fff_out = test.workpath('work', 'subdir', 'fff.out')

opts = "-Y " + test.workpath('repository')

#
test.write(['repository', 'SConstruct'], r"""
def copy(env, source, target):
    source = str(source[0])
    target = str(target[0])
    print('copy() < %s > %s' % (source, target))
    with open(target, "w") as ofp, open(source, "r") as ifp:
        ofp.write(ifp.read())

Build = Builder(action=copy)
env = Environment(BUILDERS={'Build':Build})
env.Build('aaa.out', 'aaa.in')
env.Build('bbb.out', 'bbb.in')
env.Build('ccc.out', 'ccc.in')
Default('bbb.out')
SConscript('subdir/SConscript', "env")
""")

test.write(['repository', 'subdir', 'SConscript'], r"""
Import("env")
Default('eee.out')
env.Build('ddd.out', 'ddd.in')
env.Build('eee.out', 'eee.in')
env.Build('fff.out', 'fff.in')
""")

test.write(['repository', 'aaa.in'], "repository/aaa.in\n")
test.write(['repository', 'bbb.in'], "repository/bbb.in\n")
test.write(['repository', 'ccc.in'], "repository/ccc.in\n")
test.write(['repository', 'subdir', 'ddd.in'], "repository/subdir/ddd.in\n")
test.write(['repository', 'subdir', 'eee.in'], "repository/subdir/eee.in\n")
test.write(['repository', 'subdir', 'fff.in'], "repository/subdir/fff.in\n")

# Make the entire repository non-writable, so we'll detect
# if we try to write into it accidentally.
test.writable('repository', 0)

test.run(chdir = 'work', options = opts, arguments = '')

test.fail_test(os.path.exists(work_aaa_out))
test.must_match(work_bbb_out, "repository/bbb.in\n", mode='r')
test.fail_test(os.path.exists(work_ccc_out))
test.fail_test(os.path.exists(work_subdir_ddd_out))
test.must_match(work_subdir_eee_out, "repository/subdir/eee.in\n", mode='r')
test.fail_test(os.path.exists(work_subdir_fff_out))

#
test.run(chdir = 'work', options = opts, arguments = '.')

test.must_match(work_aaa_out, "repository/aaa.in\n", mode='r')
test.must_match(work_ccc_out, "repository/ccc.in\n", mode='r')
test.must_match(work_subdir_ddd_out, "repository/subdir/ddd.in\n", mode='r')
test.must_match(work_subdir_fff_out, "repository/subdir/fff.in\n", mode='r')

test.up_to_date(chdir = 'work', options = opts, arguments = '.')

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
