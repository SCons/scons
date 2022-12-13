#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.subdir('repository', ['repository', 'src'],
            'work1', ['work1', 'src'],
            'work2', ['work2', 'src'])

opts = "-Y " + test.workpath('repository')

#
test.write(['repository', 'SConstruct'], r"""
DefaultEnvironment(tools=[])  # test speedup
VariantDir('build0', 'src', duplicate=0)
VariantDir('build1', 'src', duplicate=1)
SConscript('build0/SConscript')
SConscript('build1/SConscript')
""")

test.write(['repository', 'src', 'SConscript'], r"""
def cat(env, source, target):
    target = str(target[0])
    source = list(map(str, source))
    print('cat(%s) > %s' % (source, target))
    with open(target, "w") as ofp:
        for src in source:
            with open(src, "r") as ifp:
                ofp.write(ifp.read())

env = Environment(BUILDERS={'Build':Builder(action=cat)})
env.Build('aaa.mid', 'aaa.in')
env.Build('bbb.mid', 'bbb.in')
env.Build('ccc.mid', 'ccc.in')
env.Build('output', ['aaa.mid', 'bbb.mid', 'ccc.mid'])
""")

test.write(['repository', 'src', 'aaa.in'], "repository/src/aaa.in\n")
test.write(['repository', 'src', 'bbb.in'], "repository/src/bbb.in\n")
test.write(['repository', 'src', 'ccc.in'], "repository/src/ccc.in\n")

# Make the entire repository non-writable, so we'll detect
# if we try to write into it accidentally.
test.writable('repository', 0)

#
test.run(chdir = 'work1', options = opts, arguments = '.')

test.must_match(['work1', 'build0', 'output'],
"""repository/src/aaa.in
repository/src/bbb.in
repository/src/ccc.in
""", mode='r')

test.fail_test(os.path.exists('work1/build0/aaa.in'))
test.fail_test(os.path.exists('work1/build0/bbb.in'))
test.fail_test(os.path.exists('work1/build0/ccc.in'))
test.fail_test(not os.path.exists('work1/build0/aaa.mid'))
test.fail_test(not os.path.exists('work1/build0/bbb.mid'))
test.fail_test(not os.path.exists('work1/build0/ccc.mid'))

test.must_match(['work1', 'build1', 'output'],
"""repository/src/aaa.in
repository/src/bbb.in
repository/src/ccc.in
""", mode='r')

test.fail_test(not os.path.exists('work1/build1/aaa.in'))
test.fail_test(not os.path.exists('work1/build1/bbb.in'))
test.fail_test(not os.path.exists('work1/build1/ccc.in'))
test.fail_test(not os.path.exists('work1/build1/aaa.mid'))
test.fail_test(not os.path.exists('work1/build1/bbb.mid'))
test.fail_test(not os.path.exists('work1/build1/ccc.mid'))

test.up_to_date(chdir = 'work1', options = opts, arguments = '.')

#
test.write(['work1', 'src', 'bbb.in'], "work1/src/bbb.in\n")

test.run(chdir = 'work1', options = opts, arguments = '.')

test.must_match(['work1', 'build0', 'output'],
"""repository/src/aaa.in
work1/src/bbb.in
repository/src/ccc.in
""", mode='r')

test.fail_test(os.path.exists('work1/build0/aaa.in'))
test.fail_test(os.path.exists('work1/build0/bbb.in'))
test.fail_test(os.path.exists('work1/build0/ccc.in'))
test.fail_test(not os.path.exists('work1/build0/aaa.mid'))
test.fail_test(not os.path.exists('work1/build0/bbb.mid'))
test.fail_test(not os.path.exists('work1/build0/ccc.mid'))

test.must_match(['work1', 'build1', 'output'],
"""repository/src/aaa.in
work1/src/bbb.in
repository/src/ccc.in
""", mode='r')

test.fail_test(not os.path.exists('work1/build1/aaa.in'))
test.fail_test(not os.path.exists('work1/build1/bbb.in'))
test.fail_test(not os.path.exists('work1/build1/ccc.in'))
test.fail_test(not os.path.exists('work1/build1/aaa.mid'))
test.fail_test(not os.path.exists('work1/build1/bbb.mid'))
test.fail_test(not os.path.exists('work1/build1/ccc.mid'))

test.up_to_date(chdir = 'work1', options = opts, arguments = '.')

# Now build the stuff in the repository,
# and redo the above steps in a fresh work directory.
test.writable('repository', 1)

test.run(chdir = 'repository', arguments = '.')

test.writable('repository', 0)

#
test.run(chdir = 'work2', options = opts, arguments = '.')

test.fail_test(os.path.exists('work2/build0/aaa.in'))
test.fail_test(os.path.exists('work2/build0/bbb.in'))
test.fail_test(os.path.exists('work2/build0/ccc.in'))
test.fail_test(os.path.exists('work2/build0/aaa.mid'))
test.fail_test(os.path.exists('work2/build0/bbb.mid'))
test.fail_test(os.path.exists('work2/build0/ccc.mid'))
test.fail_test(os.path.exists('work2/build0/output'))

test.fail_test(not os.path.exists('work2/build1/aaa.in'))
test.fail_test(not os.path.exists('work2/build1/bbb.in'))
test.fail_test(not os.path.exists('work2/build1/ccc.in'))
test.fail_test(os.path.exists('work2/build1/aaa.mid'))
test.fail_test(os.path.exists('work2/build1/bbb.mid'))
test.fail_test(os.path.exists('work2/build1/ccc.mid'))
test.fail_test(os.path.exists('work2/build1/output'))

test.up_to_date(chdir = 'work2', options = opts, arguments = '.')

#
test.write(['work2', 'src', 'bbb.in'], "work2/src/bbb.in\n")

test.run(chdir = 'work2', options = opts, arguments = '.')

test.must_match(['work2', 'build0', 'output'],
"""repository/src/aaa.in
work2/src/bbb.in
repository/src/ccc.in
""", mode='r')

test.fail_test(os.path.exists('work2/build0/aaa.in'))
test.fail_test(os.path.exists('work2/build0/bbb.in'))
test.fail_test(os.path.exists('work2/build0/ccc.in'))
test.fail_test(os.path.exists('work2/build0/aaa.mid'))
test.fail_test(not os.path.exists('work2/build0/bbb.mid'))
test.fail_test(os.path.exists('work2/build0/ccc.mid'))

test.must_match(['work2', 'build1', 'output'],
"""repository/src/aaa.in
work2/src/bbb.in
repository/src/ccc.in
""", mode='r')

test.fail_test(not os.path.exists('work2/build1/aaa.in'))
test.fail_test(not os.path.exists('work2/build1/bbb.in'))
test.fail_test(not os.path.exists('work2/build1/ccc.in'))
test.fail_test(os.path.exists('work2/build1/aaa.mid'))
test.fail_test(not os.path.exists('work2/build1/bbb.mid'))
test.fail_test(os.path.exists('work2/build1/ccc.mid'))

test.up_to_date(chdir = 'work2', options = opts, arguments = '.')

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
