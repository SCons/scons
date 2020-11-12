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

import os
import TestSCons

test = TestSCons.TestSCons()

test.dir_fixture('hash-format')

# Test passing the hash format by command-line.
for algorithm in ['md5', 'sha1', 'sha256', None]:
    if algorithm is not None:
        expected_dblite = test.workpath('.sconsign_%s.dblite' % algorithm)
        test.run('--hash-format=%s .' % algorithm)
    else:
        # The SConsign file in the hash-format folder has logic to call
        # SCons.Util.set_hash_format('sha256') if the default algorithm is
        # being used. So this test of algorithm==None effectively validates
        # that the sconsign db includes the algorithm name if that function is
        # used instead of --hash-format. This is useful because consumers are
        # expected to call that function if they want to opt into stronger
        # hashes.
        expected_dblite = test.workpath('.sconsign_sha256.dblite')
        test.run('.')

    assert os.path.isfile(expected_dblite), \
        "%s does not exist when running algorithm %s" % (expected_dblite,
                                                         algorithm)

    test.run('-C .')
    os.unlink(expected_dblite)

# In this case, the SConstruct file will use SetOption to override the hash
# format.
test.run()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
