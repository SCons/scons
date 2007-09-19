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
            'csig', [ 'csig', 'subdir' ],
            'cmd-bsig', [ 'cmd-bsig', 'subdir' ],
            'cmd-csig', [ 'cmd-csig', 'subdir' ])

test.write('SConstruct', """\
def writeTarget(target, source, env):
    f=open(str(target[0]), 'wb')
    f.write("stuff\\n")
    f.close()
    return 0

test_bld_dir = Builder(action=writeTarget,
                       source_factory=Dir,
                       source_scanner=DirScanner)
test_bld_file = Builder(action=writeTarget)
env = Environment()
env['BUILDERS']['TestDir'] = test_bld_dir
env['BUILDERS']['TestFile'] = test_bld_file

env_bsig = env.Clone()
env_bsig.TargetSignatures('build')
env_bsig.TestFile(source='junk.txt', target='bsig/junk.out')
env_bsig.TestDir(source='bsig', target='bsig.out')
env_bsig.Command('cmd-bsig-noscan.out', 'cmd-bsig', writeTarget)
env_bsig.Command('cmd-bsig.out', 'cmd-bsig', writeTarget,
                 source_scanner=DirScanner)

env_csig = env.Clone()
env_csig.TargetSignatures('content')
env_csig.TestFile(source='junk.txt', target='csig/junk.out')
env_csig.TestDir(source='csig', target='csig.out')
env_csig.Command('cmd-csig-noscan.out', 'cmd-csig', writeTarget)
env_csig.Command('cmd-csig.out', 'cmd-csig', writeTarget,
                 source_scanner=DirScanner)
""")

test.write([ 'bsig', 'foo.txt' ], 'foo.txt 1\n')
test.write([ 'bsig', '#hash.txt' ], 'hash.txt 1\n')
test.write([ 'bsig', 'subdir', 'bar.txt'], 'bar.txt 1\n')
test.write([ 'bsig', 'subdir', '#hash.txt'], 'hash.txt 1\n')
test.write([ 'csig', 'foo.txt' ], 'foo.txt 1\n')
test.write([ 'csig', '#hash.txt' ], 'hash.txt 1\n')
test.write([ 'csig', 'subdir', 'bar.txt' ], 'bar.txt 1\n')
test.write([ 'csig', 'subdir', '#hash.txt' ], 'hash.txt 1\n')
test.write([ 'cmd-bsig', 'foo.txt' ], 'foo.txt 1\n')
test.write([ 'cmd-bsig', '#hash.txt' ], 'hash.txt 1\n')
test.write([ 'cmd-bsig', 'subdir', 'bar.txt' ], 'bar.txt 1\n')
test.write([ 'cmd-bsig', 'subdir', '#hash.txt' ], 'hash.txt 1\n')
test.write([ 'cmd-csig', 'foo.txt' ], 'foo.txt 1\n')
test.write([ 'cmd-csig', '#hash.txt' ], '#hash.txt 1\n')
test.write([ 'cmd-csig', 'subdir', 'bar.txt' ], 'bar.txt 1\n')
test.write([ 'cmd-csig', 'subdir', '#hash.txt' ], 'hash.txt 1\n')
test.write('junk.txt', 'junk.txt\n')

test.run(arguments=".", stderr=None)
test.must_match('bsig.out', 'stuff\n')
test.must_match('csig.out', 'stuff\n')
test.must_match('cmd-bsig.out', 'stuff\n')
test.must_match('cmd-csig.out', 'stuff\n')
test.must_match('cmd-bsig-noscan.out', 'stuff\n')
test.must_match('cmd-csig-noscan.out', 'stuff\n')

test.up_to_date(arguments='bsig.out')
test.up_to_date(arguments='csig.out')
test.up_to_date(arguments='cmd-bsig.out')
test.up_to_date(arguments='cmd-csig.out')
test.up_to_date(arguments='cmd-bsig-noscan.out')
test.up_to_date(arguments='cmd-csig-noscan.out')

test.write([ 'bsig', 'foo.txt' ], 'foo.txt 2\n')
test.not_up_to_date(arguments='bsig.out')

test.write([ 'bsig', 'new.txt' ], 'new.txt\n')
test.not_up_to_date(arguments='bsig.out')

test.write([ 'csig', 'foo.txt' ], 'foo.txt 2\n')
test.not_up_to_date(arguments='csig.out')

test.write([ 'csig', 'new.txt' ], 'new.txt\n')
test.not_up_to_date(arguments='csig.out')

test.write([ 'cmd-bsig', 'foo.txt' ], 'foo.txt 2\n')
test.not_up_to_date(arguments='cmd-bsig.out')
test.up_to_date(arguments='cmd-bsig-noscan.out')

test.write([ 'cmd-bsig', 'new.txt' ], 'new.txt\n')
test.not_up_to_date(arguments='cmd-bsig.out')
test.up_to_date(arguments='cmd-bsig-noscan.out')

test.write([ 'cmd-csig', 'foo.txt' ], 'foo.txt 2\n')
test.not_up_to_date(arguments='cmd-csig.out')
test.up_to_date(arguments='cmd-csig-noscan.out')

test.write([ 'cmd-csig', 'new.txt' ], 'new.txt\n')
test.not_up_to_date(arguments='cmd-csig.out')
test.up_to_date(arguments='cmd-csig-noscan.out')

test.write([ 'bsig', 'subdir', 'bar.txt' ], 'bar.txt 2\n')
test.not_up_to_date(arguments='bsig.out')

test.write([ 'bsig', 'subdir', 'new.txt' ], 'new.txt\n')
test.not_up_to_date(arguments='bsig.out')

test.write([ 'csig', 'subdir', 'bar.txt' ], 'bar.txt 2\n')
test.not_up_to_date(arguments='csig.out')

test.write([ 'csig', 'subdir', 'new.txt' ], 'new.txt\n')
test.not_up_to_date(arguments='csig.out')

test.write([ 'cmd-bsig', 'subdir', 'bar.txt' ], 'bar.txt 2\n')
test.not_up_to_date(arguments='cmd-bsig.out')
test.up_to_date(arguments='cmd-bsig-noscan.out')

test.write([ 'cmd-bsig', 'subdir', 'new.txt' ], 'new.txt\n')
test.not_up_to_date(arguments='cmd-bsig.out')
test.up_to_date(arguments='cmd-bsig-noscan.out')

test.write([ 'cmd-csig', 'subdir', 'bar.txt' ], 'bar.txt 2\n')
test.not_up_to_date(arguments='cmd-csig.out')
test.up_to_date(arguments='cmd-csig-noscan.out')

test.write([ 'cmd-csig', 'subdir', 'new.txt' ], 'new.txt\n')
test.not_up_to_date(arguments='cmd-csig.out')
test.up_to_date(arguments='cmd-csig-noscan.out')

test.write('junk.txt', 'junk.txt 2\n')
test.not_up_to_date(arguments='bsig.out')
test.not_up_to_date(arguments='csig.out')

test.pass_test()
