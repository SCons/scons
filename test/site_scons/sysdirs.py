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

"""
Verify site_scons system dirs are getting loaded.
Uses an internal test fixture to get at the site_scons dirs.

TODO: it would be great to test if it can actually load site_scons
files from the system dirs, but the test harness can't put files in
those dirs (which may not even exist on a build system).
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
import SCons.Script
SCons.Script.Main.test_load_all_site_scons_dirs(Dir('.').get_internal_path())
""")

test.run(arguments = '-Q .')

import SCons.Platform
platform = SCons.Platform.platform_default()
if platform in ('win32', 'cygwin'):
    dir_to_check_for='Application Data'
elif platform in 'darwin':
    dir_to_check_for='Library'
else:
    dir_to_check_for='.scons'

if 'Loading site dir' not in test.stdout():
    print(test.stdout())
    test.fail_test()
if dir_to_check_for not in test.stdout():
    print(test.stdout())
    test.fail_test()

test.pass_test()

# end of file

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
