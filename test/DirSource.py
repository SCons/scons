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
This test tests directories as source files.  The correct behavior is that
any file under a directory acts like a source file of that directory.
In other words, if a build has a directory as a source file, any
change in any file under that directory should trigger a rebuild.
"""

import sys
import TestSCons


test = TestSCons.TestSCons()

test.subdir('bsig', [ 'bsig', 'subdir' ],
            'csig', [ 'csig', 'subdir' ])
test.write([ 'bsig', 'foo.txt' ], 'foo.txt\n')
test.write([ 'bsig', 'subdir', 'bar.txt'], 'bar.txt\n')
test.write([ 'csig', 'foo.txt' ], 'foo.txt\n')
test.write([ 'csig', 'subdir', 'bar.txt' ], 'bar.txt\n')
test.write('junk.txt', 'junk.txt\n')

test.write('SConstruct',
"""def writeTarget(target, source, env):
    f=open(str(target[0]), 'wb')
    f.write("stuff\\n")
    f.close()
    return 0

test_bld_dir = Builder(action=writeTarget, source_factory=Dir)
test_bld_file = Builder(action=writeTarget)
env_bsig = Environment()
env_bsig['BUILDERS']['TestDir'] = test_bld_dir
env_bsig['BUILDERS']['TestFile'] = test_bld_file

env_bsig.TargetSignatures('build')
env_bsig.TestFile(source='junk.txt', target='bsig/junk.out')
env_bsig.TestDir(source='bsig', target='bsig.out')

env_csig = env_bsig.Copy()
env_csig.TargetSignatures('content')
env_csig.TestFile(source='junk.txt', target='csig/junk.out')
env_csig.TestDir(source='csig', target='csig.out')
""")

test.run(arguments=".", stderr=None)
test.fail_test(test.read('bsig.out') != 'stuff\n')
test.fail_test(test.read('csig.out') != 'stuff\n')

test.up_to_date(arguments='bsig.out')
test.up_to_date(arguments='csig.out')

test.write([ 'bsig', 'foo.txt' ], 'foo2.txt\n')
test.not_up_to_date(arguments='bsig.out')

test.write([ 'csig', 'foo.txt' ], 'foo2.txt\n')
test.not_up_to_date(arguments='csig.out')

test.write([ 'bsig', 'foo.txt' ], 'foo3.txt\n')
test.not_up_to_date(arguments='bsig.out')

test.write([ 'bsig', 'subdir', 'bar.txt' ], 'bar2.txt\n')
test.not_up_to_date(arguments='bsig.out')

test.write([ 'csig', 'subdir', 'bar.txt' ], 'bar2.txt\n')
test.not_up_to_date(arguments='csig.out')

test.write('junk.txt', 'junk2.txt\n')
test.not_up_to_date(arguments='bsig.out')
# XXX For some reason, 'csig' is still reported as up to date.
# XXX Comment out this test until someone can look at it.
#test.not_up_to_date(arguments='csig.out')

test.pass_test()
