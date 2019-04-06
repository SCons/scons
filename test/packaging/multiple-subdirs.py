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
Verify that we can build packages in different subdirectories.

Test case courtesy Andrew Smith.
"""

import TestSCons

test = TestSCons.TestSCons()

tar = test.detect('TAR', 'tar')

if not tar:
    test.skip_test('No TAR executable found; skipping test\n')

test.subdir('one', 'two', 'three')

test.write('SConstruct', """\
env = Environment(tools=['packaging', 'filesystem', 'tar'])
Export('env')
SConscript(dirs = ['one', 'two', 'three'])
""")

SConscript_template = """\
Import('*')

files = env.Install('/usr/bin', '%s.sh')

pkg = env.Package(NAME          = '%s',
                  VERSION       = '1.0.0',
                  PACKAGETYPE   = 'targz',
                  source        = [files]
                  )
"""

test.write(['one',   'SConscript'], SConscript_template % ('one', 'one'))
test.write(['two',   'SConscript'], SConscript_template % ('two', 'two'))
test.write(['three', 'SConscript'], SConscript_template % ('three', 'three'))

test.write(['one',   'one.sh'],     "one/one.sh\n")
test.write(['two',   'two.sh'],     "two/two.sh\n")
test.write(['three', 'three.sh'],   "three/three.sh\n")

test.run(arguments = '.')

test.must_match(['one', 'one-1.0.0', 'usr', 'bin', 'one.sh'], "one/one.sh\n")
test.must_match(['two', 'two-1.0.0', 'usr', 'bin', 'two.sh'], "two/two.sh\n")
test.must_match(['three', 'three-1.0.0', 'usr', 'bin', 'three.sh'], "three/three.sh\n")

test.must_exist(['one', 'one-1.0.0.tar.gz'])
test.must_exist(['two', 'two-1.0.0.tar.gz'])
test.must_exist(['three', 'three-1.0.0.tar.gz'])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
