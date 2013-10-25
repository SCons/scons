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

import unittest
import os.path
import os
import sys

import SCons.Errors
from SCons.Tool.PharLapCommon import *

class PharLapCommonTestCase(unittest.TestCase):
    def test_addPathIfNotExists(self):
        """Test the addPathIfNotExists() function"""
        env_dict = { 'FOO' : os.path.normpath('/foo/bar') + os.pathsep + \
                     os.path.normpath('/baz/blat'),
                     'BAR' : os.path.normpath('/foo/bar') + os.pathsep + \
                     os.path.normpath('/baz/blat'),
                     'BLAT' : [ os.path.normpath('/foo/bar'),
                                os.path.normpath('/baz/blat') ] }
        addPathIfNotExists(env_dict, 'FOO', os.path.normpath('/foo/bar'))
        addPathIfNotExists(env_dict, 'BAR', os.path.normpath('/bar/foo'))
        addPathIfNotExists(env_dict, 'BAZ', os.path.normpath('/foo/baz'))
        addPathIfNotExists(env_dict, 'BLAT', os.path.normpath('/baz/blat'))
        addPathIfNotExists(env_dict, 'BLAT', os.path.normpath('/baz/foo'))

        assert env_dict['FOO'] == os.path.normpath('/foo/bar') + os.pathsep + \
               os.path.normpath('/baz/blat'), env_dict['FOO']
        assert env_dict['BAR'] == os.path.normpath('/bar/foo') + os.pathsep + \
               os.path.normpath('/foo/bar') + os.pathsep + \
               os.path.normpath('/baz/blat'), env_dict['BAR']
        assert env_dict['BAZ'] == os.path.normpath('/foo/baz'), env_dict['BAZ']
        assert env_dict['BLAT'] == [ os.path.normpath('/baz/foo'),
                                     os.path.normpath('/foo/bar'),
                                     os.path.normpath('/baz/blat') ], env_dict['BLAT' ]

if __name__ == "__main__":
    suite = unittest.makeSuite(PharLapCommonTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
