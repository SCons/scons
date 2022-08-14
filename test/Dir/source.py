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

"""
This test tests directories as source files.  The correct behavior is that
any file under a directory acts like a source file of that directory.
In other words, if a build has a directory as a source file, any
change in any file under that directory should trigger a rebuild.
"""

import TestSCons


test = TestSCons.TestSCons()

test.subdir('tstamp', [ 'tstamp', 'subdir' ],
            'content', [ 'content', 'subdir' ],
            'cmd-tstamp', [ 'cmd-tstamp', 'subdir' ],
            'cmd-content', [ 'cmd-content', 'subdir' ])

test.write('SConstruct', """\
DefaultEnvironment(tools=[])

def writeTarget(target, source, env):
    f = open(str(target[0]), 'w')
    f.write("stuff\\n")
    f.close()
    return 0

test_bld_dir = Builder(
    action=writeTarget, source_factory=Dir, source_scanner=DirScanner
)
test_bld_file = Builder(action=writeTarget)
env = Environment(tools=[])
env['BUILDERS']['TestDir'] = test_bld_dir
env['BUILDERS']['TestFile'] = test_bld_file

env_tstamp = env.Clone()
env_tstamp.Decider('timestamp-newer')
env_tstamp.TestFile(source='junk.txt', target='tstamp/junk.out')
env_tstamp.TestDir(source='tstamp', target='tstamp.out')
env_tstamp.Command('cmd-tstamp-noscan.out', 'cmd-tstamp', writeTarget)
env_tstamp.Command(
    'cmd-tstamp.out', 'cmd-tstamp', writeTarget, source_scanner=DirScanner
)

env_content = env.Clone()
env_content.Decider('content')
env_content.TestFile(source='junk.txt', target='content/junk.out')
env_content.TestDir(source='content', target='content.out')
env_content.Command('cmd-content-noscan.out', 'cmd-content', writeTarget)
env_content.Command(
    'cmd-content.out', 'cmd-content', writeTarget, source_scanner=DirScanner
)
""")

test.write(['tstamp', 'foo.txt'], 'foo.txt 1\n')
test.write(['tstamp', '#hash.txt'], 'hash.txt 1\n')
test.write(['tstamp', 'subdir', 'bar.txt'], 'bar.txt 1\n')
test.write(['tstamp', 'subdir', '#hash.txt'], 'hash.txt 1\n')
test.write(['content', 'foo.txt'], 'foo.txt 1\n')
test.write(['content', '#hash.txt'], 'hash.txt 1\n')
test.write(['content', 'subdir', 'bar.txt'], 'bar.txt 1\n')
test.write(['content', 'subdir', '#hash.txt'], 'hash.txt 1\n')
test.write(['cmd-tstamp', 'foo.txt'], 'foo.txt 1\n')
test.write(['cmd-tstamp', '#hash.txt'], 'hash.txt 1\n')
test.write(['cmd-tstamp', 'subdir', 'bar.txt'], 'bar.txt 1\n')
test.write(['cmd-tstamp', 'subdir', '#hash.txt'], 'hash.txt 1\n')
test.write(['cmd-content', 'foo.txt'], 'foo.txt 1\n')
test.write(['cmd-content', '#hash.txt'], '#hash.txt 1\n')
test.write(['cmd-content', 'subdir', 'bar.txt'], 'bar.txt 1\n')
test.write(['cmd-content', 'subdir', '#hash.txt'], 'hash.txt 1\n')
test.write('junk.txt', 'junk.txt\n')

test.run(arguments=".", stderr=None)
test.must_match('tstamp.out', 'stuff\n', mode='r')
test.must_match('content.out', 'stuff\n', mode='r')
test.must_match('cmd-tstamp.out', 'stuff\n', mode='r')
test.must_match('cmd-content.out', 'stuff\n', mode='r')
test.must_match('cmd-tstamp-noscan.out', 'stuff\n', mode='r')
test.must_match('cmd-content-noscan.out', 'stuff\n', mode='r')

test.up_to_date(arguments='tstamp.out')
test.up_to_date(arguments='content.out')
test.up_to_date(arguments='cmd-tstamp.out')
test.up_to_date(arguments='cmd-content.out')
test.up_to_date(arguments='cmd-tstamp-noscan.out')
test.up_to_date(arguments='cmd-content-noscan.out')

test.sleep()  # delay for timestamps

test.write(['tstamp', 'foo.txt'], 'foo.txt 2\n')
test.not_up_to_date(arguments='tstamp.out')

test.write(['tstamp', 'new.txt'], 'new.txt\n')
test.not_up_to_date(arguments='tstamp.out')

test.write(['content', 'foo.txt'], 'foo.txt 2\n')
test.not_up_to_date(arguments='content.out')

test.write(['content', 'new.txt'], 'new.txt\n')
test.not_up_to_date(arguments='content.out')

test.write(['cmd-tstamp', 'foo.txt'], 'foo.txt 2\n')
test.not_up_to_date(arguments='cmd-tstamp.out')
test.up_to_date(arguments='cmd-tstamp-noscan.out')

test.write(['cmd-tstamp', 'new.txt'], 'new.txt\n')
test.not_up_to_date(arguments='cmd-tstamp.out')
test.up_to_date(arguments='cmd-tstamp-noscan.out')

test.write(['cmd-content', 'foo.txt'], 'foo.txt 2\n')
test.not_up_to_date(arguments='cmd-content.out')
test.up_to_date(arguments='cmd-content-noscan.out')

test.write(['cmd-content', 'new.txt'], 'new.txt\n')
test.not_up_to_date(arguments='cmd-content.out')
test.up_to_date(arguments='cmd-content-noscan.out')

test.write(['tstamp', 'subdir', 'bar.txt'], 'bar.txt 2\n')
test.not_up_to_date(arguments='tstamp.out')

test.write(['tstamp', 'subdir', 'new.txt'], 'new.txt\n')
test.not_up_to_date(arguments='tstamp.out')

test.write(['content', 'subdir', 'bar.txt'], 'bar.txt 2\n')
test.not_up_to_date(arguments='content.out')

test.write(['content', 'subdir', 'new.txt'], 'new.txt\n')
test.not_up_to_date(arguments='content.out')

test.write(['cmd-tstamp', 'subdir', 'bar.txt'], 'bar.txt 2\n')
test.not_up_to_date(arguments='cmd-tstamp.out')
test.up_to_date(arguments='cmd-tstamp-noscan.out')

test.write(['cmd-tstamp', 'subdir', 'new.txt'], 'new.txt\n')
test.not_up_to_date(arguments='cmd-tstamp.out')
test.up_to_date(arguments='cmd-tstamp-noscan.out')

test.write(['cmd-content', 'subdir', 'bar.txt'], 'bar.txt 2\n')
test.not_up_to_date(arguments='cmd-content.out')
test.up_to_date(arguments='cmd-content-noscan.out')

test.write(['cmd-content', 'subdir', 'new.txt'], 'new.txt\n')
test.not_up_to_date(arguments='cmd-content.out')
test.up_to_date(arguments='cmd-content-noscan.out')

test.write('junk.txt', 'junk.txt 2\n')
test.not_up_to_date(arguments='tstamp.out')
test.not_up_to_date(arguments='content.out')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
