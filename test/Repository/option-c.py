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

repository_aaa_in = test.workpath('repository', 'aaa.in')
repository_aaa_mid = test.workpath('repository', 'aaa.mid')
repository_aaa_out = test.workpath('repository', 'aaa.out')
repository_bbb_in = test.workpath('repository', 'bbb.in')
repository_bbb_mid = test.workpath('repository', 'bbb.mid')
repository_bbb_out = test.workpath('repository', 'bbb.out')
repository_subdir_ccc_in = test.workpath('repository', 'subdir', 'ccc.in')
repository_subdir_ccc_mid = test.workpath('repository', 'subdir', 'ccc.mid')
repository_subdir_ccc_out = test.workpath('repository', 'subdir', 'ccc.out')
repository_subdir_ddd_in = test.workpath('repository', 'subdir', 'ddd.in')
repository_subdir_ddd_mid = test.workpath('repository', 'subdir', 'ddd.mid')
repository_subdir_ddd_out = test.workpath('repository', 'subdir', 'ddd.out')

work_aaa_in = test.workpath('work', 'aaa.in')
work_aaa_mid = test.workpath('work', 'aaa.mid')
work_aaa_out = test.workpath('work', 'aaa.out')
work_bbb_in = test.workpath('work', 'bbb.in')
work_bbb_mid = test.workpath('work', 'bbb.mid')
work_bbb_out = test.workpath('work', 'bbb.out')
work_subdir_ccc_in = test.workpath('work', 'subdir', 'ccc.in')
work_subdir_ccc_mid = test.workpath('work', 'subdir', 'ccc.mid')
work_subdir_ccc_out = test.workpath('work', 'subdir', 'ccc.out')
work_subdir_ddd_in = test.workpath('work', 'subdir', 'ddd.in')
work_subdir_ddd_mid = test.workpath('work', 'subdir', 'ddd.mid')
work_subdir_ddd_out = test.workpath('work', 'subdir', 'ddd.out')

opts = "-Y " + test.workpath('repository')

#
test.write(['repository', 'SConstruct'], r"""
def copy(env, source, target):
    source = str(source[0])
    target = str(target[0])
    print('copy() < %s > %s' % (source, target))
    with open(target, 'w') as ofp, open(source, 'r') as ifp:
        ofp.write(ifp.read())

Build = Builder(action=copy)
env = Environment(BUILDERS={'Build':Build})
env.Build('aaa.mid', 'aaa.in')
env.Build('aaa.out', 'aaa.mid')
env.Build('bbb.mid', 'bbb.in')
env.Build('bbb.out', 'bbb.mid')
SConscript('subdir/SConscript', "env")
""")

test.write(['repository', 'subdir', 'SConscript'], r"""
Import("env")
env.Build('ccc.mid', 'ccc.in')
env.Build('ccc.out', 'ccc.mid')
env.Build('ddd.mid', 'ddd.in')
env.Build('ddd.out', 'ddd.mid')
""")

test.write(repository_aaa_in, "repository/aaa.in\n")
test.write(repository_bbb_in, "repository/bbb.in\n")

test.write(repository_subdir_ccc_in, "repository/subdir/ccc.in\n")
test.write(repository_subdir_ddd_in, "repository/subdir/ddd.in\n")

# Make the entire repository non-writable, so we'll detect
# if we try to write into it accidentally.
test.writable('repository', 0)

# Build in the work subdirectory first, so that it really
# builds all of the target files locally instead of possibly
# copying them from the Repository.
test.run(chdir = 'work', options = opts, arguments = '.')

test.must_match(work_aaa_mid, "repository/aaa.in\n", mode='r')
test.must_match(work_aaa_out, "repository/aaa.in\n", mode='r')
test.must_match(work_bbb_mid, "repository/bbb.in\n", mode='r')
test.must_match(work_bbb_out, "repository/bbb.in\n", mode='r')
test.must_match(work_subdir_ccc_mid, "repository/subdir/ccc.in\n", mode='r')
test.must_match(work_subdir_ccc_out, "repository/subdir/ccc.in\n", mode='r')
test.must_match(work_subdir_ddd_mid, "repository/subdir/ddd.in\n", mode='r')
test.must_match(work_subdir_ddd_out, "repository/subdir/ddd.in\n", mode='r')

test.up_to_date(chdir = 'work', options = opts, arguments = '.')

# Make the repository writable, so we can build in it.
test.writable('repository', 1)

# Now build everything in the repository.
test.run(chdir = 'repository', options = opts, arguments = '.')

test.must_match(repository_aaa_mid, "repository/aaa.in\n", mode='r')
test.must_match(repository_aaa_out, "repository/aaa.in\n", mode='r')
test.must_match(repository_bbb_mid, "repository/bbb.in\n", mode='r')
test.must_match(repository_bbb_out, "repository/bbb.in\n", mode='r')
test.must_match(repository_subdir_ccc_mid, "repository/subdir/ccc.in\n", mode='r')
test.must_match(repository_subdir_ccc_out, "repository/subdir/ccc.in\n", mode='r')
test.must_match(repository_subdir_ddd_mid, "repository/subdir/ddd.in\n", mode='r')
test.must_match(repository_subdir_ddd_out, "repository/subdir/ddd.in\n", mode='r')

test.up_to_date(chdir = 'repository', options = opts, arguments = '.')

# Make the entire repository non-writable again, so we'll detect
# if we try to write into it accidentally.
test.writable('repository', 0)

#
test.run(chdir = 'work', options = opts + ' -c', arguments = 'bbb.mid bbb.out')

test.must_match(work_aaa_mid, "repository/aaa.in\n", mode='r')
test.must_match(work_aaa_out, "repository/aaa.in\n", mode='r')
test.fail_test(os.path.exists(work_bbb_mid))
test.fail_test(os.path.exists(work_bbb_out))
test.must_match(work_subdir_ccc_mid, "repository/subdir/ccc.in\n", mode='r')
test.must_match(work_subdir_ccc_out, "repository/subdir/ccc.in\n", mode='r')
test.must_match(work_subdir_ddd_mid, "repository/subdir/ddd.in\n", mode='r')
test.must_match(work_subdir_ddd_out, "repository/subdir/ddd.in\n", mode='r')

#
test.run(chdir = 'work', options = opts + ' -c', arguments = 'subdir')

test.must_match(work_aaa_mid, "repository/aaa.in\n", mode='r')
test.must_match(work_aaa_out, "repository/aaa.in\n", mode='r')
test.fail_test(os.path.exists(work_bbb_mid))
test.fail_test(os.path.exists(work_bbb_out))
test.fail_test(os.path.exists(work_subdir_ccc_mid))
test.fail_test(os.path.exists(work_subdir_ccc_out))
test.fail_test(os.path.exists(work_subdir_ddd_mid))
test.fail_test(os.path.exists(work_subdir_ddd_out))

#
test.run(chdir = 'work', options = opts + ' -c', arguments = '.')

test.fail_test(os.path.exists(work_aaa_mid))
test.fail_test(os.path.exists(work_aaa_out))
test.fail_test(os.path.exists(work_bbb_mid))
test.fail_test(os.path.exists(work_bbb_out))
test.fail_test(os.path.exists(work_subdir_ccc_mid))
test.fail_test(os.path.exists(work_subdir_ccc_out))
test.fail_test(os.path.exists(work_subdir_ddd_mid))
test.fail_test(os.path.exists(work_subdir_ddd_out))

# Double-check that nothing in the repository got deleted.
test.must_match(repository_aaa_mid, "repository/aaa.in\n", mode='r')
test.must_match(repository_aaa_out, "repository/aaa.in\n", mode='r')
test.must_match(repository_bbb_mid, "repository/bbb.in\n", mode='r')
test.must_match(repository_bbb_out, "repository/bbb.in\n", mode='r')
test.must_match(repository_subdir_ccc_mid, "repository/subdir/ccc.in\n", mode='r')
test.must_match(repository_subdir_ccc_out, "repository/subdir/ccc.in\n", mode='r')
test.must_match(repository_subdir_ddd_mid, "repository/subdir/ddd.in\n", mode='r')
test.must_match(repository_subdir_ddd_out, "repository/subdir/ddd.in\n", mode='r')

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
