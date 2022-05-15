#!/usr/bin/env python
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
Test the content-timestamp decider (formerly known as md5-timestamp)
correctly detects modification of a source file which is a symlink.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

if not test.platform_has_symlink():
    test.skip_test('Symbolic links not reliably available on this platform, skipping test.\n')

# a dummy "compiler" for the builder
test.write('build.py', r"""
import sys

with open(sys.argv[1], 'wb') as ofp:
    for infile in sys.argv[2:]:
        with open (infile, 'rb') as ifp:
            ofp.write(ifp.read())
sys.exit(0)
""")

test.write('SConstruct', """
DefaultEnvironment(tools=[])
Build = Builder(action=r'%(_python_)s build.py $TARGET $SOURCES')
env = Environment(tools=[], BUILDERS={'Build': Build})
env.Decider('content-timestamp')
env.Build(target='match1.out', source='match1.in')
env.Build(target='match2.out', source='match2.in')
""" % locals())

test.write('match1.in', 'match1.in\n')
test.symlink('match1.in', 'match2.in')

test.run(arguments='.')
test.must_match('match1.out', 'match1.in\n')
test.must_match('match2.out', 'match1.in\n')

# first make sure some time has elapsed, so a low-granularity timestamp
# doesn't fail to trigger
test.sleep()
# Now update the source file contents, both targets should rebuild
test.write('match1.in', 'match2.in\n')

test.run(arguments='.')
test.must_match('match1.out', 'match2.in\n', message="match1.out not rebuilt\n")
test.must_match('match2.out', 'match2.in\n', message="match2.out not rebuilt\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
