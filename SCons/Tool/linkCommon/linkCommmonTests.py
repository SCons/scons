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
Unit tests for linkCommon package
"""

import unittest

from SCons.Environment import Environment


class SharedLibraryTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_shlib_symlink_emitter(self):
        """Test shlib_symlink_emitter() """
        env = Environment(tools=['gnulink'])

        target = env.SharedLibrary('lib', 'lib.c', SHLIBPREFIX='lib', SHLIBSUFFIX=".so")

        target_name = str(target[0])
        self.assertEqual(str(target_name), 'liblib.so', "Expected target 'liblib.so' != '%s'" % target_name)

        target = env.SharedLibrary('xyz', 'lib.c', SHLIBPREFIX='xyz', SHLIBSUFFIX=".so", SHLIBVERSION='1.2.3')

        t0 = target[0]
        target_name = str(t0)

        assert target_name == 'xyzxyz.so.1.2.3', "Expected target 'xyzxyz.so.1.2.3' != '%s'" % target_name

        if hasattr(t0.attributes, 'shliblinks'):
            (soname_symlink, t0_1) = t0.attributes.shliblinks[0]
            (shlib_noversion_symlink, t0_2) = t0.attributes.shliblinks[1]

            self.assertEqual(t0_1, t0, "soname_symlink target is not target[0]")
            self.assertEqual(t0_2, t0, "shlib_noversion_symlink target is not target[0]")
            self.assertEqual(str(soname_symlink), 'xyzxyz.so.1',
                             "soname symlink is not 'xyzxyz.so.1': '%s'" % str(soname_symlink))
            self.assertEqual(str(shlib_noversion_symlink), 'xyzxyz.so',
                             "shlib_noversion_symlink is not 'xyzxyz.so': '%s'" % str(shlib_noversion_symlink))

        else:
            self.fail('Target xyzxyz.so.1.2.3 has no .attributes.shliblinks')


if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
