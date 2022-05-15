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

import hashlib
import os
import TestSCons
from SCons.Util import ALLOWED_HASH_FORMATS, DEFAULT_HASH_FORMATS

# Test passing the hash format by command-line.
INVALID_ALGORITHM = 'testfailure'

for algorithm in [*DEFAULT_HASH_FORMATS, INVALID_ALGORITHM, None]:
    test = TestSCons.TestSCons()
    test.dir_fixture('hash-format')

    # Expect failure due to an unsupported/invalid algorithm.
    # The error message however changes if SCons detects that the host system doesn't support one or more algorithms
    # Primary reason the message changes is so user doesn't have to start with unsupported algorithm A and then attempt
    # to switch to unsupported algorithm B.
    # On normal systems (allowed=default) this will output a fixed message, but on FIPS-enabled or other weird systems
    # that don't have default allowed algorithms, it informs the user of the mismatch _and_ the currently supported
    # algorithms on the system they're using.
    # In Python 3.9 this becomes somewhat obselete as the hashlib is informed we don't use hashing for security but
    # for loose integrity.
    if algorithm == INVALID_ALGORITHM:
        if ALLOWED_HASH_FORMATS == DEFAULT_HASH_FORMATS:
            test.run('--hash-format=%s .' % algorithm, stderr=r"""
scons: \*\*\* Hash format "{}" is not supported by SCons. Only the following hash formats are supported: {}
File "[^"]+", line \d+, in \S+
""".format(algorithm, ', '.join(DEFAULT_HASH_FORMATS)), status=2, match=TestSCons.match_re)
        else:
            test.run('--hash-format=%s .' % algorithm, stderr=r"""
scons: \*\*\* Hash format "{}" is not supported by SCons. SCons supports more hash formats than your local system is reporting; SCons supports: {}. Your local system only supports: {}
File "[^"]+", line \d+, in \S+
""".format(algorithm, ', '.join(DEFAULT_HASH_FORMATS), ', '.join(ALLOWED_HASH_FORMATS)), status=2, match=TestSCons.match_re)
        continue
    elif algorithm is not None:
        if algorithm in ALLOWED_HASH_FORMATS:
            expected_dblite = test.workpath('.sconsign_%s.dblite' % algorithm)
            test.run('--hash-format=%s .' % algorithm)
        else:
            test.run('--hash-format=%s' % algorithm, stderr=r"""
scons: \*\*\* While hash format "{}" is supported by SCons, the local system indicates only the following hash formats are supported by the hashlib library: {}
File "[^"]+", line \d+, in \S+
Error in atexit._run_exitfuncs:
Traceback \(most recent call last\):
  File "[^"]+", line \d+, in \S+
    assert csig == '[a-z0-9]+', csig
AssertionError: [a-z0-9]+
""".format(algorithm, ', '.join(ALLOWED_HASH_FORMATS)), status=2, match=TestSCons.match_re)
            continue
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
