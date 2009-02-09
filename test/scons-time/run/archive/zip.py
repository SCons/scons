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
Verify basic generation of timing information from an input fake-project
.zip file.
"""

import sys

import TestSCons_time

test = TestSCons_time.TestSCons_time()

test.write_fake_scons_py()

test.write_sample_project('foo.zip')

try:
    import zipfile
    # There's a bug in the Python 2.1 zipfile library that makes it blow
    # up on 64-bit architectures, when trying to read normal 32-bit zip
    # files.  Check for it by trying to read the archive we just created,
    # and skipping the test gracefully if there's a problem.
    zf = zipfile.ZipFile('foo.zip', 'r')
    for name in zf.namelist():
        zf.read(name)
except ImportError:
    # This "shouldn't happen" because the early Python versions that
    # have no zipfile module don't support the scons-time script,
    # so the initialization above should short-circuit this test.
    # But just in case...
    fmt = "Python %s has no zipfile module.  Skipping test.\n"
    test.skip_test(fmt % sys.version[:3])
except zipfile.BadZipfile, e:
    if str(e)[:11] == 'Bad CRC-32 ':
        fmt = "Python %s zipfile module doesn't work on 64-bit architectures.  Skipping test.\n"
        test.skip_test(fmt % sys.version[:3])
    raise

test.run(arguments = 'run foo.zip')

test.must_exist('foo-000-0.log',
                'foo-000-0.prof',
                'foo-000-1.log',
                'foo-000-1.prof',
                'foo-000-2.log',
                'foo-000-2.prof')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
