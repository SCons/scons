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

test.subdir('repository', ['repository', 'src'],
            'work', ['work', 'src'])

repository_aaa_out = test.workpath('repository', 'aaa.out')
repository_build_bbb_1 = test.workpath('repository', 'build', 'bbb.1')
repository_build_bbb_2 = test.workpath('repository', 'build', 'bbb.2')
work_aaa_mid = test.workpath('work', 'aaa.mid')
work_aaa_out = test.workpath('work', 'aaa.out')
work_build_bbb_1 = test.workpath('work', 'build', 'bbb.1')
work_build_bbb_2 = test.workpath('work', 'build', 'bbb.2')

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
env = Environment(BUILDERS={'Build':Build}, BBB='bbb')
env.Build('aaa.mid', 'aaa.in')
env.Build('aaa.out', 'aaa.mid')
Local('aaa.out')

Export("env")
VariantDir('build', 'src')
SConscript('build/SConscript')
""")

test.write(['repository', 'src', 'SConscript'], r"""
def bbb_copy(env, source, target):
    target = str(target[0])
    print('bbb_copy()')
    with open(target, 'w') as fo, open('build/bbb.1', 'r') as fi:
        fo.write(fi.read())

Import("env")
env.Build('bbb.1', 'bbb.0')
env.Local('${BBB}.1')
env.Command('bbb.2', 'bbb.x', bbb_copy)
env.Depends('bbb.2', 'bbb.1')
""")

test.write(['repository', 'aaa.in'], "repository/aaa.in\n")
test.write(['repository', 'src', 'bbb.0'], "repository/src/bbb.0\n")
test.write(['repository', 'src', 'bbb.x'], "repository/src/bbb.x\n")

#
test.run(chdir = 'repository', options = opts, arguments = '.')

test.must_match(repository_aaa_out, "repository/aaa.in\n", mode='r')
test.must_match(repository_build_bbb_2, "repository/src/bbb.0\n", mode='r')

test.up_to_date(chdir = 'repository', options = opts, arguments = '.')

# Make the entire repository non-writable, so we'll detect
# if we try to write into it accidentally.
test.writable('repository', 0)

#
test.run(chdir = 'work', options = opts, arguments = 'aaa.out build/bbb.2')

test.fail_test(os.path.exists(work_aaa_mid))
test.must_match(work_aaa_out, "repository/aaa.in\n", mode='r')
test.must_match(work_build_bbb_1, "repository/src/bbb.0\n", mode='r')
test.fail_test(os.path.exists(work_build_bbb_2))

#
test.write(['work', 'aaa.in'], "work/aaa.in\n")

#
test.run(chdir = 'work', options = opts, arguments = '.')

test.must_match(work_aaa_mid, "work/aaa.in\n", mode='r')
test.must_match(work_aaa_out, "work/aaa.in\n", mode='r')

test.up_to_date(chdir = 'work', options = opts, arguments = '.')

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
