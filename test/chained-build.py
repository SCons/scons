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

import TestSCons

test = TestSCons.TestSCons()

# During the development of 0.96, there was a --save-explain-info
# option for a brief moment that would surpress storing extra
# info in the .sconsign file(s).  At that time, this test used two
# working subdirectories to test both with and without the saved info.
# We eliminated the --save-explain-info option and the second working
# subdirectory here, but didn't go back and change all the filenames.
test.subdir('w1')

SConstruct1_contents = """\
def build(env, target, source):
    with open(str(target[0]), 'wt') as fo, open(str(source[0]), 'rt') as fi:
        fo.write(fi.read())

env=Environment(BUILDERS={'B' : Builder(action=build)})
env.B('foo.mid', 'foo.in')
"""

SConstruct2_contents = """\
def build(env, target, source):
    with open(str(target[0]), 'wt') as fo, open(str(source[0]), 'rt') as fi:
        fo.write(fi.read())

env=Environment(BUILDERS={'B' : Builder(action=build)})
env.B('foo.out', 'foo.mid')
"""

test.write(['w1', 'SConstruct1'], SConstruct1_contents)
test.write(['w1', 'SConstruct2'], SConstruct2_contents)
test.write(['w1', 'foo.in'], "foo.in 1")

test.run(
    chdir='w1',
    arguments="--max-drift=0 -f SConstruct1 foo.mid",
    stdout=test.wrap_stdout('build(["foo.mid"], ["foo.in"])\n'),
)
test.run(
    chdir='w1',
    arguments="--max-drift=0 -f SConstruct2 foo.out",
    stdout=test.wrap_stdout('build(["foo.out"], ["foo.mid"])\n'),
)
test.up_to_date(chdir='w1', options="--max-drift=0 -f SConstruct1", arguments="foo.mid")
test.up_to_date(chdir='w1', options="--max-drift=0 -f SConstruct2", arguments="foo.out")

test.sleep()  # delay for timestamps
test.write(['w1', 'foo.in'], "foo.in 2")

# Because we're using --max-drift=0, we use the cached csig value
# and think that foo.in hasn't changed even though it has on disk.
test.up_to_date(chdir='w1',
         options="--max-drift=0 -f SConstruct1",
         arguments="foo.mid")

# Now try with --max-drift disabled.  The build of foo.out should still
# be considered up-to-date, but the build of foo.mid now detects the
# change and rebuilds, too, which then causes a rebuild of foo.out.
test.up_to_date(
    chdir='w1', options="--max-drift=-1 -f SConstruct2", arguments="foo.out"
)
test.run(
    chdir='w1',
    arguments="--max-drift=-1 -f SConstruct1 foo.mid",
    stdout=test.wrap_stdout('build(["foo.mid"], ["foo.in"])\n'),
)
test.run(
    chdir='w1',
    arguments="--max-drift=-1 -f SConstruct2 foo.out",
    stdout=test.wrap_stdout('build(["foo.out"], ["foo.mid"])\n'),
)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
